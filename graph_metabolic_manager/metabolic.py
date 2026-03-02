"""
Metabolic Control — Adaptive edge weight decay.

Implements the core "metabolism" of the graph: edges in crowded
regions decay faster than edges in sparse regions, automatically
maintaining a healthy graph density without full traversal.

Patent claims: 1–10
Key formula: lambda(C) = beta * (1 + gamma * C^alpha)
"""

from __future__ import annotations

import logging
import math
from typing import TYPE_CHECKING

from ._logging import TRACE

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .graph import Graph


# ------------------------------------------------------------------
# Default parameters (Patent specification, Fig. 13B)
# ------------------------------------------------------------------
DEFAULT_ALPHA = 2.0      # Congestion sensitivity exponent
DEFAULT_BETA = 0.05      # Base decay rate
DEFAULT_GAMMA = 0.5      # Congestion scaling factor
DEFAULT_PRUNE_THRESHOLD = 0.1  # Weight threshold for edge removal


# ------------------------------------------------------------------
# Mathematical functions
# ------------------------------------------------------------------

def decay_rate(
    C: float,
    alpha: float = DEFAULT_ALPHA,
    beta: float = DEFAULT_BETA,
    gamma: float = DEFAULT_GAMMA,
) -> float:
    """Calculate the decay rate based on local congestion.

    Formula: lambda(C) = beta * (1 + gamma * C^alpha)

    The decay rate increases with congestion, meaning edges in
    crowded regions are pruned more aggressively, while edges
    in sparse regions are preserved.

    Args:
        C: Local congestion value (typically deg(u) + deg(v)).
        alpha: Exponent controlling sensitivity to congestion.
        beta: Base decay rate (minimum rate when C=0).
        gamma: Scaling factor for the congestion term.

    Returns:
        Decay rate lambda.

    Example:
        >>> decay_rate(2.0)   # Sparse area: low decay
        0.15
        >>> decay_rate(10.0)  # Crowded area: high decay
        2.55
    """
    return float(beta * (1.0 + gamma * (C ** alpha)))


def update_weight(w: float, lam: float, dt: float) -> float:
    """Update edge weight using exponential decay.

    Formula: w_new = w * exp(-lambda * dt)

    Args:
        w: Current edge weight.
        lam: Decay rate (from decay_rate()).
        dt: Time step size.

    Returns:
        Updated weight.

    Example:
        >>> update_weight(1.0, decay_rate(10.0), 5.0)
        3.16...e-06
    """
    return w * math.exp(-lam * dt)


# ------------------------------------------------------------------
# MetabolicControl class
# ------------------------------------------------------------------

class MetabolicControl:
    """Adaptive edge weight decay based on local congestion.

    This is the core "metabolism" engine. On each step:
    1. For each edge, compute local congestion C = deg(u) + deg(v)
    2. Calculate decay rate lambda(C) — higher in crowded areas
    3. Update weight: w *= exp(-lambda * dt)
    4. Remove edges whose weight falls below the prune threshold
    5. Remove isolated nodes (degree 0) that are not protected

    Key insight: only local statistics are used (degrees of the
    two endpoints), so this scales to very large graphs.

    Args:
        alpha: Congestion sensitivity exponent (default 2.0).
        beta: Base decay rate (default 0.05).
        gamma: Congestion scaling factor (default 0.5).
        prune_threshold: Remove edges with weight below this (default 0.1).

    Example:
        >>> g = Graph()
        >>> # ... build graph ...
        >>> mc = MetabolicControl()
        >>> mc.step(g, dt=1.0)
        >>> print(mc.stats)
    """

    def __init__(
        self,
        alpha: float = DEFAULT_ALPHA,
        beta: float = DEFAULT_BETA,
        gamma: float = DEFAULT_GAMMA,
        prune_threshold: float = DEFAULT_PRUNE_THRESHOLD,
    ):
        if alpha <= 0:
            raise ValueError(f"alpha must be positive, got {alpha}")
        if beta < 0:
            raise ValueError(f"beta must be non-negative, got {beta}")
        if gamma < 0:
            raise ValueError(f"gamma must be non-negative, got {gamma}")
        if prune_threshold < 0:
            raise ValueError(f"prune_threshold must be non-negative, got {prune_threshold}")
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.prune_threshold = prune_threshold

        # Cumulative statistics
        self.total_pruned_edges: int = 0
        self.total_pruned_nodes: int = 0

    @property
    def stats(self) -> dict[str, int]:
        """Return cumulative pruning statistics."""
        return {
            "pruned_edges": self.total_pruned_edges,
            "pruned_nodes": self.total_pruned_nodes,
        }

    def step(
        self,
        graph: Graph,
        dt: float = 1.0,
        protected: set[int] | None = None,
        skip_layers: set[str] | None = None,
    ) -> dict[str, int]:
        """Execute one metabolic control step.

        Args:
            graph: The graph to process.
            dt: Time step size (default 1.0).
            protected: Set of node IDs that should not be pruned.
            skip_layers: Set of hierarchy layer names to skip this step.
                When the hierarchy system is active, edges whose **both**
                endpoints belong to a skipped layer are not decayed.
                For example ``{"edge"}`` skips edge-layer-only connections.

        Returns:
            Dict with step results: edges_pruned, nodes_pruned,
            edges_skipped (number of edges skipped due to hierarchy).
        """
        protected = protected or set()
        skip_layers = skip_layers or set()
        edges_pruned = 0
        edges_skipped = 0
        nodes_pruned = 0
        to_remove = []

        # Phase 1: Decay all unprotected edge weights
        for (u, v), w in list(graph.edges.items()):
            if u in protected or v in protected:
                continue
            # Hierarchy: skip edges where BOTH endpoints are in a skipped layer
            if skip_layers:
                u_layer = graph.nodes[u].layer if u in graph.nodes else "edge"
                v_layer = graph.nodes[v].layer if v in graph.nodes else "edge"
                if u_layer in skip_layers and v_layer in skip_layers:
                    edges_skipped += 1
                    if logger.isEnabledFor(TRACE):
                        logger.log(
                            TRACE,
                            "metabolic: edge(%d,%d) SKIP layer=%s/%s",
                            u, v, u_layer, v_layer,
                        )
                    continue
            C = graph.local_congestion(u, v)
            lam = decay_rate(C, self.alpha, self.beta, self.gamma)
            new_w = update_weight(w, lam, dt)
            if logger.isEnabledFor(TRACE):
                logger.log(
                    TRACE,
                    "metabolic: edge(%d,%d) "
                    "C=deg(%d)+deg(%d)=%.1f, "
                    "lam(C)=%.4f*(1+%.4f*%.1f^%.1f)=%.6f, "
                    "w: %.6f -> %.6f*exp(-%.6f*%.1f)=%.6f%s",
                    u, v,
                    graph.degree(u), graph.degree(v), C,
                    self.beta, self.gamma, C, self.alpha, lam,
                    w, w, lam, dt, new_w,
                    " [PRUNE]" if new_w < self.prune_threshold else "",
                )
            graph.set_weight(u, v, new_w)
            if new_w < self.prune_threshold:
                to_remove.append((u, v))

        # Phase 2: Remove dead edges
        for u, v in to_remove:
            graph.remove_edge(u, v)
            edges_pruned += 1
            if logger.isEnabledFor(TRACE):
                logger.log(
                    TRACE,
                    "metabolic: edge(%d,%d) REMOVED (w < %.4f)",
                    u, v, self.prune_threshold,
                )

        # Phase 3: Remove isolated unprotected nodes
        for nid in list(graph.nodes.keys()):
            if graph.degree(nid) == 0 and nid not in protected:
                graph.remove_node(nid)
                nodes_pruned += 1
                if logger.isEnabledFor(TRACE):
                    logger.log(
                        TRACE,
                        "metabolic: node(%d) REMOVED (isolated, degree=0)",
                        nid,
                    )

        logger.debug(
            "Metabolic step: %d edges pruned, %d nodes pruned, %d edges skipped",
            edges_pruned, nodes_pruned, edges_skipped,
        )

        self.total_pruned_edges += edges_pruned
        self.total_pruned_nodes += nodes_pruned

        return {
            "edges_pruned": edges_pruned,
            "nodes_pruned": nodes_pruned,
            "edges_skipped": edges_skipped,
        }
