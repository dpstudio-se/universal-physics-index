"""Validation module for UPI nodes and bridges."""

import json
from pathlib import Path
from typing import Dict, Any, List, Tuple

from .models import PhysicsNode, Bridge, ScientificStatus


def validate_json_schema(
    data: Dict[str, Any],
    schema_path: Path
) -> Tuple[bool, List[str]]:
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
        with open(schema_path, "r") as f:
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


def validate_node_status(node: PhysicsNode) -> List[str]:
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
    
    return errors


def validate_bridge_consistency(bridge: Bridge) -> List[str]:
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


def validate_node_json(data: Dict[str, Any], schema_path: Path) -> Tuple[bool, List[str]]:
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
    
    return len(errors) == 0, errors


def validate_bridge_json(data: Dict[str, Any], schema_path: Path) -> Tuple[bool, List[str]]:
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
