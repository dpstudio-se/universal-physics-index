# `src/python` — exploratory numerical demos

**Status: `SYM` / software illustrations only.**

Scripts here are **not** part of the core `upi` package API. They must not be
read as experimental confirmation of G2 Ricci flow, Primakoff signals,
Omega-1766, Torstone physics, or any Theory of Everything.

| Script | Role |
|--------|------|
| `g2_ricci_flow_rk4_sim.py` | Toy RK4 integrator (corrected after a915735) |
| `g2_ricci_flow_sim.py` | Toy Euler walk on the same demo ODE family |
| `plot_ricci_flow.py` | Optional CSV plot helper |
| `primakoff_spectrum.py` | Toy bump spectrum CSV |

When tests cover these scripts, report `verification_type: software_test`.

Canonical science/engineering boundaries live in the top-level README and
`AGENTS.md`. Machine-readable examples: `data/examples/`.
