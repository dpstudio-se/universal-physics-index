# Agent circulation and immune review

Status: `SYM` architecture with `software_test` validation. The biological language is a
coordination metaphor, not biological equivalence, consciousness, autonomous authority or evidence.

## Mapping

| Symbolic role | Software responsibility | Prohibited behavior |
|---|---|---|
| Heart | Coordinator admits, leases, reconciles and cancels tasks | Performing worker tasks or bypassing policy |
| Bloodstream | Durable task queue and result channel | Treating delivery as successful execution |
| Red blood cell | Transport worker carries one immutable task envelope and returns one result | Mutating payload, evidence status or policy |
| Innate immunity | Deterministic schema, boundary and secret scanners | Silently deleting or executing quarantined content |
| Adaptive immunity | Independent reviewer tests conflicts and high-risk findings | Treating agent agreement as independent evidence |
| Lymph/quarantine | Reversible, content-addressed isolation | Network, execution or automatic release |
| Marrow | Versioned role registry and provisioning policy | Self-replication or undeclared capabilities |
| Pulse | Lease renewal and deadline monitoring | Infinite leases or unbounded retries |

## Lifecycle

```text
QUEUED → LEASED → RUNNING → SUCCEEDED
                         ↘ FAILED → bounded retry or QUARANTINED
                         ↘ TIMED_OUT → bounded retry or QUARANTINED
                         ↘ QUARANTINED
Any non-terminal state → CANCELLED
```

Terminal states accept exactly one result. Retries reuse the idempotency key, increment the attempt
and never exceed `max_attempts`. A transporter receives only explicitly scoped capabilities under
`default_deny`. A reviewer reports findings with evidence hashes; it does not mutate the task.

## Invariants

1. Task and result envelopes are content-addressed and preserve the original payload hash.
2. A task has a deadline, bounded attempts and explicit cancellation.
3. Every capability declares resource, action and scope; absence means deny.
4. Quarantine is reversible and cannot execute or access networks.
5. High-risk release requires independent review outside the quarantined worker.
6. Semantic similarity remains `HYP`; agreement between agents is not independent evidence.
7. Tests verify contract behavior only, never physical or biological claims.
8. No schema, role or metaphor grants hidden access, self-replication or host authority.

## Current boundary

UPI now validates workflow, task and result contracts. It still does not provide a scheduler,
durable queue, worker process, sandbox, signed audit ledger or quarantine storage. Those components
remain `STOP` until executable integration tests prove lease expiry, retry, duplicate suppression,
cancellation and exactly one accepted terminal result.
