import json
from pathlib import Path

import jsonschema
import pytest


SCHEMA = json.loads(Path("schemas/node.schema.json").read_text(encoding="utf-8"))


def test_schema_is_valid() -> None:
    jsonschema.Draft202012Validator.check_schema(SCHEMA)


def test_example_records_validate() -> None:
    validator = jsonschema.Draft202012Validator(SCHEMA)
    for path in Path("data/examples").glob("*.json"):
        if path.name.startswith("invalid_") or path.name == "eight_hz.json":
            continue
        validator.validate(json.loads(path.read_text(encoding="utf-8")))


def test_hypothesis_without_testability_fails() -> None:
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate({"address": {"domain": "X", "generation": "G1", "torus": "T1", "node": "N1"}, "title": "X", "description": "X", "scientific_domain": "X", "status": "HYP", "schema_version": "0.1.0", "provenance": [{"source_type": "note", "source_status": "personal_note"}]}, SCHEMA)
