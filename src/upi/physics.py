"""Physics functions implementing core UPI equations."""

import math
from dataclasses import dataclass
from typing import cast

from .constants import (
    AMPLITUDE_TOLERANCE_DEFAULT,
    EPSILON_Z_DEFAULT,
    N8_DENOMINATOR,
    PHASE_TOLERANCE_DEFAULT,
    C,
    H,
)
from .models import RuntimeMatchResult


@dataclass(frozen=True, slots=True)
class HelicalMotionResult:
    """Scalar invariants for uniform helical motion around the x-axis."""

    radius_m: float
    axial_speed_m_s: float
    angular_speed_rad_s: float
    tangential_speed_m_s: float
    total_speed_m_s: float
    turns_per_second_hz: float
    period_s: float
    pitch_per_turn_m: float
    reduced_pitch_m_per_rad: float
    path_angle_to_axis_rad: float
    curvature_per_m: float
    torsion_per_m: float
    radial_acceleration_m_s2: float
    helicity_sign: int
    centripetal_force_n: float | None = None
    point_kinetic_energy_j: float | None = None
    rotor_kinetic_energy_j: float | None = None
    angular_momentum_kg_m2_s: float | None = None
    axial_power_w: float | None = None
    rotational_power_w: float | None = None
    total_power_w: float | None = None
    model_status: str = "EST"
    verification_type: str = "mathematical_check"
    claims_experimental_verification: bool = False


@dataclass(frozen=True, slots=True)
class ScrewCouplingResult:
    """Idealized linear-rotational conversion through a screw pitch."""

    pitch_m_per_turn: float
    angular_speed_rad_s: float
    efficiency: float
    axial_speed_m_s: float
    torque_nm: float
    axial_force_n: float
    input_power_w: float
    output_power_w: float
    dissipated_power_w: float
    model_status: str = "DER"
    verification_type: str = "mathematical_check"
    claims_experimental_verification: bool = False


@dataclass(frozen=True, slots=True)
class CoupledRotorResult:
    """Angular-momentum and energy balance for two coaxial rotors."""

    angular_momentum_1_kg_m2_s: float
    angular_momentum_2_kg_m2_s: float
    total_angular_momentum_kg_m2_s: float
    rotational_energy_1_j: float
    rotational_energy_2_j: float
    total_rotational_energy_j: float
    reaction_balance_ratio: float
    model_status: str = "EST"
    verification_type: str = "mathematical_check"
    claims_experimental_verification: bool = False


def _finite_real(value: float, name: str) -> float:
    """Return a finite real number while rejecting booleans and non-numeric input."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a real number")
    normalized = float(value)
    if not math.isfinite(normalized):
        raise ValueError(f"{name} must be finite")
    return normalized


def _finite_nonnegative(value: float, name: str) -> float:
    """Return a finite non-negative real number."""
    normalized = _finite_real(value, name)
    if normalized < 0:
        raise ValueError(f"{name} must be non-negative")
    return normalized


def _finite_positive(value: float, name: str) -> float:
    """Return a finite positive real number."""
    normalized = _finite_real(value, name)
    if normalized <= 0:
        raise ValueError(f"{name} must be positive")
    return normalized


def _finite_nonzero(value: float, name: str) -> float:
    """Return a finite non-zero real number."""
    normalized = _finite_real(value, name)
    if normalized == 0:
        raise ValueError(f"{name} must be non-zero")
    return normalized


def _finite_numeric(value: float | complex, name: str) -> float | complex:
    """Return a finite real or complex number."""
    if isinstance(value, bool) or not isinstance(value, (int, float, complex)):
        raise TypeError(f"{name} must be numeric")
    normalized = complex(value)
    if not math.isfinite(normalized.real) or not math.isfinite(normalized.imag):
        raise ValueError(f"{name} must be finite")
    return value


def _optional_finite(value: float | None, name: str) -> float | None:
    return None if value is None else _finite_real(value, name)


def _optional_positive(value: float | None, name: str) -> float | None:
    return None if value is None else _finite_positive(value, name)


def energy_from_frequency(frequency_hz: float) -> float:
    """Calculate energy from frequency using E = h*f."""
    frequency = _finite_positive(frequency_hz, "Frequency")
    return H * frequency


def mass_from_frequency(frequency_hz: float) -> float:
    """Calculate the mass-energy equivalent m = h*f/c^2 for a declared frequency."""
    frequency = _finite_positive(frequency_hz, "Frequency")
    return (H * frequency) / (C**2)


def frequency_from_mass(mass_kg: float) -> float:
    """Calculate invariant rest-mass frequency using f = m*c^2/h."""
    mass = _finite_positive(mass_kg, "Mass")
    return (mass * C**2) / H


def index8_from_frequency(frequency_hz: float) -> float:
    """Calculate the dimensionless reference index N8 = f/(8 Hz)."""
    frequency = _finite_nonnegative(frequency_hz, "Frequency")
    return frequency / N8_DENOMINATOR


def normalize_value(value: float, reference: float) -> float:
    """Return Z = value/reference for finite signed values and a non-zero reference."""
    finite_value = _finite_real(value, "value")
    finite_reference = _finite_real(reference, "reference")
    if finite_reference == 0:
        raise ZeroDivisionError("reference must not be zero")
    return finite_value / finite_reference


def normalized_match(value: float, reference: float, tolerance: float = 1e-9) -> bool:
    """Compare a normalized value with one; this is not evidence of physical identity."""
    finite_tolerance = _finite_nonnegative(tolerance, "tolerance")
    return abs(normalize_value(value, reference) - 1.0) <= finite_tolerance


def propagated_mass_uncertainty(frequency_uncertainty_hz: float) -> float:
    """Propagate frequency standard uncertainty through m = h*f/c^2.

    In SI, h and c are exact; this function assumes frequency is the only uncertain input.
    A zero uncertainty is valid and maps to zero mass uncertainty.
    """
    uncertainty = _finite_nonnegative(
        frequency_uncertainty_hz,
        "frequency_uncertainty_hz",
    )
    return (H * uncertainty) / (C**2)


def index8_from_mass(mass_kg: float) -> float:
    """Calculate the dimensionless reference index N8 = m*c^2/(8*h)."""
    mass = _finite_nonnegative(mass_kg, "Mass")
    return (mass * C**2) / (N8_DENOMINATOR * H)


def relativistic_total_frequency(
    momentum_wavelength_m: float,
    rest_mass_frequency_hz: float,
) -> float:
    """Calculate total temporal frequency using nu^2 = (c/lambda)^2 + f^2."""
    wavelength = _finite_positive(momentum_wavelength_m, "Wavelength")
    rest_frequency = _finite_nonnegative(rest_mass_frequency_hz, "Frequency")
    return math.hypot(C / wavelength, rest_frequency)


def helical_position(
    time_s: float,
    radius_m: float,
    axial_speed_m_s: float,
    angular_speed_rad_s: float,
    phase_rad: float = 0.0,
) -> tuple[float, float, float]:
    """Return r(t) = (v_a t, R cos(theta), R sin(theta)) in metres."""
    time = _finite_real(time_s, "time_s")
    radius = _finite_positive(radius_m, "radius_m")
    axial_speed = _finite_real(axial_speed_m_s, "axial_speed_m_s")
    angular_speed = _finite_nonzero(angular_speed_rad_s, "angular_speed_rad_s")
    phase = _finite_real(phase_rad, "phase_rad")
    theta = angular_speed * time + phase
    return axial_speed * time, radius * math.cos(theta), radius * math.sin(theta)


def helical_velocity(
    time_s: float,
    radius_m: float,
    axial_speed_m_s: float,
    angular_speed_rad_s: float,
    phase_rad: float = 0.0,
) -> tuple[float, float, float]:
    """Return the velocity vector for uniform helical motion in m/s."""
    time = _finite_real(time_s, "time_s")
    radius = _finite_positive(radius_m, "radius_m")
    axial_speed = _finite_real(axial_speed_m_s, "axial_speed_m_s")
    angular_speed = _finite_nonzero(angular_speed_rad_s, "angular_speed_rad_s")
    phase = _finite_real(phase_rad, "phase_rad")
    theta = angular_speed * time + phase
    return (
        axial_speed,
        -radius * angular_speed * math.sin(theta),
        radius * angular_speed * math.cos(theta),
    )


def helical_acceleration(
    time_s: float,
    radius_m: float,
    angular_speed_rad_s: float,
    phase_rad: float = 0.0,
) -> tuple[float, float, float]:
    """Return the centripetal acceleration vector for uniform helical motion in m/s^2."""
    time = _finite_real(time_s, "time_s")
    radius = _finite_positive(radius_m, "radius_m")
    angular_speed = _finite_nonzero(angular_speed_rad_s, "angular_speed_rad_s")
    phase = _finite_real(phase_rad, "phase_rad")
    theta = angular_speed * time + phase
    radial_acceleration = radius * angular_speed**2
    return 0.0, -radial_acceleration * math.cos(theta), -radial_acceleration * math.sin(theta)


def evaluate_helical_motion(
    radius_m: float,
    axial_speed_m_s: float,
    angular_speed_rad_s: float,
    *,
    mass_kg: float | None = None,
    moment_of_inertia_kg_m2: float | None = None,
    axial_force_n: float | None = None,
    torque_nm: float | None = None,
) -> HelicalMotionResult:
    """Evaluate uniform helical kinematics, geometry, forces, energies, and power.

    The axis is x. Angular speed follows the right-hand rule around +x. A non-zero
    angular speed is required; omega = 0 is linear motion rather than a helix.
    """
    radius = _finite_positive(radius_m, "radius_m")
    axial_speed = _finite_real(axial_speed_m_s, "axial_speed_m_s")
    angular_speed = _finite_nonzero(angular_speed_rad_s, "angular_speed_rad_s")
    mass = _optional_positive(mass_kg, "mass_kg")
    inertia = _optional_positive(moment_of_inertia_kg_m2, "moment_of_inertia_kg_m2")
    axial_force = _optional_finite(axial_force_n, "axial_force_n")
    torque = _optional_finite(torque_nm, "torque_nm")

    angular_speed_abs = abs(angular_speed)
    tangential_speed = radius * angular_speed_abs
    total_speed = math.hypot(axial_speed, tangential_speed)
    turns_per_second = angular_speed_abs / (2.0 * math.pi)
    period = 1.0 / turns_per_second
    pitch_per_turn = axial_speed * period
    reduced_pitch = axial_speed / angular_speed
    denominator = radius**2 + reduced_pitch**2
    curvature = radius / denominator
    torsion = reduced_pitch / denominator
    path_angle = math.atan2(tangential_speed, abs(axial_speed))
    radial_acceleration = radius * angular_speed**2
    helicity_sign = 1 if reduced_pitch > 0 else -1 if reduced_pitch < 0 else 0

    centripetal_force = None if mass is None else mass * radial_acceleration
    point_energy = None if mass is None else 0.5 * mass * total_speed**2
    rotor_energy = None if inertia is None else 0.5 * inertia * angular_speed**2
    angular_momentum = None if inertia is None else inertia * angular_speed
    axial_power = None if axial_force is None else axial_force * axial_speed
    rotational_power = None if torque is None else torque * angular_speed
    total_power = (
        None
        if axial_power is None or rotational_power is None
        else axial_power + rotational_power
    )

    return HelicalMotionResult(
        radius_m=radius,
        axial_speed_m_s=axial_speed,
        angular_speed_rad_s=angular_speed,
        tangential_speed_m_s=tangential_speed,
        total_speed_m_s=total_speed,
        turns_per_second_hz=turns_per_second,
        period_s=period,
        pitch_per_turn_m=pitch_per_turn,
        reduced_pitch_m_per_rad=reduced_pitch,
        path_angle_to_axis_rad=path_angle,
        curvature_per_m=curvature,
        torsion_per_m=torsion,
        radial_acceleration_m_s2=radial_acceleration,
        helicity_sign=helicity_sign,
        centripetal_force_n=centripetal_force,
        point_kinetic_energy_j=point_energy,
        rotor_kinetic_energy_j=rotor_energy,
        angular_momentum_kg_m2_s=angular_momentum,
        axial_power_w=axial_power,
        rotational_power_w=rotational_power,
        total_power_w=total_power,
    )


def evaluate_screw_coupling(
    pitch_m_per_turn: float,
    angular_speed_rad_s: float,
    *,
    efficiency: float = 1.0,
    torque_nm: float | None = None,
    axial_force_n: float | None = None,
) -> ScrewCouplingResult:
    """Convert rotation to translation using work and power conservation.

    Exactly one of torque_nm and axial_force_n must be supplied. Efficiency is the
    forward mechanical efficiency, 0 < eta <= 1. Static friction, backlash, lead
    angle limits, buckling, and material failure are outside this idealized model.
    """
    pitch = _finite_positive(pitch_m_per_turn, "pitch_m_per_turn")
    angular_speed = _finite_nonzero(angular_speed_rad_s, "angular_speed_rad_s")
    eta = _finite_positive(efficiency, "efficiency")
    if eta > 1.0:
        raise ValueError("efficiency must not exceed one")
    if (torque_nm is None) == (axial_force_n is None):
        raise ValueError("supply exactly one of torque_nm or axial_force_n")

    axial_speed = pitch * angular_speed / (2.0 * math.pi)
    if torque_nm is not None:
        torque = _finite_real(torque_nm, "torque_nm")
        axial_force = 2.0 * math.pi * eta * torque / pitch
        input_power = torque * angular_speed
        output_power = axial_force * axial_speed
    else:
        axial_force = _finite_real(cast(float, axial_force_n), "axial_force_n")
        torque = axial_force * pitch / (2.0 * math.pi * eta)
        output_power = axial_force * axial_speed
        input_power = torque * angular_speed
    dissipated_power = input_power - output_power

    return ScrewCouplingResult(
        pitch_m_per_turn=pitch,
        angular_speed_rad_s=angular_speed,
        efficiency=eta,
        axial_speed_m_s=axial_speed,
        torque_nm=torque,
        axial_force_n=axial_force,
        input_power_w=input_power,
        output_power_w=output_power,
        dissipated_power_w=dissipated_power,
    )


def evaluate_coupled_rotors(
    moment_of_inertia_1_kg_m2: float,
    angular_speed_1_rad_s: float,
    moment_of_inertia_2_kg_m2: float,
    angular_speed_2_rad_s: float,
) -> CoupledRotorResult:
    """Evaluate angular-momentum cancellation and stored energy for two rotors."""
    inertia_1 = _finite_positive(moment_of_inertia_1_kg_m2, "moment_of_inertia_1_kg_m2")
    inertia_2 = _finite_positive(moment_of_inertia_2_kg_m2, "moment_of_inertia_2_kg_m2")
    angular_speed_1 = _finite_real(angular_speed_1_rad_s, "angular_speed_1_rad_s")
    angular_speed_2 = _finite_real(angular_speed_2_rad_s, "angular_speed_2_rad_s")

    angular_momentum_1 = inertia_1 * angular_speed_1
    angular_momentum_2 = inertia_2 * angular_speed_2
    total_angular_momentum = angular_momentum_1 + angular_momentum_2
    energy_1 = 0.5 * inertia_1 * angular_speed_1**2
    energy_2 = 0.5 * inertia_2 * angular_speed_2**2
    momentum_scale = abs(angular_momentum_1) + abs(angular_momentum_2)
    balance_ratio = 0.0 if momentum_scale == 0.0 else abs(total_angular_momentum) / momentum_scale

    return CoupledRotorResult(
        angular_momentum_1_kg_m2_s=angular_momentum_1,
        angular_momentum_2_kg_m2_s=angular_momentum_2,
        total_angular_momentum_kg_m2_s=total_angular_momentum,
        rotational_energy_1_j=energy_1,
        rotational_energy_2_j=energy_2,
        total_rotational_energy_j=energy_1 + energy_2,
        reaction_balance_ratio=balance_ratio,
    )


class ZeroReferenceError(ZeroDivisionError, ValueError):
    """A zero normalization reference, compatible with legacy callers."""


def normalize_signal(
    observed: float | complex,
    reference: float | complex,
) -> float | complex:
    """Normalize signal Z(t,x) = z(t,x)/z_ref(t,x)."""
    if reference != reference:
        raise ValueError("Reference is NaN")
    if observed != observed:
        raise ValueError("Observed signal is NaN")
    _finite_numeric(reference, "Reference")
    _finite_numeric(observed, "Observed")
    if reference == 0:
        raise ZeroReferenceError("Reference signal cannot be zero")
    return observed / reference


def signal_match(
    observed: float,
    reference: float,
    epsilon: float = EPSILON_Z_DEFAULT,
) -> RuntimeMatchResult:
    """Check whether abs(observed/reference - 1) is within epsilon."""
    finite_epsilon = _finite_nonnegative(epsilon, "epsilon")
    normalized = cast(float, normalize_signal(observed, reference))
    error = abs(normalized - 1.0)
    matches = error <= finite_epsilon

    return RuntimeMatchResult(
        normalized_value=normalized,
        observed=observed,
        reference=reference,
        epsilon=finite_epsilon,
        matches=matches,
        error=error,
    )


def complex_signal_match(
    observed_amplitude: float,
    observed_phase: float,
    reference_amplitude: float,
    reference_phase: float,
    amplitude_tolerance: float = AMPLITUDE_TOLERANCE_DEFAULT,
    phase_tolerance: float = PHASE_TOLERANCE_DEFAULT,
) -> RuntimeMatchResult:
    """Check a complex signal represented by amplitude and phase."""
    if reference_amplitude == 0:
        raise ValueError("Reference amplitude cannot be zero")
    observed_amp = _finite_nonnegative(observed_amplitude, "observed_amplitude")
    reference_amp = _finite_positive(reference_amplitude, "reference_amplitude")
    observed_phi = _finite_real(observed_phase, "observed_phase")
    reference_phi = _finite_real(reference_phase, "reference_phase")
    amplitude_eps = _finite_nonnegative(amplitude_tolerance, "amplitude_tolerance")
    phase_eps = _finite_nonnegative(phase_tolerance, "phase_tolerance")

    normalized_amplitude = observed_amp / reference_amp
    amplitude_error = abs(normalized_amplitude - 1.0)
    amplitude_matches = amplitude_error <= amplitude_eps

    phase_diff = observed_phi - reference_phi
    phase_diff = (phase_diff + math.pi) % (2 * math.pi) - math.pi
    phase_matches = abs(phase_diff) <= phase_eps

    return RuntimeMatchResult(
        normalized_value=normalized_amplitude,
        observed=observed_amp,
        reference=reference_amp,
        epsilon=amplitude_eps,
        matches=amplitude_matches and phase_matches,
        error=amplitude_error,
        notes=f"Phase diff: {phase_diff:.6e} rad (tolerance: {phase_eps:.6e})",
    )
