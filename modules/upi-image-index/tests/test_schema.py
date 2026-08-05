"""Tests for image_index JSON schema validation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

jsonschema = pytest.importorskip("jsonschema", reason="jsonschema not installed")

_SCHEMA_PATH = (
    Path(__file__).parent.parent / "src" / "image_index" / "schemas" / "image-node.schema.json"
)
_DATA_DIR = Path(__file__).parent.parent / "data" / "images"


@pytest.fixture(scope="module")
def schema():
    return json.loads(_SCHEMA_PATH.read_text())


@pytest.fixture(scope="module")
def validator(schema):
    cls = jsonschema.validators.validator_for(schema)
    return cls(schema)


def _all_data_nodes():
    return list(_DATA_DIR.glob("*.json"))


class TestSchemaItself:
    def test_schema_file_exists(self):
        assert _SCHEMA_PATH.exists(), f"Schema not found at {_SCHEMA_PATH}"

    def test_schema_is_valid_json(self):
        schema = json.loads(_SCHEMA_PATH.read_text())
        assert isinstance(schema, dict)

    def test_schema_has_draft07_marker(self, schema):
        assert schema.get("$schema") == "http://json-schema.org/draft-07/schema#"

    def test_required_properties_declared(self, schema):
        for prop in ("address", "image_hash_sha256", "extraction_layers", "generation"):
            assert prop in schema.get("required", [])


class TestDataNodesExist:
    def test_all_four_nodes_exist(self):
        expected = [
            "torus_dna_tf_rf_ygl_ro.json",
            "brane_fs_phi1766.json",
            "vortex_dna_v9_homochiral.json",
            "vortex_dna_frank_model.json",
        ]
        for name in expected:
            path = _DATA_DIR / name
            assert path.exists(), f"Missing template node: {name}"


class TestDataNodeSchemaValidity:
    @pytest.mark.parametrize("node_path", _all_data_nodes(), ids=lambda p: p.name)
    def test_node_validates_against_schema(self, validator, node_path):
        node = json.loads(node_path.read_text())
        errors = list(validator.iter_errors(node))
        assert not errors, (
            f"{node_path.name} has schema validation errors:\n"
            + "\n".join(f"  {e.json_path}: {e.message}" for e in errors[:5])
        )

    @pytest.mark.parametrize("node_path", _all_data_nodes(), ids=lambda p: p.name)
    def test_node_has_address(self, node_path):
        node = json.loads(node_path.read_text())
        assert "address" in node
        assert node["address"].startswith("UPI<IMAGE,")

    @pytest.mark.parametrize("node_path", _all_data_nodes(), ids=lambda p: p.name)
    def test_node_image_hash_is_64_hex_or_placeholder(self, node_path):
        node = json.loads(node_path.read_text())
        h = node.get("image_hash_sha256", "")
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    @pytest.mark.parametrize("node_path", _all_data_nodes(), ids=lambda p: p.name)
    def test_no_claims_experimental_verification(self, node_path):
        node = json.loads(node_path.read_text())
        assert node.get("claims_experimental_verification") is False

    @pytest.mark.parametrize("node_path", _all_data_nodes(), ids=lambda p: p.name)
    def test_all_layers_have_content_hash(self, node_path):
        node = json.loads(node_path.read_text())
        for i, layer in enumerate(node.get("extraction_layers", [])):
            h = layer.get("content_hash", "")
            assert len(h) == 64, f"Layer {i} ({layer.get('layer_type')}) has invalid content_hash"

    @pytest.mark.parametrize("node_path", _all_data_nodes(), ids=lambda p: p.name)
    def test_shadow_layers_always_hyp(self, node_path):
        node = json.loads(node_path.read_text())
        for layer in node.get("extraction_layers", []):
            if layer.get("layer_type") == "SHADOW_LAYER":
                assert layer["status"] == "HYP", (
                    f"SHADOW_LAYER in {node_path.name} must be HYP, got {layer['status']}"
                )

    @pytest.mark.parametrize("node_path", _all_data_nodes(), ids=lambda p: p.name)
    def test_symbolic_layers_always_sym(self, node_path):
        node = json.loads(node_path.read_text())
        for layer in node.get("extraction_layers", []):
            if layer.get("layer_type") == "SYMBOLIC_ELEMENT":
                assert layer["status"] == "SYM", (
                    f"SYMBOLIC_ELEMENT in {node_path.name} must be SYM, got {layer['status']}"
                )

    @pytest.mark.parametrize("node_path", _all_data_nodes(), ids=lambda p: p.name)
    def test_sym_layers_have_confusion_guard(self, node_path):
        node = json.loads(node_path.read_text())
        for layer in node.get("extraction_layers", []):
            if layer.get("status") == "SYM":
                assert "confusion_guard" in layer, (
                    f"SYM layer {layer.get('layer_type')} in {node_path.name} missing confusion_guard"
                )

    @pytest.mark.parametrize("node_path", _all_data_nodes(), ids=lambda p: p.name)
    def test_hyp_layers_have_stop_reason(self, node_path):
        node = json.loads(node_path.read_text())
        for layer in node.get("extraction_layers", []):
            if layer.get("status") == "HYP":
                assert "stop_reason" in layer, (
                    f"HYP layer {layer.get('layer_type')} in {node_path.name} missing stop_reason"
                )


class TestSchemaRejectsInvalidNodes:
    def test_rejects_missing_address(self, validator):
        node = {
            "title": "T",
            "description": "D",
            "status": "SYM",
            "information_layer": "PUBLIC",
            "image_hash_sha256": "a" * 64,
            "extraction_layers": [],
            "generation": 1,
            "version": "0.1.0",
            "verification_type": "software_test",
            "claims_experimental_verification": False,
            "tags": [],
        }
        errors = list(validator.iter_errors(node))
        assert any("address" in str(e.message) or "required" in str(e.message) for e in errors)

    def test_rejects_short_image_hash(self, validator):
        node = {
            "address": "UPI<IMAGE,1,TEST,TEST>",
            "title": "T",
            "description": "D",
            "status": "SYM",
            "information_layer": "PUBLIC",
            "image_hash_sha256": "abc",  # too short
            "extraction_layers": [],
            "generation": 1,
            "version": "0.1.0",
            "verification_type": "software_test",
            "claims_experimental_verification": False,
            "tags": [],
        }
        errors = list(validator.iter_errors(node))
        assert errors, "Schema should reject short image_hash_sha256"

    def test_rejects_invalid_status(self, validator):
        node = {
            "address": "UPI<IMAGE,1,TEST,TEST>",
            "title": "T",
            "description": "D",
            "status": "INVALID_STATUS",
            "information_layer": "PUBLIC",
            "image_hash_sha256": "a" * 64,
            "extraction_layers": [],
            "generation": 1,
            "version": "0.1.0",
            "verification_type": "software_test",
            "claims_experimental_verification": False,
            "tags": [],
        }
        errors = list(validator.iter_errors(node))
        assert errors, "Schema should reject invalid status enum value"
