"""Minimal, dependency-free physics calculations required by VR-ASI."""

from dataclasses import dataclass
from math import isfinite
from typing import Final

PLANCK_CONSTANT_J_S: Final[float] = 6.62607015e-34
SPEED_OF_LIGHT_M_S: Final[float] = 299_792_458.0
DEFAULT_REFERENCE_FREQUENCY_HZ: Final[float] = 8.0


def _positive_finite(value: float, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a real number")
    normalized = float(value)
    if not isfinite(normalized) or normalized <= 0.0:
        raise ValueError(f"{name} must be finite and greater than zero")
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
