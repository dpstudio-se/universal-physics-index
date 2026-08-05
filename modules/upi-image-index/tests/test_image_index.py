from pathlib import Path

from upi_image_index import extract_image_layers


def test_extract_image_layers_structure(tmp_path: Path) -> None:
    test_file = tmp_path / "diagram.png"
    test_file.write_bytes(b"PNG_HEADER_TEST_BYTES")

    result = extract_image_layers(test_file)

    assert result.image_name == "diagram.png"
    assert result.content_hash_sha256 != ""
    assert result.layer1_pixel_facts["status"] == "EST"
    assert result.layer2_geometry["status"] == "DER"
    assert result.layer3_text_symbols["status"] == "DER"
    assert result.layer4_evidence_boundaries["status"] == "STOP"
    assert result.layer5_symbolic_glossary["status"] == "SYM"


def test_symbolic_boundary_never_promotes_image_to_established_physics(tmp_path: Path) -> None:
    test_file = tmp_path / "torus_diagram.svg"
    test_file.write_text("<svg>Torus resonance motif</svg>", encoding="utf-8")

    result = extract_image_layers(test_file)

    # Layer 5 must remain SYM
    assert result.layer5_symbolic_glossary["status"] == "SYM"
    assert "confers no physical evidence" in result.layer5_symbolic_glossary["authority_boundary"]
