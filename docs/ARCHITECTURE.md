# Architecture

The conceptual address `UPI<D,G,T,N>` separates domain/system (`D`), governing relation or transformation context (`G`), evidence/status type (`T`) and normalization/notation context (`N`). The historical `Address` fields remain compatible in v0.1.0-alpha while records add explicit scientific domain, status, evidence, provenance and normalization fields.

The dependency-free Python core uses typed dataclasses. `models.py` defines records, `physics.py` contains narrow reference transformations, `validation.py` applies boundary rules to typed and untrusted JSON records, and `cli.py` exposes non-networked operations. JSON IDs, parent/child links, dependencies, revision history and source hashes provide stable extension points without requiring CrokPedia.
