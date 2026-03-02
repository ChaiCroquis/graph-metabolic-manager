"""Tests for Hierarchy: layer differential processing and activity computation."""

from __future__ import annotations

import random

from graph_metabolic_manager import Graph, GraphMetabolicManager
from graph_metabolic_manager.manager import (
    DEFAULT_ACTIVITY_THRESHOLD,
    DEFAULT_DT_CORE,
    DEFAULT_DT_EDGE,
    DEFAULT_DT_RARE,
)
from graph_metabolic_manager.rarity import DEFAULT_TWAIT1, DEFAULT_TWAIT2


def _build_hierarchy_graph() -> Graph:
    """Build a graph with distinct dense/sparse regions for hierarchy tests.

    Returns a graph with:
    - 10 densely connected "core-like" nodes (high degree → high activity)
    - 10 sparsely connected "edge-like" nodes (low degree → low activity)
    - 4 isolated "rare-like" nodes (degree ≤ 1)
    """
    random.seed(42)
    g = Graph()

    # Dense cluster: will become "core" layer
    dense = [g.add_node(f"Dense_{i}", node_type="normal") for i in range(10)]
    for i in range(10):
        for j in range(i + 1, 10):
            if random.random() < 0.7:
                g.add_edge(dense[i], dense[j], weight=random.uniform(0.6, 1.0))

    # Sparse cluster: will remain "edge" layer
    sparse = [g.add_node(f"Sparse_{i}", node_type="normal") for i in range(10)]
    for i in range(10):
        for j in range(i + 1, 10):
            if random.random() < 0.15:
                g.add_edge(sparse[i], sparse[j], weight=random.uniform(0.3, 0.6))

    # Connect sparse cluster to dense cluster weakly
    g.add_edge(dense[0], sparse[0], weight=0.3)

    # Isolated rare nodes (degree ≤ 1)
    for i in range(4):
        nid = g.add_node(f"Rare_{i}", node_type="truth")
        if i < 2:
            g.add_edge(nid, dense[i], weight=0.05)

    return g


class TestHierarchyParams:
    """HierarchyParams: layer default parameters (Patent claim 21)."""

    def test_dt_ratio_5_3_1(self) -> None:
        """Computation interval ratio dt_edge:dt_core:dt_rare = 5:3:1."""
        assert DEFAULT_DT_EDGE == 5
        assert DEFAULT_DT_CORE == 3
        assert DEFAULT_DT_RARE == 1

    def test_rare_layer_most_frequent(self) -> None:
        """Rare layer is evaluated most frequently (smallest dt)."""
        assert DEFAULT_DT_RARE < DEFAULT_DT_CORE < DEFAULT_DT_EDGE

    def test_phase_periods_in_range(self) -> None:
        """Phase wait periods should be in range 30-70."""
        assert 30 <= DEFAULT_TWAIT1 <= 70
        assert 30 <= DEFAULT_TWAIT2 <= 70


class TestHierarchyProcessing:
    """HierarchyProcessing: layer differential processing with real behavior."""

    def test_hierarchy_enabled_skips_edge_layer(self) -> None:
        """With hierarchy enabled, edge-layer edges are skipped on non-dt_edge steps."""
        g = _build_hierarchy_graph()
        mgr = GraphMetabolicManager(
            g, enable_hierarchy=True, enable_rarity=True,
            enable_meta=False, seed=42,
        )
        # Step 1 (time=0): all layers processed (0%5==0, 0%3==0, 0%1==0)
        r0 = mgr.step()
        assert r0["edges_skipped"] == 0  # No layers skipped at t=0

        # Step 2 (time=1): edge and core skipped, only rare processed
        r1 = mgr.step()
        assert r1["edges_skipped"] > 0  # Some edges skipped

    def test_hierarchy_disabled_no_skipping(self) -> None:
        """With hierarchy disabled (default), no edges are ever skipped."""
        g = _build_hierarchy_graph()
        mgr = GraphMetabolicManager(
            g, enable_hierarchy=False, enable_rarity=True,
            enable_meta=False, seed=42,
        )
        for _ in range(5):
            r = mgr.step()
            assert "edges_skipped" not in r

    def test_rare_layer_processed_every_step(self) -> None:
        """Rare-layer edges are processed on every single step."""
        g = _build_hierarchy_graph()
        mgr = GraphMetabolicManager(
            g, enable_hierarchy=True, enable_rarity=True,
            enable_meta=False, seed=42,
        )
        # Run 15 steps (covers full dt_edge=5 cycle × 3)
        # Check skip_layers computation: rare should never be skipped
        for t in range(15):
            skip = mgr._compute_skip_layers()
            assert "rare" not in skip, f"Rare layer skipped at t={t}"
            mgr.step()

    def test_edge_layer_processed_every_5_steps(self) -> None:
        """Edge-layer is only processed when time % dt_edge == 0."""
        g = _build_hierarchy_graph()
        mgr = GraphMetabolicManager(
            g, enable_hierarchy=True, enable_rarity=True,
            enable_meta=False, seed=42,
        )
        for t in range(15):
            skip = mgr._compute_skip_layers()
            if t % 5 == 0:
                assert "edge" not in skip, f"Edge layer wrongly skipped at t={t}"
            else:
                assert "edge" in skip, f"Edge layer not skipped at t={t}"
            mgr.step()

    def test_core_layer_processed_every_3_steps(self) -> None:
        """Core-layer is only processed when time % dt_core == 0."""
        g = _build_hierarchy_graph()
        mgr = GraphMetabolicManager(
            g, enable_hierarchy=True, enable_rarity=True,
            enable_meta=False, seed=42,
        )
        for t in range(15):
            skip = mgr._compute_skip_layers()
            if t % 3 == 0:
                assert "core" not in skip, f"Core layer wrongly skipped at t={t}"
            else:
                assert "core" in skip, f"Core layer not skipped at t={t}"
            mgr.step()


class TestActivityComputation:
    """ActivityComputation: node activity from real graph statistics each step."""

    def test_activity_is_computed(self) -> None:
        """After running steps, node activity scores are non-zero for connected nodes."""
        g = _build_hierarchy_graph()
        mgr = GraphMetabolicManager(
            g, enable_hierarchy=True, enable_rarity=False,
            enable_meta=False, seed=42,
        )
        # Run a few steps to build up activity history
        for _ in range(3):
            mgr.step()

        connected = [nid for nid in g.nodes if g.degree(nid) > 0]
        assert len(connected) > 0
        # At least some connected nodes should have non-zero activity
        activities = [g.nodes[nid].activity for nid in connected]
        assert any(a > 0 for a in activities)

    def test_dense_nodes_higher_activity(self) -> None:
        """Densely connected nodes have higher activity than sparse nodes."""
        g = _build_hierarchy_graph()
        mgr = GraphMetabolicManager(
            g, enable_hierarchy=True, enable_rarity=False,
            enable_meta=False, seed=42,
        )
        for _ in range(5):
            mgr.step()

        # Dense nodes (ids 0-9) should have higher average activity
        dense_activity = [
            g.nodes[nid].activity for nid in range(10) if nid in g.nodes
        ]
        sparse_activity = [
            g.nodes[nid].activity for nid in range(10, 20) if nid in g.nodes
        ]

        if dense_activity and sparse_activity:
            assert sum(dense_activity) / len(dense_activity) > (
                sum(sparse_activity) / len(sparse_activity)
            )

    def test_activity_in_valid_range(self) -> None:
        """All activity scores are in [0, 1]."""
        g = _build_hierarchy_graph()
        mgr = GraphMetabolicManager(
            g, enable_hierarchy=True, enable_rarity=False,
            enable_meta=False, seed=42,
        )
        for _ in range(10):
            mgr.step()

        for nid, node in g.nodes.items():
            assert 0.0 <= node.activity <= 1.0, (
                f"Node {nid} activity {node.activity} out of range"
            )

    def test_layer_assignment_reflects_activity(self) -> None:
        """Hierarchy layers are assigned based on activity threshold."""
        g = _build_hierarchy_graph()
        mgr = GraphMetabolicManager(
            g, enable_hierarchy=True, enable_rarity=False,
            enable_meta=False, seed=42,
        )
        for _ in range(5):
            mgr.step()

        for nid, node in g.nodes.items():
            if not node.is_protected:
                if node.activity > DEFAULT_ACTIVITY_THRESHOLD:
                    assert node.layer == "core", (
                        f"Node {nid} has activity {node.activity:.3f} > threshold "
                        f"but layer is '{node.layer}'"
                    )
                else:
                    assert node.layer == "edge", (
                        f"Node {nid} has activity {node.activity:.3f} <= threshold "
                        f"but layer is '{node.layer}'"
                    )

    def test_activity_updated_even_without_hierarchy(self) -> None:
        """Activity is always computed, even when hierarchy is disabled."""
        g = _build_hierarchy_graph()
        mgr = GraphMetabolicManager(
            g, enable_hierarchy=False, enable_rarity=False,
            enable_meta=False, seed=42,
        )
        for _ in range(3):
            mgr.step()

        connected = [nid for nid in g.nodes if g.degree(nid) > 0]
        activities = [g.nodes[nid].activity for nid in connected]
        assert any(a > 0 for a in activities)
