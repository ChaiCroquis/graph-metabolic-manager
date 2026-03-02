"""
Graph — Data structure with local statistics store.

Provides the core graph operations used by all other components.
Local statistics (degree, congestion) are computed in O(1) per edge
without requiring full graph traversal.

Patent claims: 1-50 (foundational data structure for all claims)
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterator
from dataclasses import dataclass, field


@dataclass
class Node:
    """A node (information object) in the graph.

    Attributes:
        id: Unique identifier.
        label: Human-readable label.
        created_at: Timestamp when the node was created.
        last_accessed: Timestamp of last access.
        access_count: Number of times this node has been accessed.
        node_type: Semantic type tag (e.g. "normal", "truth", "garbage").
        is_protected: Whether this node is under rarity protection.
        phase: Rarity protection phase ("normal", "phase1", "phase2").
        phase_start_time: When the current protection phase started.
        spoke_up: Whether this node gained connections during protection.
        layer: Hierarchy layer ("edge", "core", "rare").
        activity: Activity score for hierarchy transitions.
        metadata: Arbitrary key-value metadata.
    """

    id: int
    label: str = ""
    created_at: float = 0.0
    last_accessed: float = 0.0
    access_count: int = 0
    node_type: str = "normal"
    is_protected: bool = False
    phase: str = "normal"
    phase_start_time: float = -1.0
    spoke_up: bool = False
    layer: str = "edge"
    activity: float = 0.0
    metadata: dict[str, object] = field(default_factory=dict)


class Graph:
    """Graph data structure with O(1) local statistics.

    This is the central data structure that all components operate on.
    It stores nodes, weighted edges, and maintains an adjacency index
    for fast local neighborhood queries.

    The design follows the patent's "local statistics store" concept:
    degree and congestion are computed from the adjacency structure
    without traversing the entire graph.

    Example:
        >>> g = Graph()
        >>> a = g.add_node("Alice")
        >>> b = g.add_node("Bob")
        >>> g.add_edge(a, b, weight=0.8)
        >>> g.degree(a)
        1
        >>> g.local_congestion(a, b)
        2.0
    """

    def __init__(self) -> None:
        self.nodes: dict[int, Node] = {}
        self.edges: dict[tuple[int, int], float] = {}
        self.adjacency: dict[int, set[int]] = defaultdict(set)
        self._next_id: int = 0

    # ------------------------------------------------------------------
    # Node operations
    # ------------------------------------------------------------------

    def add_node(
        self,
        label: str = "",
        node_type: str = "normal",
        created_at: float = 0.0,
        **metadata: object,
    ) -> int:
        """Add a new node and return its ID.

        Args:
            label: Human-readable label.
            node_type: Semantic type (default "normal").
            created_at: Creation timestamp.
            **metadata: Additional key-value data stored in node.metadata.

        Returns:
            The new node's integer ID.
        """
        nid = self._next_id
        self._next_id += 1
        node = Node(
            id=nid,
            label=label,
            node_type=node_type,
            created_at=created_at,
            last_accessed=created_at,
            metadata=metadata,
        )
        self.nodes[nid] = node
        return nid

    def remove_node(self, nid: int) -> None:
        """Remove a node and all its incident edges.

        Args:
            nid: Node ID to remove.
        """
        for neighbor in list(self.adjacency.get(nid, set())):
            self.remove_edge(nid, neighbor)
        self.adjacency.pop(nid, None)
        self.nodes.pop(nid, None)

    def has_node(self, nid: int) -> bool:
        """Check if a node exists."""
        return nid in self.nodes

    # ------------------------------------------------------------------
    # Edge operations
    # ------------------------------------------------------------------

    @staticmethod
    def _edge_key(u: int, v: int) -> tuple[int, int]:
        """Canonical edge key (smaller ID first)."""
        return (min(u, v), max(u, v))

    def add_edge(self, u: int, v: int, weight: float = 1.0) -> None:
        """Add or update an edge between u and v.

        Args:
            u: Source node ID.
            v: Target node ID.
            weight: Edge weight (default 1.0).

        Raises:
            ValueError: If u == v, either endpoint is missing, or weight < 0.
        """
        if u == v:
            raise ValueError("Self-loops are not allowed: u == v")
        if u not in self.nodes or v not in self.nodes:
            raise ValueError(
                f"Both endpoints must exist: node {u} or {v} not found"
            )
        if weight < 0:
            raise ValueError(f"Edge weight must be non-negative, got {weight}")
        key = self._edge_key(u, v)
        self.edges[key] = weight
        self.adjacency[u].add(v)
        self.adjacency[v].add(u)

    def remove_edge(self, u: int, v: int) -> None:
        """Remove the edge between u and v if it exists."""
        key = self._edge_key(u, v)
        if key in self.edges:
            del self.edges[key]
            self.adjacency[u].discard(v)
            self.adjacency[v].discard(u)

    def has_edge(self, u: int, v: int) -> bool:
        """Check if an edge exists between u and v."""
        return self._edge_key(u, v) in self.edges

    def get_weight(self, u: int, v: int) -> float:
        """Get edge weight. Returns 0.0 if the edge doesn't exist."""
        return self.edges.get(self._edge_key(u, v), 0.0)

    def set_weight(self, u: int, v: int, weight: float) -> None:
        """Update the weight of an existing edge."""
        key = self._edge_key(u, v)
        if key in self.edges:
            self.edges[key] = weight

    # ------------------------------------------------------------------
    # Local statistics (O(1) per query) — Patent claim 7
    # ------------------------------------------------------------------

    def degree(self, v: int) -> int:
        """Return the degree (number of neighbors) of node v."""
        return len(self.adjacency.get(v, set()))

    def local_congestion(self, u: int, v: int) -> float:
        """Compute local congestion C = deg(u) + deg(v).

        This is the key metric for adaptive decay rate calculation.
        It requires only the degrees of the two endpoints — no graph
        traversal needed.

        Args:
            u: First node ID.
            v: Second node ID.

        Returns:
            Sum of degrees of u and v.
        """
        return float(self.degree(u) + self.degree(v))

    def neighbors(self, v: int) -> set[int]:
        """Return the set of node v's neighbors."""
        return self.adjacency.get(v, set()).copy()

    # ------------------------------------------------------------------
    # Subgraph extraction
    # ------------------------------------------------------------------

    def subgraph(self, center: int, k_hop: int = 2) -> Graph:
        """Extract a k-hop neighborhood subgraph around a center node.

        Used by ConsistencyDiscovery to compute structural
        representations of local neighborhoods.

        Args:
            center: The center node ID.
            k_hop: Number of hops to expand (default 2).

        Returns:
            A new Graph containing only the neighborhood.
        """
        visited = {center}
        frontier = {center}
        for _ in range(k_hop):
            next_frontier: set[int] = set()
            for n in frontier:
                for nb in self.neighbors(n):
                    if nb not in visited:
                        visited.add(nb)
                        next_frontier.add(nb)
            frontier = next_frontier

        sub = Graph()
        id_map = {}
        for i, nid in enumerate(sorted(visited)):
            id_map[nid] = i
            original = self.nodes.get(nid)
            sub.nodes[i] = Node(
                id=i,
                label=original.label if original else f"sub_{nid}",
            )
            sub._next_id = max(sub._next_id, i + 1)

        for (u, v), w in self.edges.items():
            if u in visited and v in visited:
                sub.add_edge(id_map[u], id_map[v], w)

        return sub

    # ------------------------------------------------------------------
    # Aggregate statistics
    # ------------------------------------------------------------------

    def node_count(self) -> int:
        """Return the total number of nodes."""
        return len(self.nodes)

    def edge_count(self) -> int:
        """Return the total number of edges."""
        return len(self.edges)

    def avg_degree(self) -> float:
        """Return the average degree across all nodes."""
        if not self.nodes:
            return 0.0
        return sum(self.degree(n) for n in self.nodes) / len(self.nodes)

    def count_by_type(self, node_type: str) -> int:
        """Count nodes with a specific node_type."""
        return sum(1 for n in self.nodes.values() if n.node_type == node_type)

    def iter_edges(self) -> Iterator[tuple[int, int, float]]:
        """Iterate over all edges as (u, v, weight) tuples."""
        for (u, v), w in self.edges.items():
            yield u, v, w

    # ------------------------------------------------------------------
    # String representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return f"Graph(nodes={self.node_count()}, edges={self.edge_count()})"

    def summary(self) -> str:
        """Return a human-readable summary of the graph."""
        lines = [
            f"Graph: {self.node_count()} nodes, {self.edge_count()} edges",
            f"  Average degree: {self.avg_degree():.2f}",
        ]
        type_counts: dict[str, int] = defaultdict(int)
        for n in self.nodes.values():
            type_counts[n.node_type] += 1
        if len(type_counts) > 1:
            for t, c in sorted(type_counts.items()):
                lines.append(f"  {t}: {c} nodes")
        return "\n".join(lines)
