# -*- coding: utf-8 -*-
"""HTML -> PNG renderelo (Playwright, helyben, ingyen).

Egy HTML fajlban levo osszes elemet, ami illeszkedik a selectorra, kulon
PNG-be menti. Karuszel-slide-okhoz, OG-kepekhez, idezet-kartyakhoz.

Hasznalat:
    python render.py karuszel.html --out ./kimenet
    python render.py kartya.html --selector ".card" --prefix kartya --scale 2

Elonye a kepgeneralassal szemben: ingyen, pixelpontos, valodi brand-font,
a szoveg szerkesztheto es ujrarenderelheto masodpercek alatt.
"""
import argparse
import io
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def main():
    ap = argparse.ArgumentParser(description="HTML elemek renderelese PNG-be.")
    ap.add_argument("html", help="A forras HTML fajl")
    ap.add_argument("--out", "-o", default="./kimenet", help="Kimeneti mappa (alap: ./kimenet)")
    ap.add_argument("--selector", "-s", default=".slide",
                    help="CSS selector — minden talalat kulon PNG lesz (alap: .slide)")
    ap.add_argument("--prefix", "-p", default="slide", help="Fajlnev-elotag (alap: slide)")
    ap.add_argument("--scale", type=float, default=1,
                    help="device_scale_factor — 2 = retina, duplaakkora PNG (alap: 1)")
    ap.add_argument("--width", type=int, default=1280, help="Viewport szelesseg")
    ap.add_argument("--height", type=int, default=1280, help="Viewport magassag")
    ap.add_argument("--wait", type=int, default=500, help="Extra varakozas ms-ban render elott")
    ap.add_argument("--jpeg", action="store_true", help="JPEG kimenet PNG helyett (kisebb fajl)")
    args = ap.parse_args()

    src = Path(args.html).expanduser().resolve()
    if not src.exists():
        sys.exit("HIBA: nincs ilyen HTML fajl: %s" % src)
    out_dir = Path(args.out).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    ext = "jpg" if args.jpeg else "png"

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        ctx = browser.new_context(
            viewport={"width": args.width, "height": args.height},
            device_scale_factor=args.scale,
        )
        page = ctx.new_page()
        page.goto(src.as_uri(), wait_until="networkidle")
        # A webfontok betoltesere varunk — enelkul fallback fonttal renderelne.
        try:
            page.evaluate("document.fonts.ready")
        except Exception:
            pass
        page.wait_for_timeout(args.wait)

        els = page.query_selector_all(args.selector)
        if not els:
            browser.close()
            sys.exit("HIBA: a '%s' selectorra nincs talalat a %s fajlban." % (args.selector, src.name))

        made = []
        for i, el in enumerate(els, 1):
            target = out_dir / ("%s-%d.%s" % (args.prefix, i, ext))
            if args.jpeg:
                el.screenshot(path=str(target), type="jpeg", quality=92)
            else:
                el.screenshot(path=str(target))
            box = el.bounding_box() or {}
            made.append((target, box))
            print("KESZ: %s  (%dx%d css px, %.0f KB)" % (
                target.name, box.get("width", 0), box.get("height", 0),
                target.stat().st_size / 1024))
        browser.close()

    print("\n%d fajl -> %s" % (len(made), out_dir))
    print("Koltseg: 0 Ft.")


if __name__ == "__main__":
    main()
