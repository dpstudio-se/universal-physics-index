import json
from pathlib import Path

from upi.cli import main


def test_derive_mass_explains_boundary(capsys: object) -> None:
    assert main(["--json", "derive-mass", "--frequency", "8"]) == 0
    payload = json.loads(capsys.readouterr().out)  # type: ignore[attr-defined]
    assert "not the mass" in payload["interpretation"]


def test_invalid_file_has_nonzero_exit(tmp_path: Path) -> None:
    path = tmp_path / "invalid.json"
    path.write_text('{"status":"HYP"}', encoding="utf-8")
    assert main(["--json", "validate", str(path)]) == 1


def test_lists_types(capsys: object) -> None:
    assert main(["--json", "list-frequency-types"]) == 0
    assert "photon_frequency" in capsys.readouterr().out  # type: ignore[attr-defined]
