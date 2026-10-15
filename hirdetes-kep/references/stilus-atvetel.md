# Meglévő stílus átvétele

Gyakori helyzet: az ügyfélnek már van hirdetéssora — ügynökségtől, vagy AI-jal generálva. A **tipográfia és a formanyelv jó**, de a képek slop-osak, a szöveg nem javítható, és a fájlok nem újrarenderelhetők.

Ilyenkor nem nulláról tervezünk. **Visszafejtjük a rendszert, és újraépítjük CSS-ben** — utána a képek valódiak lesznek, a szöveg meg egy karakterrel javítható.

---

## A sorrend

### 1. Nézd meg mindet, ne egyet

Egy kreatívból nem látszik, mi a **rendszer** és mi az **eset**. Nyiss meg 5-6-ot, és keresd, **mi ismétlődik**: ugyanaz a sarokvágás? ugyanott a logó? ugyanaz a gomb?

Ami mind a hatban ott van, az a rendszer. Ami egyben, az díszítés — azt ne másold.

### 2. Színt a LOGÓBÓL mintázz, ne a hirdetésből

```python
from PIL import Image
im = Image.open('wordmark.png').convert('RGB')
print(im.getpixel((100, 250)))
```

A hirdetésképeken a márkaszín szinte mindig sötétebb, mint az igazi — textúra, gradiens, JPEG-tömörítés ül rajta. Ha onnan pipettázol, **egy fokkal mindig sötétebb márkát építesz.**

A dominánsokra viszont jó a hirdetés:

```python
from collections import Counter
c = Counter(im.resize((300, 375)).get_flattened_data())
print([('#%02X%02X%02X' % k, v) for k, v in c.most_common(8)])
```

### 3. A betűtípus — légy őszinte magaddal

Rasztert nézve **nem lehet biztosan** azonosítani egy fontot. Amit tehetsz: kirendereled a jelölteket ugyanazzal a szöveggel, és egymás mellé teszed az eredetivel.

```html
<img src="eredeti-kivagas.png" style="width:900px">
<p style="font-family:Archivo;font-weight:700;font-stretch:72%;font-size:60px">UGYANAZ A SZÖVEG</p>
```

Amit nézz: az **`R` lábát**, az **`a` hasát**, az **`e` vízszintes szárát**, és a **szóköz-arányt** (mennyi betű fér egy sorba azonos magasságnál).

**Változó fontot válassz**, ha a referencián két különböző szélesség van (keskeny verzál fejléc + szélesebb kis-nagybetűs). Egy `wdth` tengelyes család mind a kettőt lefedi. Bevált: **Archivo** (wdth 62-125, wght 100-900), teljes magyar készlettel.

> Mondd ki a usernek, hogy ez a **legközelebbi ingyenes megfelelő**, nem az eredeti. Egy ilyen mondat többet ér, mint egy magabiztos, téves azonosítás.

### 4. A "hatás" általában textúra

Ha a referencia nagy betűi élnek és nem laposak, az szinte mindig **textúra a betűben** — kő, beton, fém, karc. Ezt CSS-ben a `background-clip: text` adja, és a textúrát generálni is lehet, nem kell stockot venni.

Lásd: [`design-system.md`](design-system.md) és [`scripts/texture.py`](../scripts/texture.py).

### 5. A formanyelv: keress EGY geometriai motívumot

A jó hirdetéssorokban egyetlen forma ismétlődik minden dobozon. Egy talajvédőburkolat-ügyfélnél ez a **levágott sarok** (a hexagonból), másutt lehet lekerekítés, ferde él vagy vágott sarok.

Ha megtaláltad, **tedd minden dobozra**: fotó, csempe, gomb, címke. Ettől áll össze rendszerré az, ami különben csak sok doboz.

---

## Amit NE vegyél át

| Ne | Miért |
|---|---|
| **A generált fotókat** | ez a fő ok, amiért újraépítjük. Valódi fotó kerül a helyükre. |
| **Az ikonlistákat 5+ tétellel** | a referencia szereti a sok apró csempét. A feedben ez zaj — háromnál állj meg, a többi a hirdetésszövegbe megy. |
| **A képaláírás-fejléceket** | „A sár nemcsak kellemetlen" típusú fejléc elmondja, ami látszik. Lásd a vasszabályt a SKILL.md-ben. |
| **A ki nem mondható állításokat** | amit a cég nem tud igazolni, az nem megy bele, akkor sem, ha a régi kreatívon rajta volt. |

---

## Ellenőrzés

Tedd egymás mellé a régit és az újat, és kérdezd meg: **egy család?** Ha az új ugyanattól a márkától jöhetne, kész vagy. Ha csak „hasonlít", nézd meg a betűközt és a sarokvágás méretét — általában abban a kettőben van.
