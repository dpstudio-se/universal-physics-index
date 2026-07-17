from upi.validation import validate_record


def test_invalid_symbolic_promotion() -> None:
    record = {"status": "EST", "symbolic_interpretation": "Odin's Eye"}
    codes = {issue.code for issue in validate_record(record)}
    assert {"UPI-E005", "UPI-E007"} <= codes
