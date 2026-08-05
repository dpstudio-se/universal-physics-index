
from upi.auto_mapper import LLMContextAutoMapper
from upi.models import Address, ScientificStatus


def test_auto_mapper_extracts_and_classifies_text_context() -> None:
    mapper = LLMContextAutoMapper()

    raw_context = """
    STATUS:EST
    UPI<physics,1,mechanics,planck_frequency>
    Quantum Planck frequency relation equation: f = 8 Hz.
    Directly established physics core.

    STATUS:HYP
    Hypothetical oscillation observed in high-energy plasma.
    Equation: f = 100 Hz.

    STATUS:SYM
    Raw model generation, speculative metaphor, non-coding conversational background context.
    """

    res = mapper.map_text_context(raw_context)

    assert res.nodes_extracted == 3
    assert res.nodes_written == 3
    assert res.dna_classification["SCIENTIFIC_CORE"] == 1
    assert res.dna_classification["HYPOTHESIS_CORE"] == 1
    assert res.dna_classification["JUNK_DNA_CORE"] == 1

    # Check Physics Engine evaluation for 8 Hz
    assert len(res.physics_evaluations) >= 1
    eval_8hz = next(e for e in res.physics_evaluations if e.get("input_frequency_hz") == 8.0)
    assert eval_8hz["output_n8"] == 1.0
    assert eval_8hz["engine_status"] == "EVALUATED_PHYSICS"


def test_auto_mapper_structured_context_ingestion() -> None:
    mapper = LLMContextAutoMapper()

    structured = [
        {
            "address": "UPI<physics,1,relativity,lorentz>",
            "title": "Lorentz Transformation",
            "description": "Relativistic spacetime transformation",
            "status": "EST",
            "equations": [],
        },
        {
            "address": "UPI<physics,1,relativity,mass_energy>",
            "title": "Mass-Energy Equivalence",
            "description": "Established Einstein relation",
            "status": "EST",
            "equations": ["m = 1.0e-30 kg"],
            "target": "UPI<physics,1,relativity,lorentz>",
            "relation": "DERIVED_FROM",
        },
        {
            "address": "UPI<information_physics,1,context,prompt_scratchpad>",
            "title": "LLM Scratchpad Context",
            "description": "Unverified model thought chain",
            "status": "SYM",
            "equations": [],
        },
    ]

    res = mapper.map_structured_context(structured)

    assert res.nodes_extracted == 3
    assert res.nodes_written == 3
    assert res.bridges_written == 1
    assert res.dna_classification["SCIENTIFIC_CORE"] == 2
    assert res.dna_classification["JUNK_DNA_CORE"] == 1

    eval_mass = res.physics_evaluations[0]
    assert eval_mass["input_mass_kg"] == 1.0e-30
    assert eval_mass["output_frequency_hz"] > 0


def test_auto_mapper_graph_integrity() -> None:
    mapper = LLMContextAutoMapper()
    mapper.map_text_context("STATUS:EST\nUPI<physics,1,core,speed_of_light>\nReference velocity: c = 299792458 m/s.")

    node = mapper.graph.get_node(Address("physics", 1, "core", "speed_of_light"))
    assert node is not None
    assert node.status == ScientificStatus.EST
