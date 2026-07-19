"""Graph module for managing typed relations between UPI nodes."""

from collections import defaultdict

from .models import Address, Bridge, EdgeType, PhysicsNode


class UPIGraph:
    """Directed typed graph for managing UPI nodes and bridges."""

    def __init__(self):
        self._nodes: dict[str, PhysicsNode] = {}
        self._bridges: list[Bridge] = []
        self._adjacency: dict[str, list[Bridge]] = defaultdict(list)
        self._reverse_adjacency: dict[str, list[Bridge]] = defaultdict(list)

    def add_node(self, node: PhysicsNode) -> None:
        """Add a node to the graph.

        Args:
            node: PhysicsNode instance

        Raises:
            ValueError: If node is invalid or already exists
        """
        address_str = str(node.address)

        errors = node.validate()
        if errors:
            raise ValueError(f"Invalid node: {'; '.join(errors)}")

        if address_str in self._nodes:
            raise ValueError(f"Node {address_str} already exists")

        self._nodes[address_str] = node

    def add_bridge(self, bridge: Bridge) -> None:
        """Add a bridge (edge) to the graph.

        Args:
            bridge: Bridge instance

        Raises:
            ValueError: If bridge is invalid
        """
        errors = bridge.validate()
        if errors:
            raise ValueError(f"Invalid bridge: {'; '.join(errors)}")

        source_str = str(bridge.source)
        target_str = str(bridge.target)

        if source_str not in self._nodes:
            raise ValueError(f"Source node {source_str} not found")
        if target_str not in self._nodes:
            raise ValueError(f"Target node {target_str} not found")

        self._bridges.append(bridge)
        self._adjacency[source_str].append(bridge)
        self._reverse_adjacency[target_str].append(bridge)

    def get_node(self, address: Address) -> PhysicsNode | None:
        """Get a node by address."""
        return self._nodes.get(str(address))

    def get_outgoing_bridges(self, address: Address) -> list[Bridge]:
        """Get all outgoing bridges from a node."""
        return self._adjacency.get(str(address), [])

    def get_incoming_bridges(self, address: Address) -> list[Bridge]:
        """Get all incoming bridges to a node."""
        return self._reverse_adjacency.get(str(address), [])

    def get_bridges_by_type(self, edge_type: EdgeType) -> list[Bridge]:
        """Get all bridges of a specific type."""
        return [b for b in self._bridges if b.relation == edge_type]

    def get_all_nodes(self) -> dict[str, PhysicsNode]:
        """Return all nodes (read-only view)."""
        return dict(self._nodes)

    def get_all_bridges(self) -> list[Bridge]:
        """Return all bridges (read-only copy)."""
        return list(self._bridges)

    def get_node_count(self) -> int:
        """Get total number of nodes."""
        return len(self._nodes)

    def get_bridge_count(self) -> int:
        """Get total number of bridges."""
        return len(self._bridges)

    def get_related_nodes(self, address: Address, edge_type: EdgeType | None = None) -> list[PhysicsNode]:
        """Get nodes directly related to the given node via outgoing bridges.

        Args:
            address: Source node address
            edge_type: Optional filter by edge type

        Returns:
            List of related PhysicsNode instances
        """
        related = []
        outgoing = self.get_outgoing_bridges(address)

        for bridge in outgoing:
            if edge_type is None or bridge.relation == edge_type:
                target_node = self.get_node(bridge.target)
                if target_node:
                    related.append(target_node)

        return related

    def get_dependency_chain(self, address: Address, max_depth: int = 10) -> set[str]:
        """Get all nodes that this node depends on (transitive closure).

        Uses breadth-first search up to max_depth.

        Args:
            address: Starting node address
            max_depth: Maximum traversal depth

        Returns:
            Set of node address strings that are reachable
        """
        visited: set[str] = set()
        queue: list[tuple] = [(str(address), 0)]

        while queue:
            current_addr, depth = queue.pop(0)

            if current_addr in visited or depth > max_depth:
                continue

            visited.add(current_addr)

            # Follow DERIVED_FROM edges as dependencies
            node = self._nodes.get(current_addr)
            if node:
                for bridge in self._adjacency.get(current_addr, []):
                    if bridge.relation == EdgeType.DERIVED_FROM:
                        target_str = str(bridge.target)
                        if target_str not in visited:
                            queue.append((target_str, depth + 1))

        return visited

    def validate_graph_consistency(self) -> list[str]:
        """Validate graph integrity.

        Returns list of error strings (empty if consistent).
        """
        errors = []

        # Check all node references
        for bridge in self._bridges:
            source_str = str(bridge.source)
            target_str = str(bridge.target)

            if source_str not in self._nodes:
                errors.append(f"Bridge references non-existent source: {source_str}")
            if target_str not in self._nodes:
                errors.append(f"Bridge references non-existent target: {target_str}")

        # Check for orphaned nodes (optional: could be valid)

        return errors

    def export_to_dict(self) -> dict:
        """Export graph to dictionary format."""
        return {
            "nodes": {
                addr: {
                    "title": node.title,
                    "status": node.status.value,
                    "description": node.description[:100] + "..." if len(node.description) > 100 else node.description
                }
                for addr, node in self._nodes.items()
            },
            "bridges": [
                {
                    "source": str(b.source),
                    "target": str(b.target),
                    "relation": b.relation.value,
                    "status": b.status.value
                }
                for b in self._bridges
            ],
            "stats": {
                "node_count": len(self._nodes),
                "bridge_count": len(self._bridges)
            }
        }
