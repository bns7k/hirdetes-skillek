# A referencia-videók elemzése és a gyártási recept

*2026-09-21. Két élő magyar hirdetés szétszedve: [Crown Roof Hungary](https://www.facebook.com/ads/library/?id=1709389053693160) (0:45) és [MesterWerb](https://www.facebook.com/ads/library/?id=1082516124232655) (0:35).*

Képkockák: [`referencia/crownroof-kepkockak.png`](referencia/crownroof-kepkockak.png) · [`referencia/mesterwerb-kepkockak.png`](referencia/mesterwerb-kepkockak.png)

---

## Az első dolog, amit észre kell venni

**Ez nem két hirdetés. Ez egy gépezet, két brandre klónozva.**

Mindkettő ugyanoda visz: `crown.cortez-pro.de` és `mesterwerb.cortez-pro.de`. Ugyanaz a funnel-üzemeltető, ugyanaz a sablon, ugyanaz az ajánlatszerkezet, más cégnév. Mindkettőnek 4 aktív variánsa fut.

Ez jó hír nekünk: **a formátum bizonyítottan reprodukálható**, nem egy egyszeri kreatív szerencse.

---

## Amit megmértem

| | Crown Roof | MesterWerb |
|---|---|---|
| Hossz | 45,5 mp | 35,4 mp |
| Felbontás (kiszolgált) | 360 × 640 (9:16) | 360 × 616 |
| Képkocka/mp | ~30 | ~30 |
| Vágások | 9,4 · 15,9 · 20,7 · 31,6 · 39,2 · 42,3 · 44,3 mp | 3,8 · 8,8 · 13,9 · 18,9 · 24,0 · 30,5 · 32,5 · 34,3 mp |
| Átlagos klipphossz | **~6 mp**, a végén 2-3-ra rövidül | **~5 mp**, a végén 2-re rövidül |
| Feliratváltás | ~1,5–2 mp, 2–5 szavanként | ugyanaz |
| Csend a hangsávban | **nincs** (-45 dB alatt 0 szegmens) | **nincs** |

**A legfontosabb mérés: a vágás lassú, a felirat gyors.** A klippek 5-6 másodpercesek — vagyis nyugodt, nézhető B-roll. A ritmust nem a vágás adja, hanem a **felirat**, ami 1,5-2 másodpercenként vált. Ez azért fontos, mert sokkal kevesebb nyersanyag kell hozzá: egy 35 másodperces videóhoz **6-8 klipp elég**.

A hangsávban sehol nincs csend → végig szól egy **zenei alap** a narráció alatt.

> **Amit nem tudok megmondani:** hogy a narráció ember vagy TTS. Hangot nem tudok meghallgatni. Annyi látszik a szövegből, hogy **felolvasásra írták** — a „Kattintson a További információ gombra" nem beszélt nyelv. Akár ember, akár gép mondja, szkriptből megy.

---

## A vizuális recept

### Felirat — ez a formátum lelke

Mindkettő ugyanazt csinálja, apró eltéréssel:

| | Crown Roof | MesterWerb |
|---|---|---|
| Betű | nehéz groteszk, csupa nagybetű | ugyanaz |
| Alapszín | fehér | fehér |
| Kiemelés | **piros** + **cián** | **zöld** + **piros** |
| Olvashatóság | fekete doboz a szó mögött | vastag fekete kontúr |
| Pozíció | képközép alatt, ~60-65% magasságban | ugyanott |
| Egység | 2–5 szó, max 2 sor | ugyanaz |

**A kulcsmechanika: szavankénti kiemelés.** Nem az egész sor vált színt — a *most elhangzó* szó. A MesterWerb-nél látszik tisztán: „11 990FT" előbb piros, a következő kártyán már fehér, és a „NÉGYZETMÉTERÉRT" lesz zöld. Ez a karaoke-felirat, amit a CapCut és a Submagic automatikusan csinál.

**Emoji mint vizuális írásjel.** A felirat alatt egy-egy emoji: 🏠 👷 📄 💵 🗑️ 🛡️ 🪵 ℹ️. Olcsó, de működik: megtöri a szövegblokkot és ad egy kapaszkodót a szemnek.

**Állandó ajánlat-bug.** A Crown Roof bal felső sarkában végig ott ül egy kis keretes tábla: *„TELJES TETŐCSERE MÁR 10 990 FT/M²-TŐL ELÉRHETŐ!"*. Aki a videó közepén kapcsolódik be, az is látja az ajánlatot.

### B-roll — és itt jön a rossz hír

**Mindkettőnél valódi, saját helyszíni felvétel megy.** Magyar családi házak, valódi brigád a tetőn, drónfelvétel, közeli kézi felvételek a lemezfektetésről. Nem stock, nem AI.

Pont ettől hitelesek. És pont ez az, amiből nekünk **nincs**.

---

## Miért működik ez

**1. A felirat a hirdetés, nem a videó.** Hang nélkül is végigolvasható — és a feed nagy része hang nélkül fut. A videó csak háttér, ami mozog. Ezért elég hozzá 6-8 klipp.

**2. Az ajánlat csinálja a munkát, nem a kreativitás.** Nézd meg a szkript vázát — mindkettő ugyanaz:

```
1. Horog          → probléma vagy ár        („30-40%-kal többet fizetnek")
2. Ár             → konkrét szám            („már 10 990 Ft/m²-től")
3. Tartalom       → tételes felsorolás      (bontás, fólia, lécezés, munkadíj…)
4. Kockázat le    → „nincs rejtett költség", „írásban rögzítjük", „előleg nélkül"
5. Garancia       → 20 év, írásban
6. Ajándék        → 20 fm ereszcsatorna
7. Határidő       → „szeptember 30-ig"
8. CTA            → „kattintson… töltse ki a kérdőívet"
```

Ez klasszikus direct response. A videó csak a hordozó.

**3. Az algoritmus felől nézve.** A formátum-tierlistában ez a **„text-on-screen / faceless videó"** családba esik — nem S-tier unicorn scaler, de **alacsony gyártási költségű, korlátlanul variálható**. Az erőssége nem az, hogy egy darab nagyot üt, hanem hogy **hetente tízet lehet belőle gyártani** ugyanazzal a nyersanyaggal, más horoggal. A kreatív-fáradás ellen ez a védekezés.

**4. Mérhető a felirat szintjén.** Ha rossz a 3 másodperces megtartás, az első feliratkártyát cseréled — nem az egész videót.

---

## Amit NEM szabad átvenni

A formátum szabadon másolható. Ezek viszont **az ő állításaik**, és a saját ügyfelünknek sajátra van szüksége:

- konkrét négyzetméterár (nekünk nincs publikus árunk)
- „20 év írásos garancia" (nem tudjuk, mit vállal a cég)
- ajándék ereszcsatorna → nálunk más ajándék kell, ha egyáltalán
- határidős akció → csak ha tényleg van

És a legfontosabb: **az ő felvételeiket nem használjuk.** Se letöltve, se „referenciaként" bevágva.

---

## A gyártósor — hogyan csináljuk meg AI-jal

Öt lépés. Mindegyiknél megírom, mi a reális, és hol törik el.

### 1. Szkript

**Ezt már tudjuk.** A `creative/minimal-copy.md` hook-mátrixa és a vevőkutatás adja a horgokat. A fenti 8 lépéses váz + a mi angle-jeink.

A szkript írásakor a felolvasásra kell optimalizálni: **rövid mondatok, 2-5 szavas egységek**, mert így lesz belőle jó feliratkártya.

### 2. Kép — ⚠️ itt a szűk keresztmetszet

Három lehetőség, csökkenő minőségi sorrendben:

| Megoldás | Mire jó | Hol törik el |
|---|---|---|
| **A) Saját felvétel** ⭐ | Minden. Ez a helyes válasz. | Nincs. Kell hozzá 10-15 perc telefonos videó a következő telepítésen. |
| **B) Mozgatott állókép** | A meglévő 3 fotónkból. Lassú ráközelítés, oldalazás (Ken Burns / 2,5D parallax). 5-6 mp-es klippekhez pont elég. | 3 fotóból max 6-8 klipp jön ki, utána ismétlés. |
| **C) AI kép→videó, VALÓDI fotóból** ⭐ | Szinte mindenre. A termék is mozoghat: guruló gép a burkolaton, kéz ami lerakja az elemet, eső a felületen. | Csak akkor működik, ha a **valódi fotó a kezdőkép**. Recept: [`mozgokep.md`](mozgokep.md). |
| **D) Tisztán szöveges AI-videó** | Hangulat, ahol a termék nincs a képen: eső a mezőn, sáros terep. | A terméket **nem** tudja megcsinálni — a geometriát elrontja. Ez az „AI slop". |

**A javaslatom: C most, A amint lehet, D csak a nem-termékes vágóképekre.**

> ⚠️ **Ez a sorrend 2026-09-22-én megfordult.** Korábban az állt itt, hogy az AI-videó a terméket „nem tudja megcsinálni". Ez **tisztán szöveges** generálásra igaz.
>
> Ha viszont a cég **valódi fotóját adjuk kezdőképnek** (image-to-video), a modell megtartja a geometriát. Egy talajvédőburkolat-ügyfélnél a hexagon rajzolat, a cikkcakkos szegély és a fekete rögzítőfülek is megmaradtak — targoncával a lapokon, kesztyűs kézzel, felszedett területtel és kilátszó geotextíliával.
>
> **Három valódi fotóból így nem hat-nyolc beállítás lesz, hanem korlátlan sok — mozgóképben.**

Az **egész folyamatot AI-val megcsinálni** így már reális. De a lánc egyetlen pontján, a **termék hiteles megmutatásánál**, egy valódi felvétel továbbra is többet ér: a generált klipp illusztráció, **referenciamunkaként nem hivatkozhatunk rá**, és „ez a mi telepítésünk" mondat nem járhat hozzá.

### 3. Narráció (TTS)

Magyar nyelvre ez a második kockázatos pont. Sorrendben, amit kipróbálnék:

| Szolgáltató | Miért |
|---|---|
| **Azure Neural TTS** | Valódi magyar neurális hangok (pl. `hu-HU-NoemiNeural`, `hu-HU-TamasNeural`). Magyarra jellemzően ez a legtermészetesebb. |
| **ElevenLabs** (multilingual) | Jobb érzelmi színezés, de a magyar nem elsődleges nyelve — hosszú összetett szavakon és számokon el tud csúszni. |
| **Gemini / OpenAI TTS** | Gyors, olcsó, de a magyar prozódia esetleges. |

**Amit mindenképp csinálni kell**, különben hallatszik a gép:
- a számokat **írd ki betűvel** a TTS-nek („tíz-kilencszáz-kilencven forint"), mert a számjegyeket rendszeresen elrontja
- rövid mondatok, sok pont és vessző — a szünet adja a természetességet
- **3-4 felvételt generálj ugyanarra**, és válaszd a legjobbat; ez pár forint
- a tempót utólag 0,95-1,05× között állítsd, ne a TTS-ben

### 4. Felirat — ezt helyben, ingyen meg tudjuk csinálni

Nem kell Submagic-előfizetés. A lánc:

```
narráció.wav → whisper (szó szintű időbélyeg) → .ass felirat karaoke-kiemeléssel → ffmpeg ráégetés
```

Az `ffmpeg` már fent van a gépen. A whisper szó szintű időbélyeget ad, abból generálható az `.ass`, ami szavanként vált színt — pontosan úgy, ahogy a referenciában. Ez teljesen automatizálható, és **0 Ft**.

A brandünk színei mennek bele a piros/cián helyett: fehér alap + **narancs `#F57507`** kiemelés.

### 5. Összerakás

`ffmpeg`: klippek egymás után → narráció ráúsztatva → zenei alap alá (kb. -18 dB) → felirat ráégetve → 1080×1920, H.264, kb. 4-6 Mbps.

Ez is szkriptelhető, egyszer megírjuk és utána minden videó 2 perc.

---

## Mibe kerül és mennyi idő

| Lépés | Eszköz | Költség |
|---|---|---|
| Szkript | megvan a kutatásból | 0 |
| Kép (B változat) | ffmpeg, meglévő fotók | 0 |
| Narráció | Azure / ElevenLabs | pár száz Ft / videó |
| Felirat | whisper + ffmpeg, helyben | 0 |
| Zene | jogtiszta könyvtár | 0 – egyszeri |
| Összerakás | ffmpeg szkript | 0 |

**A gépsor megépítése után egy új videó ~15 perc**, aminek a nagy része a szkriptírás.

---

## A döntés, ami előttünk áll

Ez a formátum **felvételre épül**. A referencia-hirdetők azért hitelesek, mert valódi brigád van a tetőn.

Nekünk három állóképünk van.

**Két út:**

1. **Kérünk felvételt a cégtől.** Egy telepítésen 10-15 perc telefonos videó: az üres terület, a lerakás, a kész felület, egy rálépés, egy targonca vagy egy vendég. Ebből 20+ videó gyártható. Ez a helyes válasz, és szinte ingyen van.

2. **Elindulunk a meglévő fotókkal**, mozgatott állóképként, és menet közben pótoljuk. Gyengébb, de holnap kész lehet.

A kettő nem zárja ki egymást — a 2-vel indulunk, és az 1-gyel váltunk, amint megjön az anyag.

**Amit kérni kell a cégtől** (ugyanaz a lista, ami a founder-statichoz is kell):
- 10-15 perc telefonos videó a következő telepítésről
- ha van drón, 2-3 rálátó felvétel
- és amit már korábban is kértünk: az alapító 3-4 mondata arról, miért csinálják

---

*Következő lépés: szkriptek és a gyártósor felépítése — `01-szkriptek.md` és `build/`.*
