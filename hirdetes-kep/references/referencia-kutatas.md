# Referencia-kutatás a Meta Hirdetéstárban

Mielőtt kreatívot tervezel egy új ügyfélnek, **nézd meg, mi fut a kategóriájában.** Ez egy órányi munka, és megspórolja, hogy olyat építs, ami sehol nem működik.

Ez a lap a gyakorlati módszer — az, ami ténylegesen működött, a buktatókkal együtt.

---

## A Hirdetéstár bejelentkezés nélkül is megy

```
https://www.facebook.com/ads/library/?active_status=active&ad_type=all
   &country=GB&q=%22skip%20hire%22&search_type=keyword_exact_phrase
```

| Paraméter | Mit csinál |
|---|---|
| `country` | `HU`, `GB`, `US`, `ALL` |
| `q` | a keresőszó; idézőjelezve + `search_type=keyword_exact_phrase` sokkal pontosabb |
| `search_type` | `keyword_unordered` (tág, sok szemét) vagy `keyword_exact_phrase` |
| `media_type=image` | csak képes hirdetések |
| `active_status` | `active` vagy `all` (az `all` a leállt hirdetéseket is hozza, dátummal) |

**Kezdd tágan, aztán szűkíts.** Az `unordered` keresés gyakran kínai nagykerek tömegspamjét hozza; a pontos kifejezés megszabadít tőle.

---

## Mit mérj: a futásidő

A Hirdetéstárban **egyetlen publikus teljesítmény-proxy** van: *„Megjelenés kezdete"*. Ha egy kreatív tíz hónapja fut, valaki nem kapcsolta ki — ez a legjobb jel, amit kívülről kaphatsz.

> ⚠️ **Gyenge mutató, és tudd, miért.** Azt méri, hogy nem kapcsolták ki, nem azt, hogy jól konvertál. És félrevezet a magánfeladóknál: ott a rövid futás azt jelenti, hogy elkelt az áru, nem azt, hogy bukott a hirdetés.

Amit még érdemes felírni: hány változatot futtat egy hirdető egyszerre (a Blue Gator 15+ változatot futtat városonként lokalizálva — ez tesztelési stratégia, nem véletlen).

---

## A technika, ami megoldja a képek megnézését

**A probléma:** a Hirdetéstár nehéz oldal, a képernyőkép-készítés rendszeresen időtúllépésbe fut, és a kreatívok gyakran nem rajzolódnak ki.

Két megoldás, mindkettő bevált:

### 1. Kontaktlap a böngészőn BELÜL

A leggyorsabb. Nem kell URL-eket mozgatni, egy képernyőképben látsz huszonötöt.

```js
(function(max, cols){
  const seen = new Set(), imgs = [];
  for (const i of document.querySelectorAll('img')) {
    if (i.naturalWidth < 180 || i.naturalHeight < 180 || !i.src.startsWith('http')) continue;
    const key = i.src.split('?')[0];
    if (seen.has(key)) continue; seen.add(key);
    let p = i, t = '';
    for (let k = 0; k < 14 && p; k++) { p = p.parentElement;
      if (p && p.innerText && p.innerText.length > 60) { t = p.innerText; break; } }
    imgs.push({src: i.src, cap: t.replace(/\s+/g,' ').slice(0, 38)});
    if (imgs.length >= max) break;
  }
  document.getElementById('__cs')?.remove();
  const d = document.createElement('div'); d.id = '__cs';
  d.style.cssText = 'position:fixed;inset:0;z-index:2147483647;background:#161618;'
    + 'overflow:hidden;display:grid;grid-template-columns:repeat('+cols+',1fr);'
    + 'gap:6px;padding:6px;align-content:start;font:10px/1.2 Arial;color:#ccc';
  d.innerHTML = imgs.map((o,n)=>
    '<div><img src="'+o.src+'" style="width:100%;aspect-ratio:1;object-fit:contain;'
    + 'background:#000"><div>'+n+'. '+o.cap.replace(/</g,'&lt;')+'</div></div>').join('');
  document.body.appendChild(d);
  window.__cells = imgs.map(o=>o.src);   // ebből szeded ki utána a nyertesek URL-jét
  return imgs.length;
})(25, 5)
```

Előtte állítsd az ablakot magasra (`1000x1500`), hogy mind a huszonöt ráférjen egy képernyőképre.

### 2. Letöltés a kiválasztottakról

Ha meg akarod tartani őket, a `window.__cells` tömbből kérd el csak a **jóknak** az URL-jét, és töltsd le:

```js
[3,4,8,10,11].map(n => 'nev'+n + '\t' + window.__cells[n]).join('\n')
```

Aztán egy `nev<TAB>url` fájlból `scripts/adlib-dl.py`. Végül PIL-lel kontaktlap, és **nézd meg a Read tool-lal** — a leírásra ne hagyatkozz.

---

## Buktatók, amikbe belefutottam

| Buktató | Megoldás |
|---|---|
| **A képernyőkép időtúllépésbe fut** | Egyszerűen **hívd meg újra**. Másodszorra általában sikerül. Ez nem hiba, csak lassú oldal. |
| **`COUNT=0` a találatok ellenére** | A lista lusta betöltésű. Görgess az aljára (`window.scrollTo(0, document.body.scrollHeight)`), várj 6 mp-et, ismételd. |
| **Az overlay eltűnik** | Az oldal újrarendereli magát. Tedd vissza: `document.body.appendChild(d)` és `scrollTo(0,0)`. |
| **Ugyanaz a hirdető sokszor** | Egy gyártó tíz változatot futtat ugyanazzal a szöveggel. Szűrd az URL alapútvonalára (`src.split('?')[0]`). |
| **Az fbcdn URL-ek lejárnak** | Az `oe=` paraméter miatt. Ha 403-at kapsz, szedd ki újra a böngészőből. |
| **A `scroll` koordinátát kér** | Előbb kell egy képernyőkép. Kerüld meg: `key: "End"` vagy JS-ből `scrollTo`. |

---

## Mit hozz haza

Ne „hangulatot". Ezeket:

1. **Melyik formátumok futnak**, és milyen arányban (statikus vs videó, nyers fotó vs tervezett).
2. **A leghosszabb futók** — hirdető, kezdődátum, és pontosan hogy néz ki a kreatív.
3. **A hirdetésszövegek első két sora, szó szerint.** Ez legalább annyit ér, mint a kép.
4. **Ami feltűnően HIÁNYZIK.** Nálunk ez volt a legerősebb eredmény: senkinél nem volt képbe égetett CTA-gomb.

> Egy hiány ugyanolyan erős adat, mint egy minta. Ha negyven kreatívból egyiken sincs valami, amit te betennél, az nem véletlen.

---

## ⛔ Légy őszinte a korlátokkal

Amikor visszaadod az eredményt, mondd meg:
- hogy a futásidő gyenge proxy;
- ha a minta nem a megrendelő piaca (pl. amerikai eladás-orientált hirdetők magyar lead-gen helyett);
- ha nem láttad a képeket, csak a szöveget;
- és **ha az adat ellentmond annak, amit vártatok.**

Ez az utolsó a legfontosabb. Nálunk a munkahipotézis az volt, hogy „a csiszolt plakát bukik" — és az adat **nem támasztotta alá.** Ezt kimondani többet ért, mint egy megerősítő jelentés.
