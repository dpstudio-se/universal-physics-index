import pytest

from upi.graph import UPIGraph
from upi.models import Address, PhysicsNode, ScientificStatus
from upi.validation import validate_record_boundaries


def node(status: ScientificStatus = ScientificStatus.SYM) -> PhysicsNode:
    return PhysicsNode(Address("TEST", 1, "T1", "N1"), "Test", "Test record", status)


def test_all_statuses_are_stable() -> None:
    assert [status.value for status in ScientificStatus] == ["EST", "DER", "HYP", "STOP", "ERR", "SYM"]


def test_hypothesis_requires_test_metadata() -> None:
    errors = validate_record_boundaries({"status": "HYP", "provenance": ["proposal"]})
    assert any(error.startswith("UPI-E004:") for error in errors)


def test_symbolic_cannot_be_established() -> None:
    errors = validate_record_boundaries(
        {"status": "EST", "symbolic_interpretation": "metaphor", "provenance": ["note"]}
    )
    assert any(error.startswith("UPI-E005:") for error in errors)


def test_graph_rejects_duplicate_addresses() -> None:
    graph = UPIGraph()
    graph.add_node(node())
    with pytest.raises(ValueError, match="already exists"):
        graph.add_node(node())
