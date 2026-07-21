import json
import subprocess
import sys
from dataclasses import asdict

import pytest
from vrasi_swarm import (
    GENERATION,
    CollectiveState,
    NodeObservation,
    SwarmCoordinator,
    SwarmNetworkBridge,
    SwarmPhase,
    Vote,
    digest_payload,
)


def node_id(number: int) -> str:
    return f"{number:016x}"


@pytest.fixture
def coordinator() -> SwarmCoordinator:
    return SwarmCoordinator({node_id(number) for number in range(1, 10)})


def observe_nodes(coordinator: SwarmCoordinator, count: int = 9) -> None:
    for number in range(1, count + 1):
        if node_id(number) in coordinator.observations:
            continue
        coordinator.observe(
            NodeObservation(
                node_id=node_id(number),
                quality=number / 10,
                latency_ms=float(10 - number),
                sequence=1,
            )
        )


def test_three_six_nine_phases(coordinator: SwarmCoordinator) -> None:
    assert coordinator.phase is SwarmPhase.EMPTY
    observe_nodes(coordinator, 3)
    assert coordinator.phase is SwarmPhase.THREE_SEED
    observe_nodes(coordinator, 6)
    assert coordinator.phase is SwarmPhase.SIX_CONTEXT
    observe_nodes(coordinator, 9)
    assert coordinator.phase is SwarmPhase.NINE_READY


def test_selects_best_three_deterministically(coordinator: SwarmCoordinator) -> None:
    observe_nodes(coordinator)
    assert [node.node_id for node in coordinator.selected_nodes()] == [
        node_id(9),
        node_id(8),
        node_id(7),
    ]


def test_unknown_node_and_replay_fail_closed(coordinator: SwarmCoordinator) -> None:
    with pytest.raises(PermissionError):
        coordinator.observe(NodeObservation("ffffffffffffffff", 1.0, 1.0, 1))
    coordinator.observe(NodeObservation(node_id(1), 0.5, 2.0, 1))
    with pytest.raises(ValueError, match="sequence"):
        coordinator.observe(NodeObservation(node_id(1), 0.6, 1.0, 1))


def test_selection_requires_all_nine_nodes(coordinator: SwarmCoordinator) -> None:
    observe_nodes(coordinator, 8)
    with pytest.raises(RuntimeError, match="nine"):
        coordinator.selected_nodes()


def test_top_three_commit_generation_four(coordinator: SwarmCoordinator) -> None:
    observe_nodes(coordinator)
    previous = "0" * 64
    proposal = coordinator.propose({"shared_fact": "public physics only"}, previous)
    state = None
    for sequence, number in enumerate((9, 8, 7), start=1):
        state = coordinator.vote(Vote(proposal.proposal_id, node_id(number), True, sequence))

    assert state is not None
    assert state.generation == GENERATION
    assert state.approvals == 3
    assert state.verification_type == "software_test"
    assert state.claims_experimental_verification is False


def test_observer_cannot_vote_and_vote_cannot_replay(coordinator: SwarmCoordinator) -> None:
    observe_nodes(coordinator)
    proposal = coordinator.propose({"value": 1}, "0" * 64)
    with pytest.raises(PermissionError):
        coordinator.vote(Vote(proposal.proposal_id, node_id(1), True, 1))
    coordinator.vote(Vote(proposal.proposal_id, node_id(9), True, 1))
    with pytest.raises(ValueError):
        coordinator.vote(Vote(proposal.proposal_id, node_id(9), True, 1))


def test_rejection_prevents_generation_four_commit(coordinator: SwarmCoordinator) -> None:
    observe_nodes(coordinator)
    proposal = coordinator.propose({"value": 1}, "0" * 64)
    assert coordinator.vote(Vote(proposal.proposal_id, node_id(9), False, 1)) is None
    assert coordinator.vote(Vote(proposal.proposal_id, node_id(8), True, 1)) is None
    assert coordinator.vote(Vote(proposal.proposal_id, node_id(7), True, 1)) is None
    assert coordinator.state is None


def test_only_payload_digest_is_retained(coordinator: SwarmCoordinator) -> None:
    observe_nodes(coordinator)
    payload = {"private_value": "must-not-be-stored"}
    proposal = coordinator.propose(payload, "0" * 64)

    assert proposal.payload_digest == digest_payload(payload)
    assert "must-not-be-stored" not in repr(coordinator.topology())
    assert "must-not-be-stored" not in repr(asdict(proposal))


def test_topology_contains_no_network_endpoints(coordinator: SwarmCoordinator) -> None:
    observe_nodes(coordinator)
    topology = dict(coordinator.topology())

    assert topology["stores_network_endpoints"] is False
    assert topology["model_status"] == "SYM"
    assert len(topology["selected_node_ids"]) == 3
    assert len(topology["observer_node_ids"]) == 6


def test_cli_demo_is_machine_readable() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "vrasi_swarm", "demo"],
        check=True,
        capture_output=True,
        text=True,
    )
    result = json.loads(completed.stdout)
    assert result["generation"] == 4
    assert result["phase"] == "nine_ready"
    assert len(result["selected_node_ids"]) == 3


class FakeAuthenticatedTransport:
    def __init__(self, observations: list[NodeObservation]) -> None:
        self.observations = observations
        self.published: list[CollectiveState] = []

    def receive_observations(self) -> list[NodeObservation]:
        return self.observations

    def publish_state(self, state: CollectiveState) -> None:
        self.published.append(state)


def test_authenticated_transport_bridge_publishes_only_committed_state(
    coordinator: SwarmCoordinator,
) -> None:
    observations = [
        NodeObservation(node_id(number), number / 10, float(10 - number), 1)
        for number in range(1, 10)
    ]
    transport = FakeAuthenticatedTransport(observations)
    bridge = SwarmNetworkBridge(coordinator, transport)
    assert bridge.synchronize() == 9
    with pytest.raises(RuntimeError, match="committed"):
        bridge.publish_committed()

    proposal = coordinator.propose({"public": "physics digest"}, "0" * 64)
    for number in (9, 8, 7):
        coordinator.vote(Vote(proposal.proposal_id, node_id(number), True, 1))
    published = bridge.publish_committed()

    assert transport.published == [published]
    assert not hasattr(published, "payload")
