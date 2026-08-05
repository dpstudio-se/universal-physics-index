# Hur Noter Fungerar & Läses (Akustik & Musiknotation i UPI)

Detta dokument beskriver den fysikaliska, matematiska och musikaliska uppbyggnaden av musiknoter samt hur de läses i notsystemet och mappas i Universal Physics Index (UPI) under adressen `UPI<acoustics,1,music,musical_notes>`.

---

## 1. Vad är en not? (Fysikalisk & Matematisk Grund)

Fysikaliskt är en musiknot en **akustisk tryckvåg** med en specifik grundfrekvens $f$ mätt i Hertz (Hz).

### Liksvävande Temperatur (12-TET)
Inom västerländsk musik delas varje oktav (frekvensfördubbling $2:1$) in i 12 logarithmisk lika stora halvtonsteg.

Frekvensförhållandet mellan två intilliggande halvtoner ges av den tolfte roten ur 2:

$$\text{Halvtonsfaktor} = \sqrt[12]{2} \approx 1,059463094$$

### Frekvensformel
Med standardstämning för **$A_4 = 440\text{ Hz}$** beräknas frekvensen för en not med halvtonsavstånd $n$ relativt $A_4$ som:

$$f(n) = 440 \cdot 2^{\frac{n}{12}}\text{ Hz}$$

---

## 2. Hur läses noter på ett notsystem?

Notsystemet består av **5 horisontella linjer** och **4 mellanrum**. Tonhöjden avläses vertikalt: ju högre upp noten placeras, desto högre är frekvensen.

```text
Diskantklav (G-klav)          Basklav (F-klav)
------------------ F5 (698 Hz)   ------------------ A3 (220 Hz)
  Mellanrum: E5                   Mellanrum: G3
------------------ D5 (587 Hz)   ------------------ F3 (175 Hz)
  Mellanrum: C5                   Mellanrum: E3
------------------ B4 (494 Hz)   ------------------ D3 (147 Hz)
  Mellanrum: A4                   Mellanrum: C3
------------------ G4 (392 Hz)   ------------------ B2 (123 Hz)
  Mellanrum: F4                   Mellanrum: A2
------------------ E4 (330 Hz)   ------------------ G2 (98 Hz)
       O                         
  ------C4------ (Middle C, 261.63 Hz)
```

### A. G-klav (Diskantklav / Treble Clef)
Används för högre instrument och röster (piano högerhand, fiol, flöjt, sång).
* **Nyckelpunkt**: G-klaven snurrar runt den **andra linjen nedifrån**, vilket markerar noten **G4** ($392,00\text{ Hz}$).
* **Linjer (nedifrån och upp)**: E4 (329,63 Hz), G4 (392,00 Hz), B4 (493,88 Hz), D5 (587,33 Hz), F5 (698,46 Hz).
* **Mellanrum (nedifrån och upp)**: F4 (349,23 Hz), A4 (440,00 Hz), C5 (523,25 Hz), E5 (659,25 Hz).

### B. F-klav (Basklav / Bass Clef)
Används för lägre instrument (piano vänsterhand, bas, cello, trombon).
* **Nyckelpunkt**: F-klavens två prickar omringar den **fjärde linjen nedifrån**, vilket markerar noten **F3** ($174,61\text{ Hz}$).
* **Linjer (nedifrån och upp)**: G2 (97,99 Hz), B2 (123,47 Hz), D3 (146,83 Hz), F3 (174,61 Hz), A3 (220,00 Hz).
* **Mellanrum (nedifrån och upp)**: A2 (110,00 Hz), C3 (130,81 Hz), E3 (164,81 Hz), G3 (196,00 Hz).

### C. Nyckeltonen C4 (Middle C)
Noten **C4** ($261,63\text{ Hz}$, $n = -9$) binder samman G-klav och F-klav och placeras på en hjälplinje (*ledger line*) mitt emellan klaverna.

---

## 3. Notvärden & Rytm (Tidsdimension)

Notens utseende anger hur länge tonen ska klinga i förhållande till takten:

| Nottyp | Symbol / Beskrivning | Relativt värde | Exempel vid 120 BPM |
|---|---|---|---|
| **Helnot** | Tom cirkel utan skaft | 1 hel takt ($4/4$) | $2000\text{ ms}$ |
| **Halvnot** | Tom cirkel med skaft | $1/2$ takt | $1000\text{ ms}$ |
| **Fjärdedelsnot** | Fylld cirkel med skaft | $1/4$ takt (1 pulsslag) | $500\text{ ms}$ |
| **Åttondelsnot** | Fylld cirkel med vimpel/balk | $1/8$ takt ($1/2$ pulsslag) | $250\text{ ms}$ |
| **Sextondelsnot** | Fylld cirkel med dubbel vimpel | $1/16$ takt | $125\text{ ms}$ |

---

## 4. Beräkningsexempel i UPI Python Engine

UPI tillhandahåller konverteringsfunktioner i `upi.physics`:

```python
from upi import note_name_to_frequency, note_frequency_from_semitone, index8_from_frequency

# 1. Hämta frekvens för A4 (Kammarton)
f_a4 = note_name_to_frequency("A4")  # 440.0 Hz

# 2. Hämta frekvens för C4 (Middle C)
f_c4 = note_name_to_frequency("C4")  # 261.6256 Hz

# 3. Beräkna 8 Hz dimlösa indexet N8 för C4
n8_c4 = index8_from_frequency(f_c4)  # N8 = 261.6256 / 8.0 = 32.7032

print(f"C4 frekvens: {f_c4:.2f} Hz | N8-index: {n8_c4:.4f}")
```
