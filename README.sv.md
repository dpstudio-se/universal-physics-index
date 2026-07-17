# Universal Physics Index (UPI)

UPI är ett öppet, maskinläsbart index för fysikaliska storheter, ekvationer, härledningar, hypoteser, observationer och källor. Projektet är ett verktyg för klassificering och granskning – inte en ny fysikalisk teori eller ersättning för sakkunniggranskning.

## Vetenskapliga lager

`EST` betecknar etablerad vetenskap, `DER` en matematisk härledning, `HYP` en testbar hypotes, `STOP` en olöst gräns, `ERR` ett ogiltigt eller avvisat uttryck och `SYM` en symbolisk tolkning. En korrekt omskrivning blir inte automatiskt en ny naturlag.

Relationen `m = hf/c²` är en energi-ekvivalent omskrivning av `E = mc²` och `E = hf` under kompatibla antaganden. Den anger inte massan hos ett godtyckligt objekt som oscillerar.

## 8 Hz

8 Hz används som konfigurerbart referensvärde och testexempel. Det är inte en universell fysikalisk konstant, gravitations- eller kvantkonstant, medicinsk behandlingsfrekvens eller bevis för en Theory of Everything. Alternativ som 7,834 och 8,200 Hz stöds. Numerisk överensstämmelse bevisar inte fysisk ekvivalens.

## Lämna in en hypotes

Ange status, ekvation, definitioner, enheter, antaganden, proveniens, osäkerhet, mätbar variabel, testmetod, förutsägelse och falsifikationsvillkor. Symboliska tolkningar ska märkas `SYM`.

## Validering

```powershell
upi validate data/examples/hypothesis_8hz.json
upi derive-mass --frequency 8
pytest
```

Se [CONTRIBUTING.md](CONTRIBUTING.md) för bidragsregler. Förslag är fria; märkning, testbarhet och transparent evidens är obligatoriska.
