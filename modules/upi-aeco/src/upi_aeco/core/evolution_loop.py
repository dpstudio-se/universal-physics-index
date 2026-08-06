"""Evolution loop: orchestrates observation, evaluation, mutation, and selection."""

from __future__ import annotations

from typing import Any

from .evaluator import evaluate
from .mutator import generate_candidates
from .observer import observe
from .selector import select


def evolution_cycle(current_version: str = "v0.1.0-initial") -> dict[str, Any]:
    """Execute a single evolution cycle for UPI-AECΩ."""
    self_model = observe(current_version)
    base_score = evaluate(current_version)

    candidates = generate_candidates(current_version, self_model)

    best_version = current_version
    best_score = base_score

    for cand in candidates:
        cand_score = evaluate(cand)
        if cand_score > best_score:
            best_version = cand
            best_score = cand_score

    promoted = select(
        current_version=current_version,
        best_candidate=best_version,
        base_score=base_score,
        best_score=best_score,
        self_model=self_model,
    )

    return {
        "operation": "upi_aeco_evolution_cycle",
        "previous_version": current_version,
        "promoted_version": promoted,
        "base_score": base_score,
        "best_score": best_score,
        "candidates_evaluated": len(candidates),
        "self_model_snapshot": self_model,
    }
