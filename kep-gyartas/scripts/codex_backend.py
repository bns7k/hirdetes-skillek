# -*- coding: utf-8 -*-
"""Kepgeneralas a ChatGPT-elofizetesbol, a Codex CLI beepitett image_gen eszkozevel.

Nem API-kredit: a `codex login` (ChatGPT-fiok) Codex-keretebol fogy. Egy kep
kb. 45 mp - 2 perc. A gen.py hivja, alapertelmezett backendkent.

A futas: `codex exec` egy ures ideiglenes mappaban, a prompt stdin-en megy at,
a referenciakepek `-i`-vel. A kesz kep a $CODEX_HOME/generated_images/<thread_id>/
mappaba kerul — onnan masoljuk a kert helyre.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

CODEX_HOME = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")
GEN_DIR = CODEX_HOME / "generated_images"
TIMEOUT = 600

QUALITY_HINT = {
    "low": "Quality: low (fast draft).",
    "medium": "Quality: medium.",
    "high": "Quality: high, maximum detail.",
    "auto": "",
}


def build_prompt(args) -> str:
    size = args.size
    if size == "auto":
        size_line = "Choose the best size and aspect ratio for the content."
    else:
        w, h = (int(x) for x in size.lower().split("x"))
        orient = "square" if w == h else ("landscape" if w > h else "portrait")
        size_line = "Output size: exactly %dx%d pixels (%s)." % (w, h, orient)
    refs = ""
    if args.edit:
        refs = ("The attached image(s) are references / the image to edit. "
                "Follow the instructions below about how to use them.\n")
    return (
        "Use your built-in image generation tool exactly once to produce a single image. "
        "Pass the image description below to the tool as faithfully as possible, "
        "without shortening or rewriting it, and keep any quoted on-image text "
        "character for character (including Hungarian accents).\n"
        "%s%s %s\n"
        "Do not run shell commands, do not write files, do not ask questions. "
        "After the image is generated, reply only with DONE.\n\n"
        "IMAGE DESCRIPTION:\n%s\n"
    ) % (refs, size_line, QUALITY_HINT.get(args.quality, ""), args.prompt)


def find_codex() -> str:
    exe = shutil.which("codex")
    if not exe:
        sys.exit(
            "HIBA: nem talalom a Codex CLI-t.\n"
            "  Telepites:  npm install -g @openai/codex@latest\n"
            "  Belepes:    codex login   (ChatGPT-fiokkal)\n"
            "  Vagy fuss API-kredittel: --api"
        )
    return exe


def run_one(exe: str, prompt: str, images: list) -> tuple:
    """Egy codex exec futas. Visszaad: (png_path | None, hibauzenet | None)."""
    cmd = [exe, "exec", "--json", "--skip-git-repo-check", "--ephemeral",
           "--ignore-user-config", "-s", "read-only"]
    for img in images:
        cmd += ["-i", str(img)]
    cmd.append("-")  # prompt stdin-rol (a -i tobb erteket is elnyelne)
    started = time.time()
    with tempfile.TemporaryDirectory(prefix="kepgyartas-") as cwd:
        try:
            proc = subprocess.run(cmd, input=prompt.encode("utf-8"), cwd=cwd,
                                  capture_output=True, timeout=TIMEOUT)
        except subprocess.TimeoutExpired:
            return None, "idotullepes (%d mp)" % TIMEOUT
    out = proc.stdout.decode("utf-8", "replace")
    err = proc.stderr.decode("utf-8", "replace")

    thread_id, errors, last_msg = None, [], ""
    for line in out.splitlines():
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        t = ev.get("type")
        if t == "thread.started":
            thread_id = ev.get("thread_id")
        elif t in ("error", "turn.failed"):
            errors.append(json.dumps(ev.get("error") or ev.get("message") or ev, ensure_ascii=False))
        elif t == "item.completed":
            item = ev.get("item") or {}
            if item.get("type") == "agent_message":
                last_msg = item.get("text", "")

    pngs = []
    if thread_id and (GEN_DIR / thread_id).is_dir():
        pngs = sorted((GEN_DIR / thread_id).glob("*.png"), key=lambda p: p.stat().st_mtime)
    if not pngs and GEN_DIR.is_dir():  # tartalek: a futas alatt keletkezett uj fajl
        pngs = sorted((p for p in GEN_DIR.rglob("*.png") if p.stat().st_mtime >= started - 1),
                      key=lambda p: p.stat().st_mtime)
    if pngs:
        return pngs[-1], None

    blob = (" ".join(errors) + " " + err + " " + last_msg).lower()
    if "usage_limit" in blob or "usage limit" in blob or "rate limit" in blob:
        return None, ("elfogyott a Codex-keret (ChatGPT-elofizetes). Nezd meg: codex -> /status. "
                      "Ha surgos, futtasd API-kredittel: --api")
    if "login" in blob or "unauthorized" in blob or "401" in blob:
        return None, "a Codex nincs bejelentkezve. Futtasd: codex login"
    detail = "; ".join(errors) or last_msg or err.strip().splitlines()[-1:] or "ismeretlen"
    return None, "nem keszult kep (exit=%s): %s" % (proc.returncode, str(detail)[:600])


def run(args, out: Path) -> None:
    if args.mask:
        print("FIGYELEM: a --mask a Codex-backenddel nem tamogatott, kihagyom "
              "(pontos regiocserehez: --api).")
    if args.format != "png":
        print("FIGYELEM: a Codex PNG-t ad; a(z) %s formatumot nem konvertalom." % args.format)
        out = out.with_suffix(".png")
    exe = find_codex()
    prompt = build_prompt(args)
    images = [Path(p).expanduser().resolve() for p in (args.edit or [])]
    for p in images:
        if not p.exists():
            sys.exit("HIBA: nincs ilyen fajl: %s" % p)

    print("-> Codex (ChatGPT-elofizetes) | %s | %s | n=%d | API-koltseg: $0" % (
        args.quality, args.size, args.n))
    if images:
        print("  %d referencia kep" % len(images))
    print("  generalas... (kepenkent ~1-2 perc)")

    with ThreadPoolExecutor(max_workers=min(args.n, 3)) as pool:
        results = list(pool.map(lambda _: run_one(exe, prompt, images), range(args.n)))

    out.parent.mkdir(parents=True, exist_ok=True)
    ok = 0
    for i, (src, error) in enumerate(results, 1):
        target = out if args.n == 1 else out.with_name("%s-%d%s" % (out.stem, i, out.suffix))
        if error:
            print("HIBA (%d. kep): %s" % (i, error))
            continue
        shutil.copyfile(src, target)
        ok += 1
        print("KESZ: %s (%.1f KB)" % (target, target.stat().st_size / 1024))
    if not ok:
        sys.exit(1)
