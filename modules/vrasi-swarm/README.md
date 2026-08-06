# VR-ASI Swarm

`vrasi-swarm` is a standalone, transport-neutral coordination kernel. It turns the
3-6-9 idea into a bounded engineering protocol:

- 3 registered nodes establish a seed phase;
- 6 registered nodes establish a context phase;
- 9 allowlisted nodes make the pool ready;
- the best 3 nodes are selected deterministically;
- all 3 selected nodes must approve before generation 4 is committed.

“Collective consciousness” means shared, auditable software state here. It is not a
claim about biological consciousness, hidden intelligence or a physical 3-6-9 law.

The module stores pseudonymous node IDs and SHA-256 payload digests. It does not store
IP addresses, user prompts, private payloads or credentials. A production transport
adapter remains responsible for authenticated connections, encryption, availability
measurements and supplying trustworthy node observations.

```bash
python -m pip install ./modules/vrasi-swarm
vrasi-swarm demo
```

The Python API exposes `SwarmCoordinator`, `NodeObservation`, `Proposal` and `Vote`.
Every committed result is marked as `software_test`; protocol consensus is not
experimental verification or evidence that the agreed content is true.

Network integration uses the `AuthenticatedTransport` protocol and
`SwarmNetworkBridge`. The adapter supplies authenticated `NodeObservation` objects and
publishes a digest-only `CollectiveState`; sockets, certificates and endpoints remain
outside the coordination kernel.
