"""Universal Physics Index reference package."""

from .constants import C, H, K_B, REFERENCE_FREQUENCY_HZ
from .physics import (
    energy_from_frequency,
    mass_from_frequency,
    frequency_from_mass,
    index8_from_frequency,
    index8_from_mass,
    normalize_signal,
)

__all__ = [
    "C", "H", "K_B", "REFERENCE_FREQUENCY_HZ",
    "energy_from_frequency", "mass_from_frequency",
    "frequency_from_mass", "index8_from_frequency",
    "index8_from_mass", "normalize_signal",
]
