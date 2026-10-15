"""
Allokepekbol mozgokep Veo-val (gflow-cli), egy manifestbol, ujrafuttathatoan.

    python veo.py <manifest.json> [--only nev1,nev2] [--proba]

manifest.json:
{
  "dir": "mozgo",                       // ide dolgozik (kezdokep/, klipp/, kontakt/)
  "model": "veo-lite",
  "style": "…",                         // opcionalis; alapbol a lenti STYLE
  "clips": [
    {"name": "k02-muszerfal", "img": "media/b01-muszerfal.png", "cx": 0.42,
     "prompt": "A worker in the background walks slowly to the right…"}
  ]
}

Lepesek klippenkent:
  1. kezdokep PONTOSAN 9:16-ra (1080x1920) vagva, a "cx" vizszintes kozepponttal
     -- kulonben a Flow fekete savval parnaz (ld. mozgokep.md)
  2. gflow video i2v  -- ami mar megvan, azt ATUGORJA (ujrafuttathato)
  3. kontaktlap 7 kockabol (0,3 ... 7,8 mp): EBBOL valaszd ki a tiszta szakaszt,
     es a trim_start-ot oda allitsd. A Veo-klippek elso 1-2 mp-e gyakran
     artefaktos (eltuno ember, ugro alak) -- ezt kell kivagni, nem az egeszet eldobni.

Minden futas elott erdemes: uv tool upgrade gflow-cli
"""
import argparse
import glob
import json
import os
import subprocess
import sys

# Windows-konzolon (cp1252) egy emoji kiirasa UnicodeEncodeError-ral az EGESZ
# renderelest leallitja. Inkabb "?" legyen a konzolon, mint osszeomlas.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

STYLE = (" Everything else in the initial frame stays exactly as it is: same framing, same objects,"
         " same layout, same light. Only a very slight handheld phone drift. Natural desaturated colours,"
         " handheld phone footage look. Any person stays small, turned away from the camera, face never"
         " visible. Screens and papers stay blurred and unreadable.")
TIMES = [0.3, 1.6, 2.9, 4.2, 5.5, 6.8, 7.8]


def crop916(src, dst, cx):
    from PIL import Image
    im = Image.open(src).convert("RGB")
    w, h = im.size
    if w / h > 9 / 16:
        cw, ch = round(h * 9 / 16), h
    else:
        cw, ch = w, round(w * 16 / 9)
    x = int(min(max(cx * w - cw / 2, 0), w - cw))
    y = (h - ch) // 2
    im.crop((x, y, x + cw, y + ch)).resize((1080, 1920), Image.LANCZOS).save(dst)


def contact(clip, out):
    from PIL import Image, ImageDraw, ImageFont
    w, h = 216, 384
    sheet = Image.new("RGB", (len(TIMES) * (w + 4), h + 30), (17, 17, 17))
    d = ImageDraw.Draw(sheet)
    try:
        f = ImageFont.truetype("arial.ttf", 18)
    except Exception:
        f = ImageFont.load_default()
    for i, t in enumerate(TIMES):
        fr = out + f".{i}.png"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", clip, "-frames:v", "1",
                        "-vf", f"scale={w}:{h}", fr])
        if os.path.exists(fr):
            sheet.paste(Image.open(fr), (i * (w + 4), 0))
            os.remove(fr)
        d.text((i * (w + 4) + 4, h + 6), f"{t}s", fill=(255, 255, 255), font=f)
    sheet.save(out, quality=85)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("--only", default="")
    ap.add_argument("--proba", action="store_true", help="csak a kezdokepek, gflow nelkul")
    a = ap.parse_args()

    root = os.path.dirname(os.path.abspath(a.manifest))
    m = json.load(open(a.manifest, encoding="utf-8"))
    wd = os.path.join(root, m.get("dir", "mozgo"))
    for sub in ("kezdokep", "klipp", "kontakt"):
        os.makedirs(os.path.join(wd, sub), exist_ok=True)
    only = {s.strip() for s in a.only.split(",") if s.strip()}
    style = m.get("style", STYLE)

    for c in m["clips"]:
        name = c["name"]
        if only and name not in only:
            continue
        start = os.path.join(wd, "kezdokep", name + ".png")
        crop916(os.path.join(root, c["img"]), start, c.get("cx", 0.5))
        if a.proba:
            print(f"  kezdokep: {start}")
            continue

        cdir = os.path.join(wd, "klipp", name)
        have = glob.glob(os.path.join(cdir, "*.mp4"))
        if have:
            print(f"  {name}: mar megvan, kihagyva ({os.path.basename(have[0])})")
        else:
            print(f"  {name}: generalas...", flush=True)
            r = subprocess.run(["gflow", "video", "i2v", start, c["prompt"].strip() + style,
                                "--aspect", "9:16", "--model", m.get("model", "veo-lite"),
                                "--out-dir", cdir], capture_output=True, text=True)
            have = glob.glob(os.path.join(cdir, "*.mp4"))
            if r.returncode != 0 or not have:
                tail = (r.stderr or r.stdout)[-800:]
                print(f"  !! {name}: nem sikerult\n{tail}")
                if "UiSelectorDrift" in tail:
                    print("     -> uv tool upgrade gflow-cli")
                continue
        ks = os.path.join(wd, "kontakt", name + ".jpg")
        contact(have[0], ks)
        print(f"     kontaktlap: {ks}")
    if not a.proba:
        print("\nKovetkezo: nezd at a kontaktlapokat, es a shot-ba:"
              ' {"clip": "<klipp>", "trim_start": <a tiszta szakasz eleje>, "audio_db": -16}')


if __name__ == "__main__":
    sys.exit(main())
