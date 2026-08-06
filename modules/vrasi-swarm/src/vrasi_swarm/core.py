"""Deterministic and data-minimizing 3-6-9 swarm coordination."""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Final

POOL_SIZE: Final[int] = 9
SELECTED_SIZE: Final[int] = 3
QUORUM_SIZE: Final[int] = 3
GENERATION: Final[int] = 4
_NODE_ID = re.compile(r"^[a-f0-9]{16,64}$")
_DIGEST = re.compile(r"^[a-f0-9]{64}$")


class SwarmPhase(str, Enum):
    EMPTY = "empty"
    THREE_SEED = "three_seed"
    SIX_CONTEXT = "six_context"
    NINE_READY = "nine_ready"


def _valid_node_id(node_id: str) -> str:
    if not isinstance(node_id, str) or _NODE_ID.fullmatch(node_id) is None:
        raise ValueError("node_id must be a 16-64 character lowercase hexadecimal identifier")
    return node_id


def _valid_digest(value: str, name: str) -> str:
    if not isinstance(value, str) or _DIGEST.fullmatch(value) is None:
        raise ValueError(f"{name} must be a lowercase SHA-256 digest")
    return value


def digest_payload(payload: Mapping[str, Any]) -> str:
    """Return a stable digest without retaining the original payload."""
    if not isinstance(payload, Mapping):
        raise TypeError("payload must be a mapping")
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class NodeObservation:
    """Transport-supplied, non-private measurements for one allowlisted node."""

    node_id: str
    quality: float
    latency_ms: float
    sequence: int

    def __post_init__(self) -> None:
        _valid_node_id(self.node_id)
        if (
            isinstance(self.quality, bool)
            or not isinstance(self.quality, (int, float))
            or not math.isfinite(self.quality)
        ):
            raise ValueError("quality must be finite")
        if not 0.0 <= self.quality <= 1.0:
            raise ValueError("quality must be between zero and one")
        if (
            isinstance(self.latency_ms, bool)
            or not isinstance(self.latency_ms, (int, float))
            or not math.isfinite(self.latency_ms)
        ):
            raise ValueError("latency_ms must be finite")
        if self.latency_ms < 0.0:
            raise ValueError("latency_ms cannot be negative")
        if isinstance(self.sequence, bool) or not isinstance(self.sequence, int) or self.sequence < 0:
            raise ValueError("sequence must be a non-negative integer")


@dataclass(frozen=True, slots=True)
class Proposal:
    proposal_id: str
    payload_digest: str
    previous_state_digest: str
    generation: int = GENERATION

    def __post_init__(self) -> None:
        _valid_digest(self.proposal_id, "proposal_id")
        _valid_digest(self.payload_digest, "payload_digest")
        _valid_digest(self.previous_state_digest, "previous_state_digest")
        if self.generation != GENERATION:
            raise ValueError(f"generation must be {GENERATION}")


@dataclass(frozen=True, slots=True)
class Vote:
    proposal_id: str
    node_id: str
    approve: bool
    sequence: int

    def __post_init__(self) -> None:
        _valid_digest(self.proposal_id, "proposal_id")
        _valid_node_id(self.node_id)
        if not isinstance(self.approve, bool):
            raise TypeError("approve must be boolean")
        if isinstance(self.sequence, bool) or not isinstance(self.sequence, int) or self.sequence < 0:
            raise ValueError("sequence must be a non-negative integer")


@dataclass(frozen=True, slots=True)
class CollectiveState:
    generation: int
    proposal_id: str
    state_digest: str
    selected_node_ids: tuple[str, ...]
    approvals: int
    model_status: str = "DER"
    verification_type: str = "software_test"
    claims_experimental_verification: bool = False


class SwarmCoordinator:
    """Bounded coordinator for one allowlisted nine-node pool."""

    def __init__(self, allowlist: set[str] | frozenset[str]) -> None:
        checked = frozenset(_valid_node_id(node_id) for node_id in allowlist)
        if len(checked) != POOL_SIZE:
            raise ValueError(f"allowlist must contain exactly {POOL_SIZE} unique node IDs")
        self._allowlist = checked
        self._nodes: dict[str, NodeObservation] = {}
        self._proposal: Proposal | None = None
        self._votes: dict[str, Vote] = {}
        self._last_vote_sequence: dict[str, int] = {}
        self._state: CollectiveState | None = None

    @property
    def phase(self) -> SwarmPhase:
        count = len(self._nodes)
        if count >= 9:
            return SwarmPhase.NINE_READY
        if count >= 6:
            return SwarmPhase.SIX_CONTEXT
        if count >= 3:
            return SwarmPhase.THREE_SEED
        return SwarmPhase.EMPTY

    @property
    def observations(self) -> Mapping[str, NodeObservation]:
        return MappingProxyType(self._nodes)

    @property
    def state(self) -> CollectiveState | None:
        return self._state

    def observe(self, observation: NodeObservation) -> None:
        if observation.node_id not in self._allowlist:
            raise PermissionError("node is not allowlisted")
        current = self._nodes.get(observation.node_id)
        if current is not None and observation.sequence <= current.sequence:
            raise ValueError("observation sequence must increase")
        self._nodes[observation.node_id] = observation

    def selected_nodes(self) -> tuple[NodeObservation, ...]:
        if self.phase is not SwarmPhase.NINE_READY:
            raise RuntimeError("selection requires all nine allowlisted nodes")
        ranked = sorted(
            self._nodes.values(),
            key=lambda node: (-node.quality, node.latency_ms, node.node_id),
        )
        return tuple(ranked[:SELECTED_SIZE])

    def propose(self, payload: Mapping[str, Any], previous_state_digest: str) -> Proposal:
        if self._proposal is not None:
            raise RuntimeError("one proposal is already active")
        selected_ids = [node.node_id for node in self.selected_nodes()]
        payload_digest = digest_payload(payload)
        previous_digest = _valid_digest(previous_state_digest, "previous_state_digest")
        proposal_material = {
            "generation": GENERATION,
            "payload_digest": payload_digest,
            "previous_state_digest": previous_digest,
            "selected_node_ids": selected_ids,
        }
        self._proposal = Proposal(
            proposal_id=digest_payload(proposal_material),
            payload_digest=payload_digest,
            previous_state_digest=previous_digest,
        )
        self._votes.clear()
        return self._proposal

    def vote(self, vote: Vote) -> CollectiveState | None:
        if self._proposal is None or vote.proposal_id != self._proposal.proposal_id:
            raise ValueError("vote does not match the active proposal")
        selected_ids = tuple(node.node_id for node in self.selected_nodes())
        if vote.node_id not in selected_ids:
            raise PermissionError("only selected nodes may vote")
        last_sequence = self._last_vote_sequence.get(vote.node_id, -1)
        if vote.sequence <= last_sequence:
            raise ValueError("vote sequence must increase")
        if vote.node_id in self._votes:
            raise ValueError("a selected node may vote only once per proposal")
        self._last_vote_sequence[vote.node_id] = vote.sequence
        self._votes[vote.node_id] = vote

        approvals = sum(item.approve for item in self._votes.values())
        if approvals == QUORUM_SIZE:
            state_material = {
                "generation": GENERATION,
                "proposal_id": self._proposal.proposal_id,
                "selected_node_ids": selected_ids,
            }
            self._state = CollectiveState(
                generation=GENERATION,
                proposal_id=self._proposal.proposal_id,
                state_digest=digest_payload(state_material),
                selected_node_ids=selected_ids,
                approvals=approvals,
            )
        return self._state

    def topology(self) -> Mapping[str, Any]:
        selected: tuple[str, ...] = ()
        if self.phase is SwarmPhase.NINE_READY:
            selected = tuple(node.node_id for node in self.selected_nodes())
        observers = tuple(sorted(set(self._nodes) - set(selected)))
        return MappingProxyType(
            {
                "generation": GENERATION,
                "phase": self.phase.value,
                "registered_nodes": len(self._nodes),
                "selected_node_ids": selected,
                "observer_node_ids": observers,
                "stores_network_endpoints": False,
                "model_status": "SYM",
            }
        )
