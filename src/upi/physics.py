"""Physics functions implementing core UPI equations."""

import math
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


def _finite_nonnegative(value: float, name: str) -> float:
    """Return a finite non-negative value or raise a stable input error."""
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    if value < 0:
        raise ValueError(f"{name} must be non-negative")
    return value


def energy_from_frequency(frequency_hz: float) -> float:
    """Calculate energy from frequency using E = h*f.

    Args:
        frequency_hz: Frequency in Hertz

    Returns:
        Energy in Joules

    Raises:
        ValueError: If frequency is invalid (NaN, zero, negative, infinity)
    """
    if frequency_hz != frequency_hz:  # NaN
        raise ValueError("Frequency is NaN")
    if frequency_hz <= 0:
        raise ValueError(f"Frequency must be positive, got {frequency_hz}")
    if not (-1e308 < frequency_hz < 1e308):
        raise ValueError(f"Frequency is infinite or out of bounds: {frequency_hz}")
    return H * frequency_hz


def mass_from_frequency(frequency_hz: float) -> float:
    """Calculate rest mass from frequency using m = h*f / c^2.

    Args:
        frequency_hz: Frequency in Hertz

    Returns:
        Rest mass in kilograms

    Raises:
        ValueError: If frequency is invalid
    """
    if frequency_hz != frequency_hz:  # NaN
        raise ValueError("Frequency is NaN")
    if frequency_hz <= 0:
        raise ValueError(f"Frequency must be positive, got {frequency_hz}")
    if not (-1e308 < frequency_hz < 1e308):
        raise ValueError(f"Frequency is infinite or out of bounds: {frequency_hz}")
    return (H * frequency_hz) / (C ** 2)


def frequency_from_mass(mass_kg: float) -> float:
    """Calculate rest-mass frequency from mass using f = m*c^2 / h.

    Args:
        mass_kg: Rest mass in kilograms

    Returns:
        Rest-mass frequency in Hertz

    Raises:
        ValueError: If mass is invalid
    """
    if mass_kg != mass_kg:  # NaN
        raise ValueError("Mass is NaN")
    if mass_kg <= 0:
        raise ValueError(f"Mass must be positive, got {mass_kg}")
    if not (-1e308 < mass_kg < 1e308):
        raise ValueError(f"Mass is infinite or out of bounds: {mass_kg}")
    return (mass_kg * C ** 2) / H


def index8_from_frequency(frequency_hz: float) -> float:
    """Calculate 8 Hz dimensionless index N8 = f / (8 Hz).

    Args:
        frequency_hz: Frequency in Hertz

    Returns:
        Dimensionless index N8

    Raises:
        ValueError: If frequency is invalid
    """
    if frequency_hz != frequency_hz:  # NaN
        raise ValueError("Frequency is NaN")
    if frequency_hz < 0:
        raise ValueError(f"Frequency cannot be negative, got {frequency_hz}")
    if not (-1e308 < frequency_hz < 1e308):
        raise ValueError(f"Frequency is infinite or out of bounds: {frequency_hz}")
    return frequency_hz / N8_DENOMINATOR


def normalize_value(value: float, reference: float) -> float:
    """Return Z = value/reference for finite values and a non-zero reference."""
    finite_value = _finite_nonnegative(value, "value")
    finite_reference = _finite_nonnegative(reference, "reference")
    if finite_reference == 0:
        raise ZeroDivisionError("reference must not be zero")
    return finite_value / finite_reference


def normalized_match(value: float, reference: float, tolerance: float = 1e-9) -> bool:
    """Compare a normalized value with one; this is not evidence of physical identity."""
    if tolerance < 0 or not math.isfinite(tolerance):
        raise ValueError("tolerance must be finite and non-negative")
    return abs(normalize_value(value, reference) - 1.0) <= tolerance


def propagated_mass_uncertainty(frequency_uncertainty_hz: float) -> float:
    """Propagate frequency standard uncertainty through m = h f / c².

    In SI, h and c are exact; this function assumes frequency is the only uncertain input.
    """
    return mass_from_frequency(frequency_uncertainty_hz)


def index8_from_mass(mass_kg: float) -> float:
    """Calculate 8 Hz dimensionless index N8 = m*c^2 / (8*h).

    Args:
        mass_kg: Rest mass in kilograms

    Returns:
        Dimensionless index N8

    Raises:
        ValueError: If mass is invalid
    """
    if mass_kg != mass_kg:  # NaN
        raise ValueError("Mass is NaN")
    if mass_kg < 0:
        raise ValueError(f"Mass cannot be negative, got {mass_kg}")
    if not (-1e308 < mass_kg < 1e308):
        raise ValueError(f"Mass is infinite or out of bounds: {mass_kg}")
    return (mass_kg * C ** 2) / (N8_DENOMINATOR * H)


def relativistic_total_frequency(
    momentum_wavelength_m: float,
    rest_mass_frequency_hz: float
) -> float:
    """Calculate total temporal frequency using nu^2 = (c/lambda)^2 + f^2.

    Args:
        momentum_wavelength_m: Momentum wavelength (de Broglie wavelength) in meters
        rest_mass_frequency_hz: Invariant rest-mass frequency in Hertz

    Returns:
        Total temporal frequency in Hertz

    Raises:
        ValueError: If inputs are invalid
    """
    if momentum_wavelength_m != momentum_wavelength_m:  # NaN
        raise ValueError("Wavelength is NaN")
    if rest_mass_frequency_hz != rest_mass_frequency_hz:  # NaN
        raise ValueError("Frequency is NaN")
    if momentum_wavelength_m <= 0:
        raise ValueError(f"Wavelength must be positive, got {momentum_wavelength_m}")
    if rest_mass_frequency_hz < 0:
        raise ValueError(f"Frequency cannot be negative, got {rest_mass_frequency_hz}")

    c_over_lambda = C / momentum_wavelength_m
    sum_of_squares = (c_over_lambda ** 2) + (rest_mass_frequency_hz ** 2)
    return math.sqrt(sum_of_squares)


class ZeroReferenceError(ZeroDivisionError, ValueError):
    """A zero normalization reference, compatible with legacy callers."""


def normalize_signal(
    observed: float | complex, reference: float | complex
) -> float | complex:
    """Normalize signal Z(t,x) = z(t,x) / z_ref(t,x).

    Args:
        observed: Observed signal value
        reference: Reference signal value

    Returns:
        Normalized signal Z

    Raises:
        ValueError: If reference is zero, NaN, or infinity
    """
    if reference != reference:  # NaN
        raise ValueError("Reference is NaN")
    if reference == 0:
        raise ZeroReferenceError("Reference signal cannot be zero")
    if abs(reference) >= 1e308:
        raise ValueError(f"Reference is infinite or out of bounds: {reference}")
    if observed != observed:  # NaN
        raise ValueError("Observed signal is NaN")

    return observed / reference


def signal_match(
    observed: float,
    reference: float,
    epsilon: float = EPSILON_Z_DEFAULT
) -> RuntimeMatchResult:
    """Check if normalized signal matches reference within tolerance.

    Implements: abs(Z - 1) <= epsilon where Z = z / z_ref

    Args:
        observed: Observed signal value
        reference: Reference signal value
        epsilon: Tolerance for match (unitless)

    Returns:
        RuntimeMatchResult with match outcome
    """
    normalized = cast(float, normalize_signal(observed, reference))
    error = abs(normalized - 1.0)
    matches = error <= epsilon

    return RuntimeMatchResult(
        normalized_value=normalized,
        observed=observed,
        reference=reference,
        epsilon=epsilon,
        matches=matches,
        error=error
    )


def complex_signal_match(
    observed_amplitude: float,
    observed_phase: float,
    reference_amplitude: float,
    reference_phase: float,
    amplitude_tolerance: float = AMPLITUDE_TOLERANCE_DEFAULT,
    phase_tolerance: float = PHASE_TOLERANCE_DEFAULT
) -> RuntimeMatchResult:
    """Check if complex signal (amplitude, phase) matches reference.

    Args:
        observed_amplitude: Magnitude of observed signal
        observed_phase: Phase of observed signal (radians)
        reference_amplitude: Magnitude of reference signal
        reference_phase: Phase of reference signal (radians)
        amplitude_tolerance: Amplitude tolerance (unitless)
        phase_tolerance: Phase tolerance (radians)

    Returns:
        RuntimeMatchResult with match outcome

    Raises:
        ValueError: If amplitudes are invalid
    """
    if reference_amplitude == 0:
        raise ValueError("Reference amplitude cannot be zero")
    if observed_amplitude != observed_amplitude or reference_amplitude != reference_amplitude:
        raise ValueError("Amplitude is NaN")

    # Normalize amplitude
    normalized_amplitude = observed_amplitude / reference_amplitude
    amplitude_error = abs(normalized_amplitude - 1.0)
    amplitude_matches = amplitude_error <= amplitude_tolerance

    # Phase difference (wrap to [-pi, pi])
    phase_diff = observed_phase - reference_phase
    phase_diff = (phase_diff + math.pi) % (2 * math.pi) - math.pi
    phase_matches = abs(phase_diff) <= phase_tolerance

    matches = amplitude_matches and phase_matches

    return RuntimeMatchResult(
        normalized_value=normalized_amplitude,
        observed=observed_amplitude,
        reference=reference_amplitude,
        epsilon=amplitude_tolerance,
        matches=matches,
        error=amplitude_error,
        notes=f"Phase diff: {phase_diff:.6e} rad (tolerance: {phase_tolerance:.6e})"
    )
