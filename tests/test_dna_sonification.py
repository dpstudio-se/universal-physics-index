import json
from pathlib import Path

import jsonschema
import pytest

from upi import dna_sequence_to_frequencies


def test_dna_sequence_to_frequencies() -> None:
    seq = "ATGC"
    results = dna_sequence_to_frequencies(seq)

    assert len(results) == 4

    # Position 1: A -> A4 (440 Hz)
    assert results[0]["nucleotide"] == "A"
    assert results[0]["note_name"] == "A4"
    assert pytest.approx(results[0]["frequency_hz"], abs=1e-4) == 440.0
    assert pytest.approx(results[0]["n8_index"], abs=1e-4) == 55.0

    # Position 2: T -> E4 (329.63 Hz)
    assert results[1]["nucleotide"] == "T"
    assert results[1]["note_name"] == "E4"
    assert pytest.approx(results[1]["frequency_hz"], abs=1e-2) == 329.63

    # Position 3: G -> G4 (392 Hz)
    assert results[2]["nucleotide"] == "G"
    assert results[2]["note_name"] == "G4"
    assert pytest.approx(results[2]["frequency_hz"], abs=1e-2) == 392.00

    # Position 4: C -> C4 (261.63 Hz)
    assert results[3]["nucleotide"] == "C"
    assert results[3]["note_name"] == "C4"
    assert pytest.approx(results[3]["frequency_hz"], abs=1e-2) == 261.63


def test_dna_sonification_example_record_validates() -> None:
    schema = json.loads(Path("schemas/node.schema.json").read_text(encoding="utf-8"))
    record = json.loads(Path("data/examples/dna_sonification_acoustics.json").read_text(encoding="utf-8"))

    validator = jsonschema.Draft202012Validator(schema)
    validator.validate(record)
