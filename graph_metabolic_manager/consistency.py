"""
Consistency Discovery — Find hidden relationships via structural similarity.

Analyzes the structural "fingerprint" of graph neighborhoods using
Laplacian eigenvalue spectra, then discovers non-obvious relationships
between nodes whose neighborhoods are structurally similar but not
directly connected.

Patent claims: 21–26

Key concepts:
- Structural representation: Laplacian eigenvalue spectrum of k-hop subgraph
- Consistency score: S = (7*S_sys + 2*S_rel + 1*S_attr) / 10
- Sandwich threshold: theta_L <= S <= theta_U
  - Too low: not similar enough
  - Too high: trivially obvious ("apple is similar to apple")
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import numpy as np

from ._logging import TRACE

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .graph import Graph


# ------------------------------------------------------------------
# Default parameters (Patent specification)
# ------------------------------------------------------------------
DEFAULT_DIM = 8           # Dimensionality of structural representation
DEFAULT_THETA_L = 0.70    # Lower threshold (too low = not similar)
DEFAULT_THETA_U = 0.80    # Upper threshold (too high = trivially obvious)
DEFAULT_W_SYS = 7         # Weight for structural similarity
DEFAULT_W_REL = 2         # Weight for relational similarity
DEFAULT_W_ATTR = 1        # Weight for attribute similarity
DEFAULT_K_HOP = 2         # Neighborhood radius for subgraph extraction


# ------------------------------------------------------------------
# Relational and Attribute similarity
# ------------------------------------------------------------------

def relational_similarity(graph: Graph, nid_a: int, nid_b: int) -> float:
    """Compute relational similarity via Jaccard coefficient of neighborhoods.

    Formula: J(A, B) = |N(A) ∩ N(B)| / |N(A) ∪ N(B)|

    Measures how much two nodes share the same structural context —
    nodes with overlapping neighborhoods are relationally similar.

    Args:
        graph: The graph containing both nodes.
        nid_a: First node ID.
        nid_b: Second node ID.

    Returns:
        Jaccard coefficient in [0, 1]. Returns 0.0 if both nodes
        have no neighbors (excluding each other).

    Example:
        >>> # If A and B share 3 of 5 total neighbors:
        >>> relational_similarity(g, a, b)
        0.6
    """
    neighbors_a = graph.neighbors(nid_a)
    neighbors_b = graph.neighbors(nid_b)

    # Remove each other to avoid trivial self-reference
    neighbors_a.discard(nid_b)
    neighbors_b.discard(nid_a)

    if not neighbors_a and not neighbors_b:
        return 0.0

    intersection = len(neighbors_a & neighbors_b)
    union = len(neighbors_a | neighbors_b)

    return intersection / union if union > 0 else 0.0


def attribute_similarity(graph: Graph, nid_a: int, nid_b: int) -> float:
    """Compute attribute similarity between two nodes.

    Formula: S_attr = (type_match + metadata_jaccard) / 2

    Components:
    - type_match: 1.0 if node_type is identical, 0.0 otherwise
    - metadata_jaccard: Fraction of shared metadata keys with equal values

    This captures both the semantic category (node_type) and the detailed
    properties (metadata) of information objects.

    Args:
        graph: The graph containing both nodes.
        nid_a: First node ID.
        nid_b: Second node ID.

    Returns:
        Attribute similarity in [0, 1].

    Example:
        >>> # Same type, 2 of 3 metadata keys match:
        >>> attribute_similarity(g, a, b)
        0.833
    """
    node_a = graph.nodes.get(nid_a)
    node_b = graph.nodes.get(nid_b)

    if node_a is None or node_b is None:
        return 0.0

    # Component 1: Type match
    type_match = 1.0 if node_a.node_type == node_b.node_type else 0.0

    # Component 2: Metadata Jaccard (keys with matching values)
    keys_a = set(node_a.metadata.keys())
    keys_b = set(node_b.metadata.keys())
    all_keys = keys_a | keys_b

    if not all_keys:
        # No metadata on either node — score based on type match only
        return type_match

    matching = sum(
        1 for k in all_keys
        if k in node_a.metadata and k in node_b.metadata
        and node_a.metadata[k] == node_b.metadata[k]
    )
    metadata_jaccard = matching / len(all_keys)

    return (type_match + metadata_jaccard) / 2.0


# ------------------------------------------------------------------
# Structural representation
# ------------------------------------------------------------------

def compute_structural_repr(graph: Graph, dim: int = DEFAULT_DIM) -> np.ndarray:
    """Compute the Laplacian eigenvalue structural representation.

    The structural fingerprint of a graph is computed as:
    1. Build the adjacency matrix A
    2. Compute the Laplacian L = D - A (D = degree matrix)
    3. Extract the lowest `dim` eigenvalues of L

    These eigenvalues capture the fundamental structural properties
    of the graph (connectivity, clustering, etc.) in a compact vector.

    Args:
        graph: Graph to compute representation for.
        dim: Number of eigenvalues to use (default 8).

    Returns:
        Numpy array of shape (dim,) containing the lowest eigenvalues.

    Example:
        >>> path_graph = make_path(5)
        >>> repr_vec = compute_structural_repr(path_graph)
        >>> repr_vec.shape
        (8,)
    """
    n = graph.node_count()
    if n <= 1:
        return np.zeros(dim)

    node_ids = sorted(graph.nodes.keys())
    id_map = {nid: i for i, nid in enumerate(node_ids)}

    # Build adjacency matrix
    A = np.zeros((n, n))
    for (u, v), w in graph.edges.items():
        if u in id_map and v in id_map:
            i, j = id_map[u], id_map[v]
            A[i][j] = w
            A[j][i] = w

    # Laplacian: L = D - A
    D = np.diag(A.sum(axis=1))
    L = D - A

    # Eigenvalue decomposition
    eigenvalues = np.sort(np.real(np.linalg.eigvalsh(L)))

    result = np.zeros(dim)
    result[: min(len(eigenvalues), dim)] = eigenvalues[:dim]
    return result


# ------------------------------------------------------------------
# Similarity metrics
# ------------------------------------------------------------------

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two vectors."""
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def structural_diff_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Inverse Euclidean distance similarity: 1 / (1 + ||a - b||)."""
    return 1.0 / (1.0 + float(np.linalg.norm(a - b)))


def sign_agreement(a: np.ndarray, b: np.ndarray) -> float:
    """Fraction of elements with matching signs."""
    if len(a) == 0:
        return 0.0
    return float(np.sum(np.sign(a) == np.sign(b)) / len(a))


def consistency_score(
    repr_rare: np.ndarray,
    repr_candidate: np.ndarray,
    s_rel: float = 0.5,
    s_attr: float = 0.5,
    w_sys: int = DEFAULT_W_SYS,
    w_rel: int = DEFAULT_W_REL,
    w_attr: int = DEFAULT_W_ATTR,
) -> float:
    """Compute the consistency score between two structural representations.

    Formula: S = (W_sys * S_sys + W_rel * S_rel + W_attr * S_attr) / total

    Where S_sys combines three sub-metrics:
    - Cosine similarity
    - Structural difference similarity (inverse Euclidean)
    - Sign agreement

    Default weight ratio is 7:2:1 (structural : relational : attribute).

    Args:
        repr_rare: Structural representation of the rare node's neighborhood.
        repr_candidate: Structural representation of the candidate's neighborhood.
        s_rel: Relational similarity score (default 0.5).
        s_attr: Attribute similarity score (default 0.5).
        w_sys: Weight for structural similarity (default 7).
        w_rel: Weight for relational similarity (default 2).
        w_attr: Weight for attribute similarity (default 1).

    Returns:
        Consistency score in [0, 1].
    """
    s_cos = cosine_similarity(repr_rare, repr_candidate)
    s_str = structural_diff_similarity(repr_rare, repr_candidate)
    s_sgn = sign_agreement(repr_rare, repr_candidate)
    s_sys = (s_cos + s_str + s_sgn) / 3.0

    total = w_sys + w_rel + w_attr
    score = (w_sys * s_sys + w_rel * s_rel + w_attr * s_attr) / total

    if logger.isEnabledFor(TRACE):
        logger.log(
            TRACE,
            "consistency: score "
            "S_cos=%.4f, S_str=%.4f, S_sgn=%.4f, "
            "S_sys=(%.4f+%.4f+%.4f)/3=%.4f, "
            "S=(%d*%.4f+%d*%.4f+%d*%.4f)/%d=%.4f",
            s_cos, s_str, s_sgn,
            s_cos, s_str, s_sgn, s_sys,
            w_sys, s_sys, w_rel, s_rel, w_attr, s_attr, total, score,
        )

    return score


# ------------------------------------------------------------------
# ConsistencyDiscovery class
# ------------------------------------------------------------------

class ConsistencyDiscovery:
    """Discover hidden relationships based on structural similarity.

    For each rare (protected) node, this component:
    1. Extracts the k-hop neighborhood subgraph
    2. Computes its Laplacian eigenvalue fingerprint
    3. Compares it against other nodes' neighborhoods
    4. Suggests new edges where the consistency score falls within
       the "sandwich threshold" range [theta_L, theta_U]

    The sandwich threshold avoids two failure modes:
    - Score too low: structures are genuinely different, no relationship
    - Score too high: structures are trivially identical (not a discovery)

    Args:
        theta_l: Lower threshold for consistency score (default 0.70).
        theta_u: Upper threshold for consistency score (default 0.80).
        k_hop: Neighborhood radius (default 2).
        dim: Structural representation dimensionality (default 8).

    Example:
        >>> cd = ConsistencyDiscovery()
        >>> discoveries = cd.discover(graph, rare_node_ids=[42])
        >>> for rare_id, candidate_id, score in discoveries:
        ...     print(f"Node {rare_id} <-> Node {candidate_id}: {score:.3f}")
    """

    def __init__(
        self,
        theta_l: float = DEFAULT_THETA_L,
        theta_u: float = DEFAULT_THETA_U,
        k_hop: int = DEFAULT_K_HOP,
        dim: int = DEFAULT_DIM,
    ):
        if theta_l < 0 or theta_l > 1:
            raise ValueError(f"theta_l must be in [0, 1], got {theta_l}")
        if theta_u < 0 or theta_u > 1:
            raise ValueError(f"theta_u must be in [0, 1], got {theta_u}")
        if theta_l > theta_u:
            raise ValueError(f"theta_l must be <= theta_u, got theta_l={theta_l}, theta_u={theta_u}")
        if k_hop < 1:
            raise ValueError(f"k_hop must be >= 1, got {k_hop}")
        if dim < 1:
            raise ValueError(f"dim must be >= 1, got {dim}")
        self.theta_l = theta_l
        self.theta_u = theta_u
        self.k_hop = k_hop
        self.dim = dim
        self._repr_cache: dict[int, np.ndarray] = {}

    def _get_repr(self, graph: Graph, nid: int) -> np.ndarray:
        """Get or compute the structural representation for a node."""
        if nid not in self._repr_cache:
            sub = graph.subgraph(nid, self.k_hop)
            self._repr_cache[nid] = compute_structural_repr(sub, self.dim)
            if logger.isEnabledFor(TRACE):
                logger.log(
                    TRACE,
                    "consistency: repr node(%d) k_hop=%d, "
                    "subgraph=%d nodes, eigenvalues=%s",
                    nid, self.k_hop, sub.node_count(),
                    np.array2string(
                        self._repr_cache[nid],
                        precision=4, separator=", ",
                    ),
                )
        result: np.ndarray = self._repr_cache[nid]
        return result

    def clear_cache(self) -> None:
        """Clear the structural representation cache."""
        self._repr_cache.clear()

    def discover(
        self,
        graph: Graph,
        rare_node_ids: list[int],
        candidate_ids: list[int] | None = None,
        s_rel: float | None = None,
        s_attr: float | None = None,
    ) -> list[tuple[int, int, float]]:
        """Discover hidden relationships for rare nodes.

        For each rare node, compares its structural fingerprint against
        candidate nodes and returns pairs whose consistency score falls
        within [theta_l, theta_u].

        When ``s_rel`` or ``s_attr`` is ``None`` (default), the actual
        relational similarity (Jaccard coefficient of neighborhoods) and
        attribute similarity (type match + metadata overlap) are computed
        per node pair.  Pass explicit float values to override.

        Args:
            graph: The graph to analyze.
            rare_node_ids: List of rare node IDs to find relationships for.
            candidate_ids: Optional list of candidate node IDs to compare against.
                If None, all non-rare nodes with degree > 0 are used.
            s_rel: Relational similarity override. None = auto-compute per pair.
            s_attr: Attribute similarity override. None = auto-compute per pair.

        Returns:
            List of (rare_id, candidate_id, score) tuples.
        """
        auto_rel = s_rel is None
        auto_attr = s_attr is None

        if candidate_ids is None:
            candidate_ids = [
                nid
                for nid in graph.nodes
                if nid not in rare_node_ids and graph.degree(nid) > 0
            ]

        discoveries = []
        for rare_id in rare_node_ids:
            if rare_id not in graph.nodes:
                continue
            repr_rare = self._get_repr(graph, rare_id)

            for cand_id in candidate_ids:
                if cand_id not in graph.nodes or graph.has_edge(rare_id, cand_id):
                    continue

                # Compute per-pair relational & attribute similarity
                rel = (
                    relational_similarity(graph, rare_id, cand_id)
                    if auto_rel
                    else s_rel
                )
                attr = (
                    attribute_similarity(graph, rare_id, cand_id)
                    if auto_attr
                    else s_attr
                )

                repr_cand = self._get_repr(graph, cand_id)
                score = consistency_score(repr_rare, repr_cand, rel, attr)

                if logger.isEnabledFor(TRACE):
                    accepted = self.theta_l <= score <= self.theta_u
                    logger.log(
                        TRACE,
                        "consistency: pair(%d,%d) "
                        "S_rel=%.4f, S_attr=%.4f, S_final=%.4f, "
                        "theta=[%.2f,%.2f] -> %s",
                        rare_id, cand_id, rel, attr, score,
                        self.theta_l, self.theta_u,
                        "ACCEPT" if accepted else "REJECT",
                    )

                if self.theta_l <= score <= self.theta_u:
                    discoveries.append((rare_id, cand_id, score))

        if discoveries:
            logger.debug("Consistency: found %d discoveries for %d rare nodes", len(discoveries), len(rare_node_ids))

        return discoveries
