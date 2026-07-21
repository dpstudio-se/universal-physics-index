from upi.validation import validate_record_boundaries


def test_invalid_symbolic_promotion() -> None:
    record = {"status": "EST", "symbolic_interpretation": "Odin's Eye"}
    codes = {error.split(":", 1)[0] for error in validate_record_boundaries(record)}
    assert {"UPI-E005", "UPI-E007"} <= codes
