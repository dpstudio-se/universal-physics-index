"""Narrow boundary between swarm consensus and an authenticated transport."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol

from .core import CollectiveState, NodeObservation, SwarmCoordinator


class AuthenticatedTransport(Protocol):
    """Adapter implemented by the network layer outside this package.

    Implementations must authenticate peers, encrypt traffic and derive observations
    from trusted measurements before yielding them to the coordinator.
    """

    def receive_observations(self) -> Iterable[NodeObservation]: ...

    def publish_state(self, state: CollectiveState) -> None: ...


class SwarmNetworkBridge:
    """Connect a coordinator to an authenticated transport implementation."""

    def __init__(
        self,
        coordinator: SwarmCoordinator,
        transport: AuthenticatedTransport,
    ) -> None:
        self._coordinator = coordinator
        self._transport = transport

    def synchronize(self) -> int:
        """Ingest validated observations and return the number received."""
        received = 0
        for observation in self._transport.receive_observations():
            self._coordinator.observe(observation)
            received += 1
        return received

    def publish_committed(self) -> CollectiveState:
        """Publish only a committed, digest-only collective state."""
        state = self._coordinator.state
        if state is None:
            raise RuntimeError("no committed generation is available")
        self._transport.publish_state(state)
        return state
