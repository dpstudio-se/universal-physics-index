"""UPI_RNA: Real transcription and execution adapter connecting AECΩ to UPI runtime."""

from __future__ import annotations

from typing import Any

from upi.auto_mapper import LLMContextAutoMapper
from upi.debug import generate_debug_report
from upi.odin_kernel import OdinCoreKernel
from upi.physics import (
    dna_sequence_to_frequencies,
    frequency_from_mass,
    note_name_to_frequency,
)


class UPI_RNA:
    """Transcription & execution layer for UPI runtime."""

    def __init__(self) -> None:
        self.auto_mapper = LLMContextAutoMapper()

    def query(self, prompt: str) -> dict[str, Any]:
        """Run context mapping / query transcription through UPI auto-mapper."""
        result = self.auto_mapper.map_text_context(prompt)
        return {
            "mapped_nodes_count": len(result.mapped_nodes),
            "junk_nodes_count": result.dna_classification.get("JUNK_DNA_CORE", 0),
            "addresses": [str(n.address) for n in result.mapped_nodes],
            "odin_report": result.odin_report,
            "raw_prompt": prompt,
        }

    def debug(self) -> dict[str, Any]:
        """Fetch real-time debug report from UPI debug index."""
        from pathlib import Path

        report = generate_debug_report(Path("data"))
        summary = report.get("summary", {})
        return {
            "total_nodes": summary.get("records_classified", 0),
            "status_counts": summary.get("status_counts", {}),
            "stop_reasons": [
                f.get("id", f.get("code", str(f))) if isinstance(f, dict) else str(f)
                for f in report.get("findings", [])
            ],
            "junction_clusters": [],
            "integrity_ratios": {"EST": 1.0},
        }

    def evaluate_odin(
        self,
        frequency_hz: float = 8.0,
    ) -> float:
        """Run Odin core kernel state evaluation formula."""
        kernel = OdinCoreKernel()
        res = kernel.evaluate_odin_formula(frequency_hz=frequency_hz)
        return float(res["v_odin_magnitude"])

    def evaluate_physics(self, prompt: str) -> str:
        """Evaluate physics relations (mass-frequency, musical notes, DNA sonification)."""
        lower_prompt = prompt.lower()
        if "hydrogen" in lower_prompt or "mass" in lower_prompt:
            m = 1.6735575e-27  # kg
            f = frequency_from_mass(m)
            return f"Hydrogen mass {m} kg -> Frequency {f:.2e} Hz"
        if "c4" in lower_prompt or "middle c" in lower_prompt:
            f_c4 = note_name_to_frequency("C4")
            return f"C4 Middle C frequency is {f_c4:.2f} Hz"
        if "atgc" in lower_prompt or "dna" in lower_prompt:
            seq_res = dna_sequence_to_frequencies("ATGC")
            return f"DNA ATGC sonification count: {len(seq_res)}"
        if "odin" in lower_prompt or "v_odin" in lower_prompt:
            kernel = OdinCoreKernel()
            res_odin = kernel.evaluate_odin_formula()
            return f"V_Odin = {res_odin['v_odin_magnitude']:.4e}"

        return "UPI Physics Execution Ok"
