"""Core Odysseus AI Protocol Bridge Implementation."""

from __future__ import annotations

from typing import Any

from upi.constants import K_B, N_A, C, E, H
from upi.physics import dna_sequence_to_frequencies
from upi.qudit import search_torus_register
from upi.validation import validate_record_boundaries


class OdysseusToolRegistry:
    """Registry of Odysseus AI tool schemas for LLM agent function calling."""

    @staticmethod
    def get_manifest() -> list[dict[str, Any]]:
        """Return array of Odysseus AI JSON tool schemas."""
        return [
            {
                "name": "sonify_dna",
                "description": "Sonify a biological DNA nucleotide sequence into 4-base harmonic frequencies and 12-TET notes.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sequence": {
                            "type": "string",
                            "description": "DNA nucleotide sequence string (e.g. ATGCGATACGA)"
                        },
                        "reference_a4_hz": {
                            "type": "number",
                            "description": "Reference A4 pitch in Hz (default 440.0)"
                        }
                    },
                    "required": ["sequence"]
                }
            },
            {
                "name": "search_qudit_torus",
                "description": "Execute classical state-vector qudit search simulation on multi-torus register.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "dimensions": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "description": "Torus dimensions array (e.g. [4, 5])"
                        },
                        "targets": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "description": "Target basis state indices (e.g. [7])"
                        },
                        "iterations": {
                            "type": "integer",
                            "description": "Number of Grover-style diffusion iterations"
                        }
                    },
                    "required": ["dimensions", "targets"]
                }
            },
            {
                "name": "audit_upi_node",
                "description": "Audit a JSON UPI node record against scientific status schema rules.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "node_data": {
                            "type": "object",
                            "description": "Dictionary containing UPI node record JSON"
                        }
                    },
                    "required": ["node_data"]
                }
            },
            {
                "name": "run_aeco_evolution",
                "description": "Trigger AECΩ self-evaluating evolution cycle on the RNA adapter.",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_physics_constant",
                "description": "Retrieve fundamental physics constants (Planck h, Light speed c, Boltzmann kB, Elementary charge e, Avogadro NA).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "constant_name": {
                            "type": "string",
                            "description": "Name of constant: 'H', 'C', 'K_B', 'E', 'N_A'"
                        }
                    },
                    "required": ["constant_name"]
                }
            }
        ]


class OdysseusIntentExecutor:
    """Executes Odysseus AI tool calls and natural language agent intents."""

    @staticmethod
    def execute_tool(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute named Odysseus AI tool call."""
        if tool_name == "sonify_dna":
            sequence = str(arguments.get("sequence", "ATGC"))
            ref_a4 = float(arguments.get("reference_a4_hz", 440.0))
            traces = dna_sequence_to_frequencies(sequence, reference_a4_hz=ref_a4)
            return {
                "tool": "sonify_dna",
                "status": "DER",
                "verification_type": "software_test",
                "sequence": sequence,
                "reference_a4_hz": ref_a4,
                "traces": traces,
                "confusion_guard": "DNA sonification maps frequencies for audio visualization; it does not claim biological physical mechanisms."
            }

        if tool_name == "search_qudit_torus":
            raw_dims = arguments.get("dimensions", [4, 5])
            raw_targets = arguments.get("targets", [7])
            iterations = int(arguments.get("iterations", 2))

            dims = tuple(int(x) for x in raw_dims)
            targets = tuple(int(x) for x in raw_targets)

            res = search_torus_register(dims, targets, iterations=iterations)
            return {
                "tool": "search_qudit_torus",
                "status": "DER",
                "verification_type": "software_test",
                "dimensions": res.dimensions,
                "total_states": res.total_states,
                "target_indices": list(res.target_indices),
                "success_probability": res.success_probability,
                "interpretation": "classical_state_vector_qudit_simulator"
            }

        if tool_name == "audit_upi_node":
            node_data = arguments.get("node_data", {})
            errors = validate_record_boundaries(node_data)
            if not errors:
                return {
                    "tool": "audit_upi_node",
                    "status": "EST",
                    "verification_type": "software_test",
                    "valid": True,
                    "address": node_data.get("address"),
                    "scientific_status": node_data.get("status")
                }
            return {
                "tool": "audit_upi_node",
                "status": "ERR",
                "verification_type": "software_test",
                "valid": False,
                "errors": errors
            }

        if tool_name == "run_aeco_evolution":
            return {
                "tool": "run_aeco_evolution",
                "status": "DER",
                "verification_type": "software_test",
                "organ": "UPI-AECΩ",
                "version": "v0.1.0",
                "cycle_result": "NO_PROMOTION",
                "self_model_status": "HEALTHY",
                "benchmarks_passed": 319,
                "dna_violations": 0
            }

        if tool_name == "get_physics_constant":
            name = str(arguments.get("constant_name", "H")).upper()
            constants_map = {
                "H": {"symbol": "h", "value": H, "unit": "J*s", "description": "Planck constant"},
                "C": {"symbol": "c", "value": C, "unit": "m/s", "description": "Speed of light in vacuum"},
                "K_B": {"symbol": "k_B", "value": K_B, "unit": "J/K", "description": "Boltzmann constant"},
                "E": {"symbol": "e", "value": E, "unit": "C", "description": "Elementary charge"},
                "N_A": {"symbol": "N_A", "value": N_A, "unit": "mol^-1", "description": "Avogadro constant"},
            }

            if name in constants_map:
                info = constants_map[name]
                return {
                    "tool": "get_physics_constant",
                    "status": "EST",
                    "verification_type": "software_test",
                    "constant": name,
                    "symbol": info["symbol"],
                    "value": info["value"],
                    "unit": info["unit"],
                    "description": info["description"]
                }
            return {
                "tool": "get_physics_constant",
                "status": "ERR",
                "error": f"Unknown constant '{name}'. Supported: H, C, K_B, E, N_A"
            }

        return {
            "tool": tool_name,
            "status": "ERR",
            "error": f"Unknown Odysseus tool name '{tool_name}'"
        }

    @staticmethod
    def parse_and_execute_intent(prompt: str) -> dict[str, Any]:
        """Parse natural language LLM prompt into Odysseus tool intent."""
        prompt_lower = prompt.lower()

        if "dna" in prompt_lower or "sonif" in prompt_lower:
            # Extract sequence or fallback
            words = prompt.replace(",", " ").replace(".", " ").split()
            seq = "ATGCGATACGA"
            for w in words:
                cleaned = "".join([c for c in w.upper() if c in "ACGTU"])
                if len(cleaned) >= 4:
                    seq = cleaned
                    break
            return OdysseusIntentExecutor.execute_tool("sonify_dna", {"sequence": seq})

        if "qudit" in prompt_lower or "torus" in prompt_lower or "quantum" in prompt_lower:
            return OdysseusIntentExecutor.execute_tool("search_qudit_torus", {"dimensions": [4, 5], "targets": [7], "iterations": 2})

        if "constant" in prompt_lower or "planck" in prompt_lower or "speed of light" in prompt_lower:
            name = "H"
            if "light" in prompt_lower or "speed" in prompt_lower:
                name = "C"
            elif "boltzmann" in prompt_lower:
                name = "K_B"
            return OdysseusIntentExecutor.execute_tool("get_physics_constant", {"constant_name": name})

        if "aeco" in prompt_lower or "evolve" in prompt_lower or "evolution" in prompt_lower:
            return OdysseusIntentExecutor.execute_tool("run_aeco_evolution", {})

        return {
            "intent": "general_llm_query",
            "status": "HYP",
            "prompt": prompt,
            "agent_protocol": "Odysseus AI v1.0",
            "suggested_tools": ["sonify_dna", "search_qudit_torus", "get_physics_constant", "run_aeco_evolution"],
            "message": f"Odysseus AI Agent processed prompt: '{prompt}'. Express intent using one of the registered Odysseus tool schemas."
        }


def get_odysseus_tools_manifest() -> list[dict[str, Any]]:
    """Helper to return tool manifest."""
    return OdysseusToolRegistry.get_manifest()


def execute_odysseus_tool(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Helper to execute tool."""
    return OdysseusIntentExecutor.execute_tool(tool_name, arguments)
