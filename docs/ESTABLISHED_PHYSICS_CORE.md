# Established Physics Core

This directory seeds UPI with compact `EST` nodes whose equations, domains, assumptions, and confusion guards are explicit.

## Included domains

| Domain | Node | Core relation |
|---|---|---|
| Classical mechanics | Newton's second law | `F_net = d p / d t` |
| Classical mechanics | Momentum conservation | `dP/dt = F_ext` |
| Classical mechanics | Work-energy theorem | `W_net = Delta K` |
| Electromagnetism | Maxwell equations | field equations in SI form |
| Special relativity | Lorentz interval | `Delta s^2 = c^2 Delta t^2 - Delta r^2` |
| Quantum mechanics | Planck-Einstein relation | `E = h f` |
| Quantum mechanics | Schroedinger equation | `i hbar partial_t psi = H psi` |
| Thermodynamics | First and second laws | `Delta U = Q - W`, `Delta S_isolated >= 0` |

## Boundary policy

`EST` means the node's scoped relation is established in its stated regime. It does not mean the equation is universally valid outside that regime, nor that every interpretation attached to it is established.

The catalog deliberately separates:

1. measured law or validated model;
2. assumptions and reference frame;
3. interpretation-level claims;
4. falsification conditions and known limits.

## Next catalog layers

Planned expansions: fluid mechanics, continuum mechanics, statistical mechanics, optics, general relativity, quantum field theory, Standard Model, nuclear physics, condensed matter, plasma physics, cosmology, and metrology.
