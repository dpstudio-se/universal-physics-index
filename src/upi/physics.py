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


def _finite_numeric(value: float | complex, name: str) -> float | complex:
    """Return a finite real or complex number."""
    if isinstance(value, bool) or not isinstance(value, (int, float, complex)):
        raise TypeError(f"{name} must be numeric")
    normalized = complex(value)
    if not math.isfinite(normalized.real) or not math.isfinite(normalized.imag):
        raise ValueError(f"{name} must be finite")
    return value


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
