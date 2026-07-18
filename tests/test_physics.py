import pytest
from upi.physics import (
    energy_from_frequency,
    frequency_from_mass,
    index8_from_frequency,
    mass_from_frequency,
    normalize_signal,
)


def test_eight_hz_reference() -> None:
    assert energy_from_frequency(8.0) == pytest.approx(5.30085612e-33)
    assert mass_from_frequency(8.0) == pytest.approx(5.897997859e-50)
    assert index8_from_frequency(8.0) == pytest.approx(1.0)


def test_round_trip() -> None:
    mass = 9.1093837139e-31
    assert mass_from_frequency(frequency_from_mass(mass)) == pytest.approx(mass)


def test_normalized_match() -> None:
    assert normalize_signal(4 + 2j, 4 + 2j) == 1 + 0j


def test_invalid_reference() -> None:
    with pytest.raises(ZeroDivisionError):
        normalize_signal(1 + 0j, 0 + 0j)
