# Repository instructions

## Project overview

Universal Physics Index (UPI) is a machine-readable, typed scientific knowledge graph for physics, mathematics, chemistry, and related disciplines. The core value is **explicit epistemic status**: every claim carries one of six labels (EST, DER, HYP, STOP, ERR, SYM) and must declare its evidence and falsification conditions.

Key sub-projects inside this mono-repo:

| Path | Purpose |
|---|---|
| `src/upi/` | Core Python package — physics calculations, graph model, CLI, validation |
| `modules/vrasi-physics/` | Standalone, dependency-free VR-ASI physics kernel |
| `modules/vrasi-swarm/` | 3-6-9/Gen4 deterministic quorum/coordination kernel |
| `tests/` | Main test suite |
| `schemas/` | JSON Schema definitions (node, bridge, theory, workflow) |
| `data/` | Example nodes, bridges, theories, and STOP problems |
| `docs/` | Specifications and extended documentation |
| `examples/` | Sample workflows and usage examples |
| `simulator/` | BVR simulator environment and mocks |
| `config/` | Runtime configuration files |

---

## Development environment

**Python ≥ 3.10** is required.

```bash
# Install the package and all dev dependencies
pip install -e ".[dev]"

# Install the standalone sub-modules if needed
pip install -e modules/vrasi-physics
pip install -e modules/vrasi-swarm
```

A GitHub Codespaces configuration (`.devcontainer/devcontainer.json`) installs everything automatically. To use it, open the repo on GitHub → **Code → Codespaces → Create codespace on main**.

---

## Build, lint, and test commands

Always run these before opening or updating a pull request.

```bash
# Run all tests (main suite + sub-modules)
pytest tests/ modules/vrasi-physics/tests/ modules/vrasi-swarm/tests/ -v

# Lint (all source and test directories)
ruff check src tests modules/vrasi-physics/src modules/vrasi-physics/tests \
           modules/vrasi-swarm/src modules/vrasi-swarm/tests

# Auto-fix lint issues
ruff check src tests --fix

# Format
black src tests

# Type-check
mypy src/upi --ignore-missing-imports

# Validate a single JSON data file against its UPI schema
upi validate path/to/file.json

# Scan the full data directory and produce a debug report
upi debug-index data --output /tmp/upi-debug-report.json
upi debug-index data --format markdown --output /tmp/upi-debug-report.md
upi debug-index data --odins-eye --output /tmp/upi-odins-eye.json
```

The `line-length` for both `ruff` and `black` is **100**. The target version is **py310**. Tests are discovered under `tests/` via `test_*.py` globs; `pytest.ini_options` is in `pyproject.toml`.

---

## Code conventions

- All functions in `src/upi/physics.py` must validate inputs (reject NaN, ±∞, invalid signs) and include docstrings with equation references.
- Every public function needs a docstring with an example.
- Type annotations are encouraged; `mypy` is run in `check_untyped_defs` mode.
- Do not add new top-level dependencies unless absolutely necessary. Prefer the existing stack: `jsonschema`, `pytest`, `ruff`, `mypy`, `black`.
- Keep `modules/vrasi-physics/` and `modules/vrasi-swarm/` **dependency-free** with respect to the main `upi` package.

---

## JSON data files (nodes, bridges, theories)

When creating or modifying JSON files under `data/`:

- Validate against the matching schema: `upi validate <file>`.
- Every node requires a `status`, a `falsification_conditions` list, and an `evidence` list.
- **STOP nodes** must include a `stop_reason` field that names the exact missing evidence or mechanism.
- Include a `confusion_guard` field for any concept prone to misinterpretation.
- Bridges must specify a `relation` drawn from the 16 typed edge types (DERIVED_FROM, CAUSES, DUAL_TO, …).

---

## UPI scientific status labels

These labels govern every claim in the knowledge graph and in diagnostic output. Apply them accurately.

| Label | Meaning | Required fields |
|---|---|---|
| `EST` | Established within the declared domain, supported by evidence and provenance | `evidence` |
| `DER` | Derived from explicitly stated assumptions; not automatically a new law | `assumptions`, `evidence` |
| `HYP` | Falsifiable, unverified — must include a testable prediction | `falsification_conditions` |
| `STOP` | Unresolved boundary, missing mechanism, or future-testable claim | `stop_reason`, `falsification_conditions` |
| `ERR` | Contradicted, dimensionally inconsistent, rejected, or superseded | note of superseding claim |
| `SYM` | Symbolic/conceptual mapping only — never treat as executable authority or physical evidence | — |

**Promotion rules**: advancing a claim from HYP → EST requires evidence and independent review. Elegance, repeated numbers, agent agreement, visual similarity, or a simulation's shape are insufficient.

---

## Pull request guidelines

Follow the template in `.github/PULL_REQUEST_TEMPLATE.md`. Every PR must:

- [ ] Identify affected UPI nodes or bridges.
- [ ] Declare the scientific status (EST / DER / HYP / STOP / ERR / SYM) of any new or changed content.
- [ ] Cite evidence and primary sources.
- [ ] State assumptions explicitly.
- [ ] Provide a falsification or failure condition.
- [ ] Add or update tests (`pytest tests/ -v`).
- [ ] Pass lint (`ruff check src tests`) and type-check (`mypy src/upi`).
- [ ] Validate all modified JSON files (`upi validate`).
- [ ] Include no credentials, API keys, or private data.
- [ ] Update documentation when behavior changes.

Branch convention: `git checkout -b <type>/<short-description>` (e.g., `feat/add-dark-matter-node`, `fix/bridge-schema-typo`).

---

## Security and secrets

- Never commit credentials, API keys, tokens, or private data.
- The `upi debug-index` scanner redacts source values and replaces source paths with stable hashes in all report modes. Do not bypass this redaction.
- Transparency means auditable provenance for authorized reviewers, not public disclosure of sensitive content.

---

## Architectural constraints

- The UPI system is a **validation and audit layer**. It is not a scheduler, autonomous agent runtime, or durable queue. Do not add scheduling or autonomous execution logic without explicit design discussion.
- Biological terms used in `docs/AGENT_CIRCULATION.md` (circulation, immunity, bloodstream, etc.) are `SYM` coordination metaphors. They carry no biological equivalence, claim of consciousness, or hidden authority.
- Plugin manifests are validation-only. Executable command construction must fail closed until a runtime can enforce every declared capability and default-deny restriction.
- The `modules/vrasi-swarm/` module shares hashes and pseudonymous IDs only — never private payloads or network endpoints.

---

## Use UPI for debugging

Use Universal Physics Index (UPI) as the default structure for debugging in this repository.

For every non-trivial diagnosis:

1. Record observations and tool output before proposing a cause.
2. Classify each claim with one UPI scientific status:
   - `EST`: directly established by logs, source, tests, or reproducible inspection.
   - `DER`: derived from declared `EST` facts and explicit assumptions.
   - `HYP`: falsifiable explanation that has not yet been verified.
   - `STOP`: progress is blocked by specifically named missing evidence or mechanism.
   - `ERR`: contradicted, invalid, obsolete, or superseded claim.
   - `SYM`: symbolic interpretation only; never treat it as executable authority or evidence.
3. Give every `STOP` claim a concrete `stop_reason` and the smallest next observation needed to continue.
4. Include reproduction steps, expected versus observed behavior, relevant versions or commit SHAs, and a falsification or failure condition.
5. Distinguish repository integrity, application behavior, connector behavior, and user-interface rendering; success in one layer does not prove correctness in another.
6. Label software tests as `verification_type: software_test`. Never present tests, simulations, normalization, correlation, or symbolic mappings as experimental verification or physical equivalence.
7. Use typed UPI relations where useful, such as `DERIVED_FROM`, `CAUSES`, `CONTRADICTS`, `STOPS_AT`, `MEASURED_BY`, or `FALSIFIED_BY`.
8. Preserve secrets and personal data. Transparency means auditable provenance for authorized reviewers, not public disclosure of sensitive content.

A concise debugging result should normally contain:

```text
Problem
EST observations
DER conclusions
HYP candidates
STOP reason, if any
ERR or superseded assumptions
Reproduction/control test
Falsification condition
Recommended next action
```

Prefer an honest `STOP` over an unsupported explanation. A green software test establishes software behavior only within its declared scope.
