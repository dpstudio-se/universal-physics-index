"""Unit tests for upi-odysseus-bridge module."""

from __future__ import annotations

from upi_odysseus_bridge.core import (
    OdysseusIntentExecutor,
    execute_odysseus_tool,
    get_odysseus_tools_manifest,
)


def test_tool_manifest_structure() -> None:
    """Verify Odysseus tool manifest returns valid tool definitions."""
    tools = get_odysseus_tools_manifest()
    assert isinstance(tools, list)
    assert len(tools) >= 5

    names = [t["name"] for t in tools]
    assert "sonify_dna" in names
    assert "search_qudit_torus" in names
    assert "audit_upi_node" in names
    assert "run_aeco_evolution" in names
    assert "get_physics_constant" in names


def test_sonify_dna_tool_execution() -> None:
    """Verify sonify_dna tool executes and returns status DER."""
    res = execute_odysseus_tool("sonify_dna", {"sequence": "ATGC", "reference_a4_hz": 440.0})
    assert res["status"] == "DER"
    assert res["verification_type"] == "software_test"
    assert len(res["traces"]) == 4
    assert res["sequence"] == "ATGC"


def test_search_qudit_torus_tool_execution() -> None:
    """Verify search_qudit_torus tool executes and returns probability."""
    res = execute_odysseus_tool("search_qudit_torus", {"dimensions": [4, 5], "targets": [7], "iterations": 2})
    assert res["status"] == "DER"
    assert res["total_states"] == 20
    assert 0.0 <= res["success_probability"] <= 1.0


def test_get_physics_constant_tool_execution() -> None:
    """Verify get_physics_constant tool returns EST status for Planck h."""
    res = execute_odysseus_tool("get_physics_constant", {"constant_name": "H"})
    assert res["status"] == "EST"
    assert res["constant"] == "H"
    assert res["value"] == 6.62607015e-34


def test_intent_parsing() -> None:
    """Verify natural language intent parsing into tool calls."""
    res = OdysseusIntentExecutor.parse_and_execute_intent("Please sonify DNA sequence ATGCGATACGA")
    assert res["tool"] == "sonify_dna"
    assert res["status"] == "DER"
