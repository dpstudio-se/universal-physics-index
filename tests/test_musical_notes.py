import json
from pathlib import Path

import jsonschema
import pytest

from upi import note_frequency_from_semitone, note_name_to_frequency


def test_note_frequency_from_semitone() -> None:
    # A4 (semitone offset 0) = 440 Hz
    assert pytest.approx(note_frequency_from_semitone(0), abs=1e-4) == 440.0

    # A5 (semitone offset +12) = 880 Hz
    assert pytest.approx(note_frequency_from_semitone(12), abs=1e-4) == 880.0

    # A3 (semitone offset -12) = 220 Hz
    assert pytest.approx(note_frequency_from_semitone(-12), abs=1e-4) == 220.0

    # C4 Middle C (semitone offset -9) = 261.6256 Hz
    assert pytest.approx(note_frequency_from_semitone(-9), abs=1e-2) == 261.63


def test_note_name_to_frequency() -> None:
    assert pytest.approx(note_name_to_frequency("A4"), abs=1e-4) == 440.0
    assert pytest.approx(note_name_to_frequency("C4"), abs=1e-2) == 261.63
    assert pytest.approx(note_name_to_frequency("A3"), abs=1e-4) == 220.0
    assert pytest.approx(note_name_to_frequency("C5"), abs=1e-2) == 523.25

    # Sharps and Flats
    f_csharp4 = note_name_to_frequency("C#4")
    f_dflat4 = note_name_to_frequency("Db4")
    assert pytest.approx(f_csharp4, abs=1e-4) == f_dflat4

    # Custom reference tuning (A4 = 432 Hz scientific pitch)
    assert pytest.approx(note_name_to_frequency("A4", reference_a4_hz=432.0), abs=1e-4) == 432.0

    with pytest.raises(ValueError, match="Invalid note name format"):
        note_name_to_frequency("InvalidNote")


def test_musical_notes_example_record_validates() -> None:
    schema = json.loads(Path("schemas/node.schema.json").read_text(encoding="utf-8"))
    record = json.loads(Path("data/examples/musical_notes_acoustics.json").read_text(encoding="utf-8"))

    validator = jsonschema.Draft202012Validator(schema)
    validator.validate(record)
