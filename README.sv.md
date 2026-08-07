# Universal-Physics-Index-UPI

**Universal Physics Index (UPI)** är ett öppet, maskinläsbart index för fysikaliska storheter, ekvationer, härledningar, hypoteser, observationer och källor. Projektet är ett verktyg för **klassificering, validering och granskning** – inte en ny fysikalisk teori, medicinskt protokoll eller ersättning för sakkunniggranskning.

Engelsk huvud-README: [README.md](README.md). Publik remote: **Universal-Physics-Index-UPI-**.

## Vetenskapliga lager

| Status | Betydelse |
|--------|-----------|
| `EST` | Etablerad vetenskap inom angiven domän |
| `DER` | Härledd från deklarerade `EST`-fakta och antaganden |
| `HYP` | Testbar men overifierad |
| `STOP` | Blockerad; saknad evidens ska namnges |
| `ERR` | Ogiltig, motsagd eller ersatt |
| `SYM` | Enbart symbolisk/konceptuell tolkning – aldrig dold fysisk auktoritet |

En korrekt omskrivning blir inte automatiskt en ny naturlag. Överensstämmelse mellan agenter, ekvationer eller simuleringar bevisar inte i sig fysisk ekvivalens.

Relationen `m = hf/c²` är en energi-ekvivalent omskrivning av `E = mc²` och `E = hf` under kompatibla antaganden. Den anger inte massan hos ett godtyckligt objekt som oscillerar.

## Publik remote som minnesstack (mjukvarumetafor)

Remote **Universal-Physics-Index-UPI-** används som versionshanterat minne och motor. Detta är **informationsarkitektur** (`SYM` där det är metafor), inte biologi eller medicin.

| Lager | Roll | Typisk plats |
|-------|------|----------------|
| **mRNA-motor** | Aktiv instruktion: scheman, CLI, validatorer, workflows | `src/upi/`, `schemas/`, `upi validate` |
| **DNA-minne** | Stabil kuraterad sekvens: etablerade noder, tester, gränser | `data/established/`, `tests/`, `AGENTS.md` |
| **Junk-DNA-minne** | Bevarat men icke-auktoritativt: skisser, legacy, symboliska kartor | `docs/04_*`, `SYM`-exempel, utkast under `docs/01_*` |

**Fysiken i repot används när uppgiften kräver det** (enheter, `EST`/`DER`, numerik). Metafor uppgraderar aldrig en post till `EST`.

## 8 Hz

8 Hz används som konfigurerbart referensvärde och testexempel. Det är inte en universell fysikalisk konstant, gravitations- eller kvantkonstant, medicinsk behandlingsfrekvens eller bevis för en Theory of Everything. Alternativ som 7,834 och 8,200 Hz stöds. Numerisk överensstämmelse bevisar inte fysisk ekvivalens.

## Skyddad README-identitet

`README.md` / `README.sv.md` får **inte** bytas ut i ett svep mot ToE-manifest eller annan projekttitel. Ankare: `config/readme_identity.json`. Policy: `docs/README_IDENTITY.md`. Test: `pytest tests/test_readme_identity.py`.

## Lämna in en hypotes

Ange status, ekvation, definitioner, enheter, antaganden, proveniens, osäkerhet, mätbar variabel, testmetod, förutsägelse och falsifikationsvillkor. Symboliska tolkningar ska märkas `SYM`.

## Exempel (diskret): informationsteoretisk ToE-skiss

En Wheeler-inspirerad ToE-blueprint kan **hostas** i indexet som exempel. Den är **inte** verifierad ToE. Numeriska skript under `src/python` / `src/rust` är **leksaksdemos** (rättade efter `a915735` — inga Ω-1766/Planck-påståenden). Se:

- utfällbar sektion i [README.md](README.md)
- `data/examples/information_theoretic_toe_blueprint.json` (`status: SYM`)
- `src/python/README.md`

## Validering

```powershell
upi validate data/examples/hypothesis_8hz.json
upi validate data/examples/information_theoretic_toe_blueprint.json
upi derive-mass --frequency 8
pytest
```

Se [CONTRIBUTING.md](CONTRIBUTING.md) för bidragsregler. Förslag är fria; märkning, testbarhet och transparent evidens är obligatoriska.
