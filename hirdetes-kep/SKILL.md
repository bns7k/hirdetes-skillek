---
name: hirdetes-kep
description: Statikus hirdetéskép gyártása HTML+CSS-ből — kategória-sorozat, összehasonlító tábla, adatlap-plakát, nyers fotó. A kategória valódi, futó hirdetéseiből visszafejtve, nem ízlés alapján. Használd, ha a user statikus hirdetést, feed-kreatívot, Meta/Facebook adot, karuszelt vagy poszt-képet kér egy termékhez vagy szolgáltatáshoz ("csinálj statikus hirdetést", "kell egy feed kreatív", "statikus ad", "hirdetéskép"), ha egy meglévő hirdetéssor vizuális stílusát kell átvenni és újraépíteni, vagy ha azt kell kideríteni, milyen statikus hirdetések működnek egy adott piacon. NEM erre való: hirdetésvideó (arra a hirdetes-video), fotórealisztikus jelenet generálása (arra a kep-gyartas).
---

# Statikus hirdetéskép

Meta feed-kreatív HTML+CSS-ből, Playwright screenshottal. **0 Ft, pixelpontos, a szöveg egy karakterrel javítható.**

A rendert a [`html-kep`](../html-kep/SKILL.md) skill végzi — ez a skill azt mondja meg, **mit** rendereljünk.

---

## A vasszabály

> **Előbb nézd meg, mi fut a kategóriában. Csak utána tervezz.**

Ez a skill azért létezik ebben a formában, mert egyszer fordítva csináltam: átvettem egy meglévő hirdetéssor *dizájnját*, és nem néztem meg, hogy az a dizájn egyáltalán működik-e. Négy szép plakát lett belőle, amin három olyan elem volt, ami a kategória egyetlen futó hirdetésén sem szerepel.

A terep-kutatás egy óra. Módszer: [`references/referencia-kutatas.md`](references/referencia-kutatas.md)

---

## A három tiltás

Ez a kutatás legkeményebb eredménye. **Minden formátumra érvényes**, és mindhárom azért van itt, mert elrontottam.

| ⛔ | Miért |
|---|---|
| **Nincs képbe égetett CTA-gomb** | A megvizsgált ~40 kategóriabeli kreatív közül **egyetlenegyen sem volt**, a tíz hónapja futón sem. A Meta úgyis odateszi a saját gombját a kép alá, plusz a link-címsort. A ráégetett gomb egy negyedik kattintási felület, és csak azt kiabálja, hogy „ez hirdetés". |
| **Nincs ikoncsempe-sor** | A referenciákon nincs. A feedben zaj. Carousel-lapra és Story-ra jó, hideg feedbe nem. |
| **A logó kicsi és halk** | A márka a landingen épül. A nagy logó a tetején az első dolog, amitől hirdetésnek olvasódik a kép. |

---

## A második vasszabály

> **A fejléc ne mondja el, mi látszik a képen.**

A kép a bizonyíték, a fejléc a **következtetés**. Ha a kép sáros terepet mutat és a fejléc azt írja, „Sáros a terep", a kreatív egyetlen információt közöl kétszer.

| Kép | ❌ Képaláírás | ✅ Következtetés |
|---|---|---|
| fesztivál nagyszínpad burkolaton | „Fesztivál burkolattal" | „Nem a pult alá. Az egész területre." |
| csapat lerakja az elemeket | „Munka közben" | „Se gép. Se beton. Se nyom." |

De vigyázz: a fenti kettő **szlogen**, és a kutatás szerint a hosszú futók nem szlogennel nyitnak. A képen elfér egy ilyen — a **szövegben viszont konkrétum kell az első sorba.** Lásd lentebb.

---

## A folyamat

```
0. ALAPOK        kinek? mi a fájdalma? melyik angle?     ← ha van kutatás, olvasd el
1. TEREP         mi fut a kategóriában? ⛔ EZ NEM KIHAGYHATÓ
2. DESIGN SYSTEM megvan? ha nem: felépítjük vagy átvesszük   ⛔ EGYSZERI
3. SZÖVEG        fejléc + hirdetésszöveg + CTA            ⛔ JÓVÁHAGYÁS
4. KÉP           melyik fotó bizonyít? (leltár)
5. LAYOUT        formátumválasztás a bizonyíték alapján
6. RENDER        html-kep → PNG                           ⛔ MINDIG NÉZD MEG
```

### 1. Terep — mi fut a kategóriában

Meta Hirdetéstár, bejelentkezés nélkül. Mit hozz haza, milyen technikával, milyen buktatókkal: [`references/referencia-kutatas.md`](references/referencia-kutatas.md)

Amit keresel: **melyik formátumok futnak**, **melyik fut a legrégebben**, **mit mond a hirdetésszövegek első két sora**, és **mi hiányzik feltűnően**.

> Egy hiány ugyanolyan erős adat, mint egy minta.

### 2. Design system

Ha az ügyfélnek van már hirdetéssora, abból fejtsd vissza: [`references/stilus-atvetel.md`](references/stilus-atvetel.md)

Ha nincs, a [`sablon/brand.css`](sablon/brand.css) egy kész, működő rendszer — írd át a `:root` tokeneket. Felépítés: [`references/design-system.md`](references/design-system.md)

### 3. Szöveg — itt megállunk

⛔ **A szöveg jóváhagyása nélkül ne rendereld le.** A render olcsó, a rossz szöveg drága: azzal fog futni.

**Az egyetlen mintázat, ami minden hosszú futó hirdetésben visszatért:**

> **Az első sor konkrét. Méret, teherbírás, ár, határidő — nem márkaígéret.**

```
✅ „The price is $160 Each / 42"x8' mats"
✅ „2' X 8' Ground Protection Mats – 90-Ton HDPE – Made in USA"
❌ „Stabil felület ott is, ahol az időjárás diktálna"
```

Ettől hat natívnak egy hirdetés — **nem a kép nyerssége, hanem hogy úgy beszél, ahogy egy szakmabeli beszél egy másikkal.**

- **A CTA a szövegbe megy, nem a képre.** Egy mondat, a végén, mindig ugyanúgy.
- **Egységes megszólítás.** Tegezés vagy magázás, de ne keveredjen.
- **Csak igazolható állítás.** Amit a cég nem tud alátámasztani, az nem megy bele.
- **Számokat betűvel**, ha mondatban vannak.

### 4. Kép

A fotó a **bizonyíték**, nem hangulat. Telefonfotót mindig `ImageOps.exif_transpose()`-szal tölts be.

Generálás csak a `hirdetes-video` skill [`kep-generalas.md`](../hirdetes-video/references/kep-generalas.md) szabályai szerint.

### 5. Formátumválasztás

Hat formátum, mindegyikhez oda van írva, hol láttuk futni és milyen erős a bizonyíték: [`references/formatumok.md`](references/formatumok.md)

**Kezdd a kategória-sorozattal** (`.cat`): egy sablon, sok kreatív, csak a fotó és egy szó változik. A Motion 550 000+ hirdetést lefedő mérése szerint a „nyertes" kreatívok a kör **~5%-át** teszik ki — nem a tökéletes képet kell megtalálni, hanem **sok próbálkozás kell**.

### 6. Render

```bash
PY="python"   # vagy a Playwright-ot tartalmazó venv pythonja
"$PY" ~/.claude/skills/html-kep/scripts/render.py ads.html \
      --out ./out --selector ".ad" --prefix ad --width 1200 --height 1400 --wait 1000
```

Egy `.ad` = egy PNG. **Méretek:** feed 4:5 = 1080×1350 (alap) · négyzet = `.square` · story = `.story`.

⛔ **Render után MINDIG nézd meg a PNG-t a Read tool-lal.** A sortörés, a túlcsordulás, az elcsúszott kivágás csak a képen látszik.

---

## ⛔ Hibák, amiket ne kövess el újra

Mind valódi, mind fájt.

| Hiba | Szabály |
|---|---|
| **Dizájnt vettem át, nem bizonyítékot** | Egy meglévő hirdetéssor szép tipográfiája nem jelenti, hogy az a sor működik. Előbb terep, aztán terv. |
| **`--S: 1080px` mértékegységgel** | Akkor a `--R` is hosszúság lesz, és minden `calc(96px * var(--R))` **px²** → érvénytelen. A CSS ezt **csendben** nyeli le, és az egész layout szétesik. `--S: 1080;` (szám), `width: calc(var(--S) * 1px)`. |
| **Logó flex-oszlopban** | A `flex-direction: column` alapból **stretch**-eli a gyerekeit → a logó szétlapul. `align-self: flex-start`. |
| **Képosztály-szabály a logóra is ráment** | A `.cat > img { width:100%; object-fit:cover }` a logóra IS érvényes volt, mert az is közvetlen gyerek. **Kösd osztályhoz:** `.cat > img.bg`. Ugyanaz a hiba kétszer, két különböző formában. |
| **Két `margin-top: auto` egy vásznon** | A két auto **szétosztja** a szabad helyet, lyuk marad köztük. Egy vásznon csak EGY elem tolhat autóval. |
| **Telefonfotó EXIF nélkül** | A PIL **nem** alkalmazza magától a tájolást → fejjel lefelé kerül a hirdetésbe. `ImageOps.exif_transpose(im)`. |
| **Fotó abszolút pozícióval a helyére tolva** | Minden szövegváltozásnál újra találgatsz. Tedd normál flow-ba `flex: 1`-gyel. |
| **Átlós vágás menti vonal szögszámítással** | A `skewX()` szöge a magasságtól függ. Helyette: a doboz háttere a vonal színe, a **képet** vágd ugyanazzal a poligonnal pár pixellel beljebb. |
| **`font-stretch` a width tengely kérése nélkül** | A változó font keskenyítése **néma marad**, ha a Google Fonts URL nem kéri: `family=Archivo:wdth,wght@62..125,400..900`. Nincs hibaüzenet. |
| **Eltérő soros fejlécek egymás melletti oszlopokban** | Ha az egyik `h3` két sorba tör, a két oszlop képe elcsúszik. `min-height` két sorra. |
| **Az összehasonlítás fejléce nem egyezett a képpel** | „Rétegelt lemez" felirat alatt sáros talaj fotója. A jobb oldali oszlop fejléce **azt** mondja, amit a kép mutat. |
| **Idegen márkajel a generált képen** | A modell magától beletesz létező márkákat olyan helyzetbe, ami sosem történt meg. **Valódi** fotón viszont a márkajel dokumentum — az maradhat, sőt hitelesít. |

---

## ⚠️ Amit a kutatás NEM igazolt

A „csúnya/natív mindig jobb" hipotézis **csábító, és a bizonyíték nem támasztja alá.**

- A legcsiszoltabb plakát (GroundGuards UK) nyolc hónapig futott.
- A leghosszabb futó **hibrid** volt: tervezett hook-lap + nyers fotó egy karusszelben.
- Két forrás **nyíltan ellentmond** egymásnak a testimonial és a csak-szöveges formátumról.

Ha egy user (vagy te) erős meggyőződéssel indul, a feladat **nem** az, hogy alátámasztó bizonyítékot keress. Mondd meg, ha az adat mást mutat — és mondd meg azt is, mit nem lehet kutatásból eldönteni, csak költésből.

---

## Kapcsolódó eszközök

| Mihez | Mit |
|---|---|
| A render motorja | `html-kep` skill (Playwright) |
| Hirdetésvideó ugyanebből az anyagból | `hirdetes-video` skill |
| Hiányzó fotó generálása | `kep-gyartas` skill |
| Beton-textúra legyártása | [`scripts/texture.py`](scripts/texture.py) |
| Hirdetéstár-kreatívok letöltése | [`scripts/adlib-dl.py`](scripts/adlib-dl.py) |
