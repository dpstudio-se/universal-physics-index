# Qudit physics index

This map separates established finite-dimensional quantum mathematics from the derived UPI torus architecture and the classical simulation boundary.

## Established nodes

| UPI address | Scope |
|---|---|
| `UPI<quantum_information,1,finite_dimensional,hilbert_state_space>` | Normalized states, orthonormal bases and unitary maps in `C^d` |
| `UPI<quantum_information,1,qudit,generalized_weyl_gates>` | Generalized cyclic shift `X_d` and phase `Z_d` operators |
| `UPI<quantum_information,1,qudit,fourier_dual_basis>` | Normalized qudit Fourier transform and inverse duality |
| `UPI<quantum_information,1,multi_qudit,tensor_product_register>` | Tensor-product composition and `N = product_i d_i` |
| `UPI<quantum_information,1,measurement,born_probability_rule>` | Ideal basis probabilities `p_j = |alpha_j|^2` |
| `UPI<quantum_algorithms,1,amplitude_amplification,phase_oracle_diffusion>` | Phase oracle, diffusion reflection and ideal Grover rotation |

## Derived nodes

| UPI address | Scope |
|---|---|
| `UPI<information_physics,3,qudit_torus,digital_multi_state_search>` | UPI mixed-radix torus coordinates, local-axis API, stage trace and ranking |
| `UPI<computational_physics,2,state_vector,classical_resource_boundary>` | Dense software memory and runtime boundary |

## Dependency chain

```text
finite-dimensional Hilbert space
    |-- generalized qudit X_d and Z_d gates
    |-- Fourier-dual basis
    |-- tensor-product register
    `-- Born probability rule

phase oracle + diffusion
              \
               > digital multi-torus qudit search
              /
local X_i, Z_i, F_i functions

Digital search --STOPS_AT--> classical dense state-vector boundary
```

## Status boundary

- `EST`: Hilbert space, tensor products, generalized qudit operators, Fourier basis change, Born probabilities and ideal amplitude-amplification mathematics.
- `DER`: mixed-radix torus naming, local-axis software API, stage trace, deterministic ranking and dense implementation analysis.
- `STOP`: physical quantum coherence, entanglement, gate fidelity or quantum speedup without independently verified hardware and a matched resource comparison.
- `SYM`: broader Vortex-DNA, biological or cosmological torus interpretations remain outside the established quantum-mechanics nodes.

## Central equations

```text
H_d = C^d
|psi> = sum_j alpha_j |j>
sum_j |alpha_j|^2 = 1

X_d |j> = |(j + 1) mod d>
Z_d |j> = exp(2 pi i j / d) |j>
F_d |j> = (1/sqrt(d)) sum_k exp(2 pi i j k / d) |k>

H = tensor_i C^(d_i)
N = product_i d_i
p_x = |alpha_x|^2

O_f |x> = (-1)^f(x) |x>
D = 2 |s><s| - I
P_success(r) = sin^2((2r + 1) asin(sqrt(M/N)))

memory_dense_state = O(N)
```

The software can reproduce these declared equations and invariants. It does not convert ordinary memory into quantum hardware.
