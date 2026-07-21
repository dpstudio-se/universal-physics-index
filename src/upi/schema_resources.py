"""Access JSON schemas bundled with the installed UPI package."""

from pathlib import Path


def schemas_dir() -> Path:
    """Return the package-local schema directory."""
    return Path(__file__).resolve().parent / "schemas"


def schema_path(record_type: str) -> Path:
    """Return the bundled schema path for a UPI record type."""
    return schemas_dir() / f"{record_type}.schema.json"
