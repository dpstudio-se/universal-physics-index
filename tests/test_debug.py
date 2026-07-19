import json
from pathlib import Path

from upi import generate_debug_report, render_debug_markdown
from upi.schema_resources import schemas_dir


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data), encoding="utf-8")


def test_debug_index_builds_exploded_map(tmp_path: Path) -> None:
    write_json(
        tmp_path / "node.json",
        {
            "address": "UPI<physics,1,classical,test>",
            "title": "Test node",
            "description": "A valid test node.",
            "status": "EST",
            "quantities": [{"name": "time", "value": 1.0, "unit": "s"}],
        },
    )

    report = generate_debug_report(tmp_path)

    assert report["summary"]["records_classified"] == 1
    assert report["summary"]["findings"] == 0
    assert report["verification_type"] == "software_test"
    assert report["claims_experimental_verification"] is False
    assert report["exploded_map"]["layers"] == [
        "record",
        "scale",
        "evidence",
        "finding",
        "correction",
    ]
    assert any(node["layer"] == "scale" for node in report["exploded_map"]["nodes"])


def test_debug_index_reports_schema_and_boundary_errors(tmp_path: Path) -> None:
    write_json(
        tmp_path / "bad.json",
        {
            "address": "UPI<physics,1,test,bad>",
            "title": "Bad node",
            "description": "Claims too much.",
            "status": "HYP",
            "normalization_method": "Z = z / z_ref",
            "causal_claim": True,
            "verification_type": "software_test",
            "claims_experimental_verification": True,
        },
    )

    report = generate_debug_report(tmp_path)
    codes = {finding["code"] for finding in report["findings"]}

    assert {"UPI-E011", "UPI-E013", "UPI-E014", "UPI-D004"} <= codes
    assert all(finding["correction"] for finding in report["findings"])


def test_debug_index_handles_invalid_json(tmp_path: Path) -> None:
    (tmp_path / "broken.json").write_text("{", encoding="utf-8")

    report = generate_debug_report(tmp_path)

    assert report["findings"][0]["code"] == "UPI-D001"
    assert report["findings"][0]["status"] == "ERR"


def test_debug_markdown_contains_correction(tmp_path: Path) -> None:
    (tmp_path / "broken.json").write_text("{", encoding="utf-8")

    rendered = render_debug_markdown(generate_debug_report(tmp_path))

    assert "# UPI debug report" in rendered
    assert "Correction:" in rendered
    assert "software_test" in rendered


def test_odins_eye_finds_exact_mirrors_without_exposing_values(tmp_path: Path) -> None:
    record = {
        "address": "UPI<physics,1,classical,mirror>",
        "title": "Mirror node",
        "description": "token=do-not-report",
        "status": "EST",
    }
    write_json(tmp_path / "one.json", record)
    write_json(tmp_path / "two.json", record)

    report = generate_debug_report(tmp_path, odins_eye=True)
    serialized = json.dumps(report)

    assert any(finding["code"] == "UPI-O001" for finding in report["findings"])
    assert report["odins_eye"]["secret_values_exposed"] is False
    assert "do-not-report" not in serialized
    assert report["odins_eye"]["mirror_groups"][0]["paths"] == ["one.json", "two.json"]


def test_odins_eye_finds_shadow_identity_conflicts(tmp_path: Path) -> None:
    base = {
        "address": "UPI<physics,1,classical,shadow>",
        "title": "Shadow node",
        "description": "First version.",
        "status": "EST",
    }
    changed = {**base, "description": "Conflicting version."}
    write_json(tmp_path / "first.json", base)
    write_json(tmp_path / "second.json", changed)

    report = generate_debug_report(tmp_path, odins_eye=True)

    assert any(finding["code"] == "UPI-O002" for finding in report["findings"])
    assert report["odins_eye"]["shadow_groups"][0]["paths"] == [
        "first.json",
        "second.json",
    ]


def test_odins_eye_marks_hidden_paths_and_semantic_mirrors(tmp_path: Path) -> None:
    hidden = tmp_path / ".shadow"
    hidden.mkdir()
    first = {
        "address": "UPI<physics,1,classical,first>",
        "title": "Shared equation",
        "description": "First interpretation.",
        "status": "HYP",
        "equations": ["E = h*f"],
        "falsification_conditions": ["A measurable mismatch."],
    }
    second = {
        **first,
        "address": "UPI<physics,1,classical,second>",
        "description": "Second interpretation.",
    }
    write_json(hidden / "first.json", first)
    write_json(tmp_path / "second.json", second)

    report = generate_debug_report(tmp_path, odins_eye=True)
    codes = {finding["code"] for finding in report["findings"]}

    assert {"UPI-O003", "UPI-O004"} <= codes
    assert report["exploded_map"]["layers"][-2:] == ["shadow", "mirror"]


def test_bundled_schemas_match_repository_schemas() -> None:
    repository_schemas = Path(__file__).parents[1] / "schemas"

    for name in ("node.schema.json", "bridge.schema.json", "theory.schema.json"):
        assert (schemas_dir() / name).read_bytes() == (repository_schemas / name).read_bytes()


def test_odins_eye_distinguishes_bridge_relation_types(tmp_path: Path) -> None:
    base = {
        "source": "UPI<physics,1,test,source>",
        "target": "UPI<physics,1,test,target>",
        "status": "DER",
    }
    write_json(tmp_path / "causes.json", {**base, "relation": "CAUSES"})
    write_json(tmp_path / "contradicts.json", {**base, "relation": "CONTRADICTS"})

    report = generate_debug_report(tmp_path, odins_eye=True)

    assert not any(finding["code"] == "UPI-O002" for finding in report["findings"])


def test_odins_eye_redacts_source_values(tmp_path: Path) -> None:
    secret = "TOKEN_DO_NOT_REPORT"
    record = {
        "address": f"UPI<physics,1,test,{secret}>",
        "title": "Redaction test",
        "description": secret,
        "status": secret,
        "scope": secret,
    }
    write_json(tmp_path / "secret.json", record)
    write_json(tmp_path / "shadow.json", {**record, "description": "Changed payload."})

    report = generate_debug_report(tmp_path, odins_eye=True)
    serialized = json.dumps(report)

    assert secret not in serialized
    assert report["root"] == "."
    assert report["odins_eye"]["source_values_redacted"] is True
    assert report["odins_eye"]["shadow_groups"]


def test_exploded_map_only_derives_from_present_evidence(tmp_path: Path) -> None:
    write_json(
        tmp_path / "node.json",
        {
            "address": "UPI<physics,1,classical,no-evidence>",
            "title": "No evidence",
            "description": "A graph-edge regression test.",
            "status": "EST",
        },
    )

    report = generate_debug_report(tmp_path, odins_eye=True)
    record_node = next(
        node for node in report["exploded_map"]["nodes"] if node["layer"] == "record"
    )

    assert "identity_hash" in record_node
    assert not any(
        edge["relation"] == "DERIVED_FROM" for edge in report["exploded_map"]["edges"]
    )
