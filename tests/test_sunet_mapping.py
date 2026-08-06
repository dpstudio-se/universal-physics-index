import json
from pathlib import Path

from upi.models import Address
from upi.sunet import load_sunet_topology


def test_sunet_source_record_exists_and_validates() -> None:
    sources_manifest_path = Path("config/external_source_manifest.json")
    if not sources_manifest_path.exists():
        sources_manifest_path = Path("data/sources/external_index_sources.json")
    sunet_record_path = Path("data/sources/sunet.json")
    if not sunet_record_path.exists():
        sunet_record_path = Path("config/sunet.json")

    assert sources_manifest_path.exists()
    assert sunet_record_path.exists()

    sources_manifest = json.loads(sources_manifest_path.read_text(encoding="utf-8"))
    sunet_record = json.loads(sunet_record_path.read_text(encoding="utf-8"))

    # Verify source manifest entry for Sunet
    sources = sources_manifest.get("sources", [])
    sunet_manifest_entry = next((s for s in sources if s.get("source_id") == "sunet"), None)
    assert sunet_manifest_entry is not None
    assert sunet_manifest_entry["adapter"] == "sitemap_and_html_metadata"
    assert sunet_manifest_entry["status"] == "DER"

    # Verify record fields
    assert sunet_record["operation"] == "upi_external_source_record"
    assert sunet_record["source_id"] == "sunet"
    assert sunet_record["canonical_url"] == "https://www.sunet.se/"
    assert sunet_record["upi_status"] == "DER"
    assert sunet_record["verification_type"] == "source_metadata_check"
    assert sunet_record["claims_experimental_verification"] is False

    # Scientific boundary checks
    assert "evidence_boundary" in sunet_record
    assert "confusion_guard" in sunet_record
    assert "does not independently verify physical laws" in sunet_record["evidence_boundary"]
    assert "must not be promoted to established physics" in sunet_record["confusion_guard"]

    # Relations syntax check
    for relation in sunet_record.get("relations", []):
        parsed_addr = Address.from_string(relation["target"])
        assert parsed_addr.domain in {"computer_science", "information_physics", "physics", "mathematics"}
        assert relation["status"] in {"EST", "DER", "HYP", "STOP", "ERR", "SYM"}


def test_sunet_topology_mapper_and_hpc_nodes() -> None:
    """Verify SUNET topology mapper loads backbone rings, NAISS HPC nodes, and SWAMID."""
    mapper = load_sunet_topology()

    assert len(mapper.nodes) >= 10
    hpc_centers = mapper.list_hpc_centers()
    assert len(hpc_centers) == 5

    # Check PDC KTH
    pdc_node = mapper.get_node("NAISS-PDC-KTH")
    assert pdc_node is not None
    assert pdc_node.name == "PDC Center for High Performance Computing (KTH Stockholm)"
    assert pdc_node.address == "UPI<computational_physics,1,hpc_supercomputing,pdc_kth>"
    assert "Dardel (HPE Cray EX)" in pdc_node.systems

    # Check institution filtering
    chalmers_nodes = mapper.find_nodes_by_institution("Chalmers")
    assert len(chalmers_nodes) >= 2

    # Check audit report
    report = mapper.generate_audit_summary()
    assert report["status"] == "DER"
    assert report["verification_type"] == "source_metadata_check"
    assert report["hpc_supercomputers"] == 5
