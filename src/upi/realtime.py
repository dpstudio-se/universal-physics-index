"""Realtime ingestion helpers for UPI.

This module provides a small, explicit pipeline for receiving live input,
classifying it, validating it, and turning it into index-ready nodes and
bridges without mutating source records implicitly.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .graph import UPIGraph
from .models import (
    Address,
    Bridge,
    EdgeType,
    EvidenceRecord,
    InformationLayer,
    PhysicsNode,
    ScientificStatus,
)


@dataclass
class RealtimePayload:
    """Incoming live observation for the index."""

    address: Address
    title: str
    description: str
    status: ScientificStatus
    source: str
    relation: EdgeType | None = None
    target: Address | None = None
    equations: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    notes: str | None = None
    information_layer: InformationLayer = InformationLayer.PRIVATE
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class RealtimeWriteResult:
    """Result of ingesting a realtime payload into the UPI graph."""

    node_address: str
    node_status: ScientificStatus
    wrote_node: bool
    wrote_bridge: bool
    validation_errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    timestamp_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class RealtimeUPIIndex:
    """Explicit realtime read/write layer for UPI.

    The class is intentionally simple: it accepts a live payload, converts it
    into index structures, validates them, and appends them to the graph only
    after checks pass.
    """

    def __init__(self, graph: UPIGraph | None = None):
        self.graph = graph or UPIGraph()

    def ingest(self, payload: RealtimePayload) -> RealtimeWriteResult:
        """Validate and write a live payload into the index graph."""
        validation_errors: list[str] = []
        warnings: list[str] = []

        node = PhysicsNode(
            address=payload.address,
            title=payload.title,
            description=payload.description,
            status=payload.status,
            equations=list(payload.equations),
            assumptions=list(payload.assumptions),
            evidence=[
                EvidenceRecord(
                    type="realtime_ingest",
                    source=payload.source,
                    date=datetime.now(timezone.utc).date().isoformat(),
                    confidence=0.5 if payload.status == ScientificStatus.HYP else 0.9,
                    notes=payload.notes,
                )
            ],
            information_layer=payload.information_layer,
            tags=list(payload.tags),
            created_at=datetime.now(timezone.utc).isoformat(),
            updated_at=datetime.now(timezone.utc).isoformat(),
        )

        validation_errors.extend(node.validate())

        wrote_node = False
        wrote_bridge = False
        if not validation_errors:
            try:
                self.graph.add_node(node)
                wrote_node = True
            except ValueError as exc:
                validation_errors.append(str(exc))

        if payload.relation is not None and payload.target is not None and wrote_node:
            bridge = Bridge(
                source=payload.address,
                target=payload.target,
                relation=payload.relation,
                assumptions=list(payload.assumptions),
                status=ScientificStatus.HYP if payload.status != ScientificStatus.EST else ScientificStatus.EST,
                evidence=[
                    EvidenceRecord(
                        type="realtime_ingest",
                        source=payload.source,
                        date=datetime.now(timezone.utc).date().isoformat(),
                        confidence=0.5 if payload.status == ScientificStatus.HYP else 0.9,
                        notes=payload.notes,
                    )
                ],
                created_at=datetime.now(timezone.utc).isoformat(),
                updated_at=datetime.now(timezone.utc).isoformat(),
            )
            bridge_errors = bridge.validate()
            if bridge_errors:
                validation_errors.extend(bridge_errors)
            else:
                try:
                    self.graph.add_bridge(bridge)
                    wrote_bridge = True
                except ValueError as exc:
                    validation_errors.append(str(exc))
        elif payload.relation is not None and payload.target is None:
            warnings.append("relation supplied without target; bridge not written")

        return RealtimeWriteResult(
            node_address=str(payload.address),
            node_status=payload.status,
            wrote_node=wrote_node,
            wrote_bridge=wrote_bridge,
            validation_errors=validation_errors,
            warnings=warnings,
        )

    def read(self, address: Address) -> PhysicsNode | None:
        """Read a node from the live index."""
        return self.graph.get_node(address)

    def export(self) -> dict[str, Any]:
        """Export the current graph state."""
        return self.graph.export_to_dict()
