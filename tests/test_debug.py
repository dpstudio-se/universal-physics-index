import json
from pathlib import Path

from upi import generate_debug_report, render_debug_markdown


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
