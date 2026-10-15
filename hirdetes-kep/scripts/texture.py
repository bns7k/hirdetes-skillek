# -*- coding: utf-8 -*-
"""Beton-textura generalasa a fejlec-betukhoz.

A jo hirdetessorok legjobb eleme: a nagy betuk nem lapos szinnel vannak
kitoltve, hanem egy foltos ko/beton felulettel. Ettol lesz "epitoipari"
a hangulat, es ettol nem nez ki sablonnak.

Nem kell hozza stockfoto -- harom oktav zaj eloallitja.

    python texture.py --out assets/
    python texture.py --out assets/ --seed 12 --size 1200
"""
import argparse
import os
import random

from PIL import Image, ImageFilter, ImageOps


def octave(w, h, cell, lo, hi, rnd):
    """Egy zajreteg: kis raszter, felnagyitva. A cell adja a foltmeretet."""
    n = Image.new("L", (max(2, w // cell), max(2, h // cell)))
    n.putdata([rnd.randint(lo, hi) for _ in range(n.width * n.height)])
    return n.resize((w, h), Image.BICUBIC)


def build(size, seed):
    rnd = random.Random(seed)
    w = h = size

    # Harom oktav: nagy foltok + kozepes szemcse + finom por.
    # Egyedul egyik sem ko; egyutt viszont igen.
    base = Image.blend(octave(w, h, 90, 120, 210, rnd),
                       octave(w, h, 26, 140, 200, rnd), 0.55)
    base = Image.blend(base, octave(w, h, 7, 150, 190, rnd), 0.35)

    # Sotet pettyek: a betonban levo kavicsok es likacsok. Enelkul a
    # textura egyenletes marad, es inkabb papirnak latszik, mint konek.
    spec = octave(w, h, 3, 0, 255, rnd).point(lambda v: 0 if v > 232 else 255)
    base = Image.composite(base.point(lambda v: max(0, v - 70)), base,
                           spec.point(lambda v: 255 - v))

    base = base.filter(ImageFilter.SMOOTH)
    return ImageOps.autocontrast(base, cutoff=2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", "-o", default="assets", help="kimeneti mappa")
    ap.add_argument("--size", type=int, default=900, help="elhossz pixelben")
    ap.add_argument("--seed", type=int, default=7, help="ugyanaz a seed = ugyanaz a textura")
    a = ap.parse_args()

    os.makedirs(a.out, exist_ok=True)
    base = build(a.size, a.seed)

    # Ket valtozat. A VILAGOS kell a szines (.tex-o) fejlechez is:
    # a sotet texturan a szin multiply utan rozsdasbarna lesz.
    base.point(lambda v: int(150 + v * 0.42)).convert("RGB") \
        .save(os.path.join(a.out, "texture-light.png"))
    base.point(lambda v: int(60 + v * 0.55)).convert("RGB") \
        .save(os.path.join(a.out, "texture-dark.png"))

    print("kesz:", os.path.join(a.out, "texture-light.png"))
    print("kesz:", os.path.join(a.out, "texture-dark.png"))


if __name__ == "__main__":
    main()
