# Universal Physics Index (UPI)

> **An open, typed knowledge graph for physics, mathematics, information, and the scientific structure of reality.**

[![Project Status: Experimental](https://img.shields.io/badge/status-experimental-orange.svg)](#project-status)
[![Default Language: English](https://img.shields.io/badge/language-English-blue.svg)](#language-policy)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![CI](https://github.com/dpstudio-se/universal-physics-index/actions/workflows/ci.yml/badge.svg)](https://github.com/dpstudio-se/universal-physics-index/actions/workflows/ci.yml)

---

## Overview

**Universal Physics Index**, abbreviated **UPI**, is an open research framework for mapping physical theories, mathematical structures, experimental evidence, unresolved problems, and candidate bridges into one common typed index.

The project is designed to answer a deceptively difficult question:

> How can we connect theories across different scales without confusing a shared mathematical form with a shared physical mechanism?

UPI treats each theory, equation, experiment, structure, and unresolved transition as a typed node in a graph. Every connection must declare what kind of relation it represents, what assumptions it depends on, how strong the evidence is, and where the argument stops.

The project does **not** claim that all theories are already unified. Its purpose is to make proposed unifications explicit, testable, inspectable, and easy to challenge.

---

## Core goals

UPI aims to:

1. Build a common index for physics and related sciences.
2. Separate established results from derivations, hypotheses, and unresolved gaps.
3. Map theories across scale, domain, geometry, information, and time.
4. Store both successful bridges and exact stopping points.
5. Support multiple visual views of the same underlying data.
6. Make scientific assumptions machine-readable.
7. Help researchers compare theories without flattening their differences.
8. Track how one stable system becomes the foundation of another.
9. Make speculative ideas falsifiable instead of vague.
10. Create an open structure that can grow into a scientific knowledge graph.

---

## Repository name

```text
universal-physics-index
```

Project abbreviation:

```text
UPI
```

Default language:

```text
English
```

Swedish material should be placed in:

```text
README.sv.md
docs/sv/
```

---

## The core index

The canonical UPI address is:

\[
\boxed{
\mathrm{UPI}\langle D,G,T,N\rangle
}
\]

where:

| Symbol | Meaning | Description |
|---|---|---|
| `D` | Domain | Physical system or scientific domain |
| `G` | Governing context | Governing relation, geometry or transformation |
| `T` | Type | Evidence and scientific-status layer |
| `N` | Normalization | Reference frame, notation or normalization context |

Extended form:

\[
\boxed{
\mathrm{UPI}\langle D,G,T,N\rangle
[x^\mu,\mathbf q,\mathcal M,r_0,\sigma]
}
\]

where:

| Symbol | Meaning |
|---|---|
| \(x^\mu\) | Spacetime address |
| \(\mathbf q\) | State variables |
| \(\mathcal M\) | Mechanism |
| \(r_0\) | Evidence or confidence record |
| \(\sigma\) | Scientific status |

Example:

```text
UPI<QUANTUM,G2,T_FIELD,N_DIRAC>
```

Extended example:

```text
UPI<QUANTUM,G2,T_FIELD,N_DIRAC>
[x_mu, q={spin:1/2, charge:-1}, mechanism=relativistic_spinor_field, r0=high, status=EST]
```

---

## Why use the word "torus"?

In UPI, a **torus** is not merely a geometric doughnut and not simply another word for "level."

A torus represents a complete system with:

- an internal state
- update rules
- feedback
- stability or conservation conditions
- internal circulation
- a boundary
- one or more bridges to other systems

A new torus begins when stable outputs from one system become active variables in another.

Example:

```text
Fields and energy
        ↓
Particles and atoms
        ↓
Chemistry
        ↓
Biology
        ↓
Cognition
        ↓
Knowledge and technology
```

In UPI notation:

\[
T_1
\rightarrow
B_{1\to2}
\rightarrow
T_2
\rightarrow
B_{2\to3}
\rightarrow
T_3
\]

where \(B\) is a bridge between torus systems.

---

## Scientific status labels

Every node and bridge must use one of the following labels:

| Label | Name | Meaning |
|---|---|---|
| `EST` | Established | Supported within the declared scientific domain |
| `DER` | Derived | Mathematically derived from explicit assumptions |
| `HYP` | Hypothesis | Falsifiable but unverified |
| `STOP` | Stop point | Missing mechanism, proof, evidence, or unique selection rule |
| `ERR` | Rejected | Contradicted, invalid, or superseded |
| `SYM` | Symbolic | Conceptual or metaphorical mapping only |

Examples:

```text
status: EST
```

```text
status: DER
assumptions:
  - special relativity
  - Planck relation
```

```text
status: HYP
falsification:
  - no predicted spectrum appears
```

```text
status: STOP
stop_reason:
  - no unique universal operator has been derived
```

This prevents a mathematically valid rewrite from being mistaken for a physical discovery.

---

## Relation and bridge types

Every edge in the graph must be typed.

Recommended bridge labels:

| Relation | Meaning |
|---|---|
| `DERIVED_FROM` | Exact derivation from another node |
| `CAUSES` | Claimed causal mechanism |
| `DUAL_TO` | Dual mathematical representation |
| `EQUIVALENT_WITHIN` | Equivalent only inside specified assumptions |
| `COARSE_GRAINS_TO` | Change of scale or resolution |
| `COMPACTIFIES_TO` | Dimensional reduction |
| `EMERGES_AS` | Effective higher-level behavior |
| `FORM_SIMILAR` | Same mathematical shape only |
| `TOPOLOGY_SHARED` | Shared topological structure |
| `MECHANISM_SHARED` | Supported shared physical mechanism |
| `CANDIDATE_BRIDGE` | Proposed testable bridge |
| `CONTRADICTS` | Incompatible claims |
| `STOPS_AT` | Exact unresolved boundary |
| `REPRESENTS` | Alternative representation of the same node |
| `MEASURED_BY` | Linked to an experimental observable |
| `FALSIFIED_BY` | Rejected by evidence |

The distinction below is central:

\[
\boxed{
\text{same form}
\neq
\text{same mechanism}
}
\]

---

## The mass-frequency bridge

UPI uses the relation:

\[
\boxed{
m=\frac{hf}{c^2}
}
\]

with the strict definition:

\[
\boxed{
f\equiv\frac{mc^2}{h}
}
\]

Here, the unqualified symbol \(f\) means the invariant rest-mass frequency associated with a massive state.

It must not automatically be confused with:

```text
f_gamma      photon frequency
f_transition atomic or molecular transition frequency
f_cavity     cavity resonance
f_clock      clock rate
f_mechanical mechanical oscillation
f_thermal    thermal frequency scale
f_string     string oscillator frequency
f_KK         Kaluza-Klein mode frequency
```

The relativistic dispersion relation remains:

\[
E^2=p^2c^2+m^2c^4
\]

Using:

\[
E=h\nu,\qquad p=\frac{h}{\lambda},\qquad m=\frac{hf}{c^2}
\]

gives:

\[
\boxed{
\nu^2=
\left(\frac{c}{\lambda}\right)^2+f^2
}
\]

This separates:

- total temporal frequency \(\nu\)
- momentum contribution \(c/\lambda\)
- invariant mass frequency \(f\)

---

## The 8 Hz reference coordinate

UPI currently uses 8 Hz as a reference coordinate:

\[
\boxed{
N_8=\frac{f}{8\,\mathrm{Hz}}
}
\]

and therefore:

\[
\boxed{
N_8=\frac{mc^2}{8h}
}
\]

This provides a common dimensionless coordinate for indexing masses and frequencies.

For an 8 Hz reference node:

\[
f_8=8\ \mathrm{Hz}
\]

\[
\tau_8=\frac{1}{8}=0.125\ \mathrm{s}
\]

\[
E_8=8h
\]

\[
m_8=\frac{8h}{c^2}
\]

Important:

> UPI does not currently claim that 8 Hz is a fundamental universal constant.

Current status:

```text
8 Hz as reference coordinate: DER
8 Hz as navigation clock: SYM
8 Hz as universal physical base mode: HYP
8 Hz as proven mass quantum: STOP
```

To promote 8 Hz from an indexing reference to a physical law, the project would need:

1. a unique physical mechanism
2. a derived spectrum
3. non-fitted predictions
4. experimental confirmation
5. compatibility with existing constraints

---

## Multi-view principle

The same underlying node may be displayed in different ways:

```text
table
spiral
graph
torus
timeline
spectrum
causal network
geometric map
```

The view may change, but the identity must remain stable.

\[
\boxed{
\text{identity first, view second}
}
\]

Example:

```yaml
node: UPI<ATOM,G1,T_ATOMIC,N_OXYGEN>

identity:
  atomic_number: 8
  symbol: O

views:
  standard_periodic_table:
    period: 2
    group: 16
    block: p

  spiral_view:
    ring: 2
    angular_position: calculated

  isotope_view:
    isotopes:
      - O-16
      - O-17
      - O-18

  biological_view:
    roles:
      - respiration
      - water chemistry
```

This allows different people to navigate the same scientific data through the representation that is easiest for them to understand.

---

## Initial domain map

UPI starts from large-scale domains before descending to micro-level detail.

```text
UPI
├── FOUNDATIONS
│   ├── constants
│   ├── units
│   ├── symmetry
│   └── logic
│
├── CLASSICAL
│   ├── mechanics
│   ├── electromagnetism
│   ├── thermodynamics
│   └── fluid dynamics
│
├── RELATIVITY
│   ├── special relativity
│   ├── general relativity
│   └── cosmology
│
├── QUANTUM
│   ├── quantum mechanics
│   ├── quantum field theory
│   ├── Standard Model
│   └── measurement theory
│
├── QUANTUM_GRAVITY
│   ├── string theory
│   ├── M-theory
│   ├── loop quantum gravity
│   ├── spin foams
│   ├── causal sets
│   ├── causal dynamical triangulations
│   ├── group field theory
│   ├── asymptotic safety
│   └── spectral geometry
│
├── INFORMATION
│   ├── Shannon information
│   ├── Landauer principle
│   ├── quantum information
│   ├── error correction
│   └── holography
│
├── MATTER
│   ├── particles
│   ├── nuclei
│   ├── atoms
│   ├── molecules
│   └── materials
│
├── LIFE
│   ├── molecular biology
│   ├── cells
│   ├── organisms
│   ├── ecosystems
│   └── evolution
│
└── KNOWLEDGE
    ├── cognition
    ├── language
    ├── institutions
    ├── technology
    └── scientific memory
```

---

## Theory map

The project currently tracks bridges among:

- classical mechanics
- electromagnetism
- thermodynamics
- special relativity
- general relativity
- quantum mechanics
- quantum field theory
- Standard Model
- Kaluza-Klein theory
- string theory
- M-theory
- loop quantum gravity
- spin foams
- group field theory
- causal set theory
- causal dynamical triangulations
- asymptotic safety
- spectral geometry
- noncommutative geometry
- AdS/CFT
- holography
- tensor networks
- quantum error correction
- topological quantum field theory
- Chern-Simons theory
- twistor theory
- amplituhedron and positive geometry
- renormalization group theory
- statistical mechanics
- information thermodynamics
- complexity science
- chemistry
- biology
- cognition
- technical and social knowledge systems

Each theory is stored as its own torus unless a valid bridge shows that two descriptions belong to the same physical structure.

---

## Example theory chain

A candidate high-level chain may be written as:

\[
\text{causal events}
\rightarrow
\text{quantum geometry}
\rightarrow
\mathcal D
\rightarrow
\operatorname{Spec}(\mathcal D)
\]

\[
\rightarrow
f_n
\rightarrow
m_n=\frac{hf_n}{c^2}
\rightarrow
\text{fields}
\rightarrow
\text{particles}
\]

\[
\rightarrow
\text{atoms}
\rightarrow
\text{chemistry}
\rightarrow
\text{biology}
\rightarrow
\text{knowledge}
\]

This is not yet a proven theory of everything.

The current major stop point is:

\[
\boxed{
\mathcal D_{\text{universe}}=?
}
\]

A complete theory would need one non-arbitrary structure capable of deriving, without fitting:

- spacetime dimension
- spacetime signature
- gauge symmetry
- particle spectrum
- particle masses
- mixing matrices
- coupling constants
- gravity
- dark matter behavior
- cosmological evolution
- the classical limit

---

## Open-problem mapping

UPI may be used to map unresolved problems such as:

1. quantum gravity
2. the Standard Model mass hierarchy
3. neutrino masses
4. dark matter
5. dark energy
6. the cosmological constant problem
7. the Hubble tension
8. vacuum selection
9. the Yang-Mills mass gap
10. confinement
11. the strong CP problem
12. baryogenesis
13. black-hole information
14. black-hole entropy
15. the Big Bang singularity
16. inflation
17. quantum measurement
18. the arrow of time
19. turbulence
20. high-temperature superconductivity

For each problem, the repository should store:

```yaml
problem:
candidate_bridge:
known_constraints:
current_stop:
required_prediction:
falsification_condition:
```

---

## Example node

```yaml
address:
  domain: SPECTRAL
  generation: G5
  torus: T_DIRAC
  node: N_ELECTRON

title: Electron mass-frequency node

status:
  - EST
  - DER

quantities:
  mass_kg: 9.1093837139e-31
  frequency_hz: 1.235589965e20
  index_8hz: 1.544487456e19

relations:
  - type: DERIVED_FROM
    source: electron_rest_mass
    equation: f = mc^2/h

mechanism:
  declared: rest-mass frequency representation

confusion_guard:
  - not a photon frequency
  - not an atomic transition frequency
  - not a directly observed mechanical oscillation

stop:
  reason: the framework does not yet derive the electron mass from first principles
```

---

## Example bridge

```yaml
bridge:
  id: B_KK_MASS

source:
  UPI<GEOMETRY,G3,T_COMPACT,N_RADIUS>

target:
  UPI<PARTICLE,G4,T_MASS_SPECTRUM,N_MODE>

relation:
  COMPACTIFIES_TO

equations:
  - p_n = n*hbar/R
  - m_n = n*hbar/(R*c)
  - f_n = n*c/(2*pi*R)
  - m_n = h*f_n/c^2

status:
  EST_WITHIN_MODEL

assumptions:
  - one compact circular dimension
  - periodic boundary condition
  - lower-dimensional observer

confusion_guard:
  - same formula does not identify a terrestrial cavity with an extra dimension
```

---

## Repository structure

```text
universal-physics-index/
├── README.md
├── README.sv.md
├── LICENSE
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── CITATION.cff
├── pyproject.toml
│
├── schemas/
│   ├── node.schema.json
│   ├── bridge.schema.json
│   └── theory.schema.json
│
├── data/
│   ├── constants/
│   ├── theories/
│   ├── particles/
│   ├── atoms/
│   ├── open-problems/
│   └── examples/
│
├── docs/
│   ├── index-specification.md
│   ├── scientific-method.md
│   ├── theory-map.md
│   ├── mass-frequency-bridge.md
│   ├── torus-model.md
│   ├── 8hz-reference.md
│   ├── open-problems.md
│   └── sv/
│
├── src/
│   └── upi/
│       ├── __init__.py
│       ├── constants.py
│       ├── physics.py
│       ├── models.py
│       ├── graph.py
│       ├── validation.py
│       └── cli.py
│
├── tests/
│   ├── test_physics.py
│   ├── test_schema.py
│   └── test_graph.py
│
└── .github/
    ├── workflows/
    ├── ISSUE_TEMPLATE/
    └── PULL_REQUEST_TEMPLATE.md
```

---

## Scientific method and safety rails

UPI uses the following rules:

### 1. Units must match

Dimensional consistency is required but does not prove a mechanism.

### 2. Definitions must be explicit

Every reused symbol must declare its meaning.

### 3. Derived is not established

A correct derivation from a speculative premise remains speculative physics.

### 4. Correlation is not causation

Frequency similarity, visual similarity, and structural analogy do not establish a shared physical cause.

### 5. No hidden parameter fitting

Observed values must not be inserted into a model and later presented as predictions.

### 6. Every hypothesis needs a failure condition

A claim that cannot fail cannot be tested.

### 7. Stop points are first-class data

An unresolved bridge must be recorded rather than covered with metaphor.

### 8. Competing theories remain separate

They may be connected through comparison nodes without being merged.

### 9. Primary sources are preferred

Research papers, official datasets, standards, and direct experimental reports should be cited whenever possible.

### 10. Symbolic layers must be labeled

Philosophical, visual, mythological, or symbolic mappings are allowed, but must use `SYM`.

---

## Contribution format

Every contribution should include:

```yaml
title:
address:
status:
domain:
equations:
definitions:
assumptions:
mechanism:
evidence:
primary_sources:
predictions:
falsification:
confusion_guard:
stop_reason:
```

A bold hypothesis is welcome.

An ambiguously labeled hypothesis is not.

---

## Proposed workflow

```text
1. Create or select a node
2. Define all symbols
3. Add equations
4. Add assumptions
5. Declare the mechanism
6. Assign status
7. Add evidence
8. Add confusion guards
9. Add falsification conditions
10. Connect the node with typed bridges
11. Record the first unresolved stop
```

---

## Roadmap

### Phase 1: Foundation

- [ ] Finalize node schema
- [ ] Finalize bridge schema
- [ ] Define status vocabulary
- [ ] Add exact SI constants
- [ ] Add mass-frequency conversion tools
- [ ] Add 8 Hz reference coordinate
- [ ] Add validation tests

### Phase 2: Physics graph

- [ ] Classical mechanics
- [ ] Electromagnetism
- [ ] Thermodynamics
- [ ] Relativity
- [ ] Quantum mechanics
- [ ] Quantum field theory
- [ ] Standard Model
- [ ] Cosmology

### Phase 3: Quantum gravity graph

- [ ] String theory
- [ ] M-theory
- [ ] Kaluza-Klein theory
- [ ] Loop quantum gravity
- [ ] Spin foams
- [ ] Group field theory
- [ ] Causal sets
- [ ] CDT
- [ ] Asymptotic safety
- [ ] Spectral geometry
- [ ] Holography

### Phase 4: Matter and life

- [ ] Particle registry
- [ ] Atomic registry
- [ ] Isotope registry
- [ ] Molecular graph
- [ ] Chemical reaction graph
- [ ] Biological organization map

### Phase 5: Interfaces

- [ ] Table view
- [ ] Spiral periodic view
- [ ] Torus view
- [ ] Theory graph
- [ ] Timeline view
- [ ] Evidence heatmap
- [ ] Stop-point explorer

### Phase 6: Open collaboration

- [ ] Public API
- [ ] Dataset export
- [ ] Citation resolver
- [ ] Community review process
- [ ] Reproducible notebooks
- [ ] Automated consistency checking

---

## Project status

```text
Status: Experimental research framework
Version: 0.1.0-alpha
Default language: English
Scientific claim level: exploratory
Production readiness: no
```

UPI is currently a framework for organizing and testing ideas.

It is not yet:

- a completed theory of everything
- a replacement for peer review
- an accepted physical theory
- a proof that 8 Hz is fundamental
- a derivation of the Standard Model
- a solution to quantum gravity

---

## Language policy

English is the default language for:

- source code
- schemas
- issue templates
- pull requests
- main documentation
- technical discussions

Swedish content is preserved where it already exists and should be placed in:

```text
README.sv.md
docs/sv/
```

Swedish concepts may remain untranslated when the original wording carries specific historical or legal meaning. In such cases, provide an English explanation beside the original term.

---

## Governance

The project should remain:

- open
- inspectable
- citation-driven
- critical
- friendly to unconventional hypotheses
- strict about scientific labels
- resistant to silent conflation

No contributor owns reality. Every node may be questioned.

---

## License

Recommended license:

```text
MIT License
```

This permits broad reuse while preserving attribution and the license notice.

For datasets, a separate open-data license may later be added if necessary.

---

## Citation

Recommended citation entry:

```bibtex
@software{universal_physics_index,
  title        = {Universal Physics Index},
  author       = {Universal Physics Index Contributors},
  year         = {2026},
  version      = {0.1.0-alpha},
  url          = {https://github.com/USERNAME/universal-physics-index},
  note         = {Experimental typed knowledge graph for physics and scientific theories}
}
```

Replace `USERNAME` after the repository is created.

---

## Final principle

\[
\boxed{
\text{causality builds the network}
}
\]

\[
\boxed{
\text{topology stabilizes the structure}
}
\]

\[
\boxed{
\text{the spectrum indexes physical modes}
}
\]

\[
\boxed{
m=\frac{hf}{c^2}
}
\]

\[
\boxed{
\text{information preserves identity}
}
\]

And the central rule of UPI remains:

\[
\boxed{
\text{connect everything that can be connected}
}
\]

\[
\boxed{
\text{but never erase the point where the connection fails}
}
\]

---

## Join the project

Open an issue for:

- a new theory node
- a mathematical bridge
- an experimental constraint
- a contradiction
- a failed derivation
- a visualization
- a data source
- a proposed test

The map becomes useful when people are allowed to improve it, break it, repair it, and show exactly why.
