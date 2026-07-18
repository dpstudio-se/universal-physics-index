from upi.models import Address, PhysicsNode, Status, VerificationType
from upi.validation import validate_node, validate_record


def symbolic_node(**kwargs: object) -> PhysicsNode:
    return PhysicsNode(
        Address("SYMBOLIC", "G1", "T1", "N1"),
        "Boundary test",
        "Boundary test record",
        "symbolic architecture",
        Status.SYM,
        **kwargs,
    )


def test_reference_frame_required_for_normalization() -> None:
    issues = validate_node(symbolic_node(normalization_method="Z = z / z_ref"))
    assert "UPI-E011" in {issue.code for issue in issues}


def test_normalization_does_not_prove_physical_equivalence() -> None:
    issues = validate_record({"status": "SYM", "normalization_claim": "physical_equivalence"})
    assert "UPI-E012" in {issue.code for issue in issues}


def test_causal_claim_requires_causal_test() -> None:
    issues = validate_node(symbolic_node(causal_claim=True))
    assert "UPI-E013" in {issue.code for issue in issues}


def test_software_test_is_not_experiment() -> None:
    issues = validate_node(
        symbolic_node(
            verification_type=VerificationType.SOFTWARE_TEST,
            claims_experimental_verification=True,
        )
    )
    assert "UPI-E014" in {issue.code for issue in issues}


def test_explicit_experimental_observation_is_not_software_error() -> None:
    issues = validate_node(
        symbolic_node(
            verification_type=VerificationType.EXPERIMENTAL_OBSERVATION,
            claims_experimental_verification=True,
        )
    )
    assert "UPI-E014" not in {issue.code for issue in issues}
