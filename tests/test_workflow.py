import json
from pathlib import Path

from upi.workflow import (
    WorkflowState,
    validate_task,
    validate_task_result_pair,
    validate_transition,
    validate_workflow,
)

HASH_A = "a" * 64
HASH_B = "b" * 64


def valid_task() -> dict:
    return {
        "task_id": "task-1",
        "workflow_id": "agent-circulation-v1",
        "role_id": "transporter",
        "state": "QUEUED",
        "idempotency_key": "workflow-1:artifact-1",
        "payload_hash": HASH_A,
        "capabilities": [
            {"resource": "filesystem", "actions": ["read"], "scopes": ["data/**"]}
        ],
        "default_deny": True,
        "attempt": 0,
        "max_attempts": 3,
        "created_at": "2026-07-19T16:00:00Z",
        "deadline_at": "2026-07-19T16:05:00Z",
    }


def valid_result() -> dict:
    return {
        "task_id": "task-1",
        "attempt": 0,
        "terminal_state": "SUCCEEDED",
        "input_hash": HASH_A,
        "output_hash": HASH_B,
        "worker_id": "transport-worker-1",
        "started_at": "2026-07-19T16:00:10Z",
        "completed_at": "2026-07-19T16:00:20Z",
        "verification_type": "software_test",
    }


def test_workflow_example_validates() -> None:
    path = Path(__file__).parents[1] / "examples" / "workflows" / "agent-circulation.workflow.json"
    assert validate_workflow(json.loads(path.read_text(encoding="utf-8"))) == []


def test_task_and_result_preserve_input_hash() -> None:
    assert validate_task_result_pair(valid_task(), valid_result()) == []

    mutated = {**valid_result(), "input_hash": HASH_B}
    assert any("immutable" in error for error in validate_task_result_pair(valid_task(), mutated))


def test_capabilities_are_scoped_and_default_deny() -> None:
    task = valid_task()
    task["default_deny"] = False
    task["capabilities"] = [{"resource": "network", "actions": ["connect"], "scopes": []}]

    assert validate_task(task)


def test_attempts_are_bounded() -> None:
    task = valid_task()
    task["attempt"] = task["max_attempts"]

    assert any("max_attempts" in error for error in validate_task(task))


def test_terminal_and_invalid_transitions_are_rejected() -> None:
    assert validate_transition(WorkflowState.QUEUED, WorkflowState.LEASED) == []
    assert validate_transition(WorkflowState.SUCCEEDED, WorkflowState.RUNNING)
