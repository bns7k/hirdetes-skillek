# Hiányzó képek pótlása

A szkript vezet — ha kell egy kép, ami nincs meg, azt pótoljuk. Nem a szkriptet szegényítjük el.

Három út, ebben a sorrendben:

1. **Kérünk felvételt a cégtől** — a legjobb és majdnem ingyen. 10-15 perc telefonos videó egy munkáról évekre elég nyersanyag.
2. **Stock** — ha általános jelenet kell.
3. **Generálás** (`kep-gyartas` skill, OpenAI gpt-image-2) — gyors és filléres, de van határa.

---

## A határ: mit szabad generálni

| | |
|---|---|
| ✅ **A probléma** | sár, felázott terep, keréknyom, eső, feltúrt gyep, borult ég, üres helyszín. **A termék nincs a képen.** |
| ⚠️ **A termék — CSAK referenciával** | `--edit`-tel, a cég valódi fotóit átadva. Enélkül a modell kitalálja a geometriát, és az látszik. |
| ❌ **Referenciamunkaként hivatkozni rá** | A generált kép nem "a mi telepítésünk". Illusztráció igen, esettanulmány nem. |

### A referenciás generálás működik

Ez a legfontosabb felfedezés. A cég három valódi fotóját `--edit`-ként átadva a modell **megtartja a termék geometriáját** — a mi esetünkben a hexagon lapokat, a cikkcakkos szegélyt, még a rögzítő füleket is.

```bash
python ~/.claude/skills/kep-gyartas/scripts/gen.py -p prompt.txt \
  -e valodi1.jpg valodi2.jpg valodi3.jpg \
  -o uj.png -q low -s 1024x1536 --n 3
```

A promptban mondd ki explicit:

> *Use the reference photos: keep EXACTLY the same [termék leírása], same size, same surface texture, same visible joints and edge clips.*

**Következmény:** három valódi fotó nem három beállítás, hanem **korlátlan sok**. A valódi fotók nem csak nyersanyag — **stílus-horgony**.

---

## ⚠️ A steril tökéletesség árulja el az AI-képet

Nem a hibái. A *hibátlansága*.

Ami lebuktatja:
- tökéletes középszimmetria, pontosan középen a fókuszpont
- nulla rendetlenség — se kuka, se kábel, se kordon
- makulátlan, vadonatúj felület
- egyenletes fény, semmi árnyék
- üres jelenet, egy lélek sem

**Amit kérni kell helyette:**

| Kérd | Konkrétan |
|---|---|
| **Embereket** | „a handful of visitors walk **away from the camera**, seen from behind, small in the frame, slightly motion-blurred. Their faces are never visible." — arc nélkül a kockázat nulla, de azonnal életre kel |
| **Aszimmetriát** | „runs **diagonally**, entering from the lower-left corner, NOT centred and NOT symmetrical" |
| **Kopást** | „the tiles are **used, not new**: scattered dried mud smears and footprints" |
| **Rendetlenséget** | „a rubbish bin and a stack of folding chairs at the edge" |
| **Kézi fotót** | „shot on a phone by someone walking: handheld, **very slightly tilted horizon**, flat diffuse overcast light, mild noise" |

> ⚠️ **Ne írj a sablonodba „No people in frame"-et.** Én beleírtam, hogy elkerüljem az AI-arcokat — és ettől lett **minden képem steril**. Az embereket hátulról, távolról kell kérni, nem kihagyni.

---

## Illeszkedés a meglévő anyaghoz

A generált kép akkor lóg ki, ha **szebb**, mint a valódi fotók. A legtöbb cég anyaga telefonnal, borult időben készült.

Kérd ugyanazt: *flat diffuse overcast light, no sun, slightly desaturated natural colours, mild noise, no lens flare, no cinematic grading, no bokeh.*

Utána futtasd át a generált képeket ugyanazon a színkorrekción, mint a valódiakat — de **enyhébb beállítással**, mert azok már eleve laposak.

---

## ⛔ Átnézés hirdetés előtt

**Idegen márkajelzés.** A modell magától teszi bele. Nálunk egy létező cidermárka neve került a festivál-pultra — használhatatlan lett volna.

> A **valódi** fotón lévő márkajel más kérdés. Az dokumentum: tényleg ott volt, és gyakran épp az adja a hitelességet (egy valódi rendezvényen van hűtő és van szponzorkordon). Ne kérd a kivágását reflexből — kérdezd meg az ügyfelet. A generált képen viszont a modell egy létező márkát tesz olyan helyzetbe, ami sosem történt meg; **ez marad tiltva.**

Ellenőrizd minden generált képen:
- olvasható márkanév, logó, felirat
- felismerhető arc
- rendszám
- bármi, ami valódi céget vagy személyt azonosít

---

## Munkamenet

1. **`-q low`, `--n 3-4`** felfedezésre. Pár forint az egész.
2. Nézd meg őket **kontaktlapon**, a valódi fotó mellé téve.
3. A nyertest futtasd újra magasabb minőségen, ha kell.
4. **Mentsd a promptot** a kép mellé. Így bármikor újragyártható, és a nyolcadik szöghöz csak egy sort kell átírni.

**Percenkénti limit:** a gpt-image-2 API-nak van rate limitje (kb. 5 input-kép/perc). Ha 429-et kapsz, várj és próbáld újra — `until ... do sleep 20; done`.
