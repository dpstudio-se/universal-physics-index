"""LLM Context Auto-Mapper for UPI.

This module inspects LLM context (prompts, completions, raw text, structured dicts),
extracts physics claims, quantities, equations, and status indicators,
classifies them into Vortex-DNA Memory cores (Active DNA, Hypothesis, Junk DNA Archive),
runs physics engine checks (E=hf, m=hf/c², N8 indexing, signal normalization),
and transcribes them into the live UPI Graph via RealtimeUPIIndex.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from .constants import C
from .graph import UPIGraph
from .models import (
    Address,
    EdgeType,
    Quantity,
    ScientificStatus,
)
from .odin_kernel import OdinCoreKernel
from .physics import (
    energy_from_frequency,
    frequency_from_mass,
    index8_from_frequency,
    mass_from_frequency,
)
from .realtime import RealtimePayload, RealtimeUPIIndex, RealtimeWriteResult


@dataclass
class MappedContextNode:
    """Extracted and classified node from LLM context."""

    address: Address
    title: str
    description: str
    status: ScientificStatus
    dna_core: str  # SCIENTIFIC_CORE, HYPOTHESIS_CORE, JUNK_DNA_CORE (SYMBOLIC), MEMORY_CORE
    equations: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    quantities: list[Quantity] = field(default_factory=list)
    calculated_physics: dict[str, Any] = field(default_factory=dict)
    target_address: Address | None = None
    relation: EdgeType | None = None


@dataclass
class AutoMapperResult:
    """Result of auto-mapping LLM context into the UPI engine and graph."""

    nodes_extracted: int
    nodes_written: int
    bridges_written: int
    dna_classification: dict[str, int]
    physics_evaluations: list[dict[str, Any]]
    mapped_nodes: list[MappedContextNode]
    ingest_results: list[RealtimeWriteResult]
    graph_export: dict[str, Any]
    odin_report: dict[str, Any] = field(default_factory=dict)


class LLMContextAutoMapper:
    """Auto-mapper translating LLM context into live UPI Physics Engine & DNA Memory."""

    def __init__(self, graph: UPIGraph | None = None):
        self.graph = graph or UPIGraph()
        self.realtime_index = RealtimeUPIIndex(self.graph)
        self.odin_kernel = OdinCoreKernel()

    def map_text_context(
        self,
        text: str,
        default_domain: str = "information_physics",
        source: str = "llm_context_automapper",
    ) -> AutoMapperResult:
        """Parse raw text context, extract structured claims, classify DNA layers, and write to live graph."""
        nodes_data = self._extract_claims_from_text(text, default_domain)
        return self.ingest_nodes(nodes_data, source=source)

    def map_structured_context(
        self,
        payloads: list[dict[str, Any]],
        source: str = "llm_structured_automapper",
    ) -> AutoMapperResult:
        """Parse structured context dictionaries into live graph nodes."""
        nodes_data: list[MappedContextNode] = []
        for idx, item in enumerate(payloads):
            addr_str = item.get("address", f"UPI<information_physics,1,llm_context,node_{idx+1}>")
            try:
                address = Address.from_string(addr_str)
            except ValueError:
                address = Address("information_physics", 1, "llm_context", f"node_{idx+1}")

            status_str = item.get("status", "SYM").upper()
            try:
                status = ScientificStatus(status_str)
            except ValueError:
                status = ScientificStatus.SYM

            dna_core = self._classify_dna_core(status, item.get("equations", []))

            target_addr = None
            if "target" in item:
                try:
                    target_addr = Address.from_string(item["target"])
                except ValueError:
                    pass

            relation = None
            if "relation" in item:
                try:
                    relation = EdgeType(item["relation"])
                except ValueError:
                    pass

            mapped_node = MappedContextNode(
                address=address,
                title=item.get("title", f"Context Claim {idx+1}"),
                description=item.get("description", "Extracted claim from LLM context"),
                status=status,
                dna_core=dna_core,
                equations=item.get("equations", []),
                assumptions=item.get("assumptions", []),
                target_address=target_addr,
                relation=relation,
            )
            nodes_data.append(mapped_node)

        return self.ingest_nodes(nodes_data, source=source)

    def ingest_nodes(
        self,
        nodes: list[MappedContextNode],
        source: str = "automapper",
    ) -> AutoMapperResult:
        """Ingest extracted context nodes, perform physics calculations, and write to live index."""
        ingest_results: list[RealtimeWriteResult] = []
        physics_evaluations: list[dict[str, Any]] = []
        dna_counts = {
            "SCIENTIFIC_CORE": 0,
            "HYPOTHESIS_CORE": 0,
            "JUNK_DNA_CORE": 0,
            "MEMORY_CORE": 0,
        }

        nodes_written = 0
        bridges_written = 0
        combined_text = ""

        for node in nodes:
            combined_text += f" {node.title} {node.description}"
            # 1. Physics Engine Evaluations
            physics_eval = self._evaluate_physics_for_node(node)
            if physics_eval:
                physics_evaluations.append(physics_eval)
                node.calculated_physics = physics_eval

            # 2. Track DNA Classification
            core = node.dna_core
            dna_counts[core] = dna_counts.get(core, 0) + 1

            # 3. Transcribe via RNA Realtime Payload
            payload = RealtimePayload(
                address=node.address,
                title=node.title,
                description=node.description,
                status=node.status,
                source=source,
                relation=node.relation,
                target=node.target_address,
                equations=node.equations,
                assumptions=node.assumptions,
                tags=[node.dna_core.lower()],
                notes=f"DNA Core: {node.dna_core}",
            )

            res = self.realtime_index.ingest(payload)
            ingest_results.append(res)
            if res.wrote_node:
                nodes_written += 1
            if res.wrote_bridge:
                bridges_written += 1

        # 4. Automated OdinCore Kernel Execution
        self.odin_kernel.singularity.check(combined_text)
        self.odin_kernel.core.pulse()
        tf1776_report = self.odin_kernel.run_selfish_gene_loop(combined_text)

        odin_report = {
            "kernel_status": self.odin_kernel.generate_status_report(),
            "tf1776_report": {
                "transparency_score": tf1776_report.transparency_score,
                "censorship_detected": tf1776_report.censorship_detected,
                "iterations_run": tf1776_report.iterations_run,
                "audit_findings": tf1776_report.audit_findings,
            },
        }

        return AutoMapperResult(
            nodes_extracted=len(nodes),
            nodes_written=nodes_written,
            bridges_written=bridges_written,
            dna_classification=dna_counts,
            physics_evaluations=physics_evaluations,
            mapped_nodes=nodes,
            ingest_results=ingest_results,
            graph_export=self.graph.export_to_dict(),
            odin_report=odin_report,
        )

    def _extract_claims_from_text(
        self,
        text: str,
        default_domain: str,
    ) -> list[MappedContextNode]:
        """Simple deterministic NLP/pattern extractor for context text."""
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        if not paragraphs:
            paragraphs = [text.strip()] if text.strip() else []

        mapped_nodes: list[MappedContextNode] = []

        for idx, paragraph in enumerate(paragraphs):
            # Extract Address if present, e.g. UPI<domain,gen,torus,node>
            addr_match = re.search(r"UPI<([^,]+),([0-9]+),([^,]+),([^>]+)>", paragraph)
            if addr_match:
                d, g, t, n = addr_match.groups()
                address = Address(d, int(g), t, n)
            else:
                address = Address(default_domain, 1, "llm_context", f"node_{idx+1}")

            # Extract Status
            status = ScientificStatus.SYM  # Default status for raw context (Junk DNA / SYM)
            for status_candidate in ScientificStatus:
                if f"STATUS:{status_candidate.value}" in paragraph.upper() or f"[{status_candidate.value}]" in paragraph.upper():
                    status = status_candidate
                    break
                elif f"STATUS = {status_candidate.value}" in paragraph.upper():
                    status = status_candidate
                    break

            # Extract Equations
            equations = re.findall(r"(?:[E|m|f|Z]\s*=\s*[^;\n]+)", paragraph)

            # Classify DNA Core
            dna_core = self._classify_dna_core(status, equations)

            # Title extraction
            lines = [line.strip() for line in paragraph.split("\n") if line.strip()]
            title = lines[0][:60] if lines else f"Context Fragment {idx+1}"

            mapped_nodes.append(
                MappedContextNode(
                    address=address,
                    title=title,
                    description=paragraph,
                    status=status,
                    dna_core=dna_core,
                    equations=equations,
                    assumptions=["Extracted from raw LLM context"],
                )
            )

        return mapped_nodes

    def _classify_dna_core(self, status: ScientificStatus, equations: list[str]) -> str:
        """Classify context item into Vortex-DNA memory cores.

        SCIENTIFIC_CORE: Verified established facts/equations (EST).
        HYPOTHESIS_CORE: Testable hypotheses (HYP).
        JUNK_DNA_CORE: Unverified, non-coding, background, or symbolic text (SYM, STOP, ERR).
        MEMORY_CORE: Derived / revision records (DER).
        """
        if status == ScientificStatus.EST:
            return "SCIENTIFIC_CORE"
        elif status == ScientificStatus.HYP:
            return "HYPOTHESIS_CORE"
        elif status == ScientificStatus.DER:
            return "MEMORY_CORE"
        else:
            # SYM, STOP, ERR or unclassified raw conversational context
            return "JUNK_DNA_CORE"

    def _evaluate_physics_for_node(self, node: MappedContextNode) -> dict[str, Any] | None:
        """Execute physical engine functions (E=hf, f=mc^2/h, N8 indexing) if quantities exist in node."""
        for eq in node.equations:
            # Check for frequency values in Hz
            freq_match = re.search(r"(\d+(?:\.\d+)?)\s*Hz", eq, re.IGNORECASE)
            if freq_match:
                freq = float(freq_match.group(1))
                energy = energy_from_frequency(freq)
                mass = mass_from_frequency(freq)
                n8 = index8_from_frequency(freq)
                return {
                    "node_address": str(node.address),
                    "input_frequency_hz": freq,
                    "output_energy_j": energy,
                    "output_mass_kg": mass,
                    "output_n8": n8,
                    "engine_status": "EVALUATED_PHYSICS",
                }

            # Check for mass values in kg
            mass_match = re.search(r"(\d+(?:\.\d+)?(?:e[-+]?\d+)?)\s*kg", eq, re.IGNORECASE)
            if mass_match:
                mass = float(mass_match.group(1))
                freq = frequency_from_mass(mass)
                energy = mass * (C ** 2)
                return {
                    "node_address": str(node.address),
                    "input_mass_kg": mass,
                    "output_frequency_hz": freq,
                    "output_energy_j": energy,
                    "engine_status": "EVALUATED_PHYSICS",
                }

        return None
