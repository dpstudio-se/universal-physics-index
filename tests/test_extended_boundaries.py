import pytest

from upi import (
    Address,
    PhysicsNode,
    ScientificStatus,
    UPIGraph,
    VerificationType,
    validate_record_boundaries,
    validate_scientific_boundaries,
)


def symbolic_node(**kwargs: object) -> PhysicsNode:
    return PhysicsNode(
        Address("SYMBOLIC", 1, "VORTEX", "BOUNDARY"),
        "Boundary test",
        "Boundary test record",
        ScientificStatus.SYM,
        **kwargs,
    )


def codes(errors: list[str]) -> set[str]:
    return {error.split(":", 1)[0] for error in errors}


def test_reference_frame_required_for_normalization() -> None:
    errors = validate_scientific_boundaries(
        symbolic_node(normalization_method="Z = z / z_ref")
    )
    assert "UPI-E011" in codes(errors)


def test_normalization_does_not_prove_physical_equivalence() -> None:
    errors = validate_record_boundaries(
        {"status": "SYM", "normalization_claim": "physical_equivalence"}
    )
    assert "UPI-E012" in codes(errors)


def test_causal_method_does_not_make_normalization_physical_equivalence() -> None:
    errors = validate_scientific_boundaries(
        symbolic_node(
            normalization_claim="physical_equivalence",
            causal_test_method="randomized intervention",
        )
    )
    assert "UPI-E012" in codes(errors)


def test_unknown_normalization_claim_cannot_bypass_boundary() -> None:
    errors = validate_record_boundaries(
        {"normalization_claim": "physical-equivalance"}
    )
    assert "UPI-E012" in codes(errors)


def test_causal_claim_requires_causal_test() -> None:
    errors = validate_scientific_boundaries(symbolic_node(causal_claim=True))
    assert "UPI-E013" in codes(errors)


def test_software_test_is_not_experiment() -> None:
    errors = validate_scientific_boundaries(
        symbolic_node(
            verification_type=VerificationType.SOFTWARE_TEST,
            claims_experimental_verification=True,
        )
    )
    assert "UPI-E014" in codes(errors)


@pytest.mark.parametrize(
    "verification_type",
    [
        VerificationType.SIMULATION,
        VerificationType.MATHEMATICAL_CHECK,
        VerificationType.NONE,
    ],
)
def test_non_experimental_verification_is_not_experiment(
    verification_type: VerificationType,
) -> None:
    errors = validate_scientific_boundaries(
        symbolic_node(
            verification_type=verification_type,
            claims_experimental_verification=True,
        )
    )
    assert "UPI-E014" in codes(errors)


def test_experimental_observation_is_not_software_error() -> None:
    errors = validate_scientific_boundaries(
        symbolic_node(
            verification_type=VerificationType.EXPERIMENTAL_OBSERVATION,
            claims_experimental_verification=True,
        )
    )
    assert "UPI-E014" not in codes(errors)


def test_replication_can_support_experimental_verification() -> None:
    errors = validate_scientific_boundaries(
        symbolic_node(
            verification_type=VerificationType.REPLICATION,
            claims_experimental_verification=True,
        )
    )
    assert "UPI-E014" not in codes(errors)


def test_model_and_graph_enforce_scientific_boundaries() -> None:
    node = symbolic_node(normalization_method="Z = z / z_ref")

    assert "UPI-E011" in codes(node.validate())
    with pytest.raises(ValueError, match="UPI-E011"):
        UPIGraph().add_node(node)
