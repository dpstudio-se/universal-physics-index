# Dual-observer trace physics

## Scientific boundary

This implementation has two layers:

1. **Established physics:** the Lorentz transformation and preservation of the Minkowski interval in special relativity.
2. **UPI audit layer:** `R0_TIR` and `r0_S`, which score reconstruction conflict relative to declared tolerances. These metrics are derived engineering quantities, not new constants or forces.

## Physical mapping

For inertial observer B moving at velocity `v` along observer A's x-axis:

```text
beta  = v / c
gamma = 1 / sqrt(1 - beta^2)

t_B = gamma * (t_A - v*x_A/c^2)
x_B = gamma * (x_A - v*t_A)
```

The inverse mapping is obtained by replacing `v` with `-v`.

The invariant is

```text
Omega = c^2*t^2 - x^2
```

and exact Lorentz transformations require

```text
Omega_A = Omega_B.
```

## Trace metric

For reconstruction residuals `epsilon_i` and positive tolerances `tau_i`:

```text
R0_TIR = (1/N) * sum_i min(1, abs(epsilon_i)/tau_i)
```

Therefore `0 <= R0_TIR <= 1`.

The finite-difference rate is

```text
r0_S = (R0_TIR_current - R0_TIR_previous) / delta_t
```

with unit `s^-1`.

## Worked calculation

Inputs:

```text
t_A = 2.0e-6 s
x_A = 300 m
beta = 0.6
v = 179875474.8 m/s
gamma = 1.25
```

Forward map:

```text
t_B = 1.7494807858041578e-6 s
x_B = -74.68868699999994 m
```

Invariant:

```text
Omega_A = 269502.0714947271 m^2
Omega_B = 269502.0714947270 m^2
relative floating-point drift = 4.3196447871909036e-16
```

With `tau_t = 1 ns` and `tau_x = 0.1 m`, the exact round trip gives:

```text
R0_TIR = 2.1175823681357506e-13
```

The tiny nonzero value is floating-point residue, not a physical violation.

Now inject observer-B offsets:

```text
delta_t_B = +2 ns
delta_x_B = +0.25 m
```

Backward reconstruction becomes:

```text
time error     = 3.125432678496633e-9 s
position error = 0.7621886869999344 m
R0_TIR         = 1.0
Omega relative error = 0.002467285898080553
```

Both components exceed their declared tolerances, so the clipped mean saturates at 1.

## Python API

```python
from upi.constants import C
from upi.dual_observer import Event1D, dual_observer_trace

result = dual_observer_trace(
    Event1D(time_s=2e-6, position_m=300.0),
    relative_velocity_m_s=0.6 * C,
    time_tolerance_s=1e-9,
    position_tolerance_m=0.1,
)

print(result.as_dict())
```

Use `observed_b=Event1D(...)` to score measured or deliberately perturbed observer-B data.

## Falsification and extension

The software profile fails if an exact forward/backward Lorentz map does not preserve the interval and reconstruct the source state within declared numerical tolerance. A claim of new physical behavior requires an additional observable, a competing-model comparison, and a preregistered experiment. Lower trace error alone is not evidence for a new mechanism.
