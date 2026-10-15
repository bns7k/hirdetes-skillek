# -*- coding: utf-8 -*-
"""Kepgyarto — gpt-image-2 CLI.

Alapbol a ChatGPT-elofizetesbol general (Codex CLI, codex_backend.py) — nincs
API-koltseg. --api kapcsoloval az OpenAI API-t hivja (kredit, de --mask es
jpeg/webp is megy). Csak Python stdlib, nincs pip install.

Hasznalat:
    python gen.py "prompt szovege" --out kep.png
    python gen.py "tedd ra a logot" --edit alap.png logo.png --out v2.png
    python gen.py "prompt" -q medium -s 1536x1024 -n 3 --out variacio.png

Kulcs: OPENAI_API_KEY kornyezeti valtozo, vagy ~/.claude/.openai-key fajl.
"""
import argparse
import base64
import io
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

API_GEN = "https://api.openai.com/v1/images/generations"
API_EDIT = "https://api.openai.com/v1/images/edits"
KEY_FILE = Path.home() / ".claude" / ".openai-key"

# Becsult ar 1024x1024-re, USD/kep. Nagyobb meret aranyosan tobb.
COST = {"low": 0.006, "medium": 0.053, "high": 0.211, "auto": 0.053}


def get_key() -> str:
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key and KEY_FILE.exists():
        key = KEY_FILE.read_text(encoding="utf-8").strip()
    if not key:
        sys.exit(
            "HIBA: nincs OpenAI API kulcs.\n"
            "  1) Szerezz egyet: https://platform.openai.com/api-keys\n"
            "  2) Mentsd ide: %s\n"
            "     (vagy allitsd be az OPENAI_API_KEY kornyezeti valtozot)" % KEY_FILE
        )
    return key


def multipart(fields: dict, files: list) -> tuple:
    """multipart/form-data osszeallitasa (a /v1/images/edits ezt varja)."""
    boundary = "----kepgyarto" + base64.urlsafe_b64encode(os.urandom(12)).decode().strip("=")
    body = bytearray()
    for name, value in fields.items():
        if value is None:
            continue
        body += b"--" + boundary.encode() + b"\r\n"
        body += ('Content-Disposition: form-data; name="%s"\r\n\r\n' % name).encode()
        body += str(value).encode("utf-8") + b"\r\n"
    for name, path in files:
        p = Path(path)
        if not p.exists():
            sys.exit("HIBA: nincs ilyen fajl: %s" % p)
        ctype = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
        body += b"--" + boundary.encode() + b"\r\n"
        body += (
            'Content-Disposition: form-data; name="%s"; filename="%s"\r\n' % (name, p.name)
        ).encode()
        body += ("Content-Type: %s\r\n\r\n" % ctype).encode()
        body += p.read_bytes() + b"\r\n"
    body += b"--" + boundary.encode() + b"--\r\n"
    return bytes(body), "multipart/form-data; boundary=" + boundary


def post(url: str, data: bytes, ctype: str, key: str, timeout: int = 600) -> dict:
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", "Bearer " + key)
    req.add_header("Content-Type", ctype)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")
        try:
            detail = json.loads(detail)["error"]["message"]
        except Exception:
            pass
        sys.exit("API HIBA (%s): %s" % (e.code, detail))
    except urllib.error.URLError as e:
        sys.exit("HALOZATI HIBA: %s" % e.reason)


def save(result: dict, out: Path, fmt: str) -> list:
    items = result.get("data") or []
    if not items:
        sys.exit("HIBA: a valasz nem tartalmazott kepet:\n%s" % json.dumps(result)[:800])
    out.parent.mkdir(parents=True, exist_ok=True)
    paths = []
    for i, item in enumerate(items, 1):
        b64 = item.get("b64_json")
        if not b64:
            continue
        target = out if len(items) == 1 else out.with_name("%s-%d%s" % (out.stem, i, out.suffix))
        target.write_bytes(base64.b64decode(b64))
        paths.append(target)
    return paths


def main():
    ap = argparse.ArgumentParser(
        description="Kepgeneralas es -szerkesztes OpenAI gpt-image-2 modellel.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("prompt", nargs="?", default=None,
                    help="A kep leirasa (angolul a legpontosabb, de a kepen levo szoveg lehet magyar)")
    ap.add_argument("--prompt-file", "-p", metavar="FAJL",
                    help="A promptot fajlbol olvassa (UTF-8) — hosszu promptokhoz, idezojel-gondok nelkul")
    ap.add_argument("--out", "-o", default="kep.png", help="Kimeneti fajl (alap: kep.png)")
    ap.add_argument("--quality", "-q", default="high", choices=["low", "medium", "high", "auto"],
                    help="Minoseg (alap: high)")
    ap.add_argument("--size", "-s", default="1024x1024",
                    help="Meret, pl. 1024x1024 | 1536x1024 | 1024x1536 | 2048x2048 | auto")
    ap.add_argument("--n", type=int, default=1, help="Hany variacio (alap: 1)")
    ap.add_argument("--edit", "-e", nargs="+", metavar="KEP",
                    help="Szerkesztendo / referencia kepek — ilyenkor az /edits vegpont fut")
    ap.add_argument("--mask", "-m", help="Maszk PNG (alfa-csatornaval), csak --edit mellett")
    ap.add_argument("--format", "-f", default="png", choices=["png", "jpeg", "webp"],
                    help="Kimeneti formatum (alap: png)")
    ap.add_argument("--model", default="gpt-image-2", help="Modell (alap: gpt-image-2, csak --api)")
    ap.add_argument("--api", action="store_true",
                    help="OpenAI API-kredittel fusson a ChatGPT-elofizetes (Codex) helyett")
    args = ap.parse_args()

    if args.prompt_file:
        pf = Path(args.prompt_file).expanduser()
        if not pf.exists():
            sys.exit("HIBA: nincs ilyen prompt-fajl: %s" % pf)
        args.prompt = pf.read_text(encoding="utf-8").strip()
    if not args.prompt:
        sys.exit("HIBA: adj meg promptot argumentumkent, vagy hasznald a --prompt-file kapcsolot.")

    out = Path(args.out).expanduser().resolve()
    if not args.api:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import codex_backend
        codex_backend.run(args, out)
        return

    key = get_key()

    est = COST.get(args.quality, 0.053) * args.n
    print("→ %s | %s | %s | n=%d | becsult koltseg: ~$%.3f" % (
        args.model, args.quality, args.size, args.n, est))

    if args.edit:
        files = [("image[]", p) for p in args.edit]
        if args.mask:
            files.append(("mask", args.mask))
        fields = {
            "model": args.model,
            "prompt": args.prompt,
            "size": args.size,
            "quality": args.quality,
            "n": args.n,
            "output_format": args.format,
        }
        data, ctype = multipart(fields, files)
        print("  szerkesztes %d referencia kep alapjan..." % len(args.edit))
        result = post(API_EDIT, data, ctype, key)
    else:
        payload = {
            "model": args.model,
            "prompt": args.prompt,
            "size": args.size,
            "quality": args.quality,
            "n": args.n,
            "output_format": args.format,
        }
        print("  generalas...")
        result = post(API_GEN, json.dumps(payload).encode("utf-8"), "application/json", key)

    paths = save(result, out, args.format)
    usage = result.get("usage") or {}
    for p in paths:
        print("KESZ: %s (%.1f KB)" % (p, p.stat().st_size / 1024))
    if usage:
        print("  tokenek: input=%s output=%s" % (
            usage.get("input_tokens", "?"), usage.get("output_tokens", "?")))


if __name__ == "__main__":
    main()
