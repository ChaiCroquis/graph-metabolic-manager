"""
Rarity Protection — Multi-phase review for isolated nodes.

Prevents valuable but low-connectivity nodes from being prematurely
deleted. Uses a two-phase grace period: if a node gains connections
during the review, it is kept; otherwise, it is safely removed.

Patent claims: 11–20

Flow:
    Node detected (degree <= 1)
      -> Phase 1: Unconditional grace period (Twait1 steps)
         -> Gained connections? -> Keep (return to normal)
         -> No connections? -> Phase 2
      -> Phase 2: Conditional observation (Twait2 steps)
         -> Gained connections? -> Keep
         -> Still isolated? -> Remove
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from ._logging import TRACE

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .graph import Graph


# ------------------------------------------------------------------
# Default parameters (Patent specification, Fig. 13B)
# ------------------------------------------------------------------
DEFAULT_TWAIT1 = 50          # Phase 1 grace period (steps)
DEFAULT_TWAIT2 = 50          # Phase 2 observation period (steps)
DEFAULT_RARE_DEGREE_MAX = 1  # Maximum degree to be considered rare


class RarityProtection:
    """Two-phase protection for rare (low-connectivity) nodes.

    Nodes with degree <= rare_degree_max are flagged as "rare candidates"
    and enter a multi-phase review process before deletion:

    - **Phase 1** (Twait1 steps): Unconditional grace period.
      The node is fully protected. If it gains connections (spoke_up),
      it returns to normal status.

    - **Phase 2** (Twait2 steps): Conditional observation.
      If the node gains connections, it is kept. If it remains
      isolated (degree 0) after this period, it is removed.

    This mechanism is inspired by biological immune systems: not every
    rare signal is noise — some are early indicators of important patterns.

    Args:
        twait1: Phase 1 duration in steps (default 50).
        twait2: Phase 2 duration in steps (default 50).
        rare_degree_max: Maximum degree to consider a node rare (default 1).

    Example:
        >>> rp = RarityProtection()
        >>> rare = rp.identify_rare(graph, t=0)
        >>> for nid in rare:
        ...     rp.enter_protection(graph, nid, t=0)
        >>> # ... run simulation steps ...
        >>> rp.update_phases(graph, t=50)
    """

    def __init__(
        self,
        twait1: int = DEFAULT_TWAIT1,
        twait2: int = DEFAULT_TWAIT2,
        rare_degree_max: int = DEFAULT_RARE_DEGREE_MAX,
    ):
        if twait1 <= 0:
            raise ValueError(f"twait1 must be positive, got {twait1}")
        if twait2 <= 0:
            raise ValueError(f"twait2 must be positive, got {twait2}")
        if rare_degree_max < 0:
            raise ValueError(f"rare_degree_max must be non-negative, got {rare_degree_max}")
        self.twait1 = twait1
        self.twait2 = twait2
        self.rare_degree_max = rare_degree_max
        self.protected: set[int] = set()

    @property
    def protected_count(self) -> int:
        """Number of currently protected nodes."""
        return len(self.protected)

    def identify_rare(self, graph: Graph, t: float) -> list[int]:
        """Find nodes that qualify as rare (low-connectivity).

        A node is a rare candidate if:
        - It is in "normal" phase (not already under protection)
        - Its degree is <= rare_degree_max

        Args:
            graph: The graph to scan.
            t: Current time step.

        Returns:
            List of node IDs that are rare candidates.
        """
        rare = [
            nid
            for nid, node in graph.nodes.items()
            if node.phase == "normal" and graph.degree(nid) <= self.rare_degree_max
        ]
        if logger.isEnabledFor(TRACE):
            for nid in rare:
                logger.log(
                    TRACE,
                    "rarity: IDENTIFY node(%d) label=%r "
                    "degree=%d <= rare_max=%d, type=%s",
                    nid, graph.nodes[nid].label, graph.degree(nid),
                    self.rare_degree_max, graph.nodes[nid].node_type,
                )
        return rare

    def enter_protection(self, graph: Graph, nid: int, t: float) -> None:
        """Start rarity protection for a node (enter Phase 1).

        Args:
            graph: The graph containing the node.
            nid: Node ID to protect.
            t: Current time step.
        """
        if nid not in graph.nodes:
            return
        node = graph.nodes[nid]
        node.is_protected = True
        node.phase = "phase1"
        node.phase_start_time = t
        node.spoke_up = False
        node.layer = "rare"
        self.protected.add(nid)
        logger.debug("Rarity: node %d entered phase1 protection (degree=%d)", nid, graph.degree(nid))
        if logger.isEnabledFor(TRACE):
            logger.log(
                TRACE,
                "rarity: node(%d) ENTER phase1 at t=%.1f, "
                "degree=%d, twait1=%d, twait2=%d, layer=%s",
                nid, t, graph.degree(nid),
                self.twait1, self.twait2, node.layer,
            )

    def update_phases(self, graph: Graph, t: float) -> dict[str, int]:
        """Update protection phases for all protected nodes.

        Call this once per time step. Handles phase transitions:
        - Phase 1 -> Phase 2 (if no connections after Twait1)
        - Phase 2 -> removal or release (after Twait2)

        Args:
            graph: The graph to update.
            t: Current time step.

        Returns:
            Dict with counts: released, removed.
        """
        released = 0
        removed = 0

        for nid in list(self.protected):
            if nid not in graph.nodes:
                self.protected.discard(nid)
                continue

            node = graph.nodes[nid]
            elapsed = t - node.phase_start_time

            if node.phase == "phase1" and elapsed >= self.twait1:
                # Phase 1 expired -> move to Phase 2
                node.phase = "phase2"
                node.phase_start_time = t
                node.layer = "core"
                logger.debug("Rarity: node %d transitioned phase1 -> phase2", nid)
                if logger.isEnabledFor(TRACE):
                    logger.log(
                        TRACE,
                        "rarity: node(%d) phase1->phase2: "
                        "elapsed=%.1f >= twait1=%d, "
                        "degree=%d, spoke_up=%s",
                        nid, elapsed, self.twait1,
                        graph.degree(nid), node.spoke_up,
                    )

            elif node.phase == "phase2" and elapsed >= self.twait2:
                if not node.spoke_up and graph.degree(nid) == 0:
                    # No connections gained -> remove
                    if logger.isEnabledFor(TRACE):
                        logger.log(
                            TRACE,
                            "rarity: node(%d) phase2->REMOVE: "
                            "elapsed=%.1f >= twait2=%d, "
                            "spoke_up=%s, degree=%d",
                            nid, elapsed, self.twait2,
                            node.spoke_up, graph.degree(nid),
                        )
                    graph.remove_node(nid)
                    self.protected.discard(nid)
                    removed += 1
                    logger.debug("Rarity: node %d removed after phase2 (no connections)", nid)
                else:
                    # Connections gained -> release from protection
                    if logger.isEnabledFor(TRACE):
                        logger.log(
                            TRACE,
                            "rarity: node(%d) phase2->RELEASE: "
                            "spoke_up=%s, degree=%d",
                            nid, node.spoke_up, graph.degree(nid),
                        )
                    node.phase = "normal"
                    node.is_protected = False
                    self.protected.discard(nid)
                    released += 1
                    logger.debug("Rarity: node %d released from protection (spoke up)", nid)

        return {"released": released, "removed": removed}
