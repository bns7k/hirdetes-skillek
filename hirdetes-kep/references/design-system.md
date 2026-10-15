# A design system

A [`sablon/brand.css`](../sablon/brand.css) egy kész, működő rendszer. Ez a lap elmondja, mi miért van benne, hogy át tudd írni egy másik márkára.

---

## A skálázás

Minden méret **egyetlen számból** jön:

```css
.ad { --S: 1080; --R: calc(var(--S) / 1080); }
.h  { font-size: calc(96px * var(--R)); }
```

Így ugyanabból a HTML-ből jön ki az 1080-as feed-kép és egy 540-es előnézet, és semmi nem csúszik el.

> ⛔ **A `--S` mértékegység NÉLKÜL van.** Ha `1080px`-et írsz, a `--R` is hosszúság lesz, a `96px * 1px` pedig px² — érvénytelen. A CSS ezt csendben nyeli le: nincs hibaüzenet, csak szétesik a layout, és sokáig keresed, miért.

---

## A négy réteg

```
::before   hexagon-vízjel      — halkan, 5-6% átlátszatlanság
::after    sarok-fény          — a háttér sosem egyenletes fekete
.photo /   a fotó              — z-index 1
.shot
.layer     minden szöveg       — z-index 2
```

### Hexagon-vízjel

A termék formája akkor is ott van a képen, amikor nem látszik burkolat. Inline SVG data-URI-ként, hogy ne kelljen fájl.

**Más márkánál** cseréld a mintát arra, ami az ő terméküket idézi — de tartsd **5-6% körül**. 10% fölött már textúrának néz ki, nem vízjelnek, és eszi a kontrasztot.

---

## A HATÁS: beton-textúrás betű

Ez az, amitől a kreatív nem néz ki Canva-sablonnak. A nagy fejléc **nem lapos színnel** van kitöltve, hanem egy foltos kő/beton felülettel.

```css
.tex { background-image: url("assets/texture-light.png");
       -webkit-background-clip: text; background-clip: text;
       color: transparent;
       filter: drop-shadow(0 4px 5px rgba(0,0,0,.85)); }
```

Három dolog kell hozzá, és mind a három:

1. **`background-clip: text`** — a textúra a betűk alakjára vágva
2. **`color: transparent`** — enélkül a szöveg kitakarja a saját textúráját
3. **`drop-shadow`** — ez adja a mélységet. Enélkül a textúra nem márványnak, hanem **piszoknak** látszik.

A textúrát a [`scripts/texture.py`](../scripts/texture.py) gyártja: három oktáv zaj + sötét pettyek. Két változat készül, világos és sötét.

**Színes változat** (`.tex-o`): a színt `linear-gradient`-tel, `multiply` módban tedd a **világos** textúrára. A sötét textúrán a narancs rozsdásbarnává válik — kipróbáltam, nem jó.

---

## A levágott sarok — a rendszer gerince

A referencián **minden** doboz sarka le van vágva. Ez viszi tovább a hexagon-formát anélkül, hogy hatszöget kéne rajzolni.

| Osztály | Mit vág |
|---|---|
| `.cut` | bal felső + jobb alsó |
| `.cut-r` | jobb felső + bal alsó |
| `.cut-all` | mind a négy |

A `--cut` változóval állítod elemenként. Nagy panelen 26-30px, kis csempén 18-20px.

> A `clip-path` **levágja a bordert is**. Ha keretes doboz kell: külső doboz = a keret színe, `padding: 2px`, belső doboz = a háttér. Erre van a `.framed`.

---

## A gomb

A referencia legerősebb eleme, és a legtöbbet másolt.

```
[ narancs blokk + nyíl ] [ sötét sáv, nagy felirat ]
        ^--- az egészet narancs hajszálkeret fogja körbe, levágott sarkokkal
```

Két változat:
- **alap** — sötét sáv, narancs kerettel. Ez megy, ha a képen más is van.
- **`.solid`** — végig narancs, sötét felirattal. Ha a CTA-nak **egyedül** kell vinnie a képet.

> **Narancs felületen mindig sötét felirat.** Fehér szöveg narancson elmosódik, és kis méretben olvashatatlan.

---

## Fotó-beillesztés

A fotó sosem sima téglalap. Három bevált forma:

| Osztály | Mikor |
|---|---|
| `.shot` | **ez az alap.** Normál flow-ban, `flex: 1` — kitölti, ami a szöveg és a CTA között marad |
| `.photo.corner` | átlós vágás a jobb felső sarokban, sötét átmenettel a szöveg alatt |
| `.split` | előtte/utána, átlós osztással és narancs vonallal |

> **A `.shot` a helyes alapértelmezés.** Abszolút pozícióval (`.photo.band`) is meg lehet csinálni, de akkor minden szövegváltozásnál újra kell találgatnod a pixeleket. Ezt a hibát elkövettem; a flow-s megoldás azóta egyszer sem csúszott el.

### Az átlós vonal — szögszámítás nélkül

A `skewX()` szöge a doboz magasságától függ, tehát minden szövegváltozásnál elcsúszik. Ehelyett:

```css
.split > div:last-child     { background: var(--orange);
                              clip-path: polygon(128px 0, 100% 0, 100% 100%, 0 100%); }
.split > div:last-child img { clip-path: polygon(134px 0, 100% 0, 100% 100%, 6px 100%); }
```

A doboz háttere a vonal színe, a kép ugyanazzal a poligonnal van vágva **pár pixellel beljebb**. A kilátszó sáv maga a vonal — és akármekkora a magasság, pontos marad.

---

## Tipográfia

| Szerep | Mi | Miért |
|---|---|---|
| Fejléc | **Archivo** változó font, `wdth 72-85`, `wght 700-800` | egy család adja a keskeny verzált fejlécet és a szélesebb kis-nagybetűs változatot is |
| Kenyér | **Noto Sans** | teljes magyar készlet, semleges, nem versenyez a fejléccel |
| Szalag / címke | Archivo `wdth 88`, nagy betűköz (`.13em`) | kisbetűs verzál — ez adja a „műszaki adatlap" érzetet |

> ⛔ A `font-stretch` **néma marad**, ha a Google Fonts URL nem kéri a width tengelyt:
> `family=Archivo:wdth,wght@62..125,400..900`
> Nincs hibaüzenet. Csak nem történik semmi, és nem érted, miért nem keskenyedik.

---

## Szín

```css
--orange: #FE7901;   /* a VALÓDI logóból mintázva */
--ink:    #07080A;   /* majdnem fekete, kékes árnyalattal — nem #000 */
--paper:  #F2F2F0;   /* nem tiszta fehér */
```

**A logóból mintázz, ne a hirdetésképekből.** A meglévő kreatívokon a narancs sötétebbnek látszik (~#E56200), de az a textúra miatt van, nem másik szín. Ha onnan pipettázol, egy fokkal mindig sötétebb márkát építesz, mint az igazi.

A `--ink` szándékosan nem `#000`: a tiszta fekete a feedben lyuknak látszik, és a fotó széle élesen elvágódik rajta.
