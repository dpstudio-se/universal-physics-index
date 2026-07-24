import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
NODE_SCHEMA = json.loads((ROOT / "schemas" / "node.schema.json").read_text(encoding="utf-8"))
BRIDGE_SCHEMA = json.loads(
    (ROOT / "schemas" / "bridge.schema.json").read_text(encoding="utf-8")
)

NODE_PATHS = (
    ROOT / "data" / "quantum_information" / "finite_dimensional_hilbert_state_space.json",
    ROOT / "data" / "quantum_information" / "generalized_qudit_weyl_gates.json",
    ROOT / "data" / "quantum_information" / "qudit_fourier_dual_basis.json",
    ROOT / "data" / "quantum_information" / "multi_qudit_tensor_product_register.json",
    ROOT / "data" / "quantum_information" / "born_probability_rule.json",
    ROOT
    / "data"
    / "quantum_algorithms"
    / "phase_oracle_diffusion_amplitude_amplification.json",
    ROOT
    / "data"
    / "computational_physics"
    / "classical_state_vector_resource_boundary.json",
    ROOT / "data" / "information_physics" / "digital_qudit_torus_search.json",
)

BRIDGE_PATHS = (
    ROOT / "data" / "bridges" / "qudit_gates_from_hilbert_space.json",
    ROOT / "data" / "bridges" / "qudit_fourier_dual_to_computational_basis.json",
    ROOT / "data" / "bridges" / "multi_qudit_register_from_hilbert_spaces.json",
    ROOT / "data" / "bridges" / "hilbert_state_measured_by_born_rule.json",
    ROOT / "data" / "bridges" / "torus_search_from_tensor_register.json",
    ROOT / "data" / "bridges" / "torus_search_from_amplitude_amplification.json",
    ROOT / "data" / "bridges" / "torus_search_from_local_qudit_functions.json",
    ROOT / "data" / "bridges" / "torus_search_from_fourier_duality.json",
    ROOT
    / "data"
    / "bridges"
    / "torus_search_stops_at_classical_resource_boundary.json",
)


def _load(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def test_qudit_physics_nodes_are_schema_valid_and_scientifically_bounded() -> None:
    nodes = [_load(path) for path in NODE_PATHS]
    addresses = [node["address"] for node in nodes]

    assert len(addresses) == len(set(addresses))
    for node in nodes:
        jsonschema.validate(instance=node, schema=NODE_SCHEMA)
        assert node["equations"]
        assert node["falsification_conditions"]
        assert node["confusion_guard"]
        assert node["claims_experimental_verification"] is False
        assert node["information_layer"] == "ACADEMIC"

    statuses = {str(node["address"]): node["status"] for node in nodes}
    assert statuses[
        "UPI<information_physics,3,qudit_torus,digital_multi_state_search>"
    ] == "DER"
    assert statuses[
        "UPI<computational_physics,2,state_vector,classical_resource_boundary>"
    ] == "DER"
    assert all(
        status == "EST"
        for address, status in statuses.items()
        if address.startswith("UPI<quantum_")
    )


def test_qudit_physics_bridges_are_valid_and_resolve_known_nodes() -> None:
    nodes = {_load(path)["address"] for path in NODE_PATHS}
    bridges = [_load(path) for path in BRIDGE_PATHS]

    for bridge in bridges:
        jsonschema.validate(instance=bridge, schema=BRIDGE_SCHEMA)
        assert bridge["source"] in nodes
        assert bridge["target"] in nodes
        assert bridge["mechanism"]
        assert bridge["confusion_guard"]

    stop_bridges = [bridge for bridge in bridges if bridge["relation"] == "STOPS_AT"]
    assert len(stop_bridges) == 1
    assert stop_bridges[0]["status"] == "STOP"
    assert stop_bridges[0]["stop_reason"]


def test_qudit_index_preserves_the_classical_hardware_boundary() -> None:
    boundary = _load(
        ROOT
        / "data"
        / "computational_physics"
        / "classical_state_vector_resource_boundary.json"
    )
    torus = _load(
        ROOT / "data" / "information_physics" / "digital_qudit_torus_search.json"
    )

    assert "O(N)" in " ".join(str(value) for value in boundary["equations"])
    assert "classical digital simulator" in str(torus["confusion_guard"])
    assert torus["verification_type"] == "software_test"
