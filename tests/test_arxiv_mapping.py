import json
from pathlib import Path

from upi.models import Address


def test_arxiv_source_record_exists_and_validates() -> None:
    sources_manifest_path = Path("data/sources/external_index_sources.json")
    arxiv_record_path = Path("data/sources/arxiv.json")

    assert sources_manifest_path.exists()
    assert arxiv_record_path.exists()

    sources_manifest = json.loads(sources_manifest_path.read_text(encoding="utf-8"))
    arxiv_record = json.loads(arxiv_record_path.read_text(encoding="utf-8"))

    # Verify source manifest entry for arXiv
    sources = sources_manifest.get("sources", [])
    arxiv_manifest_entry = next((s for s in sources if s.get("source_id") == "arxiv"), None)
    assert arxiv_manifest_entry is not None
    assert arxiv_manifest_entry["adapter"] == "arxiv_api_and_bulk_metadata"
    assert arxiv_manifest_entry["status"] == "DER"

    # Verify record fields
    assert arxiv_record["operation"] == "upi_external_source_record"
    assert arxiv_record["source_id"] == "arxiv"
    assert arxiv_record["canonical_url"] == "https://arxiv.org/"
    assert arxiv_record["upi_status"] == "DER"
    assert arxiv_record["verification_type"] == "source_metadata_check"
    assert arxiv_record["claims_experimental_verification"] is False

    # Scientific boundary checks
    assert "evidence_boundary" in arxiv_record
    assert "confusion_guard" in arxiv_record
    assert "preprint" in arxiv_record["evidence_boundary"].lower()
    assert "must not be promoted to established physical law" in arxiv_record["confusion_guard"]

    # Relations syntax check
    for relation in arxiv_record.get("relations", []):
        parsed_addr = Address.from_string(relation["target"])
        assert parsed_addr.domain in {"computer_science", "information_physics", "physics", "mathematics"}
        assert relation["status"] in {"EST", "DER", "HYP", "STOP", "ERR", "SYM"}
