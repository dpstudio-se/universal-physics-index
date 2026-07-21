"""Minimal, dependency-free physics calculations required by VR-ASI."""

from dataclasses import dataclass
from math import atan2, cos, hypot, isfinite, pi, sin
from typing import Final

PLANCK_CONSTANT_J_S: Final[float] = 6.62607015e-34
SPEED_OF_LIGHT_M_S: Final[float] = 299_792_458.0
DEFAULT_REFERENCE_FREQUENCY_HZ: Final[float] = 8.0


@dataclass(frozen=True, slots=True)
class FrequencyEvaluation:
    """Auditable result envelope for the simulator preflight."""

    frequency_hz: float
    reference_frequency_hz: float
    energy_j: float
    mass_equivalent_kg: float
    reference_index: float
    model_status: str = "DER"
    interpretation: str = "simulator_coordinate"
    verification_type: str = "software_test"
    claims_experimental_verification: bool = False


@dataclass(frozen=True, slots=True)
class HelicalMotionEvaluation:
    """Uniform helical-motion invariants around the x-axis."""

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
    model_status: str = "EST"
    verification_type: str = "mathematical_check"
    claims_experimental_verification: bool = False


@dataclass(frozen=True, slots=True)
class ScrewCouplingEvaluation:
    """Idealized screw conversion between torque and axial force."""

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
class CoupledRotorEvaluation:
    """Angular-momentum and energy balance for two coaxial rotors."""

    total_angular_momentum_kg_m2_s: float
    total_rotational_energy_j: float
    reaction_balance_ratio: float
    model_status: str = "EST"
    verification_type: str = "mathematical_check"
    claims_experimental_verification: bool = False


def _finite(value: float, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a real number")
    normalized = float(value)
    if not isfinite(normalized):
        raise ValueError(f"{name} must be finite")
    return normalized


def _positive_finite(value: float, name: str) -> float:
    normalized = _finite(value, name)
    if normalized <= 0.0:
        raise ValueError(f"{name} must be finite and greater than zero")
    return normalized


def _nonzero_finite(value: float, name: str) -> float:
    normalized = _finite(value, name)
    if normalized == 0.0:
        raise ValueError(f"{name} must be non-zero")
    return normalized


def energy_from_frequency(frequency_hz: float) -> float:
    """Return photon energy in joules using E = h f."""
    frequency = _positive_finite(frequency_hz, "frequency_hz")
    return PLANCK_CONSTANT_J_S * frequency


def mass_equivalent_from_frequency(frequency_hz: float) -> float:
    """Return the algebraic mass-energy equivalent h f / c² in kilograms."""
    energy_j = energy_from_frequency(frequency_hz)
    return energy_j / (SPEED_OF_LIGHT_M_S**2)


def reference_index(
    frequency_hz: float,
    reference_frequency_hz: float = DEFAULT_REFERENCE_FREQUENCY_HZ,
) -> float:
    """Normalize a frequency against an explicit positive reference."""
    frequency = _positive_finite(frequency_hz, "frequency_hz")
    reference = _positive_finite(reference_frequency_hz, "reference_frequency_hz")
    return frequency / reference


def evaluate_frequency(
    frequency_hz: float,
    reference_frequency_hz: float = DEFAULT_REFERENCE_FREQUENCY_HZ,
) -> FrequencyEvaluation:
    """Calculate exactly the values consumed by the VR-ASI simulator."""
    frequency = _positive_finite(frequency_hz, "frequency_hz")
    reference = _positive_finite(reference_frequency_hz, "reference_frequency_hz")
    return FrequencyEvaluation(
        frequency_hz=frequency,
        reference_frequency_hz=reference,
        energy_j=energy_from_frequency(frequency),
        mass_equivalent_kg=mass_equivalent_from_frequency(frequency),
        reference_index=reference_index(frequency, reference),
    )


def helical_position(
    time_s: float,
    radius_m: float,
    axial_speed_m_s: float,
    angular_speed_rad_s: float,
    phase_rad: float = 0.0,
) -> tuple[float, float, float]:
    """Return r(t) = (v_a t, R cos(theta), R sin(theta)) in metres."""
    time = _finite(time_s, "time_s")
    radius = _positive_finite(radius_m, "radius_m")
    axial_speed = _finite(axial_speed_m_s, "axial_speed_m_s")
    angular_speed = _nonzero_finite(angular_speed_rad_s, "angular_speed_rad_s")
    phase = _finite(phase_rad, "phase_rad")
    theta = angular_speed * time + phase
    return axial_speed * time, radius * cos(theta), radius * sin(theta)


def evaluate_helical_motion(
    radius_m: float,
    axial_speed_m_s: float,
    angular_speed_rad_s: float,
) -> HelicalMotionEvaluation:
    """Evaluate uniform helical kinematics and differential geometry."""
    radius = _positive_finite(radius_m, "radius_m")
    axial_speed = _finite(axial_speed_m_s, "axial_speed_m_s")
    angular_speed = _nonzero_finite(angular_speed_rad_s, "angular_speed_rad_s")
    angular_speed_abs = abs(angular_speed)
    tangential_speed = radius * angular_speed_abs
    total_speed = hypot(axial_speed, tangential_speed)
    turns_per_second = angular_speed_abs / (2.0 * pi)
    period = 1.0 / turns_per_second
    pitch_per_turn = axial_speed * period
    reduced_pitch = axial_speed / angular_speed
    denominator = radius**2 + reduced_pitch**2
    helicity_sign = 1 if reduced_pitch > 0 else -1 if reduced_pitch < 0 else 0
    return HelicalMotionEvaluation(
        radius_m=radius,
        axial_speed_m_s=axial_speed,
        angular_speed_rad_s=angular_speed,
        tangential_speed_m_s=tangential_speed,
        total_speed_m_s=total_speed,
        turns_per_second_hz=turns_per_second,
        period_s=period,
        pitch_per_turn_m=pitch_per_turn,
        reduced_pitch_m_per_rad=reduced_pitch,
        path_angle_to_axis_rad=atan2(tangential_speed, abs(axial_speed)),
        curvature_per_m=radius / denominator,
        torsion_per_m=reduced_pitch / denominator,
        radial_acceleration_m_s2=radius * angular_speed**2,
        helicity_sign=helicity_sign,
    )


def evaluate_screw_coupling(
    pitch_m_per_turn: float,
    angular_speed_rad_s: float,
    *,
    efficiency: float = 1.0,
    torque_nm: float | None = None,
    axial_force_n: float | None = None,
) -> ScrewCouplingEvaluation:
    """Convert torque and rotation into axial speed and force."""
    pitch = _positive_finite(pitch_m_per_turn, "pitch_m_per_turn")
    angular_speed = _nonzero_finite(angular_speed_rad_s, "angular_speed_rad_s")
    eta = _positive_finite(efficiency, "efficiency")
    if eta > 1.0:
        raise ValueError("efficiency must not exceed one")
    if (torque_nm is None) == (axial_force_n is None):
        raise ValueError("supply exactly one of torque_nm or axial_force_n")

    axial_speed = pitch * angular_speed / (2.0 * pi)
    if torque_nm is not None:
        torque = _finite(torque_nm, "torque_nm")
        axial_force = 2.0 * pi * eta * torque / pitch
    else:
        axial_force = _finite(float(axial_force_n), "axial_force_n")
        torque = axial_force * pitch / (2.0 * pi * eta)
    input_power = torque * angular_speed
    output_power = axial_force * axial_speed
    return ScrewCouplingEvaluation(
        pitch_m_per_turn=pitch,
        angular_speed_rad_s=angular_speed,
        efficiency=eta,
        axial_speed_m_s=axial_speed,
        torque_nm=torque,
        axial_force_n=axial_force,
        input_power_w=input_power,
        output_power_w=output_power,
        dissipated_power_w=input_power - output_power,
    )


def evaluate_coupled_rotors(
    moment_of_inertia_1_kg_m2: float,
    angular_speed_1_rad_s: float,
    moment_of_inertia_2_kg_m2: float,
    angular_speed_2_rad_s: float,
) -> CoupledRotorEvaluation:
    """Return total angular momentum, energy, and cancellation ratio."""
    inertia_1 = _positive_finite(moment_of_inertia_1_kg_m2, "moment_of_inertia_1_kg_m2")
    inertia_2 = _positive_finite(moment_of_inertia_2_kg_m2, "moment_of_inertia_2_kg_m2")
    angular_speed_1 = _finite(angular_speed_1_rad_s, "angular_speed_1_rad_s")
    angular_speed_2 = _finite(angular_speed_2_rad_s, "angular_speed_2_rad_s")
    angular_momentum_1 = inertia_1 * angular_speed_1
    angular_momentum_2 = inertia_2 * angular_speed_2
    total_angular_momentum = angular_momentum_1 + angular_momentum_2
    energy_1 = 0.5 * inertia_1 * angular_speed_1**2
    energy_2 = 0.5 * inertia_2 * angular_speed_2**2
    momentum_scale = abs(angular_momentum_1) + abs(angular_momentum_2)
    balance_ratio = 0.0 if momentum_scale == 0.0 else abs(total_angular_momentum) / momentum_scale
    return CoupledRotorEvaluation(
        total_angular_momentum_kg_m2_s=total_angular_momentum,
        total_rotational_energy_j=energy_1 + energy_2,
        reaction_balance_ratio=balance_ratio,
    )
