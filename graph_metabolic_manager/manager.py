"""
GraphMetabolicManager — Unified interface for all components.

Combines metabolic control, rarity protection, consistency discovery,
and meta control into a single easy-to-use manager class.

Patent claims: 20-26, 33-50
Key formula: Hierarchy layers edge/core/rare with dt ratio 5:3:1.
"""

from __future__ import annotations

import logging
import random
from typing import Any

from ._logging import TRACE
from .consistency import ConsistencyDiscovery
from .graph import Graph
from .meta_control import MetaControl
from .metabolic import DEFAULT_ALPHA, MetabolicControl
from .rarity import RarityProtection

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# Hierarchy layer default intervals (Patent claims 21–26)
# ------------------------------------------------------------------
DEFAULT_DT_EDGE = 5   # Edge layer: processed every 5 steps (slowest)
DEFAULT_DT_CORE = 3   # Core layer: processed every 3 steps
DEFAULT_DT_RARE = 1   # Rare layer: processed every step (fastest)
DEFAULT_ACTIVITY_THRESHOLD = 0.5  # Activity score threshold for core promotion

# ------------------------------------------------------------------
# Activity EMA (Exponential Moving Average) smoothing coefficients
# ------------------------------------------------------------------
_EMA_RETAIN = 0.7   # Weight on previous activity (stability)
_EMA_UPDATE = 0.3   # Weight on new raw activity (responsiveness)


class GraphMetabolicManager:
    """All-in-one graph management with metabolic control.

    Integrates all four components:
    - MetabolicControl: Automatic edge pruning
    - RarityProtection: Multi-phase protection for rare nodes
    - ConsistencyDiscovery: Hidden relationship detection
    - MetaControl: Automatic parameter tuning

    And two cross-cutting features:
    - **Hierarchy layers**: Differential processing intervals per layer.
      Edge-layer nodes are processed every ``dt_edge`` steps (default 5),
      core-layer nodes every ``dt_core`` steps (default 3), and rare-layer
      nodes every ``dt_rare`` step (default 1).  Enable with
      ``enable_hierarchy=True``.
    - **Activity tracking**: Each node's ``activity`` score is recomputed
      every step based on its relative degree and degree change rate.
      The score drives automatic layer promotion (edge -> core) when
      ``enable_hierarchy`` is active.

    Each call to step() executes one full cycle:
    1. Meta control adjusts parameters based on graph health
    2. Activity scores updated for all nodes
    3. Hierarchy layers assigned (if enabled)
    4. Rare node identification and protection entry
    5. Consistency discovery for protected nodes (optional)
    6. Rarity phase updates
    7. Metabolic control (edge decay and pruning with layer awareness)

    Args:
        graph: The graph to manage.
        enable_meta: Enable meta control (default True).
        enable_rarity: Enable rarity protection (default True).
        enable_consistency: Enable consistency discovery (default False).
            Set to True to automatically discover hidden relationships
            for rare nodes. This adds computational cost.
        enable_hierarchy: Enable hierarchy layer differential processing
            (default False).  When True, edges are processed at different
            frequencies depending on endpoint node layers.
        seed: Random seed for reproducibility (default None).
        alpha: Congestion sensitivity exponent for metabolic control (default 2.0).
        beta: Base decay rate for metabolic control (default 0.05).
        gamma: Congestion scaling factor for metabolic control (default 0.5).
        prune_threshold: Weight threshold for edge removal (default 0.1).
        twait1: Phase 1 grace period in steps for rarity protection (default 50).
        twait2: Phase 2 observation period in steps for rarity protection (default 50).
        theta_l: Lower consistency score threshold (default 0.70).
        theta_u: Upper consistency score threshold (default 0.80).
        k_opt: Optimal average degree for meta control (default 5.0).
        h_target: Target health index for meta control (default 0.7).
        dt_edge: Edge layer processing interval (default 5).
        dt_core: Core layer processing interval (default 3).
        dt_rare: Rare layer processing interval (default 1).
        activity_threshold: Activity score threshold for core promotion (default 0.5).

    Example:
        >>> g = Graph()
        >>> # ... build your graph ...
        >>> mgr = GraphMetabolicManager(g, enable_hierarchy=True)
        >>> for t in range(100):
        ...     result = mgr.step()
        ...     if t % 10 == 0:
        ...         print(f"Step {t}: {g.node_count()} nodes, {g.edge_count()} edges")
    """

    def __init__(
        self,
        graph: Graph,
        enable_meta: bool = True,
        enable_rarity: bool = True,
        enable_consistency: bool = False,
        enable_hierarchy: bool = False,
        seed: int | None = None,
        *,
        # MetabolicControl parameters
        alpha: float = DEFAULT_ALPHA,
        beta: float = 0.05,
        gamma: float = 0.5,
        prune_threshold: float = 0.1,
        # RarityProtection parameters
        twait1: int = 50,
        twait2: int = 50,
        # ConsistencyDiscovery parameters
        theta_l: float = 0.70,
        theta_u: float = 0.80,
        # MetaControl parameters
        k_opt: float = 5.0,
        h_target: float = 0.7,
        # Hierarchy layer parameters
        dt_edge: int = DEFAULT_DT_EDGE,
        dt_core: int = DEFAULT_DT_CORE,
        dt_rare: int = DEFAULT_DT_RARE,
        activity_threshold: float = DEFAULT_ACTIVITY_THRESHOLD,
    ) -> None:
        # Validate hierarchy parameters
        if dt_edge < 1:
            raise ValueError(f"dt_edge must be >= 1, got {dt_edge}")
        if dt_core < 1:
            raise ValueError(f"dt_core must be >= 1, got {dt_core}")
        if dt_rare < 1:
            raise ValueError(f"dt_rare must be >= 1, got {dt_rare}")
        if not 0 <= activity_threshold <= 1:
            raise ValueError(f"activity_threshold must be in [0, 1], got {activity_threshold}")

        self.graph = graph
        self.enable_meta = enable_meta
        self.enable_rarity = enable_rarity
        self.enable_consistency = enable_consistency
        self.enable_hierarchy = enable_hierarchy

        # Hierarchy layer intervals (Patent: dt_edge : dt_core : dt_rare = 5:3:1)
        self.dt_edge = dt_edge
        self.dt_core = dt_core
        self.dt_rare = dt_rare
        self.activity_threshold = activity_threshold

        if seed is not None:
            random.seed(seed)

        # Initialize components
        self.metabolic = MetabolicControl(
            alpha=alpha,
            beta=beta,
            gamma=gamma,
            prune_threshold=prune_threshold,
        )
        self.rarity = RarityProtection(
            twait1=twait1,
            twait2=twait2,
        )
        self.consistency = ConsistencyDiscovery(
            theta_l=theta_l,
            theta_u=theta_u,
        )
        self.meta = MetaControl(
            k_opt=k_opt,
            h_target=h_target,
            initial_alpha=alpha,
        )

        self._time: int = 0
        self._discoveries: list[tuple[int, int, float]] = []
        self._prev_degrees: dict[int, int] = {}

    @property
    def time(self) -> int:
        """Current simulation time step."""
        return self._time

    @property
    def discoveries(self) -> list[tuple[int, int, float]]:
        """All discovered hidden relationships so far."""
        return list(self._discoveries)

    # ------------------------------------------------------------------
    # Activity & hierarchy layer management
    # ------------------------------------------------------------------

    def _update_activity(self) -> None:
        """Recompute activity scores for every node.

        Activity is a [0, 1] score combining two signals:

        - **Relative degree**: ``degree / avg_degree`` — nodes with
          above-average connectivity score higher.
        - **Change rate**: ``|degree - prev_degree| / avg_degree`` —
          nodes whose connectivity changed recently score higher.

        The raw score is smoothed with an exponential moving average
        (alpha=0.3) to avoid jitter from single-step fluctuations.
        """
        avg_deg = max(1.0, self.graph.avg_degree())
        for nid, node in self.graph.nodes.items():
            curr_deg = self.graph.degree(nid)
            prev_deg = self._prev_degrees.get(nid, curr_deg)

            degree_ratio = curr_deg / avg_deg
            change_rate = abs(curr_deg - prev_deg) / avg_deg
            raw_activity = min(1.0, (degree_ratio + change_rate) / 2.0)

            # Exponential moving average for stability
            old_activity = node.activity
            node.activity = _EMA_RETAIN * node.activity + _EMA_UPDATE * raw_activity

            if logger.isEnabledFor(TRACE):
                logger.log(
                    TRACE,
                    "manager: activity node(%d) deg=%d, prev_deg=%d, "
                    "raw=(%.4f+%.4f)/2=%.4f, "
                    "activity=%.1f*%.4f+%.1f*%.4f=%.4f",
                    nid, curr_deg, prev_deg,
                    degree_ratio, change_rate, raw_activity,
                    _EMA_RETAIN, old_activity, _EMA_UPDATE, raw_activity,
                    node.activity,
                )

        # Store current degrees for next step
        self._prev_degrees = {
            nid: self.graph.degree(nid) for nid in self.graph.nodes
        }

    def _update_layers(self) -> None:
        """Assign hierarchy layers based on activity scores.

        - Protected nodes keep their rarity-assigned layer ("rare" or "core").
        - Unprotected nodes with activity > threshold -> "core" layer.
        - Unprotected nodes with activity <= threshold -> "edge" layer.
        """
        for _nid, node in self.graph.nodes.items():
            if node.is_protected:
                continue  # Rarity system owns this node's layer
            if node.activity > self.activity_threshold:
                node.layer = "core"
            else:
                node.layer = "edge"
            if logger.isEnabledFor(TRACE):
                logger.log(
                    TRACE,
                    "manager: layer node(%d) activity=%.4f %s "
                    "threshold=%.4f -> %s",
                    _nid, node.activity,
                    ">" if node.activity > self.activity_threshold else "<=",
                    self.activity_threshold, node.layer,
                )

    def _compute_skip_layers(self) -> set[str]:
        """Determine which layers to skip on the current time step.

        The hierarchy system uses differential processing intervals:

        - ``dt_rare=1``: Rare-layer processed every step (fastest)
        - ``dt_core=3``: Core-layer processed every 3 steps
        - ``dt_edge=5``: Edge-layer processed every 5 steps (slowest)

        Returns:
            Set of layer names to skip on this step.
        """
        skip: set[str] = set()
        if self._time % self.dt_edge != 0:
            skip.add("edge")
        if self._time % self.dt_core != 0:
            skip.add("core")
        # Rare layer: dt_rare=1, never skipped (1 % 1 == 0 always)
        if self._time % self.dt_rare != 0:
            skip.add("rare")

        if logger.isEnabledFor(TRACE):
            logger.log(
                TRACE,
                "manager: hierarchy t=%d skip_layers=%s "
                "(edge: t%%%d=%d, core: t%%%d=%d, rare: t%%%d=%d)",
                self._time, skip,
                self.dt_edge, self._time % self.dt_edge,
                self.dt_core, self._time % self.dt_core,
                self.dt_rare, self._time % self.dt_rare,
            )

        return skip

    # ------------------------------------------------------------------
    # Main step
    # ------------------------------------------------------------------

    def step(self, dt: float = 1.0) -> dict[str, Any]:
        """Execute one full management cycle.

        Args:
            dt: Time step size (default 1.0).

        Returns:
            Dict with step results including edges_pruned, nodes_pruned,
            health, new_discoveries, etc.
        """
        result: dict[str, Any] = {"time": self._time}

        if logger.isEnabledFor(TRACE):
            logger.log(
                TRACE,
                "manager: === step t=%d begin === "
                "nodes=%d, edges=%d, avg_deg=%.2f",
                self._time, self.graph.node_count(),
                self.graph.edge_count(), self.graph.avg_degree(),
            )

        # 1. Meta control: adjust parameters
        if self.enable_meta:
            meta_info = self.meta.step(self.graph)
            self.metabolic.alpha = self.meta.current_alpha
            result["health"] = meta_info["H"]
            result["alpha"] = meta_info["alpha"]

        # 2. Activity tracking: recompute scores for all nodes
        self._update_activity()

        # 3. Hierarchy layer assignment
        if self.enable_hierarchy:
            self._update_layers()

        # 4. Rarity protection: identify and protect rare nodes
        if self.enable_rarity:
            rare_candidates = self.rarity.identify_rare(self.graph, self._time)
            for nid in rare_candidates:
                self.rarity.enter_protection(self.graph, nid, self._time)
            result["rare_protected"] = self.rarity.protected_count

        # 5. Consistency discovery: find hidden relationships
        new_discoveries: list[tuple[int, int, float]] = []
        if self.enable_consistency and self.enable_rarity:
            rare_ids = list(self.rarity.protected)
            if rare_ids:
                new_discoveries = self.consistency.discover(
                    self.graph, rare_ids
                )
                for rare_id, cand_id, score in new_discoveries:
                    self.graph.add_edge(rare_id, cand_id, weight=score)
                    if rare_id in self.graph.nodes:
                        self.graph.nodes[rare_id].spoke_up = True
                    if logger.isEnabledFor(TRACE):
                        logger.log(
                            TRACE,
                            "manager: discovery edge(%d,%d) "
                            "score=%.4f -> add_edge(w=%.4f), "
                            "spoke_up=True",
                            rare_id, cand_id, score, score,
                        )
                self._discoveries.extend(new_discoveries)
        result["new_discoveries"] = len(new_discoveries)

        # 6. Rarity phase updates
        if self.enable_rarity:
            phase_result = self.rarity.update_phases(self.graph, self._time)
            result["rare_released"] = phase_result["released"]
            result["rare_removed"] = phase_result["removed"]

        # 7. Metabolic control: decay and prune (with hierarchy awareness)
        protected = self.rarity.protected if self.enable_rarity else set()
        skip_layers = self._compute_skip_layers() if self.enable_hierarchy else None
        mc_result = self.metabolic.step(
            self.graph, dt=dt, protected=protected, skip_layers=skip_layers
        )
        result["edges_pruned"] = mc_result["edges_pruned"]
        result["nodes_pruned"] = mc_result["nodes_pruned"]
        if self.enable_hierarchy:
            result["edges_skipped"] = mc_result["edges_skipped"]

        # Summary stats
        result["nodes"] = self.graph.node_count()
        result["edges"] = self.graph.edge_count()

        logger.debug(
            "Step %d: %d nodes, %d edges, %d pruned, %d discoveries",
            self._time, self.graph.node_count(), self.graph.edge_count(),
            mc_result["edges_pruned"], len(new_discoveries),
        )

        if logger.isEnabledFor(TRACE):
            logger.log(
                TRACE,
                "manager: === step t=%d end === "
                "nodes=%d, edges=%d, "
                "pruned_edges=%d, pruned_nodes=%d, discoveries=%d",
                self._time, self.graph.node_count(),
                self.graph.edge_count(),
                mc_result["edges_pruned"], mc_result["nodes_pruned"],
                len(new_discoveries),
            )

        self._time += 1
        return result

    def run(self, steps: int, dt: float = 1.0, verbose: bool = False) -> list[dict[str, Any]]:
        """Run multiple steps and return all results.

        Args:
            steps: Number of steps to run.
            dt: Time step size (default 1.0).
            verbose: Print progress every 10% (default False).

        Returns:
            List of result dicts, one per step.
        """
        results = []
        for i in range(steps):
            result = self.step(dt=dt)
            results.append(result)
            if verbose and steps >= 10 and i % (steps // 10) == 0:
                logger.info(
                    "  Step %4d: %4d nodes, %4d edges",
                    i, self.graph.node_count(), self.graph.edge_count(),
                )
        if verbose:
            logger.info(
                "  Done:     %4d nodes, %4d edges",
                self.graph.node_count(), self.graph.edge_count(),
            )
        return results

    def summary(self) -> str:
        """Return a human-readable summary of the current state."""
        lines = [
            f"GraphMetabolicManager (t={self._time})",
            f"  {self.graph.summary()}",
            f"  Metabolic: {self.metabolic.stats}",
            f"  Rarity: {self.rarity.protected_count} currently protected",
            f"  Discoveries: {len(self._discoveries)} total",
        ]
        if self.enable_hierarchy:
            lines.append(
                f"  Hierarchy: dt_edge={self.dt_edge}, "
                f"dt_core={self.dt_core}, dt_rare={self.dt_rare}"
            )
        if self.enable_meta and self.meta.history:
            last = self.meta.history[-1]
            lines.append(
                f"  Health: H={last['H']:.3f}, alpha={last['alpha']:.3f}"
            )
        return "\n".join(lines)
