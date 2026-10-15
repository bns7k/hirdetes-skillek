# Konfiguráció

Két fájl. A **`client.json`** a márkáé — ügyfelenként egyszer állítod be. A **`script.json`** a videóé — ezt írod minden új videónál.

A szkript a `"client"` mezővel hivatkozik rá. Ami a szkriptben szerepel, az felülírja a márka-alapértéket.

```
ugyfel/
├── client.json          a márka: hang, szín, tábla, CTA, zene
├── media/               a képek és videók
├── zene/alap.mp3
└── videok/
    ├── a-elso.json      ← "client": "../client.json"
    └── b-masodik.json
```

---

## client.json — márka-szint

| Mező | Mit csinál |
|---|---|
| `voice_id` | ElevenLabs hang azonosítója. Voice Library → a hang → ID |
| `model` | `eleven_multilingual_v2` — ez megy a `/with-timestamps` végponttal |
| `voice_settings` | `stability` 0.55, `style` **0.0**, `speed` 0.93 — magyarra bevált értékek |
| `music` | a zenei alap útvonala |
| `music_start` | **honnan induljon a zene.** Lásd lentebb, fontos |
| `music_db` | a zene szintje a narráció alatt (alap: −24) |
| `caption_size` | feliratméret (84) |
| `caption_margin` | a feliratblokk közepe hány pixelre a képaljától (430) |
| `emoji_size` / `emoji_hold` | emoji mérete, és hogy meddig marad kint szóra kötve (1,8 mp) |
| `max_clip_sec` | egy állókép meddig mehet vágás nélkül (6) |
| `logo` | `{file, width, x, y, shadow}` — **az ügyfél saját logója** a bal felső sarokban. Ha meg van adva, ez megy a `badge` helyett |
| `badge` | `{brand, claim, size, x, y}` — rajzolt tábla. **Csak akkor, ha nincs használható logó** |
| `auto` | **automatikus vágás, emoji és hang** a `szakasz`-ból és a szövegből (alap: `true`). `false` = csak ami kézzel meg van adva |
| `sfx_auto` | automatikus hangeffektek (vágás, emoji, kulcsszó) — `false` csak a hangokat kapcsolja ki (alap: `true`) |
| `sfx_db` | az ÖSSZES hangeffekt együttes eltolása dB-ben (alap: 0). Ha soknak érzed: `-4` |
| `emoji_auto` | kulcsszóból emoji, legfeljebb minden második beatre, a CTA-n mindig (alap: az `auto` értéke) |
| `cut_default` | a vágástípus `"auto": false` esetén, ha a beat nem mond mást (alap: `cut`) |
| `cta` | `{text, size, y}` — gomb az utolsó mondat alatt |
| `accent` | a kiemelt szó színe, `#RRGGBB` (alap: narancs). Sötét márkaszín helyett a világosabb árnyalatát add meg, a felirat képen van |
| `cta_bg` / `cta_fg` | a CTA-gomb háttere és felirata, `#RRGGBB` (alap: narancs / sötét). egy sötét SaaS-márkánál fehér / ink |

### `voice_settings` — miért ezek

- **`style: 0.0`** — a `style` az eredeti hang beszédmintázatát erősíti fel. Angol-natív hangnál magyar szövegen ez épp **az akcentust hangsúlyozza ki**. Tartsd nullán.
- **`stability: 0.55`** — alacsonyabb értéknél idegen fonémákon becsúszik a furcsa hangsúly. 0.7 fölött viszont monoton lesz.
- **`speed: 0.93`** — a magyar mássalhangzó-torlódások lassabban tisztábbak.

### `logo` — mindig ez nyer a rajzolt tábla helyett

Ha az ügyfélnek van logója, **azt tedd be.** A rajzolt `badge` egy pótmegoldás arra az esetre, amikor nincs használható márkajel — nem egy stílusválasztás.

```json
"logo": { "file": "assets/brand/wordmark.png",
          "width": 430, "x": 46, "y": 46, "shadow": true }
```

- **`width`** — csak a szélességet add meg. A magasság ebből jön; a logó aránya szent.
  1080 széles képnél a **380–460** sáv működik: felismerhető, de nem tolakszik.
- **`shadow`** — lágy sötét vetett árnyék. Hagyd bekapcsolva: a legtöbb wordmark majdnem fehér, és egy világos képen (sátorponyva, ég, hó) nyomtalanul eltűnne.
- A szkript az **alfa-bboxra vágja** a fájlt, mielőtt méretezne. Enélkül a márkafájlok körüli üres keret miatt a logó optikailag beljebb ülne, mint a feliratmargó.

Átlátszó hátterű **PNG** kell. Fehér hátterű JPG-ből fehér doboz lesz a képen.

---

### `music_start` — ezt mindig mérd meg

Szinte minden zenei alapnak van felvezetése. Ha a track elejéről indítod, a videó eleje halk lesz, majd a közepén hirtelen beesik a zene — ez feltűnőbb hiba, mint a halk zene.

Pásztázd végig 3 másodperces ablakokkal:

```bash
for t in 0 3 6 9 12 15 18 21 24; do
  echo -n "${t}s: "
  ffmpeg -hide_banner -ss $t -t 3 -i zene.mp3 -af volumedetect -f null - 2>&1 | grep mean_volume
done
```

Oda tedd a `music_start`-ot, ahol stabilan eléri a maximumot. Tapasztalt értékek: **0, 15, 21** másodperc — nem lehet megsaccolni.

---

## script.json — egy videó

```json
{
  "id": "a-elso-video",
  "client": "../client.json",
  "beats": [ ... ]
}
```

### Egy beat

| Mező | Mit csinál |
|---|---|
| `text` | amit a hang mond **és** amit a felirat ír. A kettő ugyanaz. |
| `emoji` | `{char, on}` — az emoji arra a **szóra** esik. Sima string esetén az egész beat alatt kint marad. |
| `szakasz` | `horog` · `tet` · `megoldas` · `felsorolas` · `kockazat` · `cta` — öröklődik a következő beatekre. **Ebből jön az automatikus vágás.** |
| `cut` | a beat ELEJÉN lévő vágás (felülírja az automatikát): `cut` · `punch` · `flash` · `whip` · `slide` — lásd lentebb |
| `punch_on` | szó (vagy szólista), amelynél a kép finoman beugrik: a kiemelés képi párja |
| `sfx` | hangeffekt: `"ding"` vagy `{file, on, db, offset}` vagy ezek listája |
| `shot` | új klippet nyit. **`null`** = az előző klipp folytatódik. |

### Állókép

```json
"shot": { "img": "media/kep.jpg", "center": [0.52, 0.62],
          "zoom": [1.00, 1.28], "drift": [0.02, 0.015] }
```

- **`center`** — a kivágás közepe a forrásképen, 0–1
- **`zoom`** — `[honnan, hova]`. `1.0` = a legszélesebb 9:16 kivágás
- **`drift`** — lassú elmozdulás a kivágás arányában

**A zoom legyen bátor.** Egy `[1.0, 1.12]` mozgás ~3%/mp — szemmel **alig érzékelhető**, a kép megállt fotónak hat. Használható tartomány: **`1.0 → 1.25-1.35`**. És adj mindig **kétirányú driftet** is; a tiszta zoom élettelen.

**Ugyanaz a fotó többször?** Adj neki **gyökeresen más `center`-t és `zoom`-ot**, különben „ugyanaz a kép megint" érzés lesz.

### Videóklipp

```json
"shot": { "clip": "media/felvetel.mp4", "trim_start": 2.4, "speed": 1.0 }
```

- **`trim_start`** — hányadik másodperctől
- **`speed`** — 1.0 = eredeti, vagy **`"fit"`**: a gépsor számolja ki. Mellé **`action`**: a klipp hány másodperce a lényeg (pl. egy UI-animáció ennyi alatt fut végig). A lényeg belefér a beatbe, a végén ~0,9 mp „megállással", hogy a néző lássa az eredményt. Lassítani nem lassít, 2,5× fölé nem gyorsít.
- **`audio_db`** — a klipp saját hangja a narráció alatt, **ennyi dB-lel a beszéd alatt** (előtte egységesítve). Veo-klippnél: **−16**. Elhagyva: néma.
- A videót **nem darabolja fel** a 6 másodperces szabály — az állóképre való.
- Ha a klipp rövidebb a beatnél, az utolsó kockán fagyaszt (`tpad`), nem rövidíti meg a beatet.

---

### Az automatika szabályai

| Mit | Honnan jön magától |
|---|---|
| **Vágás** | a `szakasz`-ból: a **megoldás** első képe `flash`, a **felsorolás** képei `slide` (kivéve egy sorozat egymást követő klippjeit, pl. `ui-hivas` → `ui-sms`: az egy folyamat), a **kockázatlevétel** első képe `whip`, a **CTA** `punch`. Minden más kemény vágás. |
| **Emoji** | kulcsszóból (telefon 📞, SMS 💬, naptár 📅, pénz 💸, lista 📋, kattints 👉 …), legfeljebb minden második beatre — a **CTA mindig** kap |
| **Hang** | kulcsszóból, beatenként legfeljebb egy (SMS → `ding`, hív/telefon → `ring`, fizet/pénz/havidíj → `coin`, naptár/beír/foglal → `click`); **felfutó hang** a megoldás elé; `hit`/`whoosh` a különleges vágásokra; `pop` az emojikra |

Amit egy beat kézzel megad, az nyer. `"emoji": false`, `"sfx": false`, `"cut": "cut"` az adott beaten kikapcsolja.

### Vágástípusok — `cut`

| Típus | Mit csinál | Hova jó | Automatikus hang |
|---|---|---|---|
| `cut` | kemény vágás | alapeset, összefüggő jelenetek között (pl. egy UI-folyamat lépései) | — |
| `punch` | a kép 10%-kal nagyobbról ugrik a helyére (0,26 mp) | fordulat, CTA, belépés egy felületbe | `hit` |
| `flash` | 5 kocka fehér villanás + fél punch | a nagy fordulat (probléma → megoldás) | `hit` |
| `whip` | gyors oldalra söprés, vízszintes elmosással | helyszínváltás, visszatérés a valóságba | `whoosh` |
| `slide` | lágy becsúszás (0,28 mp) | felsorolás | `whoosh-soft` |

A `whip` és a `slide` átfedéses: a gépsor az **előző** klippet ennyivel hosszabban rendereli, így az idővonal nem rövidül és a feliratszinkron megmarad. **Egy videóban 3-5 különleges vágás elég** — ha minden vágás „csinál valamit", egyik sem hat.

### Hangeffektek — `sfx`

```json
{ "text": "Ha nem veszik fel, SMS-t küld.",
  "sfx": { "file": "ding", "on": "SMS-t" } }

{ "text": "Mi felépítünk neked egy rendszert…",
  "sfx": [ { "file": "riser", "offset": -1.05 } ] }        ← a beat ELŐTT indul, a fordulatra fut fel
```

| Mező | |
|---|---|
| `file` | beépített név, vagy saját fájl (a projekt `sfx/` mappájából, azonos névvel felülírja a beépítettet) |
| `on` | a szó eleje, amire essen. Nélküle a beat első szavára |
| `offset` | eltolás mp-ben (negatív is lehet) |
| `db` | egyedi szint; alapból a beépített táblázat |

**Beépített könyvtár** (`assets/sfx/`, szintetizált, licencmentes, `scripts/sfx_gen.py` gyártja újra): `whoosh`, `whoosh-soft`, `pop`, `ding` (SMS/értesítés), `click`, `tick`, `ring` (puha csörgés), `riser` (felfutás a fordulat elé), `hit` (tompa ütés), `coin`.

A hangeffekt a zene ducking-ja **után** keveredik be: nem nyomja le a zenét, a narrációhoz képest fix szinten marad.

**Videóklipp saját hangja:** `"shot": {"clip": …, "audio_db": -16}` — a Veo-klippek utcazaja, léptei halkan a narráció alatt. Ettől lesz „valódi felvétel" érzete. Csak 1.0-s sebességnél. A gépsor előbb egységes szintre hozza (a nyers Veo-hangok között 24 dB is lehet).

### Emoji — animálva

Az emoji most **beugrik** (túllövéssel, 0,22 mp) és a végén **kiugrik** — nem egyszerűen megjelenik. Mellé automatikusan egy halk `pop` szól (`"emoji": {"char":"💬","on":"SMS-t","sfx":false}` kikapcsolja).

- **Sűrűség:** ~5-7 emoji 30 mp-re. Ennél több már zaj.
- **UI-klipp alatt is mehet:** az emoji a felirat alatt ül (y ≈ 1600), a rendszer-animáció 1400 fölött ér véget.
- `"emoji": false` — ide az `emoji_auto` se tegyen.

### Kijelzőcsere — `screen`

Egy fotón lévő telefon/laptop kijelzőjére **videót** vetít, perspektívában, a Ken Burns mozgással együtt:

```json
"shot": { "img": "media/b05-laptop.png", "center": [0.37, 0.55], "zoom": [1.30, 1.50],
  "screen": { "clip": "media/rendszer-lista.mp4",
              "corners": [[208,742], [520,717], [540,893], [227,930]],
              "crop": [40, 200, 1000, 1200], "fit": "contain" } }
```

| Mező | |
|---|---|
| `corners` | a kijelző 4 sarka **a forráskép pixeleiben**: bal-felső, jobb-felső, jobb-alsó, bal-alsó |
| `crop` | a klipp melyik része kerüljön a kijelzőre `[x, y, w, h]` |
| `fit` | `contain` (alap; a maradék `bg` színű) vagy `cover` |
| `trim_start`, `speed` | mint a videóklippnél |
| `brightness` (0.88), `glare` (0.14), `soften` (0.6) | a „lefotózott kijelző" hatás: enyhe sötétítés, az eredeti tükröződés visszakeverése, lágyítás |

**A sarkak mérése:** rajzolj rácsot a képre 20 px-es lépésekkel, nagyítsd 2-3×, és olvasd le. Két perc, és pontosabb, mint bármilyen becslés. A telefon kerekített sarkainál a kijelző *egyenes* éleinek meghosszabbítását vedd.

**Csak állóképen működik.** Videóklippen (pl. Veo) a kamera mozog, a sarkakat követni kellene — ezt nem tudja.

**Miért éri meg:** a természetes fotó és a rendszer egy képben — nem egy külön grafika, hanem *a te laptopodon* töltődik be a lista. Egy generált kép üres kijelzője így válik bizonyítékká.

---

### UI-animáció — a rendszer működés közben

Ha a termék egy felület vagy folyamat, a `sablon/ui-anim/anim.html`-ből indulj (a `pelda-hivaskezelo.html` egy kész, ötjelenetes példa: lista → hívás → SMS → újrahívás → naptár).

**A szerződés:** `window.SCENES = {név: mp}` és egy **determinisztikus** `window.render(név, t)`. Minden jelenet az előző végállapotából induljon — így a vágások ellenére egy folyamatnak látszik.

```bash
python scripts/ui_render.py anim.html --out media --proba    # kontaktlap, 10 mp
python scripts/ui_render.py anim.html --out media            # media/ui-<jelenet>.mp4
```

A shot-ban: `{"clip": "media/ui-hivas.mp4", "speed": "fit", "action": 2.6}`, vagy egy fotó kijelzőjén: `"screen": {"clip": "media/ui-lista.mp4", …}`.

---

## Futtatás

```bash
python scripts/make.py ugyfel/videok/a-elso.json --offline --qa   # néma előnézet
python scripts/make.py ugyfel/videok/a-elso.json --qa             # éles

# a TTS gyorsítótárból jön, ha a szöveg és a hang nem változott
# (.tts-cache/ a config mellett) -- kép- és vágásmódosítás ingyenes
```

Kimenet: a config melletti `out/` mappa, `<id>.mp4` néven.

---

## Ellenőrzés a kész fájlon

Mindig a **végeredményt** mérd, ne az összetevőket:

```bash
ffmpeg -i out/video.mp4 -af ebur128=framelog=quiet -f null -          # cél: kb. -14 LUFS
ffmpeg -i out/video.mp4 -af silencedetect=noise=-45dB:d=0.25 -f null - # cél: 0 találat
ffmpeg -i out/video.mp4 -f null -                                      # cél: néma kimenet
```
