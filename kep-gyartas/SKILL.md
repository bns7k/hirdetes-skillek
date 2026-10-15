---
name: kep-gyartas
description: Képgenerálás és képszerkesztés OpenAI gpt-image-2 modellel — hirdetés-kreatívok, közösségi posztok, blog-fejlécek, mockupok, logó-variációk, personal brand vizuálok. Használd, ha a user képet, kreatívot, hirdetést, posztot, illusztrációt, thumbnailt vagy grafikát kér: "/kep-gyartas", "csinálj egy képet", "generálj kreatívot", "kell egy hirdetés-kép", "kép a poszthoz", "make an image", "generate a creative". Támogatja a meglévő kép szerkesztését és a referencia-képes (brand-konzisztens) generálást is.
---

# Képgyártás — gpt-image-2

Kreatívok generálása hirdetéshez, közösségi médiához és márkaanyagokhoz. Minden helyben fut,
közvetlenül az OpenAI API-ra, köztes szolgáltató nélkül.

## ⚠️ Előbb: tényleg ez kell?

**Ha a kreatívon a SZÖVEG a fő tartalom** (karuszel, slide, idézet-kártya, OG-kép,
ár-tábla), akkor **ne ezt használd — használd a `html-kep` skillt.** Az ingyen van,
valódi Space Grotesk fonttal renderel, és a szöveg utólag szerkeszthető. Ez a skill
fizetős, és a betűtípus sosem lesz pontosan márkahű.

Ez a skill akkor jó, ha **képi tartalom** kell: fotórealisztikus jelenet, illusztráció,
absztrakt grafika, mockup, textúra.

**Hibrid (a legjobb):** itt generáld a jelenetet szöveg nélkül, üres negatív térrel —
aztán a `html-kep`-pel ültesd rá a szöveget valódi fonttal.

## Előfeltétel (egyszeri)

API kulcs kell a `~/.claude/.openai-key` fájlban (vagy `OPENAI_API_KEY` env-ben).
Ha hiányzik, a szkript pontosan megmondja, mit tegyen a user — **ne generálj kulcsot,
és ne kérd el chatben.** Irányítsd a https://platform.openai.com/api-keys oldalra.

## Alap használat

```bash
python ~/.claude/skills/kep-gyartas/scripts/gen.py "<prompt>" --out <fajl.png>
```

| Kapcsoló | Mit csinál | Alap |
|---|---|---|
| `--out, -o` | kimeneti fájl | `kep.png` |
| `--quality, -q` | `low` / `medium` / `high` / `auto` | `high` |
| `--size, -s` | `1024x1024`, `1536x1024` (fekvő), `1024x1536` (álló), `2048x2048`, `auto` | `1024x1024` |
| `--n` | hány variáció (több fájl: `nev-1.png`, `nev-2.png`…) | 1 |
| `--edit, -e` | meglévő kép(ek) szerkesztése / referenciaként használata | — |
| `--mask, -m` | maszk PNG — csak a maszkolt rész változik | — |
| `--format, -f` | `png` / `jpeg` / `webp` | `png` |

**Költség 1024×1024-re:** `low` ~$0.006 · `medium` ~$0.053 · `high` ~$0.211.
Nagyobb méret arányosan több. A szkript minden futásnál kiírja a becslést.

**Minőség-választás:** vázlathoz/ötleteléshez `-q low` (fillérek, 3-4 variáció),
és csak a nyertes verziót futtasd újra `-q high`-on. Ne égess `high`-t a felfedezésre.

## Szerkesztés és brand-konzisztencia

A `--edit` a legerősebb funkció: több referencia-képet is átadhatsz, és a modell
megtartja belőlük a stílust/arcot/terméket.

```bash
# meglévő kreatív átszabása
python gen.py "change the headline to 'Soha többé elmulasztott hívás'" -e kreativ-v1.png -o kreativ-v2.png

# brand-konzisztens új kép korábbi kreatívok alapján
python gen.py "same visual style, new scene: HVAC technician in a van" -e ref1.png ref2.png -o uj.png

# csak egy régió cseréje
python gen.py "replace the phone with a modern smartphone" -e alap.png -m maszk.png -o javitott.png
```

## Prompt-írás gpt-image-2-höz

A modell erőssége a **vizuális érvelés és a szövegrenderelés** — ezt használd ki.

1. **Angolul promptolj**, de a képen megjelenő szöveget **valódi magyar ékezetekkel**,
   idézőjelben add meg. Vezesd fel így: `render this Hungarian text with perfectly
   correct accents, character for character:` — utána a szöveg.

   ⚠️ **A leggyakoribb hiba: ASCII-ra egyszerűsíted a magyar szöveget a promptban.**
   Ha azt írod, hogy `Soha tobbe elmulasztott hivas`, a modell pontosan azt is
   rendereli — ékezet nélkül. Nem a modell hibája, a tiéd. Írd ki: `Soha többé
   elmulasztott hívás`.

   Bizonyítottan működik (2026-07 teszt, gpt-image-2, medium): `ő`, `ű`, `ö`, `ü`,
   `í`, `á`, `é`, `ó` mind hibátlan, a dupla vessző is helyes. Az argv UTF-8-ban
   átjut PowerShellen — a konzol *kiírása* töri el, az adat ép, ne ijedj meg tőle.

2. **Hosszú prompthoz használd a `--prompt-file`-t.** Írd a promptot UTF-8 fájlba,
   és add át `-p prompt.txt`-vel. Így nincs PowerShell idézőjel- és escape-gond.
3. **Layoutot írj le, ne hangulatot.** Rossz: „modern, professzionális hirdetés".
   Jó: „left third: bold headline; bottom-right: orange CTA button; dark background,
   subject on the right".
4. **Sorrend számít:** először a jelenet, aztán a kompozíció, aztán a szöveg, végül a stílus.
5. **Negatívokat kerüld** („no text", „without people") — helyette írd le pozitívan, mi legyen.
6. Ha nem stimmel, **ne kezdd elölről** — `--edit`-tel iterálj a legjobb verzión.

## Brand-blokk (példa — írd át a saját márkádra, és másold a promptba)

Ha van a márkának írott stílusleírása, abból töltsd ki. Egy sötét, narancs akcentusú SaaS-márka példája:

```
Brand style: deep dark background (#0A0A0F), single warm orange accent (#FF6A1A),
never a second loud color. Glass-morphism cards: dark translucent surface with
subtle 1px light hairline border, 20px rounded corners. Headline typography:
Space Grotesk Bold, tight negative letter-spacing. Body text: Inter, cream (#F5F5F7).
CTA button: orange gradient (#FF8A3D → #F15C0E), 12px radius, DARK text (#1A0D04)
on the orange — never white. Icons: thin geometric line style. Mood: energetic,
confident, high-tech. Clean, generous negative space.
```

**Vasszabályok** (a példa-márka szabályai; a sajátodéval cseréld le):
- Narancs felületen **mindig sötét** felirat, sosem fehér.
- Egy akcentus. Nincs második hangos szín.
- A narancs csak kiemelés (CTA, ikon) — sosem nagy felület.
- Sötét alap mindig; nincs világos szekció.

## Tipikus feladatok

| Feladat | Méret | Minőség |
|---|---|---|
| Facebook / Instagram feed hirdetés | `1024x1024` | high |
| Story / Reels háttér | `1024x1536` | high |
| Blog-fejléc, OG-kép | `1536x1024` | medium |
| LinkedIn personal brand poszt | `1024x1024` | medium |
| Ötletelés, variáció-vadászat | `1024x1024` | **low**, `-n 4` |

## Munkamenet

1. Kérdezd meg (ha nem derül ki): **melyik márka stílusában?** — céges és személyes márka mást kér.
2. Ötleteléskor: `-q low -n 4`, mutasd meg a variációkat a usernek.
3. A nyertesre: `-q high`, vagy `--edit`-tel finomíts rajta.
4. A kész képet **mindig nézd meg** a Read tool-lal, mielőtt késznek nyilvánítod —
   főleg a magyar szöveget és az ékezeteket a képen.
5. Kreatívok helye: kérdezd meg a usert, hová mentsd.

## Amit ne csinálj

- Ne generálj valós személyt ábrázoló képet (ügyfél, konkurens) az engedélyük nélkül.
- Ne rakj kitalált statisztikát a kreatívra — a BRAND.md tiltja („kitalált statisztikát ne").
- Ne posztold ki magadtól a képet sehova. A generálás után a user dönt.
