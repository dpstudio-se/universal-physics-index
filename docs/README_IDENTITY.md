# README identity protection

Top-level `README.md` and `README.sv.md` are **protected project identity surfaces**.

They must describe **Universal-Physics-Index-UPI** (Universal Physics Index): a machine-readable classification, validation, and audit layer — not a substitute Theory of Everything document.

## Why

Agents and drive-by edits have replaced the entire README with exploratory ToE text. That breaks onboarding, packaging (`pyproject.toml` → `readme = "README.md"`), and scientific boundary communication.

## Enforcement

| Layer | Mechanism |
|-------|-----------|
| Machine anchors | [`config/readme_identity.json`](../config/readme_identity.json) |
| Automated test | [`tests/test_readme_identity.py`](../tests/test_readme_identity.py) (runs in normal `pytest`) |
| Review routing | [`.github/CODEOWNERS`](../.github/CODEOWNERS) |
| Agent policy | [`AGENTS.md`](../AGENTS.md) — do not wholesale-replace README |
| Contributor checklist | [`CONTRIBUTING.md`](../CONTRIBUTING.md) |

## Legitimate README changes

1. Keep H1 exactly: `# Universal-Physics-Index-UPI`
2. Keep required substrings/sections listed in `config/readme_identity.json`
3. Put speculative ToE / symbolic narrative only under an **Example only** (or clearly `SYM`) section
4. If you must change an anchor string, **update `config/readme_identity.json` in the same PR** and explain why
5. Run: `pytest tests/test_readme_identity.py -v`

## Illegal pattern

```text
# THE UNIFIED BLUEPRINT FOR AN INFORMATION-THEORETIC THEORY OF EVERYTHING (ToE)
…entire file is manifesto…
```

That content may live as:

- a collapsible **example** inside README, and/or
- `data/examples/*.json` with `"status": "SYM"`, and/or
- drafts under `docs/01_theory_and_fundamentals/`

It must **not** become the repository title or sole README body.

## Source-of-truth order (unchanged)

1. tests and executable validation  
2. schemas and `src/upi/`  
3. top-level `README.md` (identity-protected)  
4. focused `docs/`  
5. examples and symbolic illustrations  
