# Double-slit information physics

This note derives the UPI node in `data/examples/double_slit_information.json` and separates the experimentally tested formalism from interpretation-dependent language.

## 1. Joint path-detector state

For equal path amplitudes, let the particle path become correlated with detector or environment states:

\[
|\Psi\rangle = \frac{|L\rangle|D_L\rangle + e^{i\phi}|R\rangle|D_R\rangle}{\sqrt{2}}.
\]

The detector states need not be macroscopic. Any physical degree of freedom that records path information can play this role.

## 2. Reduced path state

The screen statistics are obtained from the reduced density operator

\[
\rho_{\mathrm{path}} = \operatorname{Tr}_D |\Psi\rangle\langle\Psi|.
\]

Define the detector overlap

\[
\gamma = \langle D_R|D_L\rangle.
\]

Then

\[
\rho_{\mathrm{path}} = \frac{1}{2}\left(
|L\rangle\langle L| + |R\rangle\langle R|
+ \gamma e^{-i\phi}|L\rangle\langle R|
+ \gamma^* e^{i\phi}|R\rangle\langle L|
\right).
\]

The off-diagonal terms carry path coherence. A path marker suppresses those terms according to the physical overlap of its states. No appeal to consciousness is required.

## 3. Screen probability

Let \(\psi_L(x)=\langle x|L\rangle\) and \(\psi_R(x)=\langle x|R\rangle\). The Born probability is

\[
P(x)=\frac{1}{2}\left(
|\psi_L(x)|^2+|\psi_R(x)|^2
+2\operatorname{Re}[\gamma e^{i\phi}\psi_L^*(x)\psi_R(x)]
\right).
\]

For equal path intensities, fringe visibility is

\[
V=|\gamma|.
\]

For two pure marker states with equal priors, optimal path distinguishability is

\[
D=\sqrt{1-|\gamma|^2},
\]

so the ideal system satisfies

\[
V^2+D^2=1.
\]

The experimentally relevant general bound is

\[
V^2+D^2\leq 1.
\]

This is the quantitative core of wave-particle complementarity in the two-path model.

## 4. Why this does not permit faster-than-light signalling

For a bipartite state \(\rho_{AB}\), let a remote party apply any trace-preserving local quantum operation \(\mathcal{E}_B\). The unconditioned local state remains

\[
\rho_A' = \operatorname{Tr}_B[(I_A\otimes\mathcal{E}_B)(\rho_{AB})]=\rho_A.
\]

Remote basis choices can change how coincidence data are partitioned after classical comparison, but cannot change the local unconditioned distribution. A quantum-eraser fringe appears only in conditioned subensembles; complementary subensembles sum to the same no-signalling distribution.

## 5. What is established and what remains interpretive

Established within standard quantum mechanics and experiment:

- path-detector entanglement controls reduced coherence;
- visibility and distinguishability satisfy the complementarity bound;
- conditioned correlations can recover complementary fringes;
- unconditioned statistics obey no-signalling.

Not selected by these equations alone:

- physical collapse versus no collapse;
- many-worlds, Bohmian, retrocausal, or superdeterministic ontology;
- consciousness-caused collapse;
- a fully predetermined future.

UPI therefore records the density-matrix and no-signalling relations as `EST`, while interpretation-specific extensions must be separate `HYP` or `DER` nodes with their own differentiating predictions.

## Primary literature

- B.-G. Englert, *Fringe Visibility and Which-Way Information: An Inequality*, Physical Review Letters 77, 2154 (1996). DOI: 10.1103/PhysRevLett.77.2154
- S. Duerr, T. Nonn, and G. Rempe, *Fringe Visibility and Which-Way Information in an Atom Interferometer*, Physical Review Letters 81, 5705 (1998). DOI: 10.1103/PhysRevLett.81.5705
- M. O. Scully and K. Druehl, *Quantum eraser: A proposed photon correlation experiment concerning observation and delayed choice in quantum mechanics*, Physical Review A 25, 2208 (1982). DOI: 10.1103/PhysRevA.25.2208
