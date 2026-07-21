from upi import (
    Address,
    PhysicsNode,
    ScientificStatus,
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


def test_experimental_observation_is_not_software_error() -> None:
    errors = validate_scientific_boundaries(
        symbolic_node(
            verification_type=VerificationType.EXPERIMENTAL_OBSERVATION,
            claims_experimental_verification=True,
        )
    )
    assert "UPI-E014" not in codes(errors)
