#!/usr/bin/env python3
"""
Fuggoleges hirdetesvideo gyartosor allokepekbol.

A lanc:
    1. TTS         ElevenLabs /with-timestamps  -> mp3 + KARAKTERSZINTU idobelyeg
    2. Szavak      a karakter-idobelyegekbol szo szintu idozites (nincs whisper, nincs csuszas)
    3. Kep         Ken Burns mozgatas az allokepekbol (PIL elovagas + ffmpeg zoompan)
    4. Felirat     .ass karaoke, szavankenti narancs kiemelessel
    5. Osszerakas  ffmpeg: klippek + narracio + zenei alap + raegetett felirat

Hasznalat:
    python make.py config/script-a.json                 # eles, ElevenLabs-szel
    python make.py config/script-a.json --offline       # kulcs nelkul, becsult idozitessel

Kornyezeti valtozo elesben:
    ELEVENLABS_API_KEY
"""

import argparse
import base64
import json
import math
import os
import re
import shutil
import subprocess
import sys

# Windows-konzolon (cp1252) egy emoji kiirasa UnicodeEncodeError-ral az EGESZ
# renderelest leallitja. Inkabb "?" legyen a konzolon, mint osszeomlas.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
# A skillben a make.py a scripts/ alatt ul, az assets/ egy szinttel feljebb.
# Ha rossz helyen keresi, a PIL csendben egy apro bitmap-fontra esik vissza.
FONTS_DIR = next((p for p in (os.path.join(HERE, "assets", "fonts"),
                              os.path.join(HERE, "..", "assets", "fonts"))
                  if os.path.isdir(p)), os.path.join(HERE, "assets", "fonts"))
FONTS_DIR = os.path.abspath(FONTS_DIR)


def load_env(path=None):
    """KULCS=ertek soronkent, # a komment. Alap: a szkript melletti .env.
    A mar beallitott valtozot nem irja felul (setdefault)."""
    path = path or os.path.join(HERE, ".env")
    if not os.path.exists(path):
        return
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


load_env()

W, H, FPS = 1080, 1920, 30
ASPECT = W / H

# --- brand ---------------------------------------------------------------
# ASS szinek BBGGRR sorrendben (!), nem RRGGBB
C_WHITE = "&H00FFFFFF"
C_ORANGE = "&H000775F5"   # #F57507
C_BLACK = "&H00000000"


def _hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def set_brand_colors(cfg):
    """client.json: "accent" (kiemelt szo), "cta_bg", "cta_fg" -- #RRGGBB.
    Ha nincs megadva, marad a narancs alap."""
    global C_ORANGE, ORANGE_RGB, DARKTEXT
    if cfg.get("accent"):
        r, g, b = _hex_rgb(cfg["accent"])
        C_ORANGE = f"&H00{b:02X}{g:02X}{r:02X}"
    if cfg.get("cta_bg"):
        ORANGE_RGB = _hex_rgb(cfg["cta_bg"])
    if cfg.get("cta_fg"):
        DARKTEXT = _hex_rgb(cfg["cta_fg"])


# =========================================================================
# 1. TTS
# =========================================================================

def tts_elevenlabs(text, voice_id, model, out_mp3, settings=None, language=None):
    """Visszaad: (karakterek listaja, kezdo idok, vege idok)."""
    import urllib.error
    import urllib.request

    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        sys.exit("HIANYZIK az ELEVENLABS_API_KEY (build/.env). Vagy: --offline")
    if not key.startswith("sk_"):
        sys.exit(
            "A kulcs nem 'sk_'-val kezdodik.\n"
            "Valoszinuleg a kulcs AZONOSITOJAT masoltad be a kulcs helyett.\n"
            "ElevenLabs -> API Keys -> uj kulcs (vagy rotate). A teljes 'sk_...' ertek\n"
            "CSAK letrehozaskor latszik egyszer - utana mar csak az azonosito."
        )

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps"
    payload = {
        "text": text,
        "model_id": model,
        "voice_settings": settings or {"stability": 0.45, "similarity_boost": 0.75},
    }
    # A multilingual_v2 NEM fogad el nyelvkodot - a szovegbol talalgat, es magyarra
    # ez hallhatoan rossz kiejtest ad. A turbo_v2_5 / flash_v2_5 / v3 elfogadja.
    if language:
        payload["language_code"] = language
    body = json.dumps(payload).encode()

    req = urllib.request.Request(
        url, data=body,
        headers={"xi-api-key": key, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        try:
            msg = json.loads(raw)["detail"]["message"]
        except Exception:
            msg = raw[:500]
        sys.exit(f"ElevenLabs HTTP {e.code}: {msg}")

    with open(out_mp3, "wb") as f:
        f.write(base64.b64decode(data["audio_base64"]))

    # FONTOS: az "alignment" kell, NEM a "normalized_alignment".
    # A normalizalt valtozat lecsereli a magyar o" es u" betuket (o, u) -
    # a feliratban "elokeszites" lenne "elokeszites" helyett. Az "alignment"
    # karakterei pontosan az eredeti szoveget adjak vissza.
    al = data.get("alignment") or data["normalized_alignment"]
    return al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]


def tts_offline(text, out_mp3):
    """
    Kulcs nelkuli elonezet: megbecsuli az idoziteseket es nema savot general.
    Csak a vagas/felirat ellenorzesere valo - a valodi ritmust a TTS adja.
    """
    CPS = 14.0          # karakter/masodperc, magyar felolvasasi tempo kozelites
    PAUSE = {",": 0.16, ".": 0.34, "!": 0.34, "?": 0.34, ":": 0.22, "-": 0.08}

    chars, starts, ends = [], [], []
    t = 0.0
    for ch in text:
        d = 0.0 if ch == "\n" else 1.0 / CPS
        chars.append(ch)
        starts.append(t)
        t += d
        ends.append(t)
        t += PAUSE.get(ch, 0.0)

    subprocess.run(
        ["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
         "-t", f"{t:.3f}", "-q:a", "9", out_mp3, "-y"], check=True)
    return chars, starts, ends


# =========================================================================
# 2. Karakter-idobelyegekbol szavak
# =========================================================================

def words_from_chars(chars, starts, ends):
    """[{'w':..., 'start':..., 'end':...}] - irasjelek a szohoz tapadnak."""
    words, buf, w_start = [], "", None
    for c, s, e in zip(chars, starts, ends):
        if c.isspace():
            if buf:
                words.append({"w": buf, "start": w_start, "end": prev_e})
                buf, w_start = "", None
            continue
        if not buf:
            w_start = s
        buf += c
        prev_e = e
    if buf:
        words.append({"w": buf, "start": w_start, "end": prev_e})
    return words


# =========================================================================
# 3. Ken Burns klippek allokepbol
# =========================================================================

def kenburns_clip(img, shot, dur, out_mp4, tmpdir, idx):
    """
    shot: {"center":[cx,cy], "zoom":[z0,z1], "drift":[dx,dy]}
      center - 0..1 a forraskepen
      zoom   - 1.0 = a legszelesebb 9:16 kivagas; 1.3 = 30%-kal beljebb
      drift  - lassu elmozdulas a mozgas soran, a kivagas szazalekaban
    A PIL elore kivagja a 9:16 savot, hogy a zoompan ne torzitson.
    """
    from PIL import Image

    cx, cy = shot.get("center", [0.5, 0.5])
    z0, z1 = shot.get("zoom", [1.0, 1.15])
    dx, dy = shot.get("drift", [0.0, 0.0])

    im = Image.open(img).convert("RGB")
    sw, sh = im.size

    # a legszelesebb 9:16 kivagas, ami belefer a forrasba
    if sw / sh > ASPECT:
        ch = sh
        cw = int(sh * ASPECT)
    else:
        cw = sw
        ch = int(sw / ASPECT)

    # a legkisebb nagyitasnal kell a legtobb kep -> ahhoz vagunk elo
    zmin = min(z0, z1)
    bw, bh = int(cw / zmin), int(ch / zmin)
    bw, bh = min(bw, sw), min(bh, sh)

    left = int(cx * sw - bw / 2)
    top = int(cy * sh - bh / 2)
    left = max(0, min(left, sw - bw))
    top = max(0, min(top, sh - bh))

    frames = max(2, int(round(dur * FPS)))
    p = f"(on/{frames - 1})"                       # 0 -> 1 a klipp alatt
    zexpr = f"{z0 / zmin}+({z1 / zmin}-{z0 / zmin})*{p}"
    xexpr = f"iw/2-(iw/zoom/2)+({dx})*iw*{p}"
    yexpr = f"ih/2-(ih/zoom/2)+({dy})*ih*{p}"

    if shot.get("screen"):
        # a kijelzon video fut -> kockankent osszerakott kep, ugyanazzal a mozgassal
        kenburns_screen(im.crop((left, top, left + bw, top + bh)), left, top, bw, bh,
                        shot, shot["_root"], frames, out_mp4, zexpr, xexpr, yexpr)
        return

    base = os.path.join(tmpdir, f"kb{idx}.png")
    # 2x a cel-felbontashoz: a zoompan igy sokkal simabb
    im.crop((left, top, left + bw, top + bh)).resize((W * 2, H * 2), Image.LANCZOS).save(base)

    vf = (f"zoompan=z='{zexpr}':x='{xexpr}':y='{yexpr}'"
          f":d={frames}:s={W}x{H}:fps={FPS},setsar=1,format=yuv420p")

    subprocess.run(
        ["ffmpeg", "-v", "error", "-loop", "1", "-i", base, "-vf", vf,
         "-frames:v", str(frames), "-c:v", "libx264", "-preset", "medium",
         "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS), out_mp4, "-y"],
        check=True)


def video_clip(src, shot, dur, out_mp4):
    """
    Videoklipp vagasa a celaranyra. Az allokeppel ellentetben ezt NEM
    daraboljuk fel: egy valodi felvetelt nem kell 6 mp-enkent vagni.
    Ha a forras rovidebb a beatnel, az utolso kockan fagyasztunk (tpad),
    hogy ne kelljen csendben megrovidteni a beatet.
    """
    trim = shot.get("trim_start", 0.0)
    speed = shot.get("speed", 1.0)
    if speed == "fit":
        # "action": a klipp ennyi mp-e a LENYEG (pl. egy UI-animacio vegigfut).
        # A sebesseget ugy valasztjuk, hogy a lenyeg beleferjen a beatbe, de
        # 0,9 mp-nyi "megallas" maradjon a vegen, hogy a nezo lassa az eredmenyt.
        # Lassitani nem lassit (min 1.0), 2.5x fole nem gyorsit (olvashatatlan).
        action = float(shot.get("action", 0) or 0)
        speed = min(2.5, max(1.0, action / max(0.3, dur - 0.9))) if action else 1.0
        speed = round(speed, 2)
        print(f"      speed=fit -> {speed}x  (lenyeg {action:.1f} mp, beat {dur:.1f} mp)")

    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "format=duration", "-of", "csv=p=0", src],
                         capture_output=True, text=True, check=True)
    src_dur = float(out.stdout.strip() or 0)
    avail = max(0.0, src_dur - trim)
    # A kimenet MINDIG a beat hossza (dur). A sebesseg csak azt donti el,
    # mennyi FORRAS kell hozza (dur * speed). Korabban itt dur / speed allt
    # kimeneti hossznak -> gyorsitott klippnel rovidebb lett a beatnel, es
    # minden kesobbi vagas elcsuszott a felirathoz kepest.
    need_src = dur * speed

    vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"
    if speed != 1.0:
        vf = f"setpts=PTS/{speed}," + vf
    if avail < need_src:
        vf += f",tpad=stop_mode=clone:stop_duration={(need_src - avail) / speed + 0.1:.3f}"

    subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{trim:.3f}", "-i", src,
                    "-t", f"{dur:.3f}", "-vf", vf + ",setsar=1,format=yuv420p",
                    "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                    "-pix_fmt", "yuv420p", "-r", str(FPS), out_mp4, "-y"],
                   check=True)

    # A klipp SAJAT hangja (pl. a Veo utcazaja, lepesei) halkan a narracio ala.
    # Csak 1.0-s sebessegnel: gyorsitott zaj termeszetellenes.
    if shot.get("audio_db") is not None and speed == 1.0:
        has_audio = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
             "stream=index", "-of", "csv=p=0", src], capture_output=True, text=True).stdout.strip()
        if has_audio:
            wav = os.path.splitext(out_mp4)[0] + "_amb.wav"
            subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{trim:.3f}", "-i", src,
                            "-t", f"{dur:.3f}", "-vn", "-af",
                            # A Veo-klippek hangereje nagyon eltero (epitkezes vs. csendes
                            # muszerfal: 24 dB kulonbseg merve). Elobb egysegesitunk:
                            # audio_db = ennyi dB-lel a -16 LUFS-os beszed ALATT.
                            f"loudnorm=I={-16 + float(shot['audio_db']):.1f}:TP=-6:LRA=7,"
                            f"afade=t=in:d=0.08,afade=t=out:st={max(0, dur - 0.12):.3f}:d=0.12",
                            "-ar", "44100", "-ac", "2", wav, "-y"], check=True)
            return wav
    return None


# =========================================================================
# 4. ASS felirat, szavankenti kiemelessel
# =========================================================================

def ts(t):
    t = max(0.0, t)
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h:d}:{m:02d}:{s:05.2f}"


def ends_sentence(w):
    return bool(re.search(r"[.!?]$", w["w"]))


def make_cards(words, max_words=4, max_chars=22):
    """
    Feliratkartyak 2-4 szoval.

    A mondatvegi irasjel MINDIG zar, meg egyetlen szonal is. Egy kartyara
    sosem kerulhet ket kulonbozo mondat.

    Korabban volt egy min_words=2 szabaly azzal az indokkal, hogy az egyszavas
    kartya ugralna. Ez ket okbol rossz volt: (1) a split_two_lines ugyis ket
    sorra parnaz, szoval a blokk magassaga allando, (2) cserebe ket kulonbozo
    mondat kerult egy kartyara - igy lett a feliratbol
    "AZONNAL TERHELHETO FELULETET / AD. A GYALOGOS FORGALOMTOL".

    A maganyos egyszavas kartya viszont a SZOVEG hibaja, nem a kode: ne zarj
    hosszu mondatot rovid szoval ("...felueltet ad.", "...elokeszites nelkul.").
    """
    cards, cur = [], []
    for w in words:
        cur.append(w)
        txt = " ".join(x["w"] for x in cur)
        if len(cur) >= max_words or len(txt) >= max_chars or ends_sentence(w):
            cards.append(cur)
            cur = []
    if cur:
        # a maradek csak akkor tapad az elozohoz, ha az nem zart mondatot
        if len(cur) == 1 and cards and not ends_sentence(cards[-1][-1]):
            cards[-1].extend(cur)
        else:
            cards.append(cur)
    return cards


def split_two_lines(words):
    """
    A kartya szavait KET, kozel egyforma hosszu sorra bontja.
    Mindig ket sor -> a blokk magassaga allando -> nem ugral a felirat.
    Visszaad: (elso sor indexei, masodik sor indexei)
    """
    n = len(words)
    if n < 2:
        return [0], []
    lens = [len(w["w"]) for w in words]
    total = sum(lens) + n - 1
    best, best_i = None, 1
    for i in range(1, n):
        a = sum(lens[:i]) + i - 1
        b = sum(lens[i:]) + (n - i) - 1
        d = abs(a - b)
        if best is None or d < best:
            best, best_i = d, i
    return list(range(best_i)), list(range(best_i, n))


def build_ass(words, out_ass, fontsize=84, margin_v=430):
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Archivo Black,{fontsize},{C_WHITE},{C_WHITE},{C_BLACK},{C_BLACK},0,0,0,0,100,100,1,0,1,8,3,5,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    # A blokk kozeppontja ALLANDO. Ez a lenyeg: ha a sorok szama kartyankent
    # valtozna, az egesz felirat fel-le ugralna. Ezert mindig KET sor van,
    # fix \pos-ra horgonyozva.
    pos_y = H - margin_v
    cards = make_cards(words)

    # Eloszor LAPOS esemenylistat epitunk (kartya, aktiv szo, kezdet), utana
    # minden esemeny a KOVETKEZO kezdeteig tart. Igy ket feliratkartya soha
    # nem lehet egyszerre a kepen - korabban ez egymasra rendereleshez vezetett,
    # mert a szovegek es a kartyahatarok nem illeszkedtek pontosan.
    events = []
    for card in cards:
        row1, row2 = split_two_lines(card)
        for i, active in enumerate(card):
            def render(idxs, act=i, c=card):
                out = []
                for j in idxs:
                    t = c[j]["w"].upper().replace("{", "").replace("}", "")
                    if j == act:
                        # az aktiv szo narancs es kicsit nagyobb
                        # CSAK szin valtozik. Meretvaltas TILOS: a szelesebb
                        # aktiv szotol a kozepre horgonyzott sor elmozdul, es
                        # az egesz felirat ugrik minden szovaltasnal.
                        out.append(f"{{\\c{C_ORANGE}}}{t}{{\\c{C_WHITE}}}")
                    else:
                        out.append(t)
                return " ".join(out)

            # ures masodik sor is helyet tart -> allando blokkmagassag
            text = (f"{{\\an5\\pos({W // 2},{pos_y})}}"
                    + render(row1) + "\\N" + (render(row2) if row2 else "\\h"))
            events.append({"start": active["start"],
                           "word_end": active["end"],
                           "text": text})

    lines = []
    for n, ev in enumerate(events):
        if n + 1 < len(events):
            end = events[n + 1]["start"]
        else:
            end = ev["word_end"] + 0.30
        if end <= ev["start"]:
            end = ev["start"] + 0.08
        lines.append(f"Dialogue: 0,{ts(ev['start'])},{ts(end)},Cap,,0,0,0,,{ev['text']}")

    with open(out_ass, "w", encoding="utf-8") as f:
        f.write(head + "\n".join(lines) + "\n")


# =========================================================================
# 4b. Emoji -> atlatszo PNG
# =========================================================================

EMOJI_FONT = r"C:\Windows\Fonts\seguiemj.ttf"


def render_emoji(ch, size, out_png):
    """Szines emoji atlatszo PNG-be. Windows: Segoe UI Emoji (COLR/CPAL)."""
    from PIL import Image, ImageDraw, ImageFont

    if not os.path.exists(EMOJI_FONT):
        return False
    # a seguiemj csak bizonyos pixelmeretekben ad szint - 109 a biztos,
    # utana atmeretezzuk a kivant meretre
    base = 109
    f = ImageFont.truetype(EMOJI_FONT, base)

    # BOSEGES vaszon: a 109-es glifa siman elfer, nem vagja le a szelet.
    # (Szuk vaszonnal a bbox-vagas a glifa TOREDEKET kapja el - igy lett
    #  korabban a satrat abrazolo emojibol egy palanta.)
    canvas = base * 3
    im = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    try:
        d.text((canvas // 2, canvas // 2), ch, font=f,
               embedded_color=True, anchor="mm")
    except Exception:
        return False

    bbox = im.getbbox()
    if not bbox:
        return False
    g = im.crop(bbox)

    # ARANYTARTO atmeretezes a cel-magassagra - a negyzetre huzas torzit
    w, h = g.size
    nw = max(1, int(round(w * size / h)))
    g.resize((nw, size), Image.LANCZOS).save(out_png)
    return True


# =========================================================================
# 4b2. Animalt emoji: beugrik (tulloves + visszarugas), a vegen kiugrik
# =========================================================================

EMOJI_AUTO = [
    # kulcsszo-eleje -> emoji. Az emoji_auto ezt hasznalja, ha a beatnek
    # nincs sajat emojija. Csak a szo ELEJET nezi, igy ragozva is talal.
    ("telefon", "📞"), ("felhív", "📞"), ("végigtelefon", "📞"), ("sms", "💬"), ("üzen", "💬"),
    ("naptár", "📅"), ("időpont", "📅"), ("határid", "⏳"), ("sosincs", "⏳"),
    ("pénz", "💸"), ("fizet", "💸"), ("havidíj", "💸"), ("lista", "📋"), ("árajánlat", "📋"),
    ("eső", "🌧️"), ("por", "💨"), ("teherautó", "🚚"), ("kattints", "👉"),
]

# kulcsszo-eleje -> hangeffekt. Az auto mod beatenkent LEGFELJEBB EGYET tesz,
# es csak oda, ahol a beatnek nincs sajat "sfx"-e. Csak a szo elejet nezi.
# Tudatosan szuk lista: csak ami a szovegben tenyleg HANGOT AD. (Az "ar" pl.
# nincs benne, mert az "arajanlat" is azzal kezdodik.)
SFX_AUTO = [
    ("sms", "ding"), ("üzen", "ding"), ("értesít", "ding"),
    ("telefon", "ring"), ("felhív", "ring"), ("végigtelefon", "ring"), ("csörög", "ring"),
    ("fizet", "coin"), ("pénz", "coin"), ("forint", "coin"), ("havidíj", "coin"),
    ("naptár", "click"), ("beír", "click"), ("foglal", "click"),
]

# A szkriptvaz szakaszai (a beat "szakasz" mezoje), ekezettel vagy anelkul.
SZAKASZ = {"horog": "horog", "tet": "tet", "tét": "tet", "megoldas": "megoldas",
           "megoldás": "megoldas", "fordulat": "megoldas", "felsorolas": "felsorolas",
           "felsorolás": "felsorolas", "kockazat": "kockazat", "kockázat": "kockazat",
           "kockazatleveles": "kockazat", "kockázatlevétel": "kockazat", "cta": "cta"}


def auto_cuts(shots, sections, beats):
    """
    Vagastipus a szkript SZERKEZETEBOL, ahol a beat nem ad meg sajatot:
      a megoldas ELSO kepe      -> flash  (a nagy fordulat: problema -> megoldas)
      a CTA kepe                -> punch
      a kockazatlevetel elso kepe -> whip (vissza a valosagba)
      a felsorolas kepei        -> slide  -- KIVEVE, ha ket egymast koveto klipp
                                   ugyanabbol a sorozatbol jon (pl. ui-hivas, ui-sms):
                                   az egy folyamat, a becsuszas szetszakitana
      minden mas                -> kemeny vagas
    """
    def series(shot):
        c = shot.get("clip") or ""
        b = os.path.basename(c)
        return b.split("-")[0] if c and "-" in b else None

    out = []
    for k, s in enumerate(shots):
        if s["cut"]:
            out.append(s["cut"]); continue
        if k == 0:
            out.append("cut"); continue
        sec, prev_sec = sections[s["beat"]], sections[shots[k - 1]["beat"]]
        same_series = series(s["shot"]) and series(s["shot"]) == series(shots[k - 1]["shot"])
        if sec == "megoldas" and prev_sec != "megoldas":
            out.append("flash")
        elif sec == "cta":
            out.append("punch")
        elif sec == "kockazat" and prev_sec != "kockazat":
            out.append("whip")
        elif sec == "felsorolas" and not same_series:
            out.append("slide")
        else:
            out.append("cut")
    return out


EMOJI_SCALE_MAX = 1.14


def render_emoji_anim(ch, size, dur, out_dir, tag):
    """
    Kepkocka-sorozat (PNG) egy emojihoz. Visszaad: (minta, vaszon_w, vaszon_h)
    vagy None. A vaszon ALLANDO meretu, az emoji a kozepen skalazodik --
    igy az overlay pozicioja nem mozog, csak a tartalom.
    """
    from PIL import Image

    big = os.path.join(out_dir, f"{tag}_big.png")
    if not render_emoji(ch, int(size * EMOJI_SCALE_MAX), big):
        return None
    base = Image.open(big).convert("RGBA")
    cw, chh = base.size
    n = max(2, int(round(dur * FPS)))
    t_in, t_out = 0.22, 0.12

    def scale_at(t):
        if t < t_in:                        # easeOutBack: tullo, majd visszaall
            p = t / t_in
            c1 = 1.9
            return max(0.0, 1 + (c1 + 1) * (p - 1) ** 3 + c1 * (p - 1) ** 2)
        if t > dur - t_out:                 # kifele: gyorsan osszemegy
            p = (t - (dur - t_out)) / t_out
            return max(0.0, 1 - p * p)
        return 1.0

    for i in range(n):
        sc = scale_at(i / FPS) / EMOJI_SCALE_MAX
        fr = Image.new("RGBA", (cw, chh), (0, 0, 0, 0))
        if sc > 0.02:
            w, h = max(1, int(cw * sc)), max(1, int(chh * sc))
            fr.alpha_composite(base.resize((w, h), Image.LANCZOS), ((cw - w) // 2, (chh - h) // 2))
        fr.save(os.path.join(out_dir, f"{tag}_{i:04d}.png"))
    return os.path.join(out_dir, f"{tag}_%04d.png"), cw, chh


# =========================================================================
# 4b3. Hangeffektek
# =========================================================================

SFX_DIR = os.path.abspath(os.path.join(HERE, "..", "assets", "sfx"))

# Alapszint dB-ben. A generalt fajlok -3 dBFS csucsuak; ezek az ertekek a
# -16 LUFS-os beszed ALA teszik oket: hallhatoan, de nem tolakodoan.
# A client.json "sfx_db" mezoje mindegyiket egyutt tolja el.
# Mert ertekek (2026-09-23, egy SaaS-ugyfel videoja): a hit -11-en 12,7 dB-lel a beszed FOLE
# ment a mondatkozi szunetben, a whoosh 4 dB-lel -- ezert vannak lejjebb.
SFX_DB = {"whoosh": -18, "whoosh-soft": -15, "pop": -11, "ding": -13, "click": -9,
          "tick": -7, "ring": -19, "riser": -8, "hit": -19, "coin": -13}


def resolve_sfx(name, root):
    """Elobb a projekt sfx/ mappaja (sajat, valodi felvetel), aztan a beepitett."""
    if os.path.splitext(name)[1] and os.path.exists(os.path.join(root, name)):
        return os.path.join(root, name)
    for d in (os.path.join(root, "sfx"), SFX_DIR):
        for ext in (".wav", ".mp3", ".m4a"):
            p = os.path.join(d, name + ext)
            if os.path.exists(p):
                return p
    print(f"  ! hangeffekt nincs meg: {name}")
    return None


# =========================================================================
# 4b4. Kijelzocsere: video a foton levo telefon/laptop kijelzojen
# =========================================================================

def _perspective_coeffs(dst, src):
    """PIL PERSPECTIVE egyutthatok: a kimeneti (dst) pontot a bemeneti (src)
    pontra kepezik le. 4 pontpar -> 8 ismeretlen."""
    import numpy as np
    A, b = [], []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); b.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); b.append(v)
    return np.linalg.solve(np.array(A, float), np.array(b, float)).tolist()


def _screen_frames(spec, root, rw, rh, n_frames):
    """A kijelzore kerulo klipp kockai rw x rh meretben, nyers RGB bajtokkent."""
    src = os.path.join(root, spec["clip"])
    trim = spec.get("trim_start", 0.0)
    speed = spec.get("speed", 1.0)
    vf = [f"setpts=PTS/{speed}", f"fps={FPS}"]
    if spec.get("crop"):
        x, y, w, h = spec["crop"]
        vf.append(f"crop={w}:{h}:{x}:{y}")
    bg = spec.get("bg", "#06090F").replace("#", "0x")
    if spec.get("fit", "contain") == "cover":
        vf.append(f"scale={rw}:{rh}:force_original_aspect_ratio=increase,crop={rw}:{rh}")
    else:
        vf.append(f"scale={rw}:{rh}:force_original_aspect_ratio=decrease,"
                  f"pad={rw}:{rh}:(ow-iw)/2:(oh-ih)/2:color={bg}")
    p = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{trim:.3f}", "-i", src,
                        "-vf", ",".join(vf), "-frames:v", str(n_frames),
                        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                       capture_output=True, check=True)
    fs = rw * rh * 3
    frames = [p.stdout[i:i + fs] for i in range(0, len(p.stdout) - fs + 1, fs)]
    if not frames:
        raise RuntimeError(f"a kijelzo-klippbol nem jott kocka: {src}")
    while len(frames) < n_frames:           # rovidebb klipp: az utolso kocka all
        frames.append(frames[-1])
    return frames


def kenburns_screen(im_crop, left, top, bw, bh, shot, root, frames, out_mp4,
                    zexpr, xexpr, yexpr):
    """
    Ken Burns egy olyan kepen, amelynek egy kijelzojen VIDEO fut.
    shot.screen.corners: a kijelzo 4 sarka a FORRASKEP pixeleiben,
    bal-felso, jobb-felso, jobb-also, bal-also sorrendben.
    Kockankent: klipp-kocka -> perspektiv torzitas a negyszogre -> enyhe
    elsotetites + a foto eredeti csillogasanak visszakeverese -> ra a fotora.
    A kesz kockakat csovon kapja a zoompan, igy a kamera mozgasa is megmarad.
    """
    from PIL import Image, ImageFilter
    import numpy as np

    spec = shot["screen"]
    BW, BH = W * 2, H * 2
    sx, sy = BW / bw, BH / bh
    quad = [((x - left) * sx, (y - top) * sy) for x, y in spec["corners"]]
    xs, ys = [q[0] for q in quad], [q[1] for q in quad]
    bx0, by0 = int(max(0, min(xs) - 2)), int(max(0, min(ys) - 2))
    bx1, by1 = int(min(BW, max(xs) + 2)), int(min(BH, max(ys) + 2))
    loc = [(x - bx0, y - by0) for x, y in quad]

    dist = lambda a, b: ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5
    rw = max(2, int(round((dist(quad[0], quad[1]) + dist(quad[3], quad[2])) / 2)) // 2 * 2)
    rh = max(2, int(round((dist(quad[0], quad[3]) + dist(quad[1], quad[2])) / 2)) // 2 * 2)
    coeffs = _perspective_coeffs(loc, [(0, 0), (rw, 0), (rw, rh), (0, rh)])
    box = (bx1 - bx0, by1 - by0)

    mask = Image.new("L", (rw, rh), 255).transform(box, Image.PERSPECTIVE, coeffs, Image.BILINEAR)
    mask = mask.filter(ImageFilter.GaussianBlur(1.2))
    base = im_crop.resize((BW, BH), Image.LANCZOS)
    orig = np.asarray(base.crop((bx0, by0, bx1, by1)), dtype=np.float32)
    bright = spec.get("brightness", 0.88)
    glare = spec.get("glare", 0.14)
    soften = spec.get("soften", 0.6)

    raw = _screen_frames(spec, root, rw, rh, frames)
    ff = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{BW}x{BH}",
         "-r", str(FPS), "-i", "-",
         "-vf", f"zoompan=z='{zexpr}':x='{xexpr}':y='{yexpr}':d=1:s={W}x{H}:fps={FPS},"
                "setsar=1,format=yuv420p",
         "-frames:v", str(frames), "-c:v", "libx264", "-preset", "medium", "-crf", "18",
         "-pix_fmt", "yuv420p", "-r", str(FPS), out_mp4, "-y"], stdin=subprocess.PIPE)
    for fr in raw:
        scr = Image.frombytes("RGB", (rw, rh), fr)
        if soften:
            scr = scr.filter(ImageFilter.GaussianBlur(soften))
        wp = np.asarray(scr.transform(box, Image.PERSPECTIVE, coeffs, Image.BICUBIC), dtype=np.float32)
        mix = np.clip(wp * bright * (1 - glare) + orig * glare, 0, 255).astype(np.uint8)
        f = base.copy()
        f.paste(Image.fromarray(mix), (bx0, by0), mask)
        ff.stdin.write(f.tobytes())
    ff.stdin.close()
    if ff.wait() != 0:
        raise RuntimeError("kijelzocsere: az ffmpeg hibaval allt le")


# =========================================================================
# 4b5. Vagastipusok es a klippek osszefuzese
# =========================================================================

# Atfedest igenylo atmenetek: az ELOZO klipp ennyivel hosszabban renderelodik,
# igy a teljes idovonal nem rovidul, es a feliratszinkron megmarad.
XFADE = {"whip": ("slideleft", 0.16), "slide": ("smoothleft", 0.28)}
PUNCH_CUT = (0.10, 0.26)                 # vagaskori beugras: (merteke, hossza mp)
PUNCH_KEY = (0.055, 0.45)                # kiemelt szora: finomabb, hosszabb
CUT_SFX = {"whip": "whoosh", "slide": "whoosh-soft", "punch": "hit", "flash": "hit"}


def join_clips(clips, starts, cuts, total, tmpdir, punches, flashes, whips):
    """
    A klippek osszefuzese a vagastipusokkal, EGY ffmpeg-futasban.
      cut   - kemeny vagas (concat)
      whip  - gyors csusztatas + vizszintes elmosas (xfade + avgblur)
      slide - lagy becsuszas (xfade)
      punch - a vagason a kep nagyobbrol ugrik a helyere (zoompan)
      flash - par kocka feher villanas (overlay)
    """
    cmd = ["ffmpeg", "-v", "error"]
    for c in clips:
        cmd += ["-i", c]
    ch = [f"[{i}:v]setpts=PTS-STARTPTS,fps={FPS},settb=1/{FPS},format=yuv420p[c{i}]"
          for i in range(len(clips))]
    counter = [0]

    def close(pend):
        if len(pend) == 1:
            return pend[0]
        lab = f"k{counter[0]}"; counter[0] += 1
        ch.append("".join(f"[{p}]" for p in pend) + f"concat=n={len(pend)}:v=1:a=0,settb=1/{FPS}[{lab}]")  # az xfade 1/FPS idoalapot var
        return lab

    pending = []
    for i in range(len(clips)):
        if i > 0 and cuts[i] in XFADE:
            acc = close(pending)
            tr, d = XFADE[cuts[i]]
            ch.append(f"[{acc}][c{i}]xfade=transition={tr}:duration={d}:offset={starts[i]:.4f}[x{i}]")
            pending = [f"x{i}"]
        else:
            pending.append(f"c{i}")
    cur = close(pending)

    if punches:
        terms = "+".join(f"{a}*pow(max(0,1-(it-{t:.3f})/{d}),2)*gte(it,{t:.3f})"
                         for t, a, d in punches)
        ch.append(f"[{cur}]zoompan=z='1+{terms}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                  f":d=1:s={W}x{H}:fps={FPS}[pz]")
        cur = "pz"
    if whips:
        en = "+".join(f"between(t,{t - 0.07:.3f},{t + 0.13:.3f})" for t in whips)
        ch.append(f"[{cur}]avgblur=sizeX=48:sizeY=1:enable='{en}'[wb]")
        cur = "wb"
    for k, t in enumerate(flashes):
        ch.append(f"color=c=white:s={W}x{H}:r={FPS}:d=0.17,format=rgba,"
                  f"fade=t=out:st=0:d=0.17:alpha=1,setpts=PTS+{t:.3f}/TB[fl{k}]")
        ch.append(f"[{cur}][fl{k}]overlay=eof_action=pass[fo{k}]")
        cur = f"fo{k}"
    ch.append(f"[{cur}]trim=duration={total:.3f},setsar=1,format=yuv420p[vj]")

    out = os.path.join(tmpdir, "video_silent.mp4")
    cmd += ["-filter_complex", ";".join(ch), "-map", "[vj]", "-an",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
            "-r", str(FPS), out, "-y"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        # a hosszu szurolancnal az ffmpeg uzenete nelkul vakon keresnenk a hibat
        sys.exit("join_clips: az ffmpeg hibaval allt le:\n" + r.stderr[-3000:]
                 + "\nSzurolanc:\n" + ";\n".join(ch))
    return out


# =========================================================================
# 4c. Allando brand-tabla (a referenciaban vegig ott ul a sarokban)
# =========================================================================

ORANGE_RGB = (245, 117, 7)
INK_RGB = (11, 13, 15)
DARKTEXT = (20, 16, 11)


def _font(size):
    from PIL import ImageFont
    fp = os.path.join(FONTS_DIR, "ArchivoBlack-Regular.ttf")
    return ImageFont.truetype(fp, size) if os.path.exists(fp) else ImageFont.load_default()


def _tracked(draw, xy, text, font, fill, track=0):
    """Betukozzel rajzolt szoveg - a PIL nem tud trackinget."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + track
    return x - xy[0] - (track if text else 0)


def _tracked_w(draw, text, font, track=0):
    w = sum(draw.textlength(c, font=font) for c in text)
    return w + track * max(0, len(text) - 1)


def _hexagon(d, cx, cy, r, fill):
    import math as _m
    pts = [(cx + r * _m.cos(_m.radians(60 * i - 90)),
            cy + r * _m.sin(_m.radians(60 * i - 90))) for i in range(6)]
    d.polygon(pts, fill=fill)


def render_badge(brand, claim, out_png, size=28):
    """
    Ketreszes tag: narancs blokk SOTET markanevvel + sotet blokk feher allitassal.
    Balrol hexagon jel. Sokkal erosebb, mint egy lapos teglalap.
    """
    from PIL import Image, ImageDraw

    f = _font(size)
    d0 = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    tr = max(1, size // 12)

    hex_r = int(size * 0.62)
    padx, pady = int(size * 0.80), int(size * 0.62)
    gap = int(size * 0.55)

    wb = _tracked_w(d0, brand, f, tr)
    wc = _tracked_w(d0, claim, f, tr)
    asc = d0.textbbox((0, 0), "MÁ", font=f)

    seg1 = int(hex_r * 2 + gap + wb + padx)
    seg2 = int(wc + padx * 2)
    W_, H_ = seg1 + seg2, int(asc[3] - asc[1] + pady * 2)

    im = Image.new("RGBA", (W_, H_), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, seg1, H_], fill=ORANGE_RGB + (255,))
    d.rectangle([seg1, 0, W_, H_], fill=INK_RGB + (238,))

    _hexagon(d, int(hex_r * 0.55 + padx * 0.35), H_ // 2, hex_r, DARKTEXT + (255,))
    ty = pady - asc[1]
    _tracked(d, (int(hex_r * 2 + gap * 0.5), ty), brand, f, DARKTEXT + (255,), tr)
    _tracked(d, (seg1 + padx, ty), claim, f, (255, 255, 255, 255), tr)

    im.save(out_png)
    return True


def render_logo(src, out_png, width=430, shadow=True):
    """
    A ceg sajat logoja a bal felso sarokba, a rajzolt tabla helyett.

    Harom dolgot csinal, es mind a harom kell:
      1. ALFA-BBOX VAGAS. A markafajlok koruli ures keret miatt a logo
         optikailag beljebb ulne, mint a felirat margoja.
      2. ATMERETEZES szelessegre. A magassag jon belole -- soha ne allitsd
         be mind a kettot, mert a logo aranya szent.
      3. LAGY SOTET ARNYEK. A wordmark majdnem feher; vilagos kepen
         (sator ponyva, eg) nyom nelkul eltunne.
    """
    from PIL import Image, ImageFilter

    if not os.path.exists(src):
        print("  ! logo nincs meg:", src)
        return False

    im = Image.open(src).convert("RGBA")
    bb = im.split()[3].getbbox()
    if bb:
        im = im.crop(bb)

    w = int(width)
    h = max(1, round(im.height * w / im.width))
    im = im.resize((w, h), Image.LANCZOS)

    if not shadow:
        im.save(out_png)
        return True

    pad = max(4, w // 60)
    canvas = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 150), (pad, pad + pad // 2), im.split()[3])
    canvas = Image.alpha_composite(canvas, sh.filter(ImageFilter.GaussianBlur(pad * 0.7)))
    canvas.alpha_composite(im, (pad, pad))
    canvas.save(out_png)
    return True


def render_cta(text, out_png, size=54):
    """
    Narancs gomb SOTET felirattal, kemeny eltolt arnyekkal es chevron nyillal.
    A kemeny (nem elmosott) arnyek adja a plakat-szeru eroteljes hatast.
    """
    from PIL import Image, ImageDraw

    f = _font(size)
    d0 = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    tr = max(1, size // 22)

    padx, pady = int(size * 0.95), int(size * 0.58)
    arrow_w = int(size * 0.62)
    gap = int(size * 0.52)
    shadow = int(size * 0.17)

    tw = _tracked_w(d0, text, f, tr)
    asc = d0.textbbox((0, 0), "MÁJ", font=f)
    bw = int(tw + gap + arrow_w + padx * 2)
    bh = int(asc[3] - asc[1] + pady * 2)

    im = Image.new("RGBA", (bw + shadow, bh + shadow), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([shadow, shadow, bw + shadow, bh + shadow], fill=INK_RGB + (255,))   # kemeny arnyek
    d.rectangle([0, 0, bw, bh], fill=ORANGE_RGB + (255,))

    ty = pady - asc[1]
    _tracked(d, (padx, ty), text, f, DARKTEXT + (255,), tr)

    # chevron nyil - vastag, nem a vekony -> glyph
    ax = padx + tw + gap
    ay = bh // 2
    t = max(6, int(size * 0.17))
    d.line([(ax, ay), (ax + arrow_w, ay)], fill=DARKTEXT + (255,), width=t)
    d.line([(ax + arrow_w - t * 2, ay - t * 2), (ax + arrow_w, ay),
            (ax + arrow_w - t * 2, ay + t * 2)], fill=DARKTEXT + (255,), width=t,
           joint="curve")

    im.save(out_png)
    return True


# =========================================================================
# 5. Osszerakas
# =========================================================================

def ffesc(p):
    """Windows-utvonal a subtitles/ass filterhez."""
    return p.replace("\\", "/").replace(":", "\\:")


def assemble(silent, vo_mp3, ass, music, out_mp4, tmpdir, music_db=-24,
             emojis=None, badge=None, cta=None, music_start=0.0, sfx=None,
             qa_dir=None):
    """
    Bemenetek sorrendje FIX, mert a szurolanc indexre hivatkozik:
        0 = nema video, 1 = narracio, [2 = zene], emojik, tabla, CTA, hangeffektek
    emojis: [{seq, y, start}] -- animalt kockasor (render_emoji_anim)
    sfx:    [{file, t, db}]   -- idoponthoz kotott hangeffekt
    """
    emojis = emojis or []
    sfx = sfx or []
    has_music = bool(music and os.path.exists(music))
    if has_music and music_start > 0:
        # A legtobb zenei alapnak lassu felvezetese van. A hirdetesnek az elso
        # masodperctol "bent" kell lennie, ezert a track kozeperol indulunk.
        trimmed = os.path.join(tmpdir, "bed.m4a")
        subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{music_start:.2f}",
                        "-i", music, "-vn", "-c:a", "aac", "-b:a", "192k",
                        trimmed, "-y"], check=True)
        music = trimmed

    cmd = ["ffmpeg", "-v", "error", "-i", silent, "-i", vo_mp3]
    if has_music:
        cmd += ["-stream_loop", "-1", "-i", music]
    emoji0 = 3 if has_music else 2
    for e in emojis:
        cmd += ["-framerate", str(FPS), "-i", e["seq"]]
    badge_idx = emoji0 + len(emojis)
    if badge:
        cmd += ["-loop", "1", "-i", badge["png"]]
    cta_idx = badge_idx + (1 if badge else 0)
    if cta:
        cmd += ["-loop", "1", "-i", cta["png"]]
    sfx0 = cta_idx + (1 if cta else 0)
    for e in sfx:
        cmd += ["-i", e["file"]]

    # --- kep: eloszor az emojik, legfelul a felirat ---
    # Az emoji-kockasor a sajat kezdetere tolva (setpts) megy ra; a vegen
    # eof_action=pass -> eltunik, nem ragad be az utolso kocka.
    chain, cur = [], "0:v"
    for i, e in enumerate(emojis):
        nxt = f"ev{i}"
        chain.append(f"[{emoji0 + i}:v]format=rgba,setpts=PTS-STARTPTS+{e['start']:.3f}/TB[es{i}]")
        chain.append(
            f"[{cur}][es{i}]overlay=x=(W-w)/2+{e.get('dx', 0)}:y={e['y']}:eof_action=pass[{nxt}]")
        cur = nxt
    if badge:
        chain.append(f"[{cur}][{badge_idx}:v]overlay=x={badge['x']}:y={badge['y']}[bdg]")
        cur = "bdg"
    if cta:
        chain.append(
            f"[{cur}][{cta_idx}:v]overlay=x=(W-w)/2:y={cta['y']}"
            f":enable='between(t,{cta['start']:.2f},{cta['end']:.2f})'[ctav]")
        cur = "ctav"
    chain.append(f"[{cur}]subtitles='{ffesc(ass)}':fontsdir='{ffesc(FONTS_DIR)}'[vout]")

    # --- hangeffektek: mind a sajat idopontjara tolva, egy savba keverve ---
    fx = None
    if sfx:
        for k, e in enumerate(sfx):
            ms = max(0, int(round(e["t"] * 1000)))
            chain.append(f"[{sfx0 + k}:a]aformat=sample_rates=44100:channel_layouts=stereo,"
                         f"volume={e['db']}dB,adelay={ms}:all=1[fx{k}]")
        if len(sfx) == 1:
            fx = "fx0"
        else:
            chain.append("".join(f"[fx{k}]" for k in range(len(sfx)))
                         + f"amix=inputs={len(sfx)}:normalize=0:duration=longest[fxall]")
            fx = "fxall"

    # --- hang: narracio parbeszed-szinten, a zene jol alatta ---
    MASTER = ("acompressor=threshold=-20dB:ratio=3:attack=5:release=90:makeup=2,"
              "loudnorm=I=-14:TP=-1.5:LRA=9,alimiter=limit=0.84:level=false")
    if has_music:
        # A narracio parbeszed-szinten. A zene fix alapszinten MEGY, plusz
        # DUCKING: beszed alatt automatikusan lejjebb, szunetben visszajon.
        # Igy sosincs csend (mint a referenciaban), de a szoveg mindig ertheto.
        chain.append("[1:a]loudnorm=I=-16:TP=-1.5:LRA=11[voN]")
        chain.append("[voN]asplit=2[vo][vosc]")
        chain.append(f"[2:a]volume={music_db}dB[bedpre]")
        chain.append("[bedpre][vosc]sidechaincompress="
                     "threshold=0.04:ratio=8:attack=15:release=350[bed]")
        chain.append("[vo][bed]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[rest]")
    else:
        chain.append("[1:a]loudnorm=I=-16:TP=-1.5:LRA=11[rest]")

    # A hangeffekt a DUCKING UTAN jon be: nem nyomja le a zenet, es a
    # narraciohoz kepest fix szinten marad. normalize=0: az amix ne ossza a
    # bemenetek szamaval. VEGSZINT: a Meta kb. -14 LUFS-ra normalizal; a
    # kompresszor nelkul a -1,5 dBTP csucskorlat miatt csak -15 jonne ki.
    qa_maps = []
    if qa_dir:
        # QA: a beszed+zene es az effektsav kulon is kimegy (a master ELOTT),
        # ebbol szamolhato az effektek szintje egy masodik render nelkul.
        chain.append("[rest]asplit=2[rest][restq]")
        qa_maps += ["-map", "[restq]", os.path.join(qa_dir, "stem_rest.wav")]
        if fx:
            chain.append(f"[{fx}]asplit=2[fxm][fxq]")
            fx = "fxm"
            qa_maps += ["-map", "[fxq]", os.path.join(qa_dir, "stem_fx.wav")]
    if fx:
        chain.append(f"[rest][{fx}]amix=inputs=2:duration=first:normalize=0,{MASTER}[a]")
    else:
        chain.append(f"[rest]{MASTER}[a]")

    cmd += ["-filter_complex", ";".join(chain),
            "-map", "[vout]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
            "-shortest", "-movflags", "+faststart", out_mp4, "-y"] + qa_maps
    subprocess.run(cmd, check=True)


# =========================================================================
# 6. QA: kontaktlap minden vagasnal + hangmeres + effektenkenti szint
# =========================================================================

def _read_wav_mono(path, sr=22050):
    import numpy as np
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(sr),
                        "-f", "f32le", "-"], capture_output=True, check=True)
    return np.frombuffer(p.stdout, dtype=np.float32)


def qa_report(out_mp4, qa_dir, parts, starts, cuts, beats, part_beat, emojis, sfx_events, total):
    """
    A kesz fajlon mer, nem az osszetevokon (ld. a hibalistat). Kimenet:
      <id>-qa.jpg  kontaktlap: minden klipp 0,15 mp-cel a vagas UTAN --
                   itt latszik azonnal, ha a regi felirat az uj kep alatt all
      <id>-qa.txt  hangossag, csucs, csend, effektenkenti szint
    """
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont

    base = os.path.splitext(out_mp4)[0]
    lines = []

    # --- hang a kesz fajlon ---
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", out_mp4, "-af",
                        "ebur128=peak=true:framelog=quiet", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    lufs = re.findall(r"I:\s+(-?[\d.]+) LUFS", r)
    peak = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r)
    sil = subprocess.run(["ffmpeg", "-hide_banner", "-i", out_mp4, "-af",
                          "silencedetect=noise=-45dB:d=0.25", "-f", "null", "-"],
                         capture_output=True, text=True).stderr.count("silence_start")
    lufs_v = float(lufs[-1]) if lufs else float("nan")
    peak_v = float(peak[-1]) if peak else float("nan")
    ok = lambda c: "OK " if c else "!! "
    lines.append("HANG (a kesz fajlon)")
    lines.append(f"  {ok(-15.5 <= lufs_v <= -13)}hangossag  {lufs_v:6.1f} LUFS   (cel: kb. -14)")
    lines.append(f"  {ok(peak_v <= -1.0)}csucs      {peak_v:6.1f} dBFS   (cel: -1 alatt)")
    lines.append(f"  {ok(sil == 0)}csend      {sil} db            (cel: 0)")

    # --- effektenkenti szint: effektsav vs. beszed+zene ugyanabban az ablakban ---
    fx_path, rest_path = os.path.join(qa_dir, "stem_fx.wav"), os.path.join(qa_dir, "stem_rest.wav")
    if sfx_events and os.path.exists(fx_path) and os.path.exists(rest_path):
        sr = 22050
        fx, rest = _read_wav_mono(fx_path, sr), _read_wav_mono(rest_path, sr)
        win = int(0.25 * sr)
        rms = lambda x: np.sqrt(np.mean(x ** 2)) if len(x) else 0.0
        db = lambda v: 20 * np.log10(v + 1e-9)
        # REFERENCIA: a beszed+zene tipikus (75. percentilis) szintje 250 ms-os
        # ablakokban -- nem a helyi kornyezet. A mondatkozi szunetben a helyi
        # szint majdnem csend, ahhoz merve minden effekt "tul hangos" lenne;
        # a fulnek az szamit, hogy a BESZEDHEZ kepest mekkora.
        ref = db(np.percentile([rms(rest[k:k + win]) for k in range(0, len(rest) - win, win)], 75))
        lines.append("")
        lines.append("HANGEFFEKTEK  (ennyi dB-lel a beszed tipikus szintje ALATT; a 0 koruli mar versenyez a szoveggel)")
        evs = sorted(sfx_events, key=lambda e: e["t"])
        groups = []
        for e in evs:                        # 0,15 mp-en beluli effektek egy csoport
            if groups and e["t"] - groups[-1][-1]["t"] < 0.15:
                groups[-1].append(e)
            else:
                groups.append([e])
        for g in groups:
            names = []
            for e in g:
                n = "klipp-alapzaj" if e.get("amb") else os.path.splitext(os.path.basename(e["file"]))[0]
                names.append(n)
            i0 = int(g[0]["t"] * sr)
            seg = fx[i0:i0 + int(0.6 * sr)]
            if len(seg) < 10:
                continue
            # az effekt LEGHANGOSABB 250 ms-os ablaka
            peak = max(rms(seg[k:k + win]) for k in range(0, max(1, len(seg) - win), win // 4))
            d = ref - db(peak)
            flag = ("!! TUL HANGOS" if d < 2 else "!  eros" if d < 6 else
                    "   alig hallik" if d > 26 else "")
            lines.append(f"  {g[0]['t']:6.2f}s  {'+'.join(names)[:30]:30s} {d:6.1f} dB  {flag}")
        lines.append("  Allitas: beatben \"db\", vagy az osszeset egyutt a client.json \"sfx_db\"-vel.")

    # --- kontaktlap ---
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except Exception:
        font = ImageFont.load_default()
    tw, th, cols = 216, 384, 6
    n = len(parts)
    rows = (n + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (tw + 6) + 6, rows * (th + 58) + 6), (17, 17, 17))
    d = ImageDraw.Draw(sheet)
    for i in range(n):
        t = min(starts[i] + 0.15, total - 0.05)
        fr = os.path.join(qa_dir, f"qa{i:02d}.png")
        subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", out_mp4, "-frames:v", "1",
                        "-vf", f"scale={tw}:{th}", fr, "-y"], check=True)
        x, y = 6 + (i % cols) * (tw + 6), 6 + (i // cols) * (th + 58)
        sheet.paste(Image.open(fr), (x, y))
        bi = part_beat[i]
        head = f"{i + 1}. {t:.1f}s" + (f"  [{cuts[i]}]" if i and cuts[i] != "cut" else "")
        d.text((x + 2, y + th + 4), head, fill=(255, 255, 255), font=font)
        txt = beats[bi]["text"]
        while txt and d.textlength(txt + "…", font=font) > tw - 4:   # a cella szelessegere vagva
            txt = txt[:-1]
        d.text((x + 2, y + th + 28), txt + ("…" if txt != beats[bi]["text"] else ""),
               fill=(160, 170, 185), font=font)
    sheet.save(base + "-qa.jpg", quality=86)

    lines.append("")
    lines.append(f"KONTAKTLAP: {os.path.basename(base)}-qa.jpg -- minden klipp 0,15 mp-cel a vagas utan.")
    lines.append("  Nezd meg: a felirat mar az UJ mondate-e? (ha a regi, csuszik a vagas)")
    txt = "\n".join(lines)
    open(base + "-qa.txt", "w", encoding="utf-8").write(txt + "\n")
    print("\n" + txt)


# =========================================================================
# fo
# =========================================================================

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--offline", action="store_true",
                    help="ElevenLabs nelkul, becsult idozitessel (elonezet)")
    ap.add_argument("--out", default=None)
    ap.add_argument("--qa", action="store_true",
                    help="kontaktlap minden vagasnal + hangmeres + effektenkenti szint")
    a = ap.parse_args()

    cfg = json.load(open(a.config, encoding="utf-8"))
    root = os.path.dirname(os.path.abspath(a.config))

    # A szkript hivatkozhat egy client.json-ra: az adja a MARKA szintu
    # alapertekeket (szin, betu, hang, formatum, tabla, CTA), a szkript
    # pedig csak a videora jellemzot (beatek). Amit a szkript megad, az nyer.
    if cfg.get("client"):
        cpath = os.path.join(root, cfg["client"])
        client = json.load(open(cpath, encoding="utf-8"))
        merged = dict(client)
        merged.update({k: v for k, v in cfg.items() if k != "client"})
        cfg = merged
        # a media utvonalak a client.json-hoz kepest relativak
        root = os.path.dirname(os.path.abspath(cpath))

    # Az API-kulcs a PROJEKTBEN is lehet: a config mappajaban vagy feljebb
    # (legfeljebb 3 szint). Igy nem kell ugyfelenkent a skillbe masolni.
    d = os.path.dirname(os.path.abspath(a.config))
    for _ in range(4):
        load_env(os.path.join(d, ".env"))
        d = os.path.dirname(d)

    set_brand_colors(cfg)
    beats = cfg["beats"]
    text = " ".join(b["text"].strip() for b in beats)

    out_dir = a.out or os.path.join(HERE, "..", "out")
    os.makedirs(out_dir, exist_ok=True)
    out_mp4 = os.path.join(out_dir, f"{cfg['id']}{'-elonezet' if a.offline else ''}.mp4")

    tmpdir = tempfile.mkdtemp(prefix="mp_vid_")
    try:
        # --- 1-2. hang + szo szintu idozites -----------------------------
        vo = os.path.join(tmpdir, "vo.mp3")
        if a.offline:
            print("[1/5] TTS kihagyva (--offline), idozites becsulve")
            chars, st, en = tts_offline(text, vo)
        else:
            # Gyorsitotar: ugyanaz a szoveg + hang + beallitas = nincs uj
            # ElevenLabs-hivas. Kep- vagy vagasmodositasnal igy nem eg kredit.
            import hashlib
            key = hashlib.sha1(json.dumps([text, cfg["voice_id"], cfg.get("model"),
                                           cfg.get("voice_settings"), cfg.get("language")],
                                          sort_keys=True).encode("utf-8")).hexdigest()[:16]
            # A gyorsitotar a CONFIG mellett el, nem a kimeneti mappaban: egy masik
            # --out mappaba renderelve is megtalalja (kulonben uj, fizetos hivas).
            cdir = os.path.join(os.path.dirname(os.path.abspath(a.config)), ".tts-cache")
            os.makedirs(cdir, exist_ok=True)
            cmp3, cjs = os.path.join(cdir, key + ".mp3"), os.path.join(cdir, key + ".json")
            if os.path.exists(cmp3) and os.path.exists(cjs):
                print("[1/5] TTS a gyorsitotarbol (nincs uj ElevenLabs-hivas)")
                shutil.copy(cmp3, vo)
                chars, st, en = json.load(open(cjs, encoding="utf-8"))
            else:
                print("[1/5] ElevenLabs TTS + karakter-idobelyegek...")
                chars, st, en = tts_elevenlabs(
                    text, cfg["voice_id"],
                    cfg.get("model", "eleven_v3"), vo,
                    cfg.get("voice_settings"), cfg.get("language"))
                shutil.copy(vo, cmp3)
                json.dump([chars, st, en], open(cjs, "w", encoding="utf-8"), ensure_ascii=False)

        words = words_from_chars(chars, st, en)
        total = words[-1]["end"] + 0.5
        print(f"[2/5] {len(words)} szo, {total:.1f} mp")

        # --- 3. beat-hosszak es klippek ----------------------------------
        # A vagas a mondatok kozotti SZUNETBEN tortenik, pontosan ott, ahol a
        # felirat is valt - NEM az utolso szo vegen.
        #
        # Miert: a felirat utolso kartyaja kitart a kovetkezo kartya kezdeteig
        # (kulonben lyuk lenne a szunetben). Ha a kep mar a szo vegen vagna,
        # minden mondathataron fel masodpercig az UJ kep alatt a REGI felirat
        # allna. Egy valodi esetben igy kerult az "ALL A BRIGAD" felirat a
        # raklapokat mutato kepre.
        wi, firsts = 0, []
        for b in beats:
            firsts.append(min(wi, len(words) - 1))
            wi = min(wi + len(b["text"].split()), len(words))

        bounds = [words[firsts[i + 1]]["start"] if i + 1 < len(beats) else total
                  for i in range(len(beats))]

        # --- emojik: beatenkent, a felirat ALATT (mint a referenciaban) ---
        # a beatek szo-tartomanya, hogy az emojit konkret szohoz lehessen kotni
        beat_ranges, _wi = [], 0
        for b in beats:
            n = len(b["text"].split())
            beat_ranges.append((_wi, min(_wi + n, len(words))))
            _wi = min(_wi + n, len(words))

        def find_word(bi, on):
            """Az adott beat elso olyan szava, ami 'on'-nal kezdodik."""
            lo, hi = beat_ranges[bi]
            on = on.lower().strip()
            for w in words[lo:hi]:
                if w["w"].lower().strip(".,!?:;…").startswith(on):
                    return w
            return None

        beat_start = [words[lo]["start"] if lo < len(words) else total for lo, _ in beat_ranges]

        # --- hangeffektek ---------------------------------------------------
        sfx_auto = cfg.get("sfx_auto", True)
        sfx_off = cfg.get("sfx_db", 0.0)
        sfx_events = []

        def add_sfx(name, t, db=None):
            f = resolve_sfx(name, root)
            if f:
                lvl = SFX_DB.get(os.path.splitext(os.path.basename(name))[0], -12) if db is None else db
                sfx_events.append({"file": f, "t": max(0.0, t), "db": lvl + sfx_off})

        # --- AUTO mod: vagas, emoji es hang a szkript szerkezetebol + a szovegbol.
        # Alapbol BE. Amit egy beat kezzel megad, az mindig nyer; "emoji": false,
        # "sfx": false, "cut": "cut" az adott beaten kikapcsolja az automatikat.
        auto = cfg.get("auto", True)
        sections, cur_sec = [], None
        for b in beats:                      # a szakasz oroklodik a kovetkezo beatekre
            raw = (b.get("szakasz") or "").strip().lower()
            if raw:
                cur_sec = SZAKASZ.get(raw)
                if not cur_sec:
                    print(f"  ! ismeretlen szakasz: '{raw}' (horog|tet|megoldas|felsorolas|kockazat|cta)")
            sections.append(cur_sec)
        if auto and not any(sections):
            print("  ! auto mod: egy beatnek sincs 'szakasz' mezoje -> vagas nem lesz automatikus "
                  "(emoji es hang igen)")

        # "sfx": "ding" | {"file":"ding","on":"SMS-t","db":-10,"offset":0} | [ ... ]
        for bi, b in enumerate(beats):
            if b.get("sfx") is False:
                continue
            specs = b.get("sfx") or []
            if not isinstance(specs, list):
                specs = [specs]
            for sp in specs:
                if isinstance(sp, str):
                    sp = {"file": sp}
                t = beat_start[bi]
                if sp.get("on"):
                    w = find_word(bi, sp["on"])
                    if w:
                        t = w["start"]
                    else:
                        print(f"  ! sfx: '{sp['on']}' nincs a {bi + 1}. beatben")
                add_sfx(sp["file"], t + sp.get("offset", 0.0), sp.get("db"))

        if auto and sfx_auto:
            # kulcsszo -> hang, beatenkent legfeljebb egy
            for bi, b in enumerate(beats):
                if "sfx" in b:
                    continue
                lo, hi = beat_ranges[bi]
                for w in words[lo:hi]:
                    lw = w["w"].lower().strip(".,!?:;…")
                    hit = next((f for k, f in SFX_AUTO if lw.startswith(k)), None)
                    if hit:
                        add_sfx(hit, w["start"])
                        print(f"      auto hang: {bi + 1}. beat, '{w['w']}' -> {hit}")
                        break
            # felfuto hang a fordulat ele: a megoldas elso beatjenek kezdetere er fel
            for bi in range(1, len(beats)):
                if sections[bi] == "megoldas" and sections[bi - 1] != "megoldas" \
                        and beats[bi].get("sfx") is not False \
                        and not any("riser" in str(x) for x in (beats[bi].get("sfx") or [])):
                    add_sfx("riser", beat_start[bi] - 1.05)
                    print(f"      auto hang: felfuto a {bi + 1}. beat (megoldas) ele")
                    break

        # --- emojik: animalva, szohoz kotve, a felirat ALATT -----------------
        emojis, prev = [], 0.0
        emoji_size = cfg.get("emoji_size", 118)
        emoji_hold = cfg.get("emoji_hold", 1.8)
        emoji_y = cfg.get("emoji_y", (H - cfg.get("caption_margin", 430)) + 118)
        emoji_auto = cfg.get("emoji_auto", auto)
        last_emoji = -9
        for bi, (b, end) in enumerate(zip(beats, bounds)):
            spec = b.get("emoji")
            # emoji_auto: kulcsszobol javasol, de legfeljebb minden masodik beatre
            # (tul surun zaj lesz belole). "emoji": false -> ide soha.
            # A CTA kivetel: ott MINDIG legyen (a 👉 a kattintasra hiv), akkor is,
            # ha az elozo beatnek volt emojija.
            if spec is None and emoji_auto and (bi - last_emoji >= 2 or sections[bi] == "cta"):
                lo, hi = beat_ranges[bi]
                for w in words[lo:hi]:
                    lw = w["w"].lower().strip(".,!?:;…")
                    hit = next((e for k, e in EMOJI_AUTO if lw.startswith(k)), None)
                    if hit:
                        spec = {"char": hit, "on": lw}
                        print(f"      emoji_auto: {bi + 1}. beat, '{w['w']}' -> {hit}")
                        break
            if not spec:
                prev = end
                continue

            # "emoji": "X"                      -> az egesz beat alatt
            # "emoji": {"char":"X","on":"szo"}  -> CSAK amig az a szo szol
            if isinstance(spec, dict):
                ch, on = spec.get("char"), (spec.get("on") or "").lower()
            else:
                ch, on, spec = spec, "", {}

            e_from = prev + 0.10
            e_to = max(prev + 0.40, end - 0.05)
            if on:
                w = find_word(bi, on)
                if w:
                    e_from = w["start"]
                    e_to = min(end, w["start"] + emoji_hold)

            anim = ch and render_emoji_anim(ch, emoji_size, e_to - e_from, tmpdir, f"emo{len(emojis)}")
            if anim:
                seq, cw, chh = anim
                y0 = spec.get("y", emoji_y)
                emojis.append({"seq": seq, "start": e_from, "dx": spec.get("dx", 0),
                               "y": int(y0 - (chh - emoji_size) / 2)})
                if sfx_auto and spec.get("sfx", True):
                    add_sfx("pop", e_from - 0.02)
                last_emoji = bi
            prev = end
        if emojis:
            print(f"      {len(emojis)} emoji")

        # a null shot folytatja az elozot -> osszevonjuk a beateket klippekbe
        # "cut": a beat ELEJEN levo vagas tipusa (cut|punch|flash|whip|slide)
        shots, prev_end = [], 0.0
        for bi_, (b, end) in enumerate(zip(beats, bounds)):
            if b.get("shot") and shots:
                shots[-1]["end"] = prev_end
            if b.get("shot"):
                shots.append({"shot": b["shot"], "start": prev_end, "end": end, "beat": bi_,
                              "cut": b.get("cut", None if auto else cfg.get("cut_default", "cut"))})
            elif shots:
                shots[-1]["end"] = end
            else:
                shots.append({"shot": beats[0]["shot"], "start": 0.0, "end": end, "cut": "cut", "beat": 0})
            prev_end = end
        shots[-1]["end"] = total
        if auto:
            for s, c in zip(shots, auto_cuts(shots, sections, beats)):
                if not s["cut"]:
                    print(f"      auto vagas: {s['beat'] + 1}. beat -> {c}") if c != "cut" else None
                s["cut"] = c or cfg.get("cut_default", "cut")

        # 6 mp fole nem megyunk egy allokeppel - a referenciaban is 5-6 mp
        MAXCLIP = cfg.get("max_clip_sec", 6.0)
        parts = []
        for s in shots:
            t0, t1 = s["start"], s["end"]
            if s["shot"].get("clip"):
                parts.append({"shot": s["shot"], "t0": t0, "t1": t1, "cut": s["cut"], "beat": s["beat"]})
                continue
            n = max(1, int(math.ceil((t1 - t0) / MAXCLIP)))
            z0, z1 = s["shot"].get("zoom", [1.0, 1.15])
            dx, dy = s["shot"].get("drift", [0.0, 0.0])
            for k in range(n):
                f0, f1 = k / n, (k + 1) / n
                sub = dict(s["shot"])
                # a mozgas folytatodik: minden darab a sajat szakaszat viszi
                sub["zoom"] = [z0 + (z1 - z0) * f0, z0 + (z1 - z0) * f1]
                sub["drift"] = [dx / n, dy / n]
                parts.append({"shot": sub, "t0": t0 + (t1 - t0) * f0, "t1": t0 + (t1 - t0) * f1,
                              "cut": s["cut"] if k == 0 else "cut", "beat": s["beat"]})

        # KEPKOCKARA PONTOS hatarok, abszolut idobol. Igy a kerekitesi hiba
        # nem adodik ossze klipprol klippre (a regi hosszalapu szamolasnal igen).
        for p in parts:
            p["f0"], p["f1"] = int(round(p["t0"] * FPS)), int(round(p["t1"] * FPS))
        parts[0]["f0"] = 0
        parts[-1]["f1"] = int(round(total * FPS))
        for i in range(1, len(parts)):
            parts[i]["f0"] = parts[i - 1]["f1"]
            parts[i]["f1"] = max(parts[i]["f1"], parts[i]["f0"] + 2)
        total = parts[-1]["f1"] / FPS
        starts = [p["f0"] / FPS for p in parts]
        cuts = [p["cut"] for p in parts]

        # vagashatasok + a hozzajuk tartozo automatikus hang
        punches, flashes, whips = [], [], []
        for i in range(1, len(parts)):
            c, t = cuts[i], starts[i]
            if c == "punch":
                punches.append((t,) + PUNCH_CUT)
            elif c == "flash":
                flashes.append(t)
                punches.append((t, PUNCH_CUT[0] * 0.5, PUNCH_CUT[1]))
            elif c == "whip":
                whips.append(t + XFADE["whip"][1] / 2)
            if sfx_auto and c in CUT_SFX:
                # a suhogas csucsa ~0.2 mp-nel van -> korabban inditjuk, hogy a vagasra essen
                add_sfx(CUT_SFX[c], t - (0.2 if c in ("whip", "slide") else 0.0))
        for bi, b in enumerate(beats):
            keys = b.get("punch_on") or []
            for k in ([keys] if isinstance(keys, str) else keys):
                w = find_word(bi, k)
                if w:
                    punches.append((w["start"],) + PUNCH_KEY)
                else:
                    print(f"  ! punch_on: '{k}' nincs a {bi + 1}. beatben")

        print(f"[3/5] {len(parts)} klipp renderelese...")
        clips = []
        for i, p in enumerate(parts):
            shot = dict(p["shot"]); shot["_root"] = root
            # atfedeses atmenet elott az elozo klipp hosszabb, kulonben rovidulne az idovonal
            ext = XFADE[cuts[i + 1]][1] if i + 1 < len(parts) and cuts[i + 1] in XFADE else 0.0
            dur = (p["f1"] - p["f0"]) / FPS + ext
            out = os.path.join(tmpdir, f"clip{i:02d}.mp4")
            if shot.get("clip"):
                src = os.path.join(root, shot["clip"])
                amb = video_clip(src, shot, dur, out)
                if amb:
                    sfx_events.append({"file": amb, "t": starts[i], "db": 0.0, "amb": True})
            else:
                src = os.path.join(root, shot["img"])
                kenburns_clip(src, shot, dur, out, tmpdir, i)
            clips.append(out)
            extra = f"  [{cuts[i]}]" if i and cuts[i] != "cut" else ""
            extra += "  +kijelzo" if shot.get("screen") else ""
            print(f"      {i + 1}. {os.path.basename(src)}  {dur:.1f} mp{extra}")

        silent = join_clips(clips, starts, cuts, total, tmpdir, punches, flashes, whips)
        if sfx_events:
            print(f"      {len(sfx_events)} hangeffekt")

        # --- 4. felirat --------------------------------------------------
        print("[4/5] felirat...")
        ass = os.path.join(tmpdir, "cap.ass")
        build_ass(words, ass,
                  fontsize=cfg.get("caption_size", 96),
                  margin_v=cfg.get("caption_margin", 430))

        # --- 5. osszerakas -----------------------------------------------
        print("[5/5] osszerakas...")
        qa_dir = None
        if a.qa:
            qa_dir = os.path.join(tmpdir, "qa"); os.makedirs(qa_dir, exist_ok=True)
        music = cfg.get("music")
        # Allando bal felso jel. Ha van "logo", AZ megy -- a sajat
        # markajel mindig tobbet er, mint egy altalunk rajzolt tabla.
        badge = None
        lcfg = cfg.get("logo")
        if lcfg and lcfg.get("file"):
            lpng = os.path.join(tmpdir, "logo.png")
            if render_logo(os.path.join(root, lcfg["file"]), lpng,
                           lcfg.get("width", 430), lcfg.get("shadow", True)):
                badge = {"png": lpng, "x": lcfg.get("x", 46), "y": lcfg.get("y", 46)}

        bcfg = cfg.get("badge")
        if badge is None and bcfg and (bcfg.get("brand") or bcfg.get("claim")):
            bpng = os.path.join(tmpdir, "badge.png")
            if render_badge(bcfg.get("brand", "MARKANEV"),
                            bcfg.get("claim", ""), bpng, bcfg.get("size", 28)):
                badge = {"png": bpng, "x": bcfg.get("x", 46), "y": bcfg.get("y", 54)}

        cta = None
        ccfg = cfg.get("cta")
        if ccfg and ccfg.get("text"):
            cpng = os.path.join(tmpdir, "cta.png")
            if render_cta(ccfg["text"], cpng, ccfg.get("size", 54)):
                c_from = bounds[-2] if len(bounds) > 1 else 0.0
                cta = {"png": cpng, "y": ccfg.get("y", 1180),
                       "start": c_from, "end": total}

        assemble(silent, vo, ass,
                 os.path.join(root, music) if music else None,
                 out_mp4, tmpdir, cfg.get("music_db", -24), emojis, badge, cta,
                 cfg.get("music_start", 0.0), sfx_events,
                 qa_dir=qa_dir)

        print(f"\nKESZ: {out_mp4}")
        if a.qa:
            qa_report(out_mp4, qa_dir, parts, starts, cuts, beats,
                      [p["beat"] for p in parts], emojis, sfx_events, total)
        if a.offline:
            print("NEMA elonezet. Eles futashoz: ELEVENLABS_API_KEY + a --offline elhagyasa.")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    main()
