"""
Koordinata-racs egy kep egy reszere -- a kijelzocsere (shot.screen.corners)
sarkainak kimeresehez. A cimkek a FORRASKEP pixelei, igy ami leolvashato,
az megy egy az egyben a config-ba.

    python racs.py <kep> [--box x0,y0,x1,y1] [--step 20] [--scale 3] [--out racs.png]

Menete: elobb --box nelkul (az egesz kep, 100-as racs), abbol latszik, hol a
kijelzo; utana --box-szal ra a kijelzore, 20-as racs, 2-3x nagyitas.
Telefonnal: a kerekitett sarkok helyett az EGYENES elek meghosszabbitasat vedd.
"""
import argparse
import os

from PIL import Image, ImageDraw, ImageFont


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("img")
    ap.add_argument("--box", default="")
    ap.add_argument("--step", type=int, default=0)
    ap.add_argument("--scale", type=float, default=0)
    ap.add_argument("--out", default="")
    a = ap.parse_args()

    im = Image.open(a.img).convert("RGB")
    box = tuple(int(v) for v in a.box.split(",")) if a.box else (0, 0, im.width, im.height)
    step = a.step or (20 if a.box else 100)
    crop = im.crop(box)
    scale = a.scale or (min(3.0, 1100 / max(crop.size)) if a.box else min(1.0, 1100 / max(crop.size)))
    crop = crop.resize((int(crop.width * scale), int(crop.height * scale)), Image.LANCZOS)
    d = ImageDraw.Draw(crop)
    try:
        f = ImageFont.truetype("arial.ttf", 15)
    except Exception:
        f = ImageFont.load_default()

    major = step * 5
    for x in range((box[0] // step + 1) * step, box[2], step):
        X = (x - box[0]) * scale
        big = x % major == 0
        d.line([(X, 0), (X, crop.height)], fill=(255, 40, 40) if big else (255, 150, 150), width=1)
        if big:
            d.text((X + 3, 3), str(x), fill=(255, 255, 0), font=f, stroke_width=2, stroke_fill=(0, 0, 0))
    for y in range((box[1] // step + 1) * step, box[3], step):
        Y = (y - box[1]) * scale
        big = y % major == 0
        d.line([(0, Y), (crop.width, Y)], fill=(40, 220, 40) if big else (150, 255, 150), width=1)
        if big:
            d.text((3, Y + 3), str(y), fill=(255, 255, 0), font=f, stroke_width=2, stroke_fill=(0, 0, 0))

    out = a.out or os.path.splitext(a.img)[0] + "-racs.png"
    crop.save(out)
    print(f"racs: {out}  (lepes {step} px, nagyitas {scale:.2f}x, a cimkek forraskep-pixelek)")


if __name__ == "__main__":
    main()
