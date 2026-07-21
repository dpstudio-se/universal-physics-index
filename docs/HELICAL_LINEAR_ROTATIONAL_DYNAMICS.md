# Helical linear-rotational dynamics

This document maps the diagram

```text
      ╭───╮     ╭───╮
   φ──╯   ╰──◎──╯   ╰──φ
      ╰───╯     ╰───╯
        ▲         ▲
  [ LINEAR ] — [ SPIRAL ]
```

to established mechanics. The diagram is a topology sketch. It becomes a physical model only after radius, pitch, mass, inertia, angular speed, force, torque, losses, and boundary interactions are declared.

## 1. Coordinate model

Choose the x-axis as the translation and rotation axis:

```text
x(t) = v_a t
y(t) = R cos(ωt + φ_0)
z(t) = R sin(ωt + φ_0)
```

Vector form:

```text
r(t) = (v_a t, R cos θ, R sin θ)
θ(t) = ωt + φ_0
```

The symbol `φ_0` is initial angular phase. It fixes where the object starts around the axis. It is not energy, force, or torque.

## 2. Velocity and acceleration

Differentiation gives:

```text
v(t) = (v_a, -Rω sin θ, Rω cos θ)
a(t) = (0, -Rω² cos θ, -Rω² sin θ)
```

Scalar quantities:

```text
v_t = R|ω|
|v| = sqrt(v_a² + (Rω)²)
a_r = Rω²
```

Uniform axial motion contributes no axial acceleration. The transverse acceleration points toward the rotation axis.

## 3. Rotation frequency and pitch

```text
f_rot = |ω|/(2π)
T_rot = 2π/|ω|
p = v_a T_rot
b = v_a/ω
```

- `p` is axial advance per temporal turn.
- `b` is reduced signed pitch per radian.
- Reversing `ω` reverses geometric handedness but does not change speed or radial-acceleration magnitude.

## 4. Differential geometry

For a circular helix:

```text
κ = R/(R² + b²)
τ_g = b/(R² + b²)
```

Here `κ` is curvature and `τ_g` is geometric torsion. Geometric torsion is not mechanical torque. The symbols describe different physical dimensions:

```text
geometric torsion τ_g: m⁻¹
mechanical torque τ_m: N m
```

## 5. Force, energy, momentum, and power

For a point mass constrained to the helix:

```text
F_r = mRω²
K_point = 1/2 m[v_a² + (Rω)²]
```

For a rigid rotor translating along its axis:

```text
K_rigid = 1/2 mv_a² + 1/2 Iω²
L_axis = Iω
τ_m = Iα
```

Instantaneous mechanical power is:

```text
P = F_a v_a + τ_m ω
```

A constant angular speed does not imply a non-zero driving torque in an ideal lossless system. Real machines require torque to overcome losses and load.

## 6. Rotation-to-linear conversion

For a screw with lead `p_s`:

```text
dx = p_s/(2π) dφ
v_a = p_s/(2π) ω
```

Work balance gives:

```text
F_a dx = τ_m dφ
```

With forward efficiency `η`:

```text
F_a = 2πητ_m/p_s
τ_m = F_a p_s/(2πη)
P_out = ηP_in
```

A smaller lead gives more ideal force for the same torque, but less axial travel per revolution. Real screws additionally require friction, thread-angle, self-locking, wear, buckling, and material-strength models.

## 7. Two coupled rotors

For the two lobes in the sketch:

```text
L_total = I_1ω_1 + I_2ω_2
K_total = 1/2 I_1ω_1² + 1/2 I_2ω_2²
```

Define a dimensionless reaction-balance ratio:

```text
R_balance = |L_total|/(|I_1ω_1| + |I_2ω_2|)
```

- `R_balance = 0` means perfect angular-momentum cancellation.
- `R_balance = 1` means no cancellation.
- Cancellation of angular momentum does not cancel rotational energy.

A linear torsional spring-damper coupling can be written:

```text
τ_c = -k_φ(φ_1 - φ_2) - c_φ(ω_1 - ω_2)
```

The central symbol `◎` can therefore represent a bearing, shaft, gear, screw, torsional spring, controller, or measurement junction. It must not remain undefined in a numerical model.

## 8. Worked 8 Hz mechanical example

This example interprets 8 Hz strictly as eight mechanical revolutions per second.

Declared inputs:

```text
R = 0.100 m
f_rot = 8.000 Hz
ω = 2πf = 50.2655 rad/s
p = 0.0500 m/turn
m = 1.000 kg
I = 1/2 mR² = 0.00500 kg m²
```

Axial and tangential motion:

```text
v_a = pf = 0.4000 m/s
v_t = Rω = 5.02655 m/s
|v| = 5.04244 m/s
```

Geometry:

```text
b = v_a/ω = 0.00795775 m/rad
κ = 9.93707 m⁻¹
τ_g = 0.790767 m⁻¹
```

Acceleration, force, energy, and momentum:

```text
a_r = Rω² = 252.662 m/s²
F_r = ma_r = 252.662 N
K_translation = 0.0800 J
K_rotation = 6.31655 J
L_axis = Iω = 0.251327 kg m²/s
```

For a screw driven with `τ_m = 1.000 N m` and `η = 0.800`:

```text
F_a = 2πητ_m/p = 100.531 N
P_in = τ_mω = 50.2655 W
P_out = F_av_a = 40.2124 W
P_loss = 10.0531 W
```

The large radial acceleration comes from the declared radius and eight full revolutions per second. It is not evidence that every biological, informational, or electromagnetic 8 Hz process produces the same force.

## 9. Public Python API

```python
from upi import (
    evaluate_coupled_rotors,
    evaluate_helical_motion,
    evaluate_screw_coupling,
    helical_acceleration,
    helical_position,
    helical_velocity,
)

helix = evaluate_helical_motion(
    radius_m=0.1,
    axial_speed_m_s=0.4,
    angular_speed_rad_s=2 * 3.141592653589793 * 8,
    mass_kg=1.0,
    moment_of_inertia_kg_m2=0.005,
)

screw = evaluate_screw_coupling(
    pitch_m_per_turn=0.05,
    angular_speed_rad_s=2 * 3.141592653589793 * 8,
    efficiency=0.8,
    torque_nm=1.0,
)

rotors = evaluate_coupled_rotors(
    moment_of_inertia_1_kg_m2=2.0,
    angular_speed_1_rad_s=3.0,
    moment_of_inertia_2_kg_m2=1.0,
    angular_speed_2_rad_s=-6.0,
)
```

The standalone `vrasi-physics` package exports matching kinematic, screw-coupling, and rotor-balance functions for lightweight simulator use.

## 10. UPI boundary

```text
EST: helix kinematics, curvature, torsion, force, energy, momentum
DER: screw output after a declared efficiency model
SYM: interpreting ◎ as an abstract observer, consciousness node, or universal force center
STOP: any claimed propulsion or energy output without declared momentum and energy exchange
```

The complete indexed record is stored at:

```text
data/mechanics/helical_linear_rotational_coupling.json
```
