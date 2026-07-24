# Digital qudit torus search

## Scope

This implementation is a classical state-vector simulator of finite-dimensional quantum mathematics. It models qudits, local shift, phase and Fourier transforms, phase oracles and amplitude amplification, but it is not quantum hardware and does not claim quantum speedup.

## Multi-torus register

Torus `i` has a cyclic coordinate

```text
j_i in {0, 1, ..., d_i - 1}
```

with arithmetic modulo `d_i`. A register with dimensions

```text
(d_1, d_2, ..., d_n)
```

has

```text
N = product_i d_i
```

basis states. The software uses mixed-radix coordinates, so `(1, 2)` in a `(4, 5)` register maps to flattened index

```text
1 * 5 + 2 = 7.
```

A torus can therefore have four, five, eight or more states. A `d = 3` carrier is a qutrit; `d > 3` gives additional local states.

## State vector

```text
|psi> = sum_x alpha_x |x>
sum_x |alpha_x|^2 = 1
```

The simulator explicitly stores all `N` complex amplitudes. This requires `O(N)` memory and does not reproduce the hardware resource scaling of a physical quantum processor.

## Functions on every torus

For one `d_i`-state torus:

```text
X_(d_i) |j_i> = |(j_i + 1) mod d_i>
omega_(d_i) = exp(2 pi i / d_i)
Z_(d_i) |j_i> = omega_(d_i)^j_i |j_i>
F_(d_i) |j_i> = (1/sqrt(d_i)) sum_k omega_(d_i)^(j_i k) |k>
```

Inside a multi-torus register these are local tensor operators:

```text
X_i = I_(d_1) tensor ... tensor X_(d_i) tensor ... tensor I_(d_n)
Z_i = I_(d_1) tensor ... tensor Z_(d_i) tensor ... tensor I_(d_n)
F_i = I_(d_1) tensor ... tensor F_(d_i) tensor ... tensor I_(d_n)
```

`X_i` changes only the selected cyclic coordinate. `Z_i` changes its relative phase while preserving every basis probability. `F_i` changes only that torus between computational and Fourier-dual representations. The implemented APIs are:

```python
local_shift_gate(state, dimensions, axis, shift)
local_phase_gate(state, dimensions, axis, power)
local_fourier_transform(state, dimensions, axis, inverse=False)
```

For example, shifting axis `0` by two in a `(4, 5)` register maps `(1, 2)` to `(3, 2)` and leaves the second torus unchanged.

## Fourier duality

The computational and Fourier bases are dual descriptions:

```text
F_(d_i)^-1 F_(d_i) = I_(d_i).
```

For a multi-torus register, the implementation applies `F_i` locally to one torus axis at a time while preserving all other coordinates. It then reverses the axis order and applies every inverse transform. The reconstruction invariant is

```text
epsilon_dual = max_x |alpha_x - alpha_hat_x|.
```

This is a numerical integrity check, not experimental evidence of quantum coherence.

## Search pipeline

The digital search has an explicit stage trace:

1. initialize a uniform state;
2. transform torus 0 to the Fourier basis;
3. transform each remaining torus;
4. invert the final torus;
5. invert each preceding torus;
6. apply a phase oracle;
7. apply diffusion;
8. repeat oracle and diffusion as declared;
9. rank the simulated measurement probabilities.

Thus the search is not restricted to three stages. With `n` toruses and `r` amplitude-amplification iterations, the trace contains

```text
2 + 2n + 2r
```

stages, counting initialization and ranked readout.

## Oracle and diffusion

For a Boolean marking function `f(x)`:

```text
O_f |x> = (-1)^f(x) |x>.
```

For the uniform state

```text
|s> = (1/sqrt(N)) sum_x |x>,
```

the diffusion operator is

```text
D = 2 |s><s| - I.
```

If `M` of `N` states are marked:

```text
theta = asin(sqrt(M/N))
P_success(r) = sin^2((2r + 1) theta)
r_opt approximately round(pi/(4 theta) - 1/2).
```

## Worked register

For dimensions `(4, 5)`:

```text
N = 4 * 5 = 20.
```

Mark flattened state `7`, corresponding to coordinate `(1, 2)`. The uniform probability is

```text
P_0 = 1/20 = 0.05.
```

For one marked state, the automatic selector chooses three iterations. The ideal analytic probability is

```text
theta = asin(sqrt(1/20))
P_success(3) = sin^2(7 theta),
```

which is greater than `0.99`. The deterministic regression suite verifies that state `7` becomes the top-ranked result and that the dual round-trip error remains near floating-point precision.

## API

```python
from upi import (
    basis_state,
    local_phase_gate,
    local_shift_gate,
    search_torus_register,
    tensor_product,
)

state = tensor_product((basis_state(4, 1), basis_state(5, 2)))
state = local_shift_gate(state, (4, 5), axis=0, shift=2)
state = local_phase_gate(state, (4, 5), axis=1, power=2)

result = search_torus_register((4, 5), (7,), top_k=5)
print(result.success_probability)
print(result.ranked_states[0])
```

Standalone package:

```bash
python -m pip install ./modules/vrasi-qudit
vrasi-qudit --dimensions 4,5 --targets 7 --top-k 5
```

## UPI boundary

- `EST`: finite-dimensional Hilbert spaces, generalized qudit gates, normalized Fourier transforms and ideal amplitude-amplification equations.
- `DER`: the UPI mixed-radix torus architecture, local-axis API, stage trace, ranking envelope and software integration.
- `SYM`: broader Vortex-DNA or cosmological interpretations of torus structure.
- `STOP`: claims of physical coherence, entanglement, quantum speedup or hardware operation without a verified quantum device and resource comparison.
