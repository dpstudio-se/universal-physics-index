"""Selector: compares base and candidate fitness scores, promoting optimal version."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE_DIR = Path(__file__).parent.parent.parent.parent / "state"
SELF_MODEL_PATH = STATE_DIR / "self_model.json"
VERSIONS_DIR = STATE_DIR / "versions"


def select(
    current_version: str,
    best_candidate: str,
    base_score: float,
    best_score: float,
    min_improvement: float = 0.02,
    self_model: dict[str, Any] | None = None,
) -> str:
    """Decide whether to promote best_candidate over current_version."""
    if best_candidate == current_version:
        promoted = current_version
    elif best_score - base_score >= min_improvement:
        promoted = best_candidate
    else:
        promoted = current_version

    # Update self_model.json snapshot if provided
    if self_model is not None:
        self_model["version_id"] = promoted
        self_model["last_updated_utc"] = datetime.now(timezone.utc).isoformat()
        self_model["fitness_score"] = best_score

        if STATE_DIR.exists():
            SELF_MODEL_PATH.write_text(json.dumps(self_model, indent=2), encoding="utf-8")

            # Save snapshot to state/versions/
            snapshot_path = VERSIONS_DIR / f"{promoted}.json"
            snapshot_path.write_text(json.dumps(self_model, indent=2), encoding="utf-8")

    return promoted
