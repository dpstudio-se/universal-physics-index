"""SUNET academic network infrastructure explorer and topology mapper."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class SunetNode:
    """Represents a physical or identity node in the SUNET academic network topology."""

    node_id: str
    name: str
    facility_type: str
    address: str
    connected_institutions: tuple[str, ...]
    capacity_gbps: int | None = None
    systems: tuple[str, ...] = ()
    backbone_uplink: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert node attributes to dictionary."""
        data: dict[str, Any] = {
            "node_id": self.node_id,
            "name": self.name,
            "facility_type": self.facility_type,
            "address": self.address,
            "connected_institutions": list(self.connected_institutions),
        }
        if self.capacity_gbps is not None:
            data["capacity_gbps"] = self.capacity_gbps
        if self.systems:
            data["systems"] = list(self.systems)
        if self.backbone_uplink:
            data["backbone_uplink"] = self.backbone_uplink
        return data


class SunetTopologyMapper:
    """Maps and audits the SUNET academic research network backbone."""

    def __init__(self, data_path: Path | str | None = None) -> None:
        if data_path is None:
            data_path = Path(__file__).resolve().parents[2] / "data" / "sources" / "sunet_network_map.json"
        else:
            data_path = Path(data_path)

        self.data_path = data_path
        self._raw_data: dict[str, Any] = {}
        self.nodes: dict[str, SunetNode] = {}
        self._load_topology()

    def _load_topology(self) -> None:
        """Load network topology from JSON data file."""
        if not self.data_path.is_file():
            raise FileNotFoundError(f"SUNET topology map file not found: {self.data_path}")

        self._raw_data = json.loads(self.data_path.read_text(encoding="utf-8"))

        # Parse backbone ring nodes
        for item in self._raw_data.get("backbone_nodes", []):
            node = SunetNode(
                node_id=item["node_id"],
                name=item["name"],
                facility_type=item.get("type", "backbone_ring"),
                address=item["address"],
                connected_institutions=tuple(item.get("connected_institutions", [])),
                capacity_gbps=item.get("capacity_gbps"),
            )
            self.nodes[node.node_id] = node

        # Parse HPC and Synchrotron research nodes
        for item in self._raw_data.get("hpc_research_nodes", []):
            node = SunetNode(
                node_id=item["node_id"],
                name=item["name"],
                facility_type=item.get("facility_type", "research_facility"),
                address=item["address"],
                connected_institutions=tuple(item.get("connected_institutions", [])),
                systems=tuple(item.get("systems", [])),
                backbone_uplink=item.get("backbone_uplink"),
            )
            self.nodes[node.node_id] = node

    def get_node(self, node_id: str) -> SunetNode | None:
        """Get a node by its ID."""
        return self.nodes.get(node_id)

    def list_hpc_centers(self) -> list[SunetNode]:
        """Return list of NAISS supercomputing nodes connected to SUNET."""
        return [node for node in self.nodes.values() if node.facility_type == "supercomputing_center"]

    def list_backbone_rings(self) -> list[SunetNode]:
        """Return list of DWDM optical backbone ring nodes."""
        return [node for node in self.nodes.values() if node.facility_type == "backbone_ring"]

    def find_nodes_by_institution(self, inst_name: str) -> list[SunetNode]:
        """Find nodes connected to a specific Swedish university or institution."""
        query = inst_name.lower()
        results: list[SunetNode] = []
        for node in self.nodes.values():
            if any(query in inst.lower() for inst in node.connected_institutions) or query in node.name.lower():
                results.append(node)
        return results

    def generate_audit_summary(self) -> dict[str, Any]:
        """Generate a UPI status-compliant network summary report."""
        return {
            "operation": "upi_sunet_topology_audit",
            "status": "DER",
            "verification_type": "source_metadata_check",
            "claims_experimental_verification": False,
            "total_nodes_mapped": len(self.nodes),
            "hpc_supercomputers": len(self.list_hpc_centers()),
            "optical_backbone_rings": len(self.list_backbone_rings()),
            "evidence_boundary": self._raw_data.get("evidence_boundary"),
            "confusion_guard": self._raw_data.get("confusion_guard"),
        }


def load_sunet_topology(data_path: Path | str | None = None) -> SunetTopologyMapper:
    """Helper to instantiate and load SUNET topology mapper."""
    return SunetTopologyMapper(data_path=data_path)
