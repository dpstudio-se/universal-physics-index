"""Universal Physics Index reference package."""

from .constants import C, H, K_B, REFERENCE_FREQUENCY_HZ
from .models import InformationLayer, VerificationType
from .physics import (
    energy_from_frequency,
    mass_from_frequency,
    frequency_from_mass,
    index8_from_frequency,
    index8_from_mass,
    normalize_signal,
    normalize_value,
    normalized_match,
    propagated_mass_uncertainty,
)

__all__ = [
    "C", "H", "K_B", "REFERENCE_FREQUENCY_HZ",
    "energy_from_frequency", "mass_from_frequency",
    "frequency_from_mass", "index8_from_frequency",
    "index8_from_mass", "normalize_signal",
    "normalize_value", "normalized_match", "propagated_mass_uncertainty",
    "InformationLayer", "VerificationType",
]
