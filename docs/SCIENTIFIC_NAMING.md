# Scientific Naming Standard

This document defines the naming policy for the Universal Physics Index (UPI).

## Principle

Primary identifiers, filenames, APIs, equations, schemas, and documentation headings MUST use established scientific or engineering terminology whenever such terminology exists.

Project-specific symbolic language MAY be retained as a documented alias, visualization label, historical name, or `SYM` concept, but it MUST NOT replace a standard scientific term.

## Naming order

Use names in this priority order:

1. SI, ISO, IUPAP, IUPAC, NIST, CODATA, or discipline-standard terminology.
2. A precise descriptive engineering term.
3. A project-specific alias, only when explicitly marked as symbolic.

## Required conventions

- Use SI quantity symbols and units.
- Reserve conventional symbols for their established meanings.
- Use ASCII identifiers in source code and JSON keys.
- Put Unicode mathematical symbols in rendered equations, not API names.
- Include subscripts in descriptive ASCII form, for example `R0_TIR`, `r0_S`, and `m_eq`.
- Distinguish a measured quantity from an equivalent or inferred quantity.
- Distinguish physical mechanisms from software architecture metaphors.
- Label non-established mappings as `DER`, `HYP`, or `SYM` rather than presenting them as standard physics.

## Canonical replacements

| Legacy or symbolic label | Canonical scientific or engineering name | Allowed alias status |
|---|---|---|
| Torus field in a UPI address | `system_class` or `boundary_topology` | `torus` only when the topology is mathematically toroidal |
| Odin's Eye | `read_only_consistency_inspector` | Historical CLI alias may remain temporarily |
| Functional DNA | `declarative_system_configuration` | `SYM` architecture alias |
| Vortex-DNA | `iterative_state_transition_model` | `SYM` architecture alias |
| Swarm | `distributed_coordination_protocol` | Informal architecture alias |
| Immunity / immune system | `validation_and_quarantine_layer` | `SYM` architecture alias |
| Heartbeat | `periodic_liveness_signal` | Engineering shorthand allowed |
| Transparency operator | `traceability_operator` or a domain-specific observable | Symbolic name requires an explicit definition |
| Mass-frequency bridge | `rest-energy Compton-frequency relation` | Use only for `E_0 = m c^2 = h f_C` |
| Frequency-derived mass | `equivalent_mass`, symbol `m_eq` | Must not be described as measured rest mass |
| 8 Hz lock | `reference_frequency` | No universal-constant claim |

## Physics notation

### Rest-energy frequency

Use

```text
E_0 = m c^2
f_C = E_0 / h = m c^2 / h
m = h f_C / c^2
```

Here `f_C` is the Compton frequency associated with rest energy. A generic oscillation frequency `f` must not automatically be converted into physical rest mass.

For a purely energy-equivalent conversion, use

```text
E = h f
m_eq = E / c^2 = h f / c^2
```

and state that `m_eq` is an energy-equivalent mass, not necessarily the invariant mass of an object.

### Reserved symbols

- `T`: thermodynamic temperature.
- `T_tr`: project-defined traceability or transparency score, only with a declared dimension and measurement procedure.
- `f_h1`: neutral harmonic-frequency identifier when no accepted physical name exists.
- `R0_TIR`: dimensionless trace-integrity conflict ratio.
- `r0_S = dR0_TIR/dt`: trace-integrity change rate in `s^-1`.
- `Omega` or `omega`: angular frequency only when defined by `omega = 2 pi f`; otherwise use a descriptive identifier.
- `phi`: phase angle or an explicitly defined scalar, not an unexplained project-wide constant.

## File and API naming

Use lowercase `snake_case` for Python modules, JSON fields, and data files.

Preferred examples:

```text
read_only_consistency_inspector.py
iterative_state_transition.json
distributed_coordination_protocol.md
traceability_metrics.py
```

Avoid unexplained names such as:

```text
odins_eye.py
vortex_dna.json
omega_core.py
cosmic_lock.json
```

When backwards compatibility is required, preserve the old name as a deprecated alias and document the canonical replacement.

## Migration rule

Every rename should include:

1. the canonical name;
2. the deprecated alias;
3. the scientific definition;
4. dimensions and SI units where applicable;
5. the status label (`EST`, `DER`, `HYP`, `STOP`, `ERR`, or `SYM`);
6. tests proving aliases resolve to the same object during the deprecation window.

New files and APIs MUST follow this standard immediately. Existing symbolic names should be migrated incrementally without breaking stored records or published interfaces.
