import pytest

from upi.physics import normalize_value, normalized_match, propagated_mass_uncertainty


@pytest.mark.parametrize("reference", [7.834, 8.0, 8.2])
def test_configurable_reference(reference: float) -> None:
    assert normalize_value(reference, reference) == 1.0


def test_tolerance_match() -> None:
    assert normalized_match(8.0001, 8.0, 0.00002)
    assert not normalized_match(8.1, 8.0, 0.001)


def test_uncertainty_propagation() -> None:
    assert propagated_mass_uncertainty(0.1) > 0
