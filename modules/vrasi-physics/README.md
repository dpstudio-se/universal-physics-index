# VR-ASI Physics

`vrasi-physics` is the standalone calculation kernel used by the VR-ASI simulator.
It intentionally contains only bounded, explicit calculations required by that module:

- photon energy from frequency, `E = h f`;
- algebraic mass-energy equivalent, `m = h f / c²`;
- normalization against an explicitly supplied reference frequency;
- uniform helical position and geometry;
- rotation-to-linear screw conversion with declared efficiency;
- two-rotor angular-momentum and energy balance.

It has no runtime dependencies and does not import Universal Physics Index. The
constants and equations follow the same SI-based foundation, while the package API,
validation and release lifecycle remain independently testable.

```bash
python -m pip install ./modules/vrasi-physics
vrasi-physics 8
```

```python
from math import pi

from vrasi_physics import (
    evaluate_coupled_rotors,
    evaluate_helical_motion,
    evaluate_screw_coupling,
)

helix = evaluate_helical_motion(0.1, 0.4, 2 * pi * 8)
screw = evaluate_screw_coupling(0.05, 2 * pi * 8, efficiency=0.8, torque_nm=1.0)
rotors = evaluate_coupled_rotors(2.0, 3.0, 1.0, -6.0)
```

The default 8 Hz frequency value is a simulator coordinate only. It is not represented
as a universal constant, physical mechanism, medical frequency or experimental result.
When used in the helix example, 8 Hz means eight declared mechanical revolutions per
second. The mass value from `h f / c²` is an algebraic energy equivalent unless the
input has independently been established as an invariant rest-mass frequency.

The full derivation and model boundaries are documented in
`docs/HELICAL_LINEAR_ROTATIONAL_DYNAMICS.md` in the parent repository.
