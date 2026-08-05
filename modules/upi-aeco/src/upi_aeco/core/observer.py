"""Observer: reads UPI-DNA and junk memory signals (STOP/ERR) to build self-model."""

from __future__ import annotations

from typing import Any

from ..adapters.upi_rna import UPI_RNA


def observe(version_id: str = "v0.1.0-initial") -> dict[str, Any]:
    """Observe current UPI state and construct self-model snapshot."""
    rna = UPI_RNA()
    dbg = rna.debug()

    status_counts = dbg.get("status_counts", {})
    stop_reasons = dbg.get("stop_reasons", [])
    junction_clusters = dbg.get("junction_clusters", [])

    weak_domains: list[str] = []
    if status_counts.get("STOP", 0) > 0 or status_counts.get("ERR", 0) > 0:
        weak_domains.append("unverified_evidence_boundary")
    if status_counts.get("SYM", 0) > 0:
        weak_domains.append("symbolic_interpretation_layer")

    self_model = {
        "version_id": version_id,
        "total_nodes": dbg.get("total_nodes", 0),
        "status_counts": status_counts,
        "junk_clusters": junction_clusters,
        "stop_reasons": stop_reasons,
        "weak_domains": weak_domains,
        "kernel_v_odin": rna.evaluate_odin(),
    }

    return self_model
