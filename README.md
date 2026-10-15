# Hirdetési skillek Claude Code-hoz

Négy [Claude Code](https://claude.com/claude-code)-skill Meta (Facebook/Instagram) hirdetési kreatívok gyártásához, magyarul. Valódi kampányokban készültek és csiszolódtak. A példák névtelenítve vannak: egy talajvédő burkolatot bérbe adó cég és egy SaaS-szolgáltatás anyagaiból.

| Skill | Mire való | Költség |
|---|---|---|
| [`hirdetes-kep`](hirdetes-kep/SKILL.md) | Statikus hirdetéskép (összehasonlítás, adatlap-plakát, kategória-sorozat, nyers fotó). A kategóriában ténylegesen futó hirdetésekből indul ki, nem ízlésből. | ingyen |
| [`html-kep`](html-kep/SKILL.md) | A render-motor: HTML+CSS → PNG, Playwrighttal. A `hirdetes-kep` erre épül. | ingyen |
| [`kep-gyartas`](kep-gyartas/SKILL.md) | Képgenerálás és -szerkesztés (OpenAI gpt-image-2), pl. hiányzó problémajelenet egy hirdetéshez. | ChatGPT-előfizetés (Codex) vagy OpenAI API |
| [`hirdetes-video`](hirdetes-video/SKILL.md) | Függőleges hirdetésvideó állóképekből vagy klipekből: narráció, szó szintű felirat, zene duckinggal. | ElevenLabs (hang) |

A skillek hivatkoznak egymásra (pl. a `hirdetes-kep` a `hirdetes-video` képgenerálási szabályaira), ezért érdemes mind a négyet együtt telepíteni.

## Telepítés

Másold a négy mappát a Claude Code skill-mappájába:

```bash
git clone https://github.com/bns7k/hirdetes-skillek.git
cp -r hirdetes-skillek/hirdetes-kep hirdetes-skillek/html-kep hirdetes-skillek/kep-gyartas hirdetes-skillek/hirdetes-video ~/.claude/skills/
```

Windows-on a cél: `C:\Users\<nev>\.claude\skills\`. Utána a Claude Code magától felismeri őket. Indítani így lehet: „csinálj statikus hirdetést…”, „kell egy reel…”, vagy `/hirdetes-kep`.

## Függőségek

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

- **Python 3.10+**
- **ffmpeg** (libass-szal) a `hirdetes-video`-hoz: Windows-on például a Gyan-buildet, macOS-en `brew install ffmpeg`.

### Kulcsok (nincs benne a repóban, magadnak kell beállítanod)

| Mihez | Hogyan |
|---|---|
| `kep-gyartas`, ChatGPT-előfizetéssel | `npm install -g @openai/codex` és `codex login`. Ilyenkor API-költség nincs, az előfizetés keretéből fogy. |
| `kep-gyartas`, API-val | `OPENAI_API_KEY` környezeti változó, vagy a kulcs a `~/.claude/.openai-key` fájlban |
| `hirdetes-video` narráció | másold a `hirdetes-video/.env.example` fájlt `.env` néven, és írd bele az ElevenLabs-kulcsot |
| `hirdetes-video` mozgókép (opcionális) | a [`gflow-cli`](https://pypi.org/project/gflow-cli/) a Google Flow / Veo eléréséhez |

## Licenc

A skillek szövegét és szkriptjeit szabadon használhatod és átírhatod. Az `hirdetes-video/assets/fonts/ArchivoBlack-Regular.ttf` betűtípus a SIL Open Font License 1.1 alatt áll (Omnibus-Type), lásd [OFL.txt](hirdetes-video/assets/fonts/OFL.txt).
