---
name: hirdetes-video
description: Függőleges hirdetésvideó gyártása állóképekből vagy videóklipekből — ElevenLabs narráció, szó szintű karaoke-felirat, Ken Burns mozgás, zenei alap duckinggal. A szkript vezet: előbb az angle és a vevő, aztán a szöveg, csak utána a kép. Használd, ha a user hirdetésvideót, reelt, rövid videót kér egy termékhez vagy szolgáltatáshoz ("csinálj videót a hirdetéshez", "kell egy reel", "videós kreatív", "hirdetésvideó"), vagy ha egy meglévő ügyfél anyagából kell videót gyártani. NEM erre való: hosszú YouTube-videó, beszélőfejes felvétel vágása (arra a reel-editor), statikus képes hirdetés (arra a hirdetes-kep).
---

# Hirdetésvideó-gyártás

Függőleges (1080×1920) hirdetésvideó, a magyar és nemzetközi lead-gen hirdetésekben bevált recept szerint: **nyugodt kép, pörgő felirat, végig szóló zene.**

A formátum mérési háttere: [`references/formatum.md`](references/formatum.md)

---

## A vasszabály

> **A szkript vezet. A kép követi.**

Nem képeket keresünk a mondatok alá. Előbb eldöntjük, **kinek** beszélünk és **mit** mondunk, és a mondat *tudja*, mit fog mutatni.

Ha ezt megfordítod, foltozgatás lesz belőle — utólag egyesével variálod a kivágásokat, és sosem áll össze.

---

## A folyamat

```
0. ALAPOK     kinek? mi a fájdalma? melyik angle?          ← ha nincs kutatás, ez az első
1. SZKRIPT    az angle + a vevő nyelvén megírva      ⛔ JÓVÁHAGYÁS
2. LELTÁR     mi van meg? mi hiányzik?
3. KÉP        a hiányzót megkérjük / generáljuk
4. SHOT-TERV  mondatonként: melyik kép, milyen kivágás
5. ELŐNÉZET   --offline, néma, ingyen                 ⛔ JÓVÁHAGYÁS
6. RENDER     éles, ElevenLabs-szel
```

Részletes recept: [`references/munkafolyamat.md`](references/munkafolyamat.md)

### 0. Alapok — mielőtt egy sort is írnál

**Kérdezd meg, ha nincs meg:**

| Mi | Miért kell |
|---|---|
| **Kinek szól?** | egy szegmens, nem "mindenki". Rendezvényszervező ≠ kivitelező. |
| **Mi a fájdalma — az ő szavaival?** | ha van vevőkutatás, onnan. Ha nincs, ez a legnagyobb hiány. |
| **Melyik angle?** | egy videó = egy angle. Ne akarj mindent elmondani. |
| **Mit tud igazolni a cég?** | amit nem, az nem megy bele. |
| **Hova visz a CTA?** | funnel? űrlap? Messenger? |

**Ha van marketingkutatás a projektben, olvasd el.** A vevő saját szóhasználata többet ér minden ötletelésnél — és a legerősebb angle jellemzően nem az, amit a cég magáról gondol.

> Példa a valóságból: egy talajvédőburkolat-cégnél végig azt hittük, a sár *kellemetlensége* ad el. A vevőkutatásból kiderült, hogy a vásárlást a **felelősség valaki más területéért** indítja el — "nem a te területed, de a helyreállítás a te számlád". Ez lett a legerősebb kreatív.

### 1. Szkript — itt megállunk

**A váz** (a bevált hirdetésekből visszafejtve):

```
1. Horog           felismerhető helyzet vagy kérdés
2. Tét             mi forog kockán, ha nem csinál semmit
3. Megoldás        mi ez, és mitől működik
4. Felsorolás      hol / mit tartalmaz / mit kap   ← ITT VANNAK A VÁGÁSOK
5. Kockázatlevétel mit NEM kell csinálnia
6. CTA             mindig ugyanaz a kattintásra hívó mondat
```

**Szabályok:**

- **Minden beat kapja meg a `szakasz`-át** (`horog` · `tet` · `megoldas` · `felsorolas` · `kockazat` · `cta`; elég a szakasz első beatjére, öröklődik). Ebből jönnek **automatikusan** a vágások — lásd lent.
- **Rövid mondatok.** Egy mondat = egy beat = egy feliratkártya-sorozat.
- **Számokat betűvel.** A TTS a számjegyeket rendszeresen elrontja.
- **Csak igazolható állítás.** Abszolút ígéret ("mindig", "garantáltan", "sértetlen marad") nem megy.
- **Aktív, igés mondatok.** Az igei állítmány nélküli mondat ("A gyep helyreállítása a te számlád") laposan, hivatalos-iratként szól a TTS szájából. Írd át: "A feltúrt gyepet neked kell helyreállítanod."

**A felsorolás ingyen vágás.** Egy hármas felsorolás három vágási pontot ad, mindegyik a saját képével. Ez a formátum legerősebb eszköze — írj bele tudatosan.

⛔ **A szkript jóváhagyása nélkül ne menj tovább.** Egy render pénzbe és percekbe kerül.

### 2-3. Leltár és a hiányzó képek

Nézd meg, mi van (`ls`, `ffprobe`), és rögzítsd fájlonként: mit mutat, mi az erőssége, milyen **kivágások** vannak benne.

A hiányzót pótold. Generálás szabályai: [`references/kep-generalas.md`](references/kep-generalas.md)

**Állókép vagy mozgókép?** A gépsor mindkettőt fogadja, akár vegyesen egy videón belül: `shot.img` = állókép Ken Burns-szel, `shot.clip` = videórészlet. Ha csak fotó van, abból **mozgóképet is tudsz csinálni** (`scripts/veo.py`, egy manifestből): [`references/mozgokep.md`](references/mozgokep.md)

**Ha a termék egy felület** (szoftver, rendszer, szolgáltatás-folyamat): mutasd **működés közben**, ne leírd. A `sablon/ui-anim/` HTML-sablonból a `scripts/ui_render.py` jelenetenként videót gyárt; a `shot.screen` pedig **egy fotón lévő telefon/laptop kijelzőjére** vetíti (sarkak: `scripts/racs.py`). A felület minden felirata pontos magyar szöveg, mert HTML — nem generált.

| Eszköz | Mire |
|---|---|
| `scripts/ui_render.py <anim.html> --out media [--proba]` | UI-animáció → `ui-<jelenet>.mp4`. Előbb `--proba` (kontaktlap), a teljes render jelenetenként ~1 perc |
| `scripts/racs.py <kép> [--box x0,y0,x1,y1]` | koordinátarács a kijelzősarkak leolvasásához |
| `scripts/veo.py <manifest.json>` | állókép → Veo-klipp: 9:16-os kezdőkép, futtatás, kontaktlap; a meglévőt átugorja |
| `scripts/sfx_gen.py` | a beépített hangeffekt-könyvtár újragyártása |

### 4. Shot-terv

A kép azt mutassa, amiről a mondat szól — de **ne vidd túlzásba**: a szoros kivágásban is lássék, mihez tartozik. Csupasz textúra kontextus nélkül értelmetlen.

### 5-6. Előnézet és render

```bash
python scripts/make.py <config.json> --offline --qa   # néma, ingyen, gyors
python scripts/make.py <config.json> --qa             # éles
```

**A `--qa` mindig menjen.** A kész fájl mellé teszi:
- `<id>-qa.jpg` — **kontaktlap minden vágás után 0,15 mp-cel**. Egy pillantás: a felirat már az új mondaté-e? (Ha a régi, csúszik a vágás.)
- `<id>-qa.txt` — hangosság, csúcs, csend a kész fájlon, és **effektenkénti szint** a beszédhez képest (`!! TÚL HANGOS`, ha versenyez a szöveggel). Egy renderből, a keverés előtti sávokból — nem kell második render.

Ezt ne kézzel csináld: minden egyes kézi kockakivétel és mérés ugyanezt ismétli, csak lassabban.

Az `--offline` a legjobban megtérülő lépés: kiderül belőle a rossz kivágás, a hibás sortörés, az elcsúszott emoji — nulla forintért.

---

### Vágás, emoji, hang — alapból automatikus

**Nem kell beatenként beírni.** A gépsor a szkript szerkezetéből (`szakasz`) és a szövegből maga teszi bele:

| Mit | Honnan jön magától |
|---|---|
| **Vágás** | a `szakasz`-ból: a **megoldás** első képe `flash`, a **felsorolás** képei `slide` (kivéve egy sorozat egymást követő klippjeit, pl. `ui-hivas` → `ui-sms`: az egy folyamat), a **kockázatlevétel** első képe `whip`, a **CTA** `punch`. Minden más kemény vágás. |
| **Emoji** | kulcsszóból (telefon 📞, SMS 💬, naptár 📅, pénz 💸, lista 📋, kattints 👉 …), legfeljebb minden második beatre — a **CTA mindig** kap |
| **Hang** | kulcsszóból, beatenként legfeljebb egy (SMS → `ding`, hív/telefon → `ring`, fizet/pénz/havidíj → `coin`, naptár/beír/foglal → `click`); **felfutó hang** a megoldás elé; `hit`/`whoosh` a különleges vágásokra; `pop` az emojikra |

Egy 12 beates, 30 mp-es videóból így tipikusan **4 különleges vágás, 5-6 emoji, 6-8 hang** lesz — ez a jó arány; ennél több már olcsó.

**Felülírás beatenként** (a kézi mindig nyer): `"cut": "whip"`, `"emoji": {"char":"⏳","on":"sosincs"}`, `"sfx": {"file":"ring","on":"hív"}`, `"punch_on": "sosincs"` (a kiemelt szó képi párja — ez sosem automatikus, videónként 1-2-szer érdemes).
**Kikapcsolás beatenként:** `"cut": "cut"` · `"emoji": false` · `"sfx": false`. **Az egész videóra:** `"auto": false` a configban.

Nézd meg a `--qa` kimenetében, mit tett bele (`auto vágás`, `auto hang`, `emoji_auto` sorok), és ahol nem illik, írd felül.

| Egyéb | Mezője | Mikor |
|---|---|---|
| **Klipp saját hangja** | `shot.audio_db` | Veo-klippeknél mindig: `-16` |
| **Kijelzőcsere** | `shot.screen` | ha a fotón telefon/laptop van, és a terméked egy felület |

Részletek: [`references/config-sema.md`](references/config-sema.md). **A mértéktartás a szabály**: ha minden vágás csinál valamit és minden szóra szól valami, a hirdetés olcsó lesz. Egy jó arány 30 mp-re: 3-5 különleges vágás, 5-7 emoji, 6-10 hangeffekt.

---

## Beállítás

**Egyszeri:** másold a `.env.example`-t `.env`-re, és írd bele az ElevenLabs kulcsot. A kulcs lehet **a projektben is**: a gépsor a config mappájában és 3 szinttel feljebb is keres `.env`-et (a skill melletti az alap).

> ⚠️ A kulcs `sk_`-val kezdődik, és **csak létrehozáskor látszik egyszer**. A Voice Library listájában az *azonosító* látszik — az nem működik. A szkript ezt előre elkapja.

**Ügyfelenként:** a `sablon/` mappa két fájlja. A `client.json` a márkáé (szín, betű, hang, formátum, logó, CTA), a `script.json` a videóé (beatek). Így új videónál csak a beateket írod.

> **Kérd el az ügyfél logóját az onboardingon**, átlátszó hátterű PNG-ben, és tedd a `client.json` `logo` mezőjébe. Minden videón ott lesz a bal felső sarokban. A rajzolt `badge` csak vésztartalék, ha nincs használható márkajel.

Teljes mezőlista: [`references/config-sema.md`](references/config-sema.md)

---

## Amit a gépsor csinál

```
1. TTS         ElevenLabs /with-timestamps → mp3 + KARAKTERSZINTŰ időbélyeg
2. Szavak      abból szó szintű időzítés (nincs whisper, nincs csúszás)
3. Kép         Ken Burns állóképből (kijelzőcserével is), vagy videóklipp vágása
               + vágástípusok (punch, flash, whip, slide), képkockára pontos határokkal
4. Felirat     .ass karaoke, szavankénti kiemeléssel, ráégetve; animált emojik
5. Hang        narráció + zenei alap duckinggal + szóhoz kötött hangeffektek
               + klippek saját hangja, −14 LUFS-ra normalizálva, −1,4 dBFS csúcs
```

---

## ⛔ Hibák, amiket ne kövess el újra

Mind valódi, mind fájt.

| Hiba | Szabály |
|---|---|
| **`normalized_alignment` az ElevenLabstől** | Lecseréli a magyar `ő`/`ű` betűket `o`/`u`-ra — "előkészítés" → "elokészítés". **Mindig az `alignment` kell.** Csendben rontja el az összes magyar videót. |
| **Felirat-kiemelés méretváltással** | Ha az aktív szó nagyobb lesz, a sor szélesebb, és a középre horgonyzott blokk **minden szóváltásnál elugrik**. Csak szín változhat. |
| **Változó sorszámú feliratkártya** | 1 sor vs 2 sor → a blokk fel-le ugrál. **Mindig pontosan két sor**, üres második sor is helyet tart. |
| **libass hiánya** | A `subtitles=` filter libass nélkül nem megy. Ellenőrizd: `ffmpeg -filters \| grep subtitles`. Ha nincs, Gyan-buildre válts. |
| **API kulcs vs. kulcs-azonosító** | Lásd fentebb. A 400-as hiba üzenete megmondja. |
| **Rajzolt tábla, pedig van logó** | Magunk rajzolt márkatáblát tettem a sarokba, miközben az ügyfélnek volt kész wordmarkja. A saját márkajel mindig többet ér. Kérd el az onboardingon, és használd a `logo` mezőt. |
| **Logó fix magassággal méretezve** | Csak a `width`-et add meg. Ha mind a kettőt beállítod, a logó aránya elcsúszik — ezt egy ügyfél azonnal észreveszi. |
| **A `center`-rel akartam kizárni egy képrészletet** | A Ken Burns-ablak **a kép széléhez tapad**, ha a kivágás kilógna — és ettől visszacsúszik arra a részre, amit ki akartál hagyni. Nálam egy angol árakkal teleírt MENU tábla került így vissza a képbe. Ha valamit nem szabad látni, **vágd ki fizikailag a forrásból**, ne a `center`-rel próbáld. |
| **Termék a felütésben** | A beállító beateket lerakott burkolatot mutató fotókkal töltöttem fel, így a videó elárulta a megoldást, mielőtt felvetette volna a problémát — és a későbbi felsorolás ugyanazokat a képeket ismételte. **A termék először a fordulatnál jelenjen meg.** |
| **Library voice fizetős csomagon** | Ingyenes fiókon a Voice Library hangjai 402-t adnak. Csak a premade hangok mennek. **Onboardingkor futtass egy pár szavas teszt-TTS-t**, ne a teljes videó után derüljön ki. |
| **Párhuzamos render ugyanarra a kimenetre** | Két ffmpeg ugyanarra a fájlra = **sérült MP4**, ami néha még le is játszható pár másodpercig. Egyszerre egy render fusson. |
| **Zenei alap a track elejéről** | Szinte minden zenének van felvezetése. Pásztázd végig 3 mp-es ablakokkal, és a `music_start`-ot oda tedd, ahol teljes energián van. Előfordult 21, 15 és 0 másodperc is. |
| **Hangszint az összetevőkön mérve** | A narráció lehet jó szinten, a **végeredmény** mégis halk (−21,6 LUFS lett, a cél −14). Mindig a kész fájlt mérd: `ffmpeg -i x.mp4 -af ebur128 -f null -` |
| **Csend a hangsávban** | A bevált hirdetésekben **sosincs csend**. Zene nélkül 9 lyuk keletkezett. Mérd: `silencedetect=noise=-45dB:d=0.25` |
| **Heredoc + backslash** | Shell heredocban a `\n` valódi sortöréssé válhat, és elrontja a Python-forrást. ASS-taget, JSON-t, kódot **Write tool-lal vagy Python `open()`-nel** írj. |
| **Font a rossz mappában** | A skillbe költözéskor a `make.py` a `scripts/assets/fonts`-ban kereste az Archivo Blacket, az viszont a skill gyökerében van. **Hibaüzenet nincs**: a PIL egy apró bitmap-fontra esik vissza, a CTA-gomb bélyegnyi lesz, a felirat pedig tartalékbetűvel megy. Javítva — ha mégis apró a gomb, ez az oka. |
| **Gyorsított klipp rövidebb a beatnél** | A `video_clip` a `speed`-del *osztotta* a kimenet hosszát, így egy 1,6×-os klipp a beat 60%-áig tartott. Két gyorsított klippnél 1,3 mp csúszás gyűlt össze, és minden későbbi kép egy másodperccel a felirata előtt vágott. **A kimenet mindig a beat hossza; a sebesség csak a forrásigényt szorozza.** Javítva. |
| **`alimiter` automatikus szintje** | Az ffmpeg `alimiter` alapból **visszahúzza a jelet 0 dBFS-re** (`level=true`). Ettől a `limit` beállításnak nem volt hatása, és a kész fájl csúcsa 0 dBFS fölé ment. **Mindig `level=false`.** A −1 dBTP-hez az AAC-kódolás ráhagyása miatt `limit=0.84` kell. |
| **TTS-gyorsítótár a kimeneti mappában** | Egy mérés kedvéért másik `--out` mappába renderelve a gyorsítótár nem találta a hangot, és **új, fizetős ElevenLabs-hívás** ment ki — ráadásul más felolvasással. A gyorsítótár most a **config mellett** van (`.tts-cache/`). |
| **Időalap a `concat` után** | A `concat` kimenete 1/1000000 időalapú, az `xfade` 1/FPS-t vár: *„First input link main timebase do not match"*. Minden `concat` után `settb=1/FPS`. |
| **Veo-klippek eltérő hangereje** | A klippek saját hangja között **24 dB** volt a különbség (építkezés vs. csendes műszerfal), azonos `audio_db` mellett. Az egyik hangosabb lett a beszédnél, a másik nem hallatszott. Most a gépsor **előbb egységesít** (loudnorm), és az `audio_db` azt jelenti: ennyivel a beszéd alatt. Ajánlott: **−16**. |
| **UI-animáció kézzel igazított sebessége** | A rendszer-klippek sebességét fejben számoltam a beat hosszához — minden szövegváltozásnál újra kellett volna. Helyette: `"speed": "fit", "action": <a lényeg hossza mp-ben>`. |
| **Hangeffekt a szünetben** | A `hit` −11 dB-en a mondatközi szünetre esve **12,7 dB-lel hangosabb** lett a beszédnél. A szünetben nincs mi elfedje — a vágásra eső effekteket (hit, whoosh) halkabbra kell venni, mint a szóra esőket. **Mérd**: egy effekt nélküli render különbsége megmutatja. |
| **Emoji a konzolkimenetben** | Az `emoji_auto` kiírta a talált emojit (`-> 📞`), és egy nem UTF-8-as Windows-konzolon ez `UnicodeEncodeError`-ral **az egész renderelést** leállította. A tesztekben nem jött elő, mert ott `PYTHONIOENCODING=utf-8` volt. Mostantól a szkriptek induláskor UTF-8-ra állítják a kimenetet. **Tanulság: a végleges tesztet a felhasználó alap környezetében futtasd.** |
| **Windows-útvonal ffmpeg filterben** | A `C:\...` kettőspontja ütközik a filter-szintaxissal. Az `ffesc()` kötelező. |
| **Két mondat egy feliratkártyán** | Egy „legyen legalább két szó a kártyán" szabály miatt az előző mondat záró szava átcsúszott a következő elejére: *„…FELÜLETET / **AD.** A GYALOGOS…"*. **A mondatvégi írásjel mindig zárjon**, egyetlen szónál is — a kártya úgyis két sorra párnázódik. A magányos egyszavas kártya viszont a **szöveg** hibája: ne zárj hosszú mondatot rövid szóval. |
| **Vágás a szó végén** | A felirat utolsó kártyája kitart a következő kezdetéig (helyesen, hogy ne legyen lyuk a szünetben), a kép viszont a szó végén vágott — így minden mondathatáron fél másodpercig az **új kép alatt a régi felirat** állt. Egy valódi esetben az „ÁLL A BRIGÁD" felirat a raklapos képre került. **A vágás is a szünetbe kerüljön**, a következő beat első szavának kezdetéhez. |
| **Elavult tiltás az AI-videóra** | A `formatum.md`-ben az állt, hogy az AI-videó a terméket nem tudja megcsinálni. Ez **tisztán szöveges** generálásra igaz — a **valódi fotóból indított** kép→videó viszont megtartja a geometriát. Ha egy szabály régi, ellenőrizd, mielőtt betartod: [`mozgokep.md`](references/mozgokep.md) |

---

## Kapcsolódó eszközök

| Mihez | Mit |
|---|---|
| Hiányzó fotó generálása | `kep-gyartas` skill (OpenAI gpt-image-2) — szabályok: [`references/kep-generalas.md`](references/kep-generalas.md) |
| Állóképből mozgókép | `gflow-cli` (Veo, a saját Google-előfizetésen) — recept és buktatók: [`references/mozgokep.md`](references/mozgokep.md) |
| Statikus képes hirdetés | `hirdetes-kep` skill (ugyanez a design system, HTML-ben) |
| Beszélőfejes nyersanyag vágása | `reel-editor` skill |
| Jogtiszta zene | pixabay.com/music — kereskedelmi használat, attribúció nélkül |
