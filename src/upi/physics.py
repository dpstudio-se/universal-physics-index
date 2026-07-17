"""Reference physics transformations for UPI."""

from __future__ import annotations

import math
from .constants import C, H, REFERENCE_FREQUENCY_HZ


def _finite_nonnegative(value: float, name: str) -> float:
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    if value < 0:
        raise ValueError(f"{name} must be non-negative")
    return value


def energy_from_frequency(frequency_hz: float) -> float:
    """Return E = h f in joules."""
    return H * _finite_nonnegative(frequency_hz, "frequency_hz")


def mass_from_frequency(frequency_hz: float) -> float:
    """Return m = h f / c^2 in kilograms.

    Here f is defined as invariant rest-mass frequency.
    """
    return energy_from_frequency(frequency_hz) / (C * C)


def frequency_from_mass(mass_kg: float) -> float:
    """Return f = m c^2 / h in hertz."""
    mass = _finite_nonnegative(mass_kg, "mass_kg")
    return mass * C * C / H


def index8_from_frequency(frequency_hz: float) -> float:
    """Return N8 = f / 8 Hz."""
    return _finite_nonnegative(frequency_hz, "frequency_hz") / REFERENCE_FREQUENCY_HZ


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
    """Return N8 = m c^2 / (8 h)."""
    return index8_from_frequency(frequency_from_mass(mass_kg))


def normalize_signal(observed: complex, reference: complex) -> complex:
    """Return Z = observed/reference."""
    if reference == 0:
        raise ZeroDivisionError("reference must not be zero")
    return observed / reference
