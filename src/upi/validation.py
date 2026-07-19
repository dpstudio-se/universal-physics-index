"""Validation module for UPI nodes and bridges."""

import json
from pathlib import Path
from typing import Any

from .models import Bridge, PhysicsNode, ScientificStatus, VerificationType

ERROR_MESSAGES = {
    "UPI-E011": "Reference-frame ambiguity",
    "UPI-E012": "Normalization presented as physical equivalence",
    "UPI-E013": "Correlation or association presented as causation without a causal test",
    "UPI-E014": "Non-experimental verification presented as experimental verification",
}


def validate_scientific_boundaries(node: PhysicsNode) -> list[str]:
    """Return stable error-code messages for evidence-boundary violations."""
    errors: list[str] = []
    if node.normalization_method and not node.reference_frame:
        errors.append(f"UPI-E011: {ERROR_MESSAGES['UPI-E011']}")
    if (
        node.normalization_claim
        and node.normalization_claim != "numerical_similarity_only"
    ):
        errors.append(f"UPI-E012: {ERROR_MESSAGES['UPI-E012']}")
    if node.causal_claim and not node.causal_test_method:
        errors.append(f"UPI-E013: {ERROR_MESSAGES['UPI-E013']}")
    if (
        node.claims_experimental_verification
        and node.verification_type
        not in {
            VerificationType.EXPERIMENTAL_OBSERVATION,
            VerificationType.REPLICATION,
        }
    ):
        errors.append(f"UPI-E014: {ERROR_MESSAGES['UPI-E014']}")
    return errors


def validate_record_boundaries(data: dict[str, Any]) -> list[str]:
    """Apply evidence-boundary guards to decoded, untrusted JSON data."""
    errors: list[str] = []
    if data.get("normalization_method") and not data.get("reference_frame"):
        errors.append(f"UPI-E011: {ERROR_MESSAGES['UPI-E011']}")
    if data.get("normalization_claim") and data.get(
        "normalization_claim"
    ) != "numerical_similarity_only":
        errors.append(f"UPI-E012: {ERROR_MESSAGES['UPI-E012']}")
    if data.get("causal_claim") is True and not data.get("causal_test_method"):
        errors.append(f"UPI-E013: {ERROR_MESSAGES['UPI-E013']}")
    if (
        data.get("claims_experimental_verification") is True
        and data.get("verification_type")
        not in {
            VerificationType.EXPERIMENTAL_OBSERVATION.value,
            VerificationType.REPLICATION.value,
        }
    ):
        errors.append(f"UPI-E014: {ERROR_MESSAGES['UPI-E014']}")
    return errors


def validate_json_schema(
    data: dict[str, Any],
    schema_path: Path
) -> tuple[bool, list[str]]:
    """Validate JSON data against a JSON schema.

    Args:
        data: JSON data to validate
        schema_path: Path to JSON schema file

    Returns:
        (is_valid, list of error messages)
    """
    try:
        import jsonschema
    except ImportError:
        return False, ["jsonschema module not installed"]

    try:
        with open(schema_path) as f:
            schema = json.load(f)
    except Exception as e:
        return False, [f"Failed to load schema: {e}"]

    try:
        jsonschema.validate(instance=data, schema=schema)
        return True, []
    except jsonschema.ValidationError as e:
        return False, [str(e)]
    except jsonschema.SchemaError as e:
        return False, [f"Schema error: {e}"]


def validate_node_status(node: PhysicsNode) -> list[str]:
    """Validate that node status is consistent.

    Returns list of error strings (empty if valid).
    """
    errors = []

    if node.status == ScientificStatus.STOP and not node.stop_reason:
        errors.append("STOP nodes must have a stop_reason field")

    if not node.address.node:
        errors.append("Node identifier cannot be empty")

    if not node.title:
        errors.append("Title cannot be empty")

    errors.extend(validate_scientific_boundaries(node))
    return errors


def validate_bridge_consistency(bridge: Bridge) -> list[str]:
    """Validate that bridge is consistent.

    Returns list of error strings (empty if valid).
    """
    errors = []

    if not bridge.relation:
        errors.append("Bridge must have a relation type")

    if bridge.status == ScientificStatus.STOP and not bridge.stop_reason:
        errors.append("STOP bridges must have a stop_reason field")

    if bridge.source == bridge.target:
        errors.append("Bridge source and target cannot be the same")

    return errors


def validate_status_enum(status_str: str) -> bool:
    """Check if string is a valid scientific status."""
    try:
        ScientificStatus(status_str)
        return True
    except ValueError:
        return False


def validate_node_json(data: dict[str, Any], schema_path: Path) -> tuple[bool, list[str]]:
    """Validate a node JSON object.

    Args:
        data: JSON data
        schema_path: Path to node.schema.json

    Returns:
        (is_valid, list of errors)
    """
    errors = []

    # Schema validation
    is_valid, schema_errors = validate_json_schema(data, schema_path)
    if not is_valid:
        errors.extend(schema_errors)

    # Additional semantic validation
    if "status" in data:
        if not validate_status_enum(data["status"]):
            errors.append(f"Unknown status: {data['status']}")

    if data.get("status") == "STOP" and not data.get("stop_reason"):
        errors.append("STOP nodes must have stop_reason")

    if not data.get("address"):
        errors.append("Empty node identifier")

    errors.extend(validate_record_boundaries(data))

    return len(errors) == 0, errors


def validate_bridge_json(data: dict[str, Any], schema_path: Path) -> tuple[bool, list[str]]:
    """Validate a bridge JSON object.

    Args:
        data: JSON data
        schema_path: Path to bridge.schema.json

    Returns:
        (is_valid, list of errors)
    """
    errors = []

    # Schema validation
    is_valid, schema_errors = validate_json_schema(data, schema_path)
    if not is_valid:
        errors.extend(schema_errors)

    # Additional semantic validation
    if not data.get("relation"):
        errors.append("Bridge must have a relation type")

    if data.get("status") == "STOP" and not data.get("stop_reason"):
        errors.append("STOP bridges must have stop_reason")

    return len(errors) == 0, errors
