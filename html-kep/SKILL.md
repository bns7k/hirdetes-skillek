---
name: html-kep
description: Kép készítése HTML+CSS-ből, helyben, ingyen (Playwright screenshot) — karuszel-slide-ok, közösségi posztok, idézet-kártyák, OG-képek, ár-táblák, bármi ami TIPOGRÁFIA-vezérelt. Valódi Space Grotesk/Inter fonttal, pixelpontos brand-színekkel, szerkeszthető szöveggel. Használd, ha a user karuszelt, slide-okat, poszt-képet, idézet-kártyát vagy OG-képet kér, vagy ha egy kreatívon a SZÖVEG a fő tartalom. Fotórealisztikus képhez NE ezt használd — arra a kep-gyartas skill való.
---

# HTML → kép

Tipográfia-vezérelt vizuálok gyártása HTML+CSS-ből, Playwright screenshottal.
**0 Ft, pixelpontos, valódi brand-font, a szöveg szerkeszthető és 2 mp alatt újrarenderelhető.**

## Mikor ezt, mikor a kep-gyartas-t

| Feladat | Eszköz | Miért |
|---|---|---|
| Karuszel, slide, idézet-kártya, OG-kép, ár-tábla | **html-kep** | ingyen, valódi Space Grotesk, javítható szöveg |
| Fotórealisztikus jelenet (szerelő a tetőn, műhely) | **kep-gyartas** | ezt a HTML nem tudja |
| Absztrakt/illusztratív képi elem | **kep-gyartas** | ugyanaz |
| Fotó + rajta márkahű szöveg | **mindkettő** | lásd lentebb |

**Vasszabály:** ha a kreatívon a szöveg a fő tartalom, HTML. AI-képgenerálással a szöveg
sosem lesz pontosan Space Grotesk, és fizetsz érte. A szöveg javításához pedig újra kell
generálni az egészet — HTML-ben egy karaktert írsz át.

## A hibrid (a legjobb minőség)

Fotós háttér + éles, márkahű szöveg:

1. `kep-gyartas`-sal generálj **csak a jelenetet**, szöveg nélkül, üres negatív térrel
   ott, ahova a szöveg jön.
2. Tedd be CSS háttérnek: `.slide { background: url("hatter.png") center/cover; }`
3. A szöveget HTML-ben ültesd rá valódi fonttal.

Így a fotó AI-minőségű, a tipográfia meg pixelpontos és ingyen javítható.

## Használat

⚠️ **A globális `python` playwright-ja csonka** (`ImportError: sync_playwright`).
Mindig a lead-gen venv-jét használd:

```bash
PY="python"   # vagy a Playwright-ot tartalmazó venv pythonja
"$PY" ~/.claude/skills/html-kep/scripts/render.py <fajl.html> --out <mappa>
```

| Kapcsoló | Mit csinál | Alap |
|---|---|---|
| `--out, -o` | kimeneti mappa | `./kimenet` |
| `--selector, -s` | **minden találat külön PNG lesz** | `.slide` |
| `--prefix, -p` | fájlnév-előtag → `slide-1.png`, `slide-2.png`… | `slide` |
| `--scale` | `2` = retina, dupla felbontás | 1 |
| `--width` / `--height` | viewport | 1280 |
| `--jpeg` | JPEG kimenet PNG helyett | — |
| `--wait` | extra várakozás ms-ban render előtt | 500 |

A szkript a `document.fonts.ready`-re vár, szóval a Google Fonts betölt render előtt.

## Sablon

Kész kiindulópont: a `hirdetes-kep` skill `sablon/` mappája (`ads.html` + `brand.css`).

Ezt másold és írd át — a `<style>` blokk teteje tartalmazza a teljes token-készletet
(a márka színeivel és betűivel írd át). Egy `.slide` = egy kimeneti PNG.

**Méretek:** feed 1:1 = 1080×1080 · story/reels 9:16 = 1080×1920 · OG-kép = 1200×630.
A `--S` CSS-változóval állítod.

## Amire figyelj

- **Hosszú szám/telefonszám törhet két sorba** → `white-space: nowrap`.
- **A `&thinsp;` törhető** — ezredes tagoláshoz `nowrap` kell mellé.
- **Narancs felületen mindig sötét felirat** (`--ink`), sosem fehér — `BRAND.md` vasszabály.
- **Egy akcentus.** Ne keverj második hangos színt a narancs mellé.
- A `.lead` `max-width`-je szabja a sortörést — ha csúnya, ezt állítsd, ne a szöveget.
- **Mindig nézd meg a kész PNG-t** a Read tool-lal render után. A layout-hibák (sortörés,
  túlcsordulás) csak a képen látszanak.
