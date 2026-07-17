from upi.models import Address, PhysicsNode, Status
from upi.validation import validate_dependency_graph, validate_node


def node(status: Status = Status.SYM, **kwargs: object) -> PhysicsNode:
    return PhysicsNode(Address("TEST", "G1", "T1", "N1"), "Test", "Test record", "test", status, **kwargs)


def test_all_statuses_are_stable() -> None:
    assert [status.value for status in Status] == ["EST", "DER", "HYP", "STOP", "ERR", "SYM"]


def test_hypothesis_requires_test_metadata() -> None:
    assert "UPI-E004" in {issue.code for issue in validate_node(node(Status.HYP))}


def test_symbolic_cannot_be_established() -> None:
    issues = validate_node(node(Status.EST, symbolic_interpretation="metaphor"))
    assert "UPI-E005" in {issue.code for issue in issues}


def test_duplicate_and_cycle_detection() -> None:
    first = node()
    second = node()
    assert "UPI-E009" in {issue.code for issue in validate_dependency_graph([first, second])}
    a = node()
    b = PhysicsNode(Address("TEST", "G1", "T1", "N2"), "B", "B", "test", Status.SYM)
    a.dependencies = [b.identifier]
    b.dependencies = [a.identifier]
    assert "UPI-E010" in {issue.code for issue in validate_dependency_graph([a, b])}
