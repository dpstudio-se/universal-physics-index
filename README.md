# Universal-Physics-Index-UPI

**Universal Physics Index (UPI)** — open, machine-readable index for physical quantities, equations, derivations, hypotheses, observations, and sources.

This repository is a **classification, validation, and audit layer** for scientific records. It is **not a new physical theory**, medical protocol, or claim of experimental discovery by itself.

| | |
|---|---|
| **Package** | `universal-physics-index` (`upi`) |
| **Version** | `0.1.0-alpha` |
| **License** | MIT |
| **Python** | ≥ 3.10 |
| **Remote (public)** | [Universal-Physics-Index-UPI-](https://github.com/dpstudio-se/universal-physics-index) |

---

## What UPI is

UPI stores and checks **typed scientific nodes** (JSON) with strict status labels, units, provenance, uncertainty, and falsification fields. Agents and humans can:

- validate records against schemas
- link nodes with typed bridges
- run bounded workflows and software tests
- keep **symbolic** architecture separate from **established** physics

### Status labels (strict)

| Status | Meaning |
|--------|---------|
| `EST` | Experimentally established / widely accepted within stated domain |
| `DER` | Derived from declared `EST` facts and explicit assumptions |
| `HYP` | Testable but unverified |
| `STOP` | Blocked; requires named missing evidence (`stop_reason`) |
| `ERR` | Contradicted, invalid, obsolete, or superseded |
| `SYM` | Symbolic or conceptual interpretation only — **never** executable authority or hidden physical proof |

Agreement between agents, shared equations, matching numbers, or simulations does **not** by itself establish physical equivalence.

---

## Public remote as memory stack (software metaphor)

The public remote **Universal-Physics-Index-UPI-** is treated here as a **versioned memory and motor** for the project. This is a **software / information architecture** framing (`SYM` where metaphorical), not a biological or medical claim.

| Layer | Role in this repo | Typical location |
|-------|-------------------|------------------|
| **mRNA-motor** | Active, expressible instructions: schemas, CLI, validators, workflows — what gets “transcribed” into checks and runs | `src/upi/`, `schemas/`, CI, `upi validate` |
| **DNA-memory** | Stable, curated sequence: established nodes, bridges, tests, boundary rules | `data/established/`, `tests/`, `AGENTS.md`, core docs |
| **Junk-DNA-memory** | Retained but non-authoritative material: sketches, legacy notes, symbolic maps, blueprints kept for audit and future splicing | `docs/04_legacy_investigation/`, `SYM` examples, exploratory `docs/01_*` stubs |

**Physics is used when the task needs it** (units, `EST`/`DER` nodes, numerical helpers). Metaphor never upgrades a record to `EST`.

Related symbolic architecture (optional): [docs/VORTEX_DNA.md](docs/VORTEX_DNA.md), example node `data/examples/vortex_dna.json` (`SYM`).

---

## Boundary rules (non-negotiable)

- **8 Hz** is a configurable reference/example in this repository, not a universal constant or proof of a physical mechanism.
- `m = hf/c²` is an energy-equivalent rewrite of `E = mc²` and `E = hf` under compatible assumptions. It does **not** give the mass of an arbitrary oscillating object.
- Symbolic language (kernels, resonance, torsion poetry, “ToE” sketches) stays `SYM` or carefully scoped `HYP` with falsification criteria.
- Software tests prove software behavior: report `verification_type: software_test` when that is what was run.
- **This README is identity-protected.** Do not wholesale-replace it with a ToE manifesto or another project title. Anchors: [`config/readme_identity.json`](config/readme_identity.json) · policy: [`docs/README_IDENTITY.md`](docs/README_IDENTITY.md) · test: `pytest tests/test_readme_identity.py`.

See [AGENTS.md](AGENTS.md), [docs/SYMBOLIC_LAYER.md](docs/SYMBOLIC_LAYER.md), and [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Quick start

```bash
# install (editable)
pip install -e ".[dev]"

# validate an example node
upi validate data/examples/hypothesis_8hz.json

# frequency ↔ energy helpers (software utilities)
upi derive-mass --frequency 8

# tests
pytest tests/ modules/vrasi-physics/tests/ modules/vrasi-swarm/tests/ -v

# lint / types (as in CONTRIBUTING)
ruff check src tests modules/vrasi-physics/src modules/vrasi-physics/tests modules/vrasi-swarm/src modules/vrasi-swarm/tests
mypy src/upi --ignore-missing-imports
```

Swedish overview: [README.sv.md](README.sv.md).

---

## Repository map

| Path | Contents |
|------|----------|
| `src/upi/` | Core Python package: models, validation, graph, CLI, runtime |
| `schemas/` · `src/upi/schemas/` | JSON schemas for nodes, bridges, workflows, results |
| `data/established/` | Curated `EST`-oriented records |
| `data/examples/` | Examples including `HYP` / `SYM` |
| `data/bridges/` · other `data/*` | Bridges, domains, sources |
| `tests/` | Primary UPI test suite |
| `docs/` | Specs, boundaries, symbolic notes, theory drafts |
| `src/python/` · `src/rust/` | Optional numerical / geometric experiment code |
| `modules/vrasi-physics/` | Standalone minimal physics kernel |
| `modules/vrasi-swarm/` | Standalone transport-neutral coordination kernel |

---

## Submit a hypothesis

Include status, equation, definitions, units, assumptions, provenance, uncertainty, measurable variable, test method, prediction, and **falsification conditions**. Mark symbolic readings as `SYM`.

Node shape follows `schemas/node.schema.json` and addresses of the form:

`UPI<Domain,Generation,Torus,Node>`

---

## Example only: information-theoretic ToE blueprint (non-authoritative)

The block below is a **discrete example** of exploratory framing that this index can *host and classify* — not a claim that UPI has verified a Theory of Everything. In UPI terms it is at most **`SYM`** (conceptual scaffold) or fragmented **`HYP`** material pending independent evidence. Directory pointers match optional layout used by draft notes under `docs/` and `src/python` / `src/rust`.

<details>
<summary>Unified blueprint sketch (example → what such notes can lead to in-repo)</summary>

### THE UNIFIED BLUEPRINT FOR AN INFORMATION-THEORETIC THEORY OF EVERYTHING (ToE)

*An integrated framework based on quantum information, 7D torsion geometry, quantum extremal surfaces, and cosmic tests for 2027*

#### 1. Introduction: from matter to information

In the quest for the universe's most fundamental laws, physics has progressed through three distinct eras, first formulated by John Archibald Wheeler: **"Everything is Particles"**, **"Everything is Fields"**, and finally **"Everything is Information"** (the universe as an emergent phenomenon arising from binary quantum choices).

At the core of this theory is the premise that **spacetime and matter are not fundamental**, but instead emerge from fundamental flows of quantum information ("It from Bit"), where geometry and quantum entanglement are dual descriptions of the same underlying reality.

#### 2. The participatory universe

The theory's unifying philosophy rests on the **participatory universe**.

1. **No objective background:** Through physical measurements and the recording of binary yes/no interactions, observers actively participate in collapsing superposition states and "weaving" the geometry of spacetime.
2. **Spacetime as a consensus property:** The individual bits of information are correlated and shared through universal entanglement, stabilizing a single macroscopic spacetime. As Wheeler noted: *"Hope produces space and time"*.

#### Example directory hooks (draft / experimental)

| Path | Role (honest) |
|------|----------------|
| `docs/01_theory_and_fundamentals/`, `docs/02_observational_predictions/` | Placeholders / `SYM` notes — not EST derivations or a funded 2027 campaign |
| `src/python/` | **Toy** RK4/Euler ODE + spectrum demos (`verification_type: software_test`). Corrected after commit `a915735` (removed fabricated Omega-1766 / Planck claims) |
| `src/rust/g2_ricci_flow_sim/` | Same toy RK4 demo in Rust — not validated G2 Ricci-flow physics |
| `data/examples/information_theoretic_toe_blueprint.json` | Machine-readable `status: SYM` record of this sketch |

**UPI handling:** do not promote this sketch to `EST`. Link any concrete claim to equations, units, provenance, and a falsification test; otherwise keep `SYM`/`HYP`/`STOP`. Scripts under `src/python` and `src/rust` never upgrade status by themselves.

</details>

Placeholder theory notes live under `docs/01_theory_and_fundamentals/`. Established physics samples live under `data/established/` (e.g. Planck relation, Schrödinger, Maxwell, Lorentz invariant).

---

## Validation & integrity

```powershell
upi validate data/examples/hypothesis_8hz.json
upi derive-mass --frequency 8
pytest
```

Proposals are welcome; **labeling, testability, and transparent evidence are mandatory**.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for node submission, bridges, tests, and PR checklist.

## Citation

See [CITATION.cff](CITATION.cff).

## Security

See [SECURITY.md](SECURITY.md).

## License

MIT — see [LICENSE](LICENSE).
