# VR-ASI Physics

`vrasi-physics` is the standalone calculation kernel used by the VR-ASI simulator.
It intentionally contains only the physics required by that module:

- photon energy from frequency, `E = h f`;
- algebraic mass-energy equivalent, `m = h f / c²`;
- normalization against an explicitly supplied reference frequency.

It has no runtime dependencies and does not import Universal Physics Index. The
constants and equations follow the same SI-based foundation, while the package API,
validation and release lifecycle are independent.

```bash
python -m pip install ./modules/vrasi-physics
vrasi-physics 8
```

The default 8 Hz value is a simulator coordinate only. It is not represented as a
universal constant, physical mechanism, medical frequency or experimental result.
The mass value is an algebraic energy equivalent unless the input has independently
been established as an invariant rest-mass frequency.
