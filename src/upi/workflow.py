"""Validation primitives for declarative UPI agent workflows.

This module validates contracts and state transitions. It does not spawn agents,
schedule work, execute tools, or provide a security boundary.
"""

from __future__ import annotations

import json
from enum import Enum
from typing import Any

import jsonschema

from .schema_resources import schema_path


class WorkflowState(str, Enum):
    """Lifecycle states for a bounded agent task."""

    QUEUED = "QUEUED"
    LEASED = "LEASED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    TIMED_OUT = "TIMED_OUT"
    QUARANTINED = "QUARANTINED"
    CANCELLED = "CANCELLED"


TERMINAL_STATES = {
    WorkflowState.SUCCEEDED,
    WorkflowState.FAILED,
    WorkflowState.TIMED_OUT,
    WorkflowState.QUARANTINED,
    WorkflowState.CANCELLED,
}

ALLOWED_TRANSITIONS = {
    WorkflowState.QUEUED: {WorkflowState.LEASED, WorkflowState.CANCELLED},
    WorkflowState.LEASED: {
        WorkflowState.RUNNING,
        WorkflowState.TIMED_OUT,
        WorkflowState.CANCELLED,
    },
    WorkflowState.RUNNING: {
        WorkflowState.SUCCEEDED,
        WorkflowState.FAILED,
        WorkflowState.TIMED_OUT,
        WorkflowState.QUARANTINED,
        WorkflowState.CANCELLED,
    },
    WorkflowState.FAILED: {WorkflowState.QUEUED, WorkflowState.QUARANTINED},
    WorkflowState.TIMED_OUT: {WorkflowState.QUEUED, WorkflowState.QUARANTINED},
    WorkflowState.SUCCEEDED: set(),
    WorkflowState.QUARANTINED: set(),
    WorkflowState.CANCELLED: set(),
}


def _validate_document(data: dict[str, Any], schema_name: str) -> list[str]:
    schema = json.loads(schema_path(schema_name).read_text(encoding="utf-8"))
    validator = jsonschema.Draft7Validator(schema, format_checker=jsonschema.FormatChecker())
    return [
        f"{error.json_path or '$'} failed {error.validator} validation."
        for error in sorted(validator.iter_errors(data), key=str)
    ]


def validate_task(data: dict[str, Any]) -> list[str]:
    """Validate an immutable task envelope."""
    errors = _validate_document(data, "agent-task")
    attempt = data.get("attempt")
    max_attempts = data.get("max_attempts")
    if isinstance(attempt, int) and isinstance(max_attempts, int) and attempt >= max_attempts:
        errors.append("$.attempt must be lower than $.max_attempts.")
    return errors


def validate_result(data: dict[str, Any]) -> list[str]:
    """Validate a terminal result envelope."""
    return _validate_document(data, "agent-result")


def validate_workflow(data: dict[str, Any]) -> list[str]:
    """Validate a declarative workflow specification."""
    errors = _validate_document(data, "workflow")
    declared_states = set(data.get("states", []))
    for transition in data.get("transitions", []):
        if not isinstance(transition, dict):
            continue
        for endpoint in ("from", "to"):
            if transition.get(endpoint) not in declared_states:
                errors.append(f"Transition {endpoint} state is not declared.")
    return errors


def validate_transition(current: WorkflowState, target: WorkflowState) -> list[str]:
    """Check a task state transition without performing it."""
    if target not in ALLOWED_TRANSITIONS[current]:
        return [f"Transition {current.value}->{target.value} is not allowed."]
    return []


def validate_task_result_pair(task: dict[str, Any], result: dict[str, Any]) -> list[str]:
    """Check provenance and immutability across a task/result pair."""
    errors = [*validate_task(task), *validate_result(result)]
    if task.get("task_id") != result.get("task_id"):
        errors.append("Result task_id does not match task envelope.")
    if task.get("attempt") != result.get("attempt"):
        errors.append("Result attempt does not match task envelope.")
    if task.get("payload_hash") != result.get("input_hash"):
        errors.append("Result input_hash does not match immutable task payload_hash.")
    return errors
