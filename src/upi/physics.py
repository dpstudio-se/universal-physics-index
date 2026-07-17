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


def index8_from_mass(mass_kg: float) -> float:
    """Return N8 = m c^2 / (8 h)."""
    return index8_from_frequency(frequency_from_mass(mass_kg))


def normalize_signal(observed: complex, reference: complex) -> complex:
    """Return Z = observed/reference."""
    if reference == 0:
        raise ZeroDivisionError("reference must not be zero")
    return observed / reference
