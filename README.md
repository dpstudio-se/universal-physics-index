# Universal Physics Index (UPI) v0.1.0-alpha

A machine-readable, typed scientific knowledge graph for physics, mathematics, chemistry, and related disciplines.

## Vision

Build an open platform for organizing scientific knowledge with:
- **Explicit status tracking**: EST (established), DER (derived), HYP (hypothesis), STOP (incomplete), ERR (erroneous), SYM (symbolic)
- **Typed relations**: 16 edge types capturing how concepts relate (DERIVED_FROM, CAUSES, DUAL_TO, etc.)
- **Precision over breadth**: Prefer declaring what is not known rather than speculating
- **Reproducibility**: All nodes support falsification conditions and evidence records

## Core Principles

### 1. Scientific Status Enum

Every claim is labeled:
- **EST**: Established within declared domain
- **DER**: Derived from explicitly stated assumptions
- **HYP**: Falsifiable but unverified
- **STOP**: Missing proof, mechanism, evidence, or selection rule
- **ERR**: Contradicted, invalid, or superseded
- **SYM**: Symbolic/conceptual interpretation only

### 2. UPI Address Format

Hierarchical, machine-readable addresses: `UPI<Domain,Generation,Torus,Node>`

- **Domain**: physics, mathematics, chemistry, etc.
- **Generation**: Derivation lineage (1 = fundamental)
- **Torus**: Feedback-bounded system (classical, quantum, relativistic)
- **Node**: Concept identifier

### 3. Mass-Frequency Bridge

Fundamental relation:
```
E = h·f          m = h·f / c²          f = m·c² / h
```

**Critical**: `f` = invariant rest-mass frequency (not any frequency)

### 4. Normalized Signal Loader

Runtime matching: `Z(t,x) = z(t,x) / z_ref(t,x)` with tolerance `abs(Z - 1) ≤ epsilon_Z`

## Quick Start

```bash
# Install
pip install universal-physics-index

# CLI examples
upi frequency-to-mass 8
upi mass-to-frequency 1e-30
upi index8 --frequency 8
upi normalize --observed 4.5 --reference 4.0
upi validate data/constants/planck.json

# Python API
from upi import mass_from_frequency, UPIGraph, PhysicsNode
mass = mass_from_frequency(1e20)
```

## Codespaces

This repository is preconfigured for GitHub Codespaces via
`.devcontainer/devcontainer.json`.

1. Open the repository in GitHub.
2. Click **Code** -> **Codespaces** -> **Create codespace on main**.
3. Wait for container initialization (dependencies are installed automatically).
4. Run:
   - `pytest tests/ -v`
   - `ruff check src tests`
   - `mypy src/upi --ignore-missing-imports`

## Autonomous Workflow Engine (UPI)

UPI now includes a deterministic workflow engine for autonomous
analyze -> plan -> debug/patch candidate -> release gate decisions.

Run it from a repo audit report:

```bash
python repo_audit.py --output report.json
upi workflow-engine --report report.json --min-score 0.75 --max-risk 0.35
```

Behavior:
- Converts audit findings into normalized issues.
- Builds ranked patch candidates (crew role: patcher).
- Applies an optimal release gate.
- Fails closed when any candidate is below score/risk threshold.

## Repository Structure

- `src/upi/` — Core modules (physics, models, validation, CLI)
- `tests/` — Test suite (38 tests, all passing)
- `schemas/` — JSON schemas (node, bridge, theory)
- `data/` — Example nodes, theories, STOP problems
- `docs/` — Specification and documentation

## Important Disclaimers

**UPI is NOT**: A Theory of Everything | Peer review replacement | Claim of universal 8 Hz constant

**UPI DOES**: Record stopping points | Support 6 status labels | Enable machine-readable science

## Testing

```bash
pytest tests/ -v        # 38 tests, all passing
ruff check src tests    # Linting
mypy src/upi            # Type checking
upi validate data/constants/planck.json  # Schema validation
```

## License

MIT - See LICENSE file

## Citation

```bibtex
@software{upi2024,
  title={Universal Physics Index},
  author={UPI Contributors},
  year={2024},
  url={https://github.com/dpstudio-se/universal-physics-index}
}
```

**Status**: Alpha v0.1.0 — API subject to change

For full documentation, see `docs/`

Functional DNA and Vortex-DNA collaboration concepts are documented in
[`docs/FUNCTIONAL_DNA.md`](docs/FUNCTIONAL_DNA.md) and
[`docs/VORTEX_DNA.md`](docs/VORTEX_DNA.md). Both are `SYM` architectures;
they do not provide independent scientific evidence or hidden authority.
