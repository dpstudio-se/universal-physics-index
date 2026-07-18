"""SI constants with exact NIST values (as of 2019 SI redefinition)."""

from typing import Final

# Planck constant
H: Final[float] = 6.62607015e-34  # J·s

# Speed of light in vacuum
C: Final[float] = 299792458  # m/s (exact by definition)

# Boltzmann constant
K_B: Final[float] = 1.380649e-23  # J/K

# Elementary charge
E: Final[float] = 1.602176634e-19  # C (exact by definition)

# Avogadro constant
N_A: Final[float] = 6.02214076e23  # mol^-1 (exact by definition)

# 8 Hz reference coordinate (derived)
N8_REFERENCE_HZ: Final[float] = 8.0  # Hz
N8_DENOMINATOR: Final[float] = N8_REFERENCE_HZ

# Tolerance for normalized signal matching (unitless)
EPSILON_Z_DEFAULT: Final[float] = 1e-10

# Tolerance for complex signal phase matching (radians)
PHASE_TOLERANCE_DEFAULT: Final[float] = 1e-9

# Tolerance for amplitude matching (unitless)
AMPLITUDE_TOLERANCE_DEFAULT: Final[float] = 1e-10


def validate_constant(value: float, name: str) -> None:
    """Validate that a constant is a valid number.
    
    Raises:
        ValueError: If value is NaN, infinite, or otherwise invalid.
    """
    if value != value:  # NaN check
        raise ValueError(f"{name} is NaN")
    if not (-1e308 < value < 1e308):  # Infinity check (loose bounds)
        raise ValueError(f"{name} is infinite or out of bounds")
    if value == 0:
        raise ValueError(f"{name} is zero")


# Validate all constants on import
validate_constant(H, "Planck constant h")
validate_constant(C, "Speed of light c")
validate_constant(K_B, "Boltzmann constant k_B")
validate_constant(E, "Elementary charge e")
validate_constant(N_A, "Avogadro constant N_A")
