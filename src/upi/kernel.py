"""Inside-Out Core Kernel Engine for the Universal Physics Index (UPI).

Coordinating core physics calculations, Qudit registers, SUNET topology,
AECΩ evolution cycles, evidence boundary auditing, and Odysseus AI Tool Routing.
"""

from __future__ import annotations

from typing import Any

from .constants import C, H
from .graph import UPIGraph
from .models import ScientificStatus
from .physics import dna_sequence_to_frequencies, frequency_from_mass, mass_from_frequency
from .qudit import search_torus_register
from .sunet import load_sunet_topology
from .validation import validate_record_boundaries


class UPIKernel:
    """Inside-out core kernel unifying UPI status-tracking, physics, and agent routing."""

    def __init__(self) -> None:
        self.graph = UPIGraph()
        self.sunet_mapper = load_sunet_topology()
        self.status = "HEALTHY"
        self.version = "0.1.0-alpha"

    def audit_status(self) -> dict[str, Any]:
        """Return system health and scientific status audit."""
        return self.generate_kernel_status()

    def execute_physics_frequency(self, frequency_hz: float) -> dict[str, Any]:
        """Calculate energy and mass equivalent from frequency (E=h*f, m=h*f/c^2)."""
        mass_kg = mass_from_frequency(frequency_hz)
        energy_j = H * frequency_hz
        return {
            "operation": "execute_physics_frequency",
            "status": ScientificStatus.DER.value,
            "verification_type": "software_test",
            "frequency_hz": frequency_hz,
            "energy_j": energy_j,
            "mass_equivalent_kg": mass_kg,
            "equation": "E = h*f, m = E / c^2",
            "confusion_guard": "Mass equivalent calculation; not the rest mass of an arbitrary oscillating particle."
        }

    def execute_physics_mass(self, mass_kg: float) -> dict[str, Any]:
        """Calculate rest-mass frequency from mass (f=m*c^2/h)."""
        frequency_hz = frequency_from_mass(mass_kg)
        return {
            "operation": "execute_physics_mass",
            "status": ScientificStatus.DER.value,
            "verification_type": "software_test",
            "mass_kg": mass_kg,
            "frequency_hz": frequency_hz,
            "equation": "f = m*c^2 / h",
        }

    def sonify_dna(self, sequence: str, reference_a4_hz: float = 440.0) -> dict[str, Any]:
        """Sonify nucleotide sequence into 12-TET frequencies and mass equivalents."""
        traces = dna_sequence_to_frequencies(sequence, reference_a4_hz=reference_a4_hz)
        return {
            "operation": "sonify_dna",
            "status": ScientificStatus.DER.value,
            "verification_type": "software_test",
            "sequence": sequence,
            "reference_a4_hz": reference_a4_hz,
            "total_bases": len(traces),
            "traces": traces,
            "confusion_guard": "Acoustic sonification maps sequence frequencies for analysis; does not claim biological mechanics."
        }

    def search_qudit(self, dimensions: list[int], targets: list[int], iterations: int = 2) -> dict[str, Any]:
        """Execute classical multi-torus qudit search simulator."""
        dims = tuple(int(x) for x in dimensions)
        targs = tuple(int(x) for x in targets)
        res = search_torus_register(dims, targs, iterations=iterations)
        return {
            "operation": "search_qudit_torus",
            "status": ScientificStatus.DER.value,
            "verification_type": "software_test",
            "dimensions": res.dimensions,
            "total_states": res.total_states,
            "target_indices": list(res.target_indices),
            "iterations": res.iterations,
            "success_probability": res.success_probability,
            "interpretation": "classical_state_vector_qudit_simulator"
        }

    def audit_record(self, record_data: dict[str, Any]) -> dict[str, Any]:
        """Validate evidence boundaries for a candidate UPI record."""
        errors = validate_record_boundaries(record_data)
        if not errors:
            return {
                "operation": "audit_record",
                "status": ScientificStatus.EST.value,
                "verification_type": "software_test",
                "valid": True,
                "address": record_data.get("address"),
                "scientific_status": record_data.get("status")
            }
        return {
            "operation": "audit_record",
            "status": ScientificStatus.ERR.value,
            "verification_type": "software_test",
            "valid": False,
            "errors": errors
        }

    def inspect_sunet(self, institution: str | None = None) -> dict[str, Any]:
        """Inspect SUNET backbone topology and connected HPC/Synchrotron nodes."""
        if institution:
            nodes = self.sunet_mapper.find_nodes_by_institution(institution)
            return {
                "operation": "inspect_sunet",
                "status": ScientificStatus.DER.value,
                "verification_type": "source_metadata_check",
                "query": institution,
                "matching_nodes": [n.to_dict() for n in nodes]
            }
        return self.sunet_mapper.generate_audit_summary()

    def generate_kernel_status(self) -> dict[str, Any]:
        """Generate inside-out kernel status report."""
        return {
            "kernel_version": self.version,
            "status": self.status,
            "graph_nodes": len(self.graph._nodes),
            "graph_bridges": len(self.graph._bridges),
            "sunet_nodes": len(self.sunet_mapper.nodes),
            "verification_type": "software_test",
            "claims_experimental_verification": False,
            "confusion_guard": "Kernel state reflects software simulation and index provenance."
        }


# Global singleton instance for inside-out runtime access
_KERNEL_INSTANCE: UPIKernel | None = None


def get_kernel() -> UPIKernel:
    """Get or initialize global UPIKernel singleton."""
    global _KERNEL_INSTANCE
    if _KERNEL_INSTANCE is None:
        _KERNEL_INSTANCE = UPIKernel()
    return _KERNEL_INSTANCE
