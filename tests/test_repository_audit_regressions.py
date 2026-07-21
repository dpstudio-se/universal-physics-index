import json
import sys
from pathlib import Path

import pytest

from upi import Address, PhysicsNode, ScientificStatus, VerificationType
from upi.cli import main
from upi.physics import (
    complex_signal_match,
    normalize_signal,
    normalize_value,
    propagated_mass_uncertainty,
    signal_match,
)


def error_codes(errors: list[str]) -> set[str]:
    return {error.split(":", 1)[0] for error in errors}


def test_graph_model_validation_closes_physical_equivalence_bypass() -> None:
    node = PhysicsNode(
        address=Address("physics", 1, "audit", "normalization"),
        title="Normalization boundary",
        description="A numerical normalization is not physical identity.",
        status=ScientificStatus.SYM,
        normalization_claim="physical_equivalence",
        causal_test_method="A causal method cannot promote a normalization identity claim.",
    )
    assert "UPI-E012" in error_codes(node.validate())


def test_non_experimental_check_cannot_claim_experimental_verification() -> None:
    node = PhysicsNode(
        address=Address("physics", 1, "audit", "verification"),
        title="Verification boundary",
        description="Mathematical checks are not experiments.",
        status=ScientificStatus.SYM,
        verification_type=VerificationType.MATHEMATICAL_CHECK,
        claims_experimental_verification=True,
    )
    assert "UPI-E014" in error_codes(node.validate())


def test_experimental_observation_may_claim_experimental_verification() -> None:
    node = PhysicsNode(
        address=Address("physics", 1, "audit", "experiment"),
        title="Experimental observation",
        description="A declared observation may carry the experimental flag.",
        status=ScientificStatus.SYM,
        verification_type=VerificationType.EXPERIMENTAL_OBSERVATION,
        claims_experimental_verification=True,
    )
    assert "UPI-E014" not in error_codes(node.validate())


def test_signal_tolerances_must_be_finite_and_non_negative() -> None:
    with pytest.raises(ValueError, match="epsilon must be non-negative"):
        signal_match(1.0, 1.0, epsilon=-1.0)
    with pytest.raises(ValueError, match="epsilon must be finite"):
        signal_match(1.0, 1.0, epsilon=float("inf"))


def test_complex_signal_rejects_invalid_amplitudes_phases_and_tolerances() -> None:
    with pytest.raises(ValueError):
        complex_signal_match(-1.0, 0.0, 1.0, 0.0)
    with pytest.raises(ValueError):
        complex_signal_match(1.0, float("inf"), 1.0, 0.0)
    with pytest.raises(ValueError):
        complex_signal_match(1.0, 0.0, 1.0, 0.0, phase_tolerance=-1.0)


def test_signed_normalization_and_zero_uncertainty_are_valid() -> None:
    assert normalize_value(-2.0, 4.0) == pytest.approx(-0.5)
    assert propagated_mass_uncertainty(0.0) == pytest.approx(0.0)


def test_signal_normalization_rejects_infinite_observation() -> None:
    with pytest.raises(ValueError, match="Observed must be finite"):
        normalize_signal(float("inf"), 1.0)


def test_address_parser_rejects_empty_and_negative_components() -> None:
    with pytest.raises(ValueError, match="must be non-empty"):
        Address.from_string("UPI<physics,1,,node>")
    with pytest.raises(ValueError, match="non-negative"):
        Address.from_string("UPI<physics,-1,classical,node>")


def test_index8_cli_accepts_explicit_zero(
    capsys: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(sys, "argv", ["upi", "index8", "--frequency", "0"])
    assert main() is None
    payload = json.loads(capsys.readouterr().out)  # type: ignore[attr-defined]
    assert payload["output_n8"] == 0.0


def test_normalize_cli_preserves_zero_epsilon(
    capsys: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "upi",
            "normalize",
            "--observed",
            "1",
            "--reference",
            "1",
            "--epsilon",
            "0",
        ],
    )
    assert main() is None
    payload = json.loads(capsys.readouterr().out)  # type: ignore[attr-defined]
    assert payload["epsilon"] == 0.0
    assert payload["matches"] is True


def test_validate_cli_routes_theory_before_node(
    tmp_path: Path,
    capsys: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    theory = {
        "address": "UPI<physics,1,relativistic,special_relativity>",
        "title": "Special relativity",
        "description": "A theory fixture for CLI schema routing.",
        "status": "EST",
        "domain": "physics",
        "scope": "inertial frames",
    }
    path = tmp_path / "theory.json"
    path.write_text(json.dumps(theory), encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["upi", "validate", str(path)])
    assert main() is None
    payload = json.loads(capsys.readouterr().out)  # type: ignore[attr-defined]
    assert payload["type"] == "theory"
    assert payload["valid"] is True


def test_operational_source_manifest_is_not_a_typed_data_record() -> None:
    assert Path("config/external_index_sources.json").is_file()
    assert not Path("data/sources/external_index_sources.json").exists()
