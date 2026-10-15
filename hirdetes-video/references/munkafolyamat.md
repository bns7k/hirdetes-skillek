# A munkafolyamat — szkript előbb, videó utána

*Ez a dokumentum a készülő skill gerince. A `make.py` a gyártósor; ez a recept, ami szerint használni kell.*

---

## A lényeg egy mondatban

**A szkript vezet, a kép követi.** Nem utólag keresünk képet a mondat alá, hanem a mondat *tudja*, mit fog mutatni.

De a szkript sem a semmiből születik: előbb tudni kell, mi van a kezünkben.

---

## A három lépés

```
1. LELTÁR      Mi van ténylegesen? Minden fájl: mit mutat, milyen minőségű, használható-e.
                  ↓
2. SZKRIPT     Ennek ismeretében megírva. → AZ ÜGYFÉL / A MEGRENDELŐ JÓVÁHAGYJA.
                  ↓
3. SHOT-TERV   Mondatonként: melyik felvétel, milyen kivágás, milyen mozgás.
                  ↓
   render
```

### 1. Leltár — a kiindulópont, nem a korlát

Előbb nézzük meg, mi van. Nem azért, hogy ez szabjon határt a szkriptnek, hanem hogy **tudjuk, mit kell még előteremteni.**

**Mit rögzíts minden fájlról:**

| Mező | Példa |
|---|---|
| fájl | `extra-c.jpg` |
| mit mutat | fesztivál-pult hexagon padlón, **körülötte ép zöld fű** |
| tájolás / méret | fekvő, 4032×3024 |
| erőssége | a fű és a burkolat határa egy képen — ez bizonyíték |
| korlátja | nincs rajta ember, nincs mozgás |
| kivágható részek | pult / fű-határ / tágas összkép → **három különböző beállítás** |

Az utolsó sor hasznos: **egy fotóból több beállítás van**, ha van benne elég felbontás és tartalom. De ez optimalizálás, nem kényszer.

#### A hiányzó képeket pótolni lehet — de nem mindegyiket

Ha a szkripthez kell egy kép, ami nincs meg, három út van: **kérünk felvételt a cégtől**, **veszünk stockot**, vagy **generálunk**. A generálásnál viszont éles a határ:

| | Generálható |
|---|---|
| ✅ **Igen** | a **probléma**: sár, felázott terep, keréknyom, feltúrt gyep, eső, borult ég, sáros cipő. Ezekben nincs benne a termék. |
| ❌ **Nem** | maga a **termék**: a hexagon elem, az illesztés, a lerakott felület. A modell nem fogja helyesen kirajzolni a rendszer geometriáját — és a saját termékünk hamis változatát mutatni amúgy is megtévesztő. |

**Ez jó hír, mert a leggyakoribb hiány pont az első kategória.** Ebben a projektben végig hiányzott egy „előtte" kép: mind a három fotónk kész állapotot mutat. Egy generált sáros terep ezt betömi.

**Egy megkötéssel:** a generált kép **nem állítható be úgy, mintha a mi helyszínünk lett volna telepítés előtt.** Általános problémaillusztrációként rendben van; valódi előtte–utána párként nem — azt csak ugyanarról a helyszínről, összevethető nézetből szabad. Lásd `campaign/research/asset-audit.md`.

**Videónál:** hossz, mit mutat, hol van benne a használható rész (időbélyeg), van-e rajta használhatatlan (arc engedély nélkül, rendszám, konkurens logó).

### 2. Szkript — a jóváhagyási pont

A szkript megírása után **megállunk.** Nem indul render, amíg nincs oké.

Oka gyakorlati: egy render három perc és ElevenLabs-kredit. Ha a szöveg nem végleges, az mind kidobott.

**A váz** (a referencia-hirdetésekből mérve, lásd `00-formatum-elemzes.md`):

```
1. Horog          felismerhető helyzet vagy kérdés
2. Tét            mi forog kockán, ha nem csinál semmit
3. Megoldás       mi ez, és mitől működik
4. Felsorolás     hol / mit tartalmaz / mit kap  ← ITT VANNAK A VÁGÁSOK
5. Kockázatlevétel mi az, amit NEM kell csinálnia
6. CTA            mindig ugyanaz: kattints és kérj árajánlatot
```

**Szabályok a szövegre:**

- **Rövid mondatok.** Egy mondat = egy beat = egy feliratkártya-sorozat. Hosszú körmondatból rossz felirat lesz.
- **Számokat betűvel** a TTS-nek. A szintetizátor a számjegyeket rendszeresen elrontja.
- **Csak igazolható állítás.** Amit nem tudunk alátámasztani, az nem megy bele. (Lásd `campaign/research/asset-audit.md`.)
- **A CTA kötött.** Mindig *„Kattints ide, és kérj tőlünk árajánlatot."* — a funnelre visz, nem kommentbe.

### 3. Shot-terv — mondatonként

Minden beat kap egy `shot`-ot, vagy `null`-t, ha az előző klipp folytatódik.

A hozzárendelés szabálya: **a kép azt mutassa, amiről a mondat szól.** Nem hangulatot — azt a konkrét dolgot.

| Mondat | Rossz | Jó |
|---|---|---|
| „A feltúrt gyep…" | tágas kép a pultról | szoros a **füvön** |
| „Szerszám nélkül kapcsolódik" | általános összkép | az **elemek illesztése** |
| „Füves, homokos vagy egyenetlen talajra" | a burkolat közepe | a **burkolat és a talaj határa** |

**De ne vidd túlzásba.** Egyszer már elrontottam: annyira ráközelítettem a mondat tárgyára, hogy csak csupasz sötét burkolat maradt a képen, kontextus nélkül. A nézőnek kell egy viszonyítási pont — a szoros kivágásban is lássék, mihez tartozik.

---

## A technika, ami ebből következik

**A felsorolás ingyen vágás.**

Nézd meg a referenciát: *„az ár tartalmazza: bontás, törmelék elszállítása, tetőfólia, lécezés, cserepeslemez, munkadíj"* — hat tétel, vagyis **hat vágási pont egyetlen mondatból**. Ezért működik ez a formátum kevés nyersanyaggal is.

Nálunk ugyanez: *„Sátrak alá, pultok köré, vendégútvonalra."* — három tagmondat, három kép, mindegyik a sajátja. Ez a videó legjobban működő három másodperce, és nem véletlenül.

**Vagyis a szkriptírásnál nem csak az a kérdés, hogy jó-e a szöveg, hanem hogy kiszolgálja-e a képet.**

Három felvételed van? Egy hármas felsorolás ingyen kiszolgálja. Ha többre van szükség, azt vagy beszerezzük, vagy a fenti szabály szerint generáljuk — de a szkript ne csak azért legyen szegényebb, mert kevés a kép.

---

## Ritmus — amit mérni kell, nem érezni

A referenciából mérve:

| | Érték | Miért |
|---|---|---|
| Klipphossz | **5-6 mp**, a végén 2-3-ra rövidül | a vágás nyugodt, a ritmust a felirat adja |
| Feliratkártya | **1,5-2 mp**, 2-4 szó | ez a tempó |
| Felsorolásnál | **1-1,5 mp** | a lista pörög, ez adja a lendületet |
| Csend a hangsávban | **nincs** | végig szól a zenei alap |

Egy állóképpel **nem megyünk 6 mp fölé** — a `make.py` automatikusan felvágja, és folytatja a mozgást. Valódi videóklippet viszont **nem szabad felvágni**: azt egyben kell hagyni.

---

## Hol vannak az ellenőrzési pontok

1. **Leltár után** — mi hiányzik? Amit a cégtől kell kérni, azt most kérjük el; amit generálni lehet, azt jelöljük meg. Ne a render után derüljön ki.
2. **Szkript után** — ⛔ **jóváhagyás nélkül nem megyünk tovább.**
3. **`--offline` előnézet után** — a vágás és a felirat ellenőrzése *hang nélkül, ingyen*. Itt derül ki a legtöbb hiba.
4. **Éles render után** — hang, ritmus, összhang.

A 3. pont a legjobban megtérülő: néma előnézetből kiderül a rossz kivágás, a hibás sortörés, az elcsúszott emoji — és nem kerül semmibe.

---

## Amit a skillbe át kell vinni

- ez a három lépés, kötelező sorrendben
- a leltár-sablon (fenti táblázat)
- a szkript-váz és a szövegszabályok
- a felsorolás-technika
- a mért ritmus-értékek
- a négy ellenőrzési pont
- és a `00-formatum-elemzes.md` + a hibalista (`ERRORS NOT TO REPEAT`)
