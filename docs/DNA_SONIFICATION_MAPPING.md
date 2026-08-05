# DNA Sonifiering & Musiknoter (Bio-Akustik i UPI)

Detta dokument beskriver hur DNA-sekvenser (genetisk kod) kan avläsas och sonifieras som musiknoter, akustiska frekvenser $f$ (Hz) och 8 Hz dimlösa index $N_8$ inom Universal Physics Index under adressen `UPI<biology,1,genetics,dna_sonification>`.

---

## 1. Mappningsprincip (Bio-Akustisk Sonifiering)

DNA-molekylen består av en sekvens av fyra kvävebaser:
- **A** (Adenin)
- **C** (Cytosin)
- **G** (Guanin)
- **T** (Tymin / Uracil **U** i RNA)

Vid **sonifiering** mappas varje bas eller kodon (trippelt) algoritmiskt till en specifik frekvens i det hörbara spektrumet.

---

## 2. 4-Bas Harmonisk Stämning (Standardmappning)

Inom standard UPI-sonifiering mappas de 4 baserna till en harmonisk ackordstruktur i den 4:e oktaven:

| Kvävebas | Notnamn | Frekvens $f$ (Hz) | $N_8$-index ($f / 8\text{ Hz}$) | Fysikalisk Massa $m = hf / c^2$ (kg) |
|---|---|---|---|---|
| **Adenin (A)** | **A4** | $440,00\text{ Hz}$ | $55,00$ | $3,24 \cdot 10^{-48}\text{ kg}$ |
| **Cytosin (C)** | **C4** | $261,63\text{ Hz}$ | $32,70$ | $1,93 \cdot 10^{-48}\text{ kg}$ |
| **Guanin (G)** | **G4** | $392,00\text{ Hz}$ | $49,00$ | $2,89 \cdot 10^{-48}\text{ kg}$ |
| **Tymin (T)** / **Uracil (U)** | **E4** | $329,63\text{ Hz}$ | $41,20$ | $2,43 \cdot 10^{-48}\text{ kg}$ |

### Exempel: Sekvensen "ATGC"
En sekvens som `ATGC` genererar en melodisk sekvens:
1. **A** $\rightarrow$ A4 ($440,00\text{ Hz}$)
2. **T** $\rightarrow$ E4 ($329,63\text{ Hz}$)
3. **G** $\rightarrow$ G4 ($392,00\text{ Hz}$)
4. **C** $\rightarrow$ C4 ($261,63\text{ Hz}$)

Detta bildar ett **A-moll 7-ackord (Am7)** eller en harmonisk nedåtgående rörelse som kan avlyssnas eller analyseras spektralt.

---

## 3. Kodon-Sonifiering (64 Kodoner $\rightarrow$ 5 Oktaver)

Inom mer avancerad genetisk sonifiering mappas de 64 mRNA-kodonerna (tripletter av baser som `AUG`, `GCU`) till 64 kromatiska halvtoner (från C2 till D7):

$$\text{Kodon-index } k \in [0, 63] \implies f(k) = f_{\text{C2}} \cdot 2^{\frac{k}{12}}$$

Detta gör att hela proteinkodande gensekvenser kan spelas upp som komplexa musikstycken där aminosyror bildar återkommande motiv och stoppkodoner motsvarar pauser.

---

## 4. Python-exempel i UPI

Funktionen `dna_sequence_to_frequencies` i `upi.physics` omvandlar DNA-strängar till strukturerad frekvensdata:

```python
from upi import dna_sequence_to_frequencies

# Omvandla en DNA-sekvens till noter och frekvenser
sequence = "ATGCATGC"
results = dna_sequence_to_frequencies(sequence)

for item in results:
    print(f"Pos {item['position']}: Base {item['nucleotide']} -> Note {item['note_name']} ({item['frequency_hz']:.2f} Hz) | N8 = {item['n8_index']:.2f}")
```

---

## 5. Vetenskapliga Gränser & Status (`DER` / `SYM`)

- **Status**: `DER` (härledd sonifieringsmodell) eller `SYM` (symbolisk bio-akustisk tolkning).
- **Gränsdragning**: Sonifiering är ett **analysverktyg för mönsterigenkänning**. Det hävdar inte att biologiska DNA-molekyler sänder ut hörbar musik i naturen utan akustiska omvandlare.
