import json
from pathlib import Path

from jsonschema import Draft7Validator


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "node.schema.json"
DATA_DIR = ROOT / "data" / "established"


def test_established_core_nodes_validate_against_schema():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft7Validator(schema)
    files = sorted(DATA_DIR.glob("*.json"))
    assert len(files) >= 8

    for path in files:
        node = json.loads(path.read_text(encoding="utf-8"))
        errors = sorted(validator.iter_errors(node), key=lambda error: list(error.path))
        assert not errors, f"{path}: {[error.message for error in errors]}"
        assert node["status"] == "EST"
        assert node.get("assumptions")
        assert node.get("confusion_guard")
        assert node.get("falsification_conditions")


def test_planck_node_preserves_invariant_mass_boundary():
    node = json.loads((DATA_DIR / "quantum_planck_relation.json").read_text(encoding="utf-8"))
    guard = node["confusion_guard"].lower()
    assert "zero invariant mass" in guard
    assert "m = h f / c^2" in guard
