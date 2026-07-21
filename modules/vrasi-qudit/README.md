# VR-ASI Qudit

`vrasi-qudit` is a dependency-free classical state-vector simulator for finite-dimensional qudits and multi-torus search registers.

Each torus is a cyclic basis with dimension `d >= 2`. A register with dimensions `(d1, d2, ..., dn)` has

```text
N = d1 * d2 * ... * dn
```

basis states. This allows four, five, eight, or many more states per torus instead of restricting the model to binary qubits or three-level qutrits.

## Functions

- generalized cyclic shift `X_d`;
- generalized phase gate `Z_d`;
- normalized discrete quantum Fourier transform;
- local Fourier transform on one torus axis;
- mixed-radix coordinate/index conversion;
- tensor products;
- phase oracle;
- diffusion/amplitude-amplification step;
- multi-stage search with dual-basis reconstruction checks.

## CLI

```bash
vrasi-qudit --dimensions 4,5 --targets 7 --top-k 5
```

The command returns JSON with ranked basis states, torus coordinates, marked-state probability, iteration count, dual round-trip error and the full search-stage trace.

## Scientific boundary

This package implements established qudit and amplitude-amplification mathematics in ordinary Python. It stores and updates every complex amplitude explicitly, so memory and runtime scale with the full basis size. It is not quantum hardware and does not claim physical coherence, entanglement, measurement, or quantum speedup.
