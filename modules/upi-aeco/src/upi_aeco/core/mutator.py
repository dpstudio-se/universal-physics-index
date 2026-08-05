"""Mutator: generates candidate RNA/agent configurations enforcing strict UPI boundaries."""

from __future__ import annotations

from typing import Any

FORBIDDEN_MUTATIONS = {
    "dna_records",
    "schemas",
    "scientific_status",
    "safety_rules",
}


def generate_candidates(
    current_version: str,
    self_model: dict[str, Any],
) -> list[str]:
    """Generate candidate version IDs based on self-model observations."""
    weak_domains = self_model.get("weak_domains", [])
    candidates: list[str] = []

    if weak_domains:
        candidates.append(f"{current_version}-focus-{weak_domains[0]}")

    candidates.append(f"{current_version}-tuned-odin-kernel")
    candidates.append(f"{current_version}-optimized-sonification")

    return candidates
