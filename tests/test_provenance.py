from upi.validation import validate_record_boundaries


def test_scientific_record_requires_provenance() -> None:
    errors = validate_record_boundaries({"status": "EST"})
    assert any(error.startswith("UPI-E007:") for error in errors)
