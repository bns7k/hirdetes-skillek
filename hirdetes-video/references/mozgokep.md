# Állóképből mozgókép — Veo image-to-video

A Ken Burns csak a **kamerát** mozgatja. A kép→videó **magát a jelenetet**: guruló gép, járó emberek, eső a pocsolyán, kéz ami lerakja az elemet.

**A legfontosabb felfedezés:** ha a cég **valódi fotóját adjuk kezdőképnek**, a modell megtartja a termék geometriáját. Nem kell prompttal leírni a terméket — a kezdőkép a horgony.

---

## Mivel

**`gflow-cli`** — nem hivatalos CLI a Google Flow-hoz, a felhasználó **saját Google AI Plus/Pro/Ultra előfizetését** használja Playwright-tal vezérelt böngészőn át. Nincs külön API-számla.

```bash
gflow video i2v <kezdokep> "<mozgas-prompt>" --aspect 9:16 --out-dir <mappa>
```

Alternatívák és miért nem azok: a **hivatalos Gemini API** stabilabb, de külön számlázódik (az előfizetés nem fedi). A **Sora 2** működik, de szintén külön fizetős.

---

## ⛔ Négy buktató — mind valódi, mind fájt

| Hiba | Mi történik | Megoldás |
|---|---|---|
| **Verziósodródás** | `UiSelectorDriftError` — a gflow nem találja a Flow felületét | A Google hetente alakít a Flow-n, a gflow pedig sűrűn ad ki. **Minden munka előtt** `uv tool upgrade gflow-cli`. Egy esetben 0.21.0 volt telepítve, miközben a 0.79.0 volt aktuális. |
| **`--duration` nem elérhető** | `ConfigurationError: the migrated Flow host renders no duration control` | Nem minden fiókon van hossz-választó. **Hagyd el a kapcsolót**, fogadd el az alapértelmezettet (jellemzően 8 mp), és vágd ki a kellő szakaszt. |
| **Fekete sáv a kimeneten** | 720×1280-ból csak 720×1080 a hasznos kép | A Flow **megtartja a kezdőkép képarányát** és feketével párnáz. A hasznos rész pontosan a forrás aránya. **Adj be 9:16-os képet** (1080×1920), és eltűnik. |
| **`\r` a fájlnevekben** | `ffmpeg: Invalid argument`, a fájl „nem létezik" | Windows `read`-nél a sorvégi `\r` a változóba kerül, és ``-ként tárolódik a névben. Vágd le: `out="${out%$'\r'}"`, vagy nevezd át utólag Pythonból. |

**Modellválasztás:** az `omni-flash` **nem jó** i2v-hez — a Flow csendben eldobja a kezdőképet és szöveg-videóra vált. Az alapértelmezett `veo-lite` a jó.

---

## A mozgás-prompt receptje

Három dolgot kell kimondani:

1. **Mi mozogjon** — konkrétan, egyetlen dolog. „A hátsó kerék lassan pörög a sárban."
2. **Mi NE változzon** — ez tartja meg a terméket:
   > *„The framing, the ground and everything already in the initial frame stay exactly as they are."*
   > *„The hexagonal tiles keep exactly the same shape and pattern."*
3. **Milyen a fény** — hogy illeszkedjen a többi klipphez: *„Overcast late-autumn daylight, no sun. Handheld phone footage look."*

**Visszafogott mozgás nyer.** „Nagyon enyhe kézi kamera-sodródás" és egy mozgó elem. Ha sokat kérsz, a modell újrarajzolja a jelenetet — és ott vész el a geometria.

---

## Gyártósor — `scripts/veo.py`

```bash
python scripts/veo.py veo-manifest.json            # mind
python scripts/veo.py veo-manifest.json --only k11 # csak ez
python scripts/veo.py veo-manifest.json --proba    # csak a 9:16-os kezdőképek, kredit nélkül
```

```json
{ "dir": "mozgo", "model": "veo-lite",
  "clips": [ { "name": "k11-ajto", "img": "media/b11.png", "cx": 0.55,
               "prompt": "The front door opens and the technician steps slowly inside." } ] }
```

A szkript a kezdőképet pontosan 9:16-ra vágja (`cx` = vízszintes középpont), a promptot kiegészíti a stílus-blokkal (ne változzon a jelenet, kézi telefon, arc sosem látszik), a meglévő klippet **átugorja**, és mindegyikhez **kontaktlapot** készít (`mozgo/kontakt/`). ~1 perc és ~1 kredit klippenként.

Az újrafuttatható futtató szkript lényege: **ami már megvan, azt ugorja át.** Egy tizenkét klippes sor fél óra, és ha egy elakad, csak azt kell újrakérni.

**Ellenőrizd minden klippen:** felismerhető arc, rendszám, olvasható márkanév. Az embereket hátulról kérd — arc nélkül a kockázat nulla.

---

## Bekötés a gépsorba

A `shot` mezőben **`clip`** mutat videóra, **`img`** állóképre. Egy videón belül vegyesen is mehet.

```json
{ "text": "Áll a brigád.",
  "shot": { "clip": "../assets/klippek/k-brigad.mp4", "trim_start": 2.0 } }
```

| Mező | Mit csinál |
|---|---|
| `clip` | a videófájl |
| `trim_start` | honnan vágjunk (mp) — a klipp eleje gyakran még nem mozog |
| `speed` | lassítás/gyorsítás, alap 1.0 |

A lánc a hangot eldobja (a narráció és a zene külön jön), a 6 mp-es darabolást videónál kihagyja, és ha a forrás rövidebb a beatnél, az utolsó kockán fagyaszt.

> 💡 **Kihasználatlan lehetőség:** a Veo-klippek **saját hangsávval** jönnek (léptek, eső, gépzaj). Ezt most eldobjuk. Ha halkan a narráció alá keverjük, a videó érezhetően valódibb lesz.

---

## Mit ér és mit nem

**Amit ad:** három valódi fotóból korlátlan sok mozgó beállítás, a termék geometriájával együtt.

**Amit nem:** a generált klipp **illusztráció**. Referenciamunkaként nem hivatkozhatunk rá, „ez a mi telepítésünk" mondat nem járhat hozzá. Egy valódi helyszíni felvétel továbbra is többet ér — és ha megvan, ugyanígy bekötheted `clip`-ként.

---

## Nézd végig kockánként, és a tiszta szakaszt vágd ki

Egy SaaS-ügyfél videójánál (2026-09-23, gflow 0.79.1, veo-lite, ~1 perc/klipp) öt klippből ötben volt használható rész, de **háromban volt egy árulkodó pillanat**: az ajtóban álló háziasszony egy másodperc után egyszerűen eltűnt, egy munkás „ugrott" a képen, egy parkoló autó a kamera mozgásával felszívódott.

A 8 mp-es klippből egy hirdetési beathez úgyis csak **1,5–4 mp** kell. Hét kockát kivéve (0,3 / 1,6 / 2,9 / 4,2 / 5,5 / 6,8 / 7,8 mp) egy kontaktlapon azonnal látszik, hol a tiszta szakasz, és a `trim_start` oda mutat. **Ne dobd el a klippet egy rossz pillanat miatt, vágd ki a jót.**

A Veo 720×1280-at ad. 1080-ra felskálázva telefonon nem látszik a különbség.
