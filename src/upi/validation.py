"""Machine-readable validation for untrusted UPI records."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from .models import FrequencyType, PhysicsNode, Status


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    code: str
    message: str
    path: str = "$"
    severity: str = "error"


class UPIValidationError(ValueError):
    def __init__(self, issues: Iterable[ValidationIssue]) -> None:
        self.issues = tuple(issues)
        super().__init__("; ".join(f"{issue.code}: {issue.message}" for issue in self.issues))


def validate_node(node: PhysicsNode) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not node.status:
        issues.append(ValidationIssue("UPI-E001", "missing status", "$.status"))
    for name, quantity in node.quantities.items():
        if not quantity.unit:
            issues.append(ValidationIssue("UPI-E002", "missing unit", f"$.quantities.{name}.unit"))
        if "frequency" in name.lower() and quantity.frequency_type is None:
            issues.append(
                ValidationIssue("UPI-E003", "frequency type unspecified", f"$.quantities.{name}")
            )
    if node.status is Status.HYP:
        test_fields = (
            node.test_method,
            node.predicted_observation,
            node.falsification_condition,
            node.required_dataset,
            node.measurable_variable,
        )
        if not any(test_fields) and node.testability != "future":
            issues.append(
                ValidationIssue("UPI-E004", "hypothesis lacks test or falsification metadata")
            )
    if node.status is Status.EST and node.symbolic_interpretation:
        issues.append(
            ValidationIssue("UPI-E005", "symbolic statement cannot be marked established")
        )
    if node.status in {Status.EST, Status.DER, Status.HYP} and not node.provenance:
        issues.append(ValidationIssue("UPI-E007", "missing provenance", "$.provenance"))
    return issues


def validate_dependency_graph(nodes: Iterable[PhysicsNode]) -> list[ValidationIssue]:
    node_list = list(nodes)
    ids = [node.identifier for node in node_list]
    issues: list[ValidationIssue] = []
    if len(ids) != len(set(ids)):
        issues.append(ValidationIssue("UPI-E009", "duplicate identifier"))
    graph = {node.identifier: node.dependencies for node in node_list}
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(identifier: str) -> bool:
        if identifier in visiting:
            return True
        if identifier in visited:
            return False
        visiting.add(identifier)
        if any(visit(dep) for dep in graph.get(identifier, []) if dep in graph):
            return True
        visiting.remove(identifier)
        visited.add(identifier)
        return False

    if any(visit(identifier) for identifier in graph if identifier not in visited):
        issues.append(ValidationIssue("UPI-E010", "cyclic dependency"))
    return issues


def validate_record(record: dict[str, Any]) -> list[ValidationIssue]:
    """Apply essential boundary checks to a decoded, untrusted JSON record."""
    issues: list[ValidationIssue] = []
    status = record.get("status")
    if status is None:
        issues.append(ValidationIssue("UPI-E001", "missing status", "$.status"))
    elif status not in {item.value for item in Status}:
        issues.append(ValidationIssue("UPI-E001", "unsupported status", "$.status"))
    quantities = record.get("quantities", {})
    if isinstance(quantities, dict):
        for name, quantity in quantities.items():
            if not isinstance(quantity, dict) or not quantity.get("unit"):
                issues.append(ValidationIssue("UPI-E002", "missing unit", f"$.quantities.{name}"))
            if "frequency" in name.lower() and (
                not isinstance(quantity, dict)
                or quantity.get("frequency_type") not in {item.value for item in FrequencyType}
            ):
                issues.append(
                    ValidationIssue("UPI-E003", "frequency type unspecified", f"$.quantities.{name}")
                )
    if status == "HYP" and not any(
        record.get(key)
        for key in (
            "test_method",
            "predicted_observation",
            "falsification_condition",
            "required_dataset",
            "measurable_variable",
        )
    ) and record.get("testability") != "future":
        issues.append(ValidationIssue("UPI-E004", "hypothesis lacks test or falsification metadata"))
    if status == "EST" and record.get("symbolic_interpretation"):
        issues.append(ValidationIssue("UPI-E005", "symbolic statement marked as established"))
    if status in {"EST", "DER", "HYP"} and not record.get("provenance"):
        issues.append(ValidationIssue("UPI-E007", "missing provenance"))
    return issues


def load_json(path: str | Path) -> dict[str, Any]:
    """Safely parse JSON without executing input content."""
    with Path(path).open(encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise UPIValidationError([ValidationIssue("UPI-E001", "root must be an object")])
    return value
