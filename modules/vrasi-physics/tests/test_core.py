import json
import subprocess
import sys
from dataclasses import asdict

import pytest
from vrasi_physics import (
    energy_from_frequency,
    evaluate_frequency,
    mass_equivalent_from_frequency,
    reference_index,
)


def test_eight_hz_simulator_coordinate() -> None:
    result = evaluate_frequency(8.0)

    assert result.energy_j == pytest.approx(5.30085612e-33)
    assert result.mass_equivalent_kg == pytest.approx(5.897997859e-50)
    assert result.reference_index == pytest.approx(1.0)
    assert result.model_status == "DER"
    assert result.verification_type == "software_test"
    assert result.claims_experimental_verification is False


def test_custom_reference_is_explicit() -> None:
    assert reference_index(10.0, 5.0) == pytest.approx(2.0)


@pytest.mark.parametrize("value", [0.0, -1.0, float("nan"), float("inf")])
def test_invalid_frequency_fails_closed(value: float) -> None:
    with pytest.raises(ValueError):
        energy_from_frequency(value)
    with pytest.raises(ValueError):
        mass_equivalent_from_frequency(value)


def test_boolean_is_not_accepted_as_frequency() -> None:
    with pytest.raises(TypeError):
        evaluate_frequency(True)  # type: ignore[arg-type]


def test_cli_emits_machine_readable_result() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "vrasi_physics", "8"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert json.loads(completed.stdout) == asdict(evaluate_frequency(8.0))
