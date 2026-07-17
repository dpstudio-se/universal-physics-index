from upi.models import Address, PhysicsNode, Status
from upi.validation import validate_node


def test_scientific_record_requires_provenance() -> None:
    record = PhysicsNode(Address("PHYSICS", "G1", "T1", "N1"), "Claim", "Claim", "physics", Status.EST)
    assert "UPI-E007" in {issue.code for issue in validate_node(record)}
