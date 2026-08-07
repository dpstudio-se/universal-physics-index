# AGENTS.md

This repository contains the Universal Physics Index (UPI): a machine-readable validation,
classification, and audit layer for scientific records, bounded workflows, and symbolic
architectures. Agent work in this repository must stay grounded in source files, schemas,
tests, and declared evidence boundaries.

## Repository map

- `src/upi/` — core Python package: models, validation, graph, CLI, runtime helpers
- `tests/` — primary UPI test suite
- `schemas/` and `src/upi/schemas/` — JSON schemas for nodes, bridges, workflows, and results
- `data/` — example and established records
- `docs/` — specifications, boundary rules, and symbolic architecture notes
- `modules/vrasi-physics/` — standalone minimal physics kernel
- `modules/vrasi-swarm/` — standalone transport-neutral coordination kernel

## Agent priorities

1. Preserve scientific and software boundaries.
2. Prefer explicit evidence over persuasive narrative.
3. Make the smallest change that fully solves the task.
4. Keep symbolic language usable, but never let it override canonical engineering meaning.
5. Do not promote metaphor, visualization, or correlation into `EST`.

## Non-negotiable scientific boundary rules

- Status values are strict: `EST`, `DER`, `HYP`, `STOP`, `ERR`, `SYM`.
- `SYM` means symbolic or conceptual interpretation only. It is never executable authority,
  physical evidence, experimental verification, or hidden permission.
- 8 Hz is a configurable reference/example in this repository, not a universal constant or proof
  of a physical mechanism.
- Agreement between agents, shared equations, matching numbers, or simulations does not by
  itself establish physical equivalence.
- Tests, audits, and validation runs must be described as
  `verification_type: software_test` when reporting what they prove.

## Image-derived symbolic guidance

The repository may reference image-driven ideas such as kernels, resonance, sovereign keys,
feedback loops, dimensional layers, or related visual metaphors. Treat these as `SYM` unless a
separate source file, schema, or test establishes a narrower software meaning.

Use this rule when interpreting the provided image basis:

- visual motif -> allowed as symbolic glossary, naming context, or documentation framing
- source code or schema behavior -> must be justified from repository files
- scientific claim -> must remain bounded by declared evidence and falsification criteria

Do not infer hidden architecture, permissions, frequencies, security properties, or physical laws
from artwork alone.

## Use UPI for debugging

Use UPI as the default structure for non-trivial diagnosis.

1. Record observations and tool output before proposing a cause.
2. Classify each claim with one UPI status:
   - `EST`: directly established by logs, source, tests, or reproducible inspection
   - `DER`: derived from declared `EST` facts and explicit assumptions
   - `HYP`: falsifiable explanation not yet verified
   - `STOP`: blocked by specifically named missing evidence or mechanism
   - `ERR`: contradicted, invalid, obsolete, or superseded claim
   - `SYM`: symbolic interpretation only
3. Give every `STOP` claim a concrete `stop_reason` and the smallest next observation needed.
4. Include reproduction steps, expected vs observed behavior, relevant versions or commit SHAs,
   and a falsification or failure condition.
5. Distinguish repository integrity, application behavior, connector behavior, and UI rendering;
   success in one layer does not prove correctness in another.
6. Use typed relations where useful, such as `DERIVED_FROM`, `CAUSES`, `CONTRADICTS`,
   `STOPS_AT`, `MEASURED_BY`, or `FALSIFIED_BY`.
7. Preserve secrets and personal data.

Preferred debug result shape:

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

Prefer an honest `STOP` over an unsupported explanation.

## Change guidance

- For Python changes, validate with the existing project commands from `README.md` and
  `CONTRIBUTING.md`:
  - `pytest tests/ modules/vrasi-physics/tests/ modules/vrasi-swarm/tests/ -v`
  - `ruff check src tests modules/vrasi-physics/src modules/vrasi-physics/tests modules/vrasi-swarm/src modules/vrasi-swarm/tests`
  - `mypy src/upi --ignore-missing-imports`
- For schema or data changes, use `upi validate <file>` when applicable.
- Do not add undocumented capabilities, network behavior, or execution paths to workflow or plugin
  contracts.
- Keep biological, cosmological, or metaphysical language explicitly marked as metaphor when used.

## Protected README identity (mandatory)

Top-level `README.md` and `README.sv.md` are **identity-protected**. Do **not** wholesale-replace
them with ToE manifestos, product pitches, chat dumps, or unrelated project titles.

1. H1 must remain `# Universal-Physics-Index-UPI` (see `config/readme_identity.json`).
2. Keep required anchors/sections; speculative ToE text only under an **Example only** / `SYM` block.
3. Prefer additive edits. If an anchor must change, update `config/readme_identity.json` in the
   **same** change and run `pytest tests/test_readme_identity.py -v`.
4. Policy doc: `docs/README_IDENTITY.md`. CI fails when identity anchors are removed.

Violating this is an `ERR`-class process failure for agent work, not a valid “rewrite for clarity”.

## Source-of-truth order

When repository materials disagree, prefer:

1. tests and executable validation behavior
2. schemas and code in `src/upi/`
3. top-level `README.md` (identity-protected; not a free-form manifesto surface)
4. focused documents under `docs/`
5. examples and symbolic illustrations

If evidence is still insufficient, report `STOP` rather than inventing resolution.
