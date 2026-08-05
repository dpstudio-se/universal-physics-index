# UPI Odysseus AI Agent Bridge (`upi-odysseus-bridge`)

Autonomous agent interface and LLM communication bridge implementing the [Odysseus AI Protocol](https://odysseusai.dev/) (`https://github.com/odysseus-dev/odysseus`) for the **Universal Physics Index (UPI)**.

## Overview

The Odysseus AI Bridge allows Large Language Models (LLMs), Autonomous AI Agents (AAI/AGI/ASI), and Puter.js applications to query, validate, and execute physics engines in UPI through structured Tool Calling manifests and intent parsing.

## Available Odysseus Tool Schemas

1. `sonify_dna`: Sonify biological DNA sequences into 4-base harmonic frequencies and 12-TET notes ($E=h \cdot f$).
2. `search_qudit_torus`: Run multi-torus classical state-vector qudit search simulations.
3. `audit_upi_node`: Validate JSON records against declared UPI scientific boundary schemas.
4. `run_aeco_evolution`: Execute self-evaluating evolution loops in the AECΩ module.
5. `get_physics_constant`: Query fundamental physical constants ($h, c, k_B, e, N_A$).

## Scientific Boundaries (`AGENTS.md`)

- Intent responses and tool outputs return status `DER` (derived from declared facts) or `HYP` (agent hypothesis).
- All tool executions are recorded with `verification_type: software_test`.
- Metaphors (Odysseus, AGI, ASI, Angelica, Torus) are strictly bound to `SYM` with mandatory confusion guards.
