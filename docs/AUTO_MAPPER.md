# LLM Context Auto-Mapper & Live Physics Engine

The UPI Auto-Mapper (`upi auto-map`) bridges LLM conversational context, prompt scratchpads, and structured completions directly into the Universal Physics Index (`universal-physics-index`).

It acts as a live **RNA Transcription Engine**, **Physics Engine**, and **DNA Memory Classifier**.

---

## Engine Architecture

```text
                               ┌──────────────────────────────────┐
                               │  Incoming LLM Context / Payload  │
                               └────────────────┬─────────────────┘
                                                │
                                                ▼
                               ┌──────────────────────────────────┐
                               │     LLMContextAutoMapper         │
                               └────────────────┬─────────────────┘
                                                │
        ┌───────────────────────────────────────┼───────────────────────────────────────┐
        │                                       │                                       │
        ▼                                       ▼                                       ▼
┌───────────────────────────────┐   ┌───────────────────────────────┐   ┌───────────────────────────────┐
│        Physics Engine         │   │      RNA Ingestion Engine     │   │       DNA Memory Cores        │
├───────────────────────────────┤   ├───────────────────────────────┤   ├───────────────────────────────┤
│ • E = h*f                     │   │ • RealtimePayload transcription│   │ • SCIENTIFIC_CORE (EST)       │
│ • m = h*f / c²                │   │ • RealtimeUPIIndex validation │   │ • HYPOTHESIS_CORE (HYP)       │
│ • N8 = f / (8 Hz) reference   │   │ • Realtime node/bridge write  │   │ • JUNK_DNA_CORE (SYM/STOP)    │
│ • Z = z / z_ref normalization │   │ • Strict boundary enforcement │   │ • MEMORY_CORE (DER)           │
└───────────────────────────────┘   └───────────────────────────────┘   └───────────────────────────────┘
```

---

## Classification of Context (Vortex-DNA Cores)

Context fragments parsed from LLMs are classified according to scientific status and functional role:

1. **Active Coding DNA (`SCIENTIFIC_CORE`)**:
   - Status: `EST`
   - Verified physical constants ($c, h, k_B$), established formulas, and empirical observations.
2. **Hypothesis Core (`HYPOTHESIS_CORE`)**:
   - Status: `HYP`
   - Testable claims awaiting falsification criteria and software verification.
3. **Derived Memory Core (`MEMORY_CORE`)**:
   - Status: `DER`
   - Derived nodes, structural relation maps, and provenance traces.
4. **Non-Coding Archive / Junk DNA (`JUNK_DNA_CORE`)**:
   - Status: `SYM` or `STOP`
   - Unverified raw model context, prompt scratchpads, speculative metaphors, and non-executing background text.
   - **Protection Rule**: Kept in the symbolic/untrusted archive; prevented from mutating or contaminating `EST`/`DER` physics nodes without passing software test verification.

---

## Physics Engine Integration

When incoming LLM context contains physical frequency ($f$) or mass ($m$) quantities, the Auto-Mapper automatically calculates:

$$\begin{aligned}
E &= h \cdot f \\
m &= \frac{h \cdot f}{c^2} \\
N_8 &= \frac{f}{8\text{ Hz}}
\end{aligned}$$

Results are recorded as machine-readable physics evaluations attached to the ingested node.

---

## Python Usage Example

```python
from upi import LLMContextAutoMapper, Address, ScientificStatus

mapper = LLMContextAutoMapper()

# 1. Map raw text context
raw_context = """
STATUS:EST
UPI<physics,1,quantum,planck>
Planck-Einstein relation equation: f = 8 Hz.

STATUS:SYM
Speculative prompt scratchpad context without empirical validation.
"""

result = mapper.map_text_context(raw_context)

print(f"Nodes Extracted: {result.nodes_extracted}")
print(f"DNA Classification: {result.dna_classification}")
print(f"Physics Evaluations: {result.physics_evaluations}")
```

---

## CLI Usage Example

```bash
# Map raw context string
upi auto-map --text "STATUS:EST\nUPI<physics,1,relativity,c>\nLight speed equation: f = 1.0e14 Hz."

# Map file containing context text or JSON
upi auto-map --file context_payload.json
```

---

## Evidence & Boundary Rules

1. **Biological Language**: Terms such as "DNA", "RNA", and "Junk DNA" are explicit symbolic metaphors (`SYM`) for structural schema storage, transcription pipelines, and unverified archival context.
2. **Untrusted Input**: All LLM context is treated as untrusted input until validated by software tests (`verification_type: software_test`).
3. **No Automatic Promotion**: Unverified scratchpad text (`SYM`/`STOP`) cannot silently promote to `EST`.
