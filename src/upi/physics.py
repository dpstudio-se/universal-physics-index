"""Physics functions implementing core UPI equations."""

import math
from typing import Tuple

from .constants import H, C, K_B, E, N_A, N8_REFERENCE_HZ, N8_DENOMINATOR
from .constants import EPSILON_Z_DEFAULT, AMPLITUDE_TOLERANCE_DEFAULT, PHASE_TOLERANCE_DEFAULT
from .models import RuntimeMatchResult


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


def normalize_signal(observed: float, reference: float) -> float:
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
        raise ValueError("Reference signal cannot be zero")
    if not (-1e308 < reference < 1e308):
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
    normalized = normalize_signal(observed, reference)
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
