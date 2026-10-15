"""
UI-animacio (HTML) -> jelenetenkent egy-egy mp4, kockarol kockara.

    python ui_render.py <anim.html> --out <mappa> [--proba] [--prefix ui] [--scenes a,b]

Az oldal szerzodese (lasd sablon/ui-anim/anim.html):
    window.SCENES = {nev: masodperc}   es   window.render(nev, t)

--proba: jelenetenkent 4 kocka (25/50/75/100%) egy kontaktlapra -- elobb ezt nezd meg,
         a teljes render jelenetenkent ~1 perc.

Miert kockankent, es nem kepernyofelvetellel: a render(t) determinisztikus, igy
minden kocka pontosan ott van, ahol kell -- nincs akadozas, nincs elcsuszott idozites,
es ugyanaz a bemenet mindig ugyanazt a videot adja.
"""
import argparse
import os
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

FPS = 30

# A globalis python playwright-ja ezen a gepen csonka (ld. html-kep skill).
# Ha itt nem importalhato, ezekkel a python-okkal inditjuk ujra magunkat.
PY_CANDIDATES = [
    os.environ.get("PLAYWRIGHT_PYTHON", ""),
]


def ensure_playwright():
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
        return
    except ImportError:
        pass
    if os.environ.get("_UI_RENDER_REEXEC"):
        sys.exit("A playwright nem erheto el. Telepites: pip install playwright && playwright install chromium\n"
                 "vagy allitsd be a PLAYWRIGHT_PYTHON valtozot egy olyan python.exe-re, ahol van.")
    for py in PY_CANDIDATES:
        if py and os.path.exists(py):
            env = dict(os.environ, _UI_RENDER_REEXEC="1")
            sys.exit(subprocess.run([py, os.path.abspath(__file__)] + sys.argv[1:], env=env).returncode)
    os.environ["_UI_RENDER_REEXEC"] = "1"
    ensure_playwright()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("--out", default=".")
    ap.add_argument("--prefix", default="ui")
    ap.add_argument("--scenes", default="", help="csak ezek, vesszovel")
    ap.add_argument("--proba", action="store_true")
    a = ap.parse_args()

    ensure_playwright()
    from playwright.sync_api import sync_playwright

    html = os.path.abspath(a.html)
    os.makedirs(a.out, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        pg.goto("file:///" + html.replace("\\", "/"))
        pg.wait_for_timeout(2000)
        pg.evaluate("document.fonts.ready")
        scenes = pg.evaluate("window.SCENES")
        if not scenes:
            sys.exit("Az oldalon nincs window.SCENES = {nev: masodperc} -- lasd a sablont.")
        if a.scenes:
            keep = [s.strip() for s in a.scenes.split(",")]
            scenes = {k: v for k, v in scenes.items() if k in keep}

        if a.proba:
            from PIL import Image
            shots = []
            for sc, dur in scenes.items():
                for q in (0.25, 0.5, 0.75, 1.0):
                    t = min(dur - 1 / FPS, dur * q)
                    pg.evaluate(f"render({sc!r}, {t})")
                    f = os.path.join(a.out, f"_proba-{sc}-{int(q * 100)}.png")
                    pg.screenshot(path=f)
                    shots.append(f)
            w, h, cols = 270, 480, 4
            sheet = Image.new("RGB", (cols * (w + 6), ((len(shots) + cols - 1) // cols) * (h + 6)), (30, 30, 30))
            for i, f in enumerate(shots):
                sheet.paste(Image.open(f).convert("RGB").resize((w, h)), ((i % cols) * (w + 6), (i // cols) * (h + 6)))
                os.remove(f)
            out = os.path.join(a.out, f"{a.prefix}-proba.jpg")
            sheet.save(out, quality=86)
            print("probakockak (soronkent egy jelenet, 25/50/75/100%):", out)
            b.close()
            return

        for sc, dur in scenes.items():
            d = os.path.join(a.out, f"_frames_{sc}")
            shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
            for i in range(int(round(dur * FPS))):
                pg.evaluate(f"render({sc!r}, {i / FPS})")
                pg.screenshot(path=os.path.join(d, f"{i:04d}.png"))
            out = os.path.join(a.out, f"{a.prefix}-{sc}.mp4")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS),
                            "-i", os.path.join(d, "%04d.png"), "-c:v", "libx264",
                            "-pix_fmt", "yuv420p", "-crf", "16", out], check=True)
            shutil.rmtree(d, ignore_errors=True)
            print(f"  {sc:12s} {dur:.1f} mp -> {out}")
        b.close()


if __name__ == "__main__":
    main()
