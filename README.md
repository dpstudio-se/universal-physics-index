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
```text
E = h·f          m = h·f / c²          f = m·c² / h
```

**Critical**: `f` = invariant rest-mass frequency when the quantity is interpreted as rest mass. For an arbitrary frequency, `h·f/c²` is an energy-equivalent mass calculation, not automatically the invariant mass of an oscillating object.

### 4. Normalized Signal Loader

Runtime matching: `Z(t,x) = z(t,x) / z_ref(t,x)` with tolerance `abs(Z - 1) ≤ epsilon_Z`.

Numerical agreement inside a declared tolerance is not evidence of physical identity or a shared mechanism.

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
upi debug-index data --output upi-debug-report.json
upi debug-index data --format markdown --output upi-debug-report.md
upi debug-index data --odins-eye --output upi-odins-eye.json
python repo_audit.py --output repo-audit.json

# Python API
python - <<'PY'
from upi import mass_from_frequency
print(mass_from_frequency(1e20))
PY
```

## Codespaces

This repository is preconfigured for GitHub Codespaces via `.devcontainer/devcontainer.json`.

1. Open the repository in GitHub.
2. Click **Code** -> **Codespaces** -> **Create codespace on main**.
3. Wait for container initialization.
4. Run:
   - `pytest tests/ -v`
   - `ruff check src tests repo_audit.py`
   - `mypy src/upi repo_audit.py --ignore-missing-imports`
   - `python repo_audit.py --output repo-audit.json`

## Repository Structure

- `src/upi/` — Core modules for physics, models, validation, graph, CLI and audit reporting
- `modules/vrasi-physics/` — Standalone, dependency-free VR-ASI physics kernel
- `modules/vrasi-swarm/` — Standalone 3-6-9/Gen4 coordination kernel
- `tests/` — UPI regression and boundary test suite
- `schemas/` — Schemas for nodes, bridges, theories and bounded workflow records
- `data/` — Schema-routed UPI nodes, bridges, theories and intentional negative fixtures
- `config/` — Operational configuration such as ports and external-source declarations
- `docs/` — Specifications, derivations and scientific-boundary documentation

Operational manifests do not belong under `data/` unless they implement one of the declared UPI record schemas.

### Standalone VR-ASI physics

The simulator does not need the complete UPI graph or workflow system. Its three required calculations are packaged separately and can be installed without `upi`:

```bash
python -m pip install ./modules/vrasi-physics
vrasi-physics 8
```

See [`modules/vrasi-physics/README.md`](modules/vrasi-physics/README.md) for the deliberately small API and its interpretation limits.

### 3-6-9 generation 4 coordination

The transport-neutral swarm module turns nine allowlisted node observations into a deterministic top-three quorum. It shares hashes and pseudonymous IDs, not private payloads or network endpoints:

```bash
python -m pip install ./modules/vrasi-swarm
vrasi-swarm demo
```

This is an auditable coordination protocol (`SYM`), not a claim of collective biological consciousness or new physics.

## Important Disclaimers

**UPI is NOT**: A Theory of Everything | Peer review replacement | Claim of universal 8 Hz constant

**UPI DOES**: Record stopping points | Support 6 status labels | Enable machine-readable science

## Testing

```bash
python -m pytest tests/ modules/vrasi-physics/tests/ modules/vrasi-swarm/tests/ -v
ruff check src tests repo_audit.py modules/vrasi-physics/src modules/vrasi-physics/tests modules/vrasi-swarm/src modules/vrasi-swarm/tests
mypy src/upi repo_audit.py --ignore-missing-imports
python repo_audit.py --output repo-audit.json
upi validate data/constants/planck.json
```

`repo_audit.py` exits non-zero when schemas, typed data, plugin manifests, source declarations, critical files or port assignments are invalid.

## Automated UPI debugging

`upi debug-index` scans every typed JSON record below a directory and produces both an error report and an exploded map across record, scale, evidence, finding, and correction layers. The same pipeline works across the full typed index while preserving domain and scale boundaries.

The scanner:

- validates node, bridge, and theory schemas;
- treats source records and filenames as untrusted input;
- redacts source values and replaces source paths with stable hashes in every report mode;
- applies stable scientific-boundary error codes;
- requires falsification conditions for testable node hypotheses;
- suggests corrections without mutating source records;
- records time/length scale as unspecified unless the source explicitly declares it;
- labels its own result as `software_test`, never experimental verification.

Shared equations or software functions across different time and length scales are mapped as relationships, not treated as proof of a shared physical mechanism.

Add `--odins-eye` for a local, read-only inspection layer. It reports exact-content mirrors, conflicting records that reuse one UPI identity, hidden JSON paths, and possible semantic mirrors. Exact matches and conflicts are hash-backed; semantic overlap remains `HYP`. Reports contain stable path identifiers and full path hashes, never raw source paths or values. The scanner does not access networks or mutate index records.

## Declarative agent workflows

UPI includes schemas for bounded agent tasks, terminal results and workflow specifications. The contracts model transport, independent review and reversible quarantine under default-deny capabilities. See `docs/AGENT_CIRCULATION.md` and `examples/workflows/`.

This is a validation and audit layer, not a scheduler or autonomous agent runtime. Biological terms such as circulation and immunity are `SYM` architecture metaphors only.

Plugin manifests are also validation-only. Executable command construction fails closed until a runtime can enforce every declared capability and default-deny restriction.

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

For full documentation, see `docs/`.

Functional DNA and Vortex-DNA collaboration concepts are documented in [`docs/FUNCTIONAL_DNA.md`](docs/FUNCTIONAL_DNA.md) and [`docs/VORTEX_DNA.md`](docs/VORTEX_DNA.md). Both are `SYM` architectures; they do not provide independent scientific evidence or hidden authority.
