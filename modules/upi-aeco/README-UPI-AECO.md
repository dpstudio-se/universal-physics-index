# UPI-AECΩ v0.1 (Autonomous Evolution Core Omega)

`UPI-AECΩ` is an autonomous, self-evolving, self-debugging module that operates within the **Universal Physics Index (UPI)** ecosystem.

## Metaphor & Evidence Mapping

- **UPI-DNA**: Immutable scientific records (`EST`/`DER` nodes, schemas, provenance records). Never mutated by AECΩ.
- **UPI-RNA**: Runtime transcription and execution layer (CLI, auto-mapper, VR-ASI kernels, physics equations).
- **UPI-JNK**: Evolutionary pressure extracted from `STOP`/`ERR` clusters, unverified claims, and low-confidence nodes.
- **UPI-AECΩ**: Autonomous evolution organ that evaluates benchmark fitness, generates candidate RNA/agent configurations, and promotes optimal candidates.

## Module Layout

```text
modules/upi-aeco/
├── README-UPI-AECO.md
├── pyproject.toml
├── src/
│   └── upi_aeco/
│       ├── __init__.py
│       ├── __main__.py
│       ├── core/
│       │   ├── observer.py
│       │   ├── evaluator.py
│       │   ├── mutator.py
│       │   ├── selector.py
│       │   └── evolution_loop.py
│       └── adapters/
│           └── upi_rna.py
├── config/
│   ├── benchmarks.yaml
│   └── mutation_rules.yaml
├── state/
│   ├── self_model.json
│   └── versions/
└── tests/
    └── test_aeco.py
```

## Non-Negotiable Boundaries

- **Forbidden Mutations**: AECΩ cannot alter immutable `UPI-DNA` records, JSON schemas, or status rules (`EST`, `DER`, `HYP`, `STOP`, `ERR`, `SYM`).
- **Verification**: Candidate promotions require software test verification against `config/benchmarks.yaml`.
