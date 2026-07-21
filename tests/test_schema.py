import json
from pathlib import Path

import jsonschema

SCHEMA = json.loads(Path("schemas/node.schema.json").read_text(encoding="utf-8"))
VALID_EXAMPLES = (
    "established_mass_energy.json",
    "hypothesis_8hz.json",
    "quadralith.json",
)


def test_schema_is_valid() -> None:
    jsonschema.Draft202012Validator.check_schema(SCHEMA)


def test_example_records_validate() -> None:
    validator = jsonschema.Draft202012Validator(SCHEMA)
    for name in VALID_EXAMPLES:
        path = Path("data/examples") / name
        validator.validate(json.loads(path.read_text(encoding="utf-8")))
