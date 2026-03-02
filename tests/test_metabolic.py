"""Tests for MetabolicControl: adaptive edge pruning."""

from __future__ import annotations

import pytest

from graph_metabolic_manager import Graph, MetabolicControl
from graph_metabolic_manager.metabolic import decay_rate


class TestMetabolicControl:
    """MetabolicControl: pruning low-weight edges based on local congestion."""

    def test_prunes_low_weight_edges(self, dense_sparse_graph: tuple) -> None:
        g, _nodes = dense_sparse_graph
        e0 = g.edge_count()
        mc = MetabolicControl()
        for _ in range(20):
            mc.step(g, dt=1.0)
        assert g.edge_count() < e0

    def test_uses_local_statistics(self) -> None:
        """Each edge's decay rate uses only deg(u) + deg(v), verified by
        comparing actual decay rates against manually computed congestion."""
        g = Graph()
        # Build a small graph with known structure:
        #   A---B---C---D
        #   |       |
        #   E       F
        a = g.add_node("A")
        b = g.add_node("B")
        c = g.add_node("C")
        d = g.add_node("D")
        e = g.add_node("E")
        f = g.add_node("F")
        g.add_edge(a, b, 1.0)
        g.add_edge(b, c, 1.0)
        g.add_edge(c, d, 1.0)
        g.add_edge(a, e, 1.0)
        g.add_edge(c, f, 1.0)

        # Manually compute expected congestion for each edge
        # deg(A)=2, deg(B)=2, deg(C)=3, deg(D)=1, deg(E)=1, deg(F)=1
        expected_congestion = {
            (a, b): 2 + 2,  # 4
            (b, c): 2 + 3,  # 5
            (c, d): 3 + 1,  # 4
            (a, e): 2 + 1,  # 3
            (c, f): 3 + 1,  # 4
        }

        for (u, v), expected_C in expected_congestion.items():
            actual_C = g.local_congestion(u, v)
            assert actual_C == pytest.approx(expected_C), (
                f"Edge ({u},{v}): expected C={expected_C}, got {actual_C}"
            )
            # Verify decay rate follows the formula exactly
            lam = decay_rate(actual_C)
            expected_lam = 0.05 * (1.0 + 0.5 * (expected_C ** 2.0))
            assert lam == pytest.approx(expected_lam), (
                f"Edge ({u},{v}): decay_rate mismatch"
            )

    def test_skip_layers_skips_matching_edges(self) -> None:
        """MetabolicControl.step() with skip_layers skips edges where
        both endpoints belong to a skipped layer."""
        g = Graph()
        a = g.add_node("A")
        b = g.add_node("B")
        c = g.add_node("C")
        g.add_edge(a, b, 1.0)
        g.add_edge(b, c, 1.0)

        # Set layers: A,B = edge; C = core
        g.nodes[a].layer = "edge"
        g.nodes[b].layer = "edge"
        g.nodes[c].layer = "core"

        mc = MetabolicControl()
        result = mc.step(g, dt=1.0, skip_layers={"edge"})

        # A-B edge: both "edge" layer → skipped
        # B-C edge: one "edge", one "core" → NOT skipped (mixed layers)
        assert result["edges_skipped"] == 1

        # The B-C edge should have been decayed (weight < 1.0)
        bc_weight = g.get_weight(b, c)
        assert bc_weight < 1.0

        # The A-B edge should NOT have been decayed (weight stays 1.0)
        ab_weight = g.get_weight(a, b)
        assert ab_weight == pytest.approx(1.0)

    def test_skip_layers_empty_means_no_skipping(self) -> None:
        """Empty skip_layers set means all edges are processed."""
        g = Graph()
        a = g.add_node("A")
        b = g.add_node("B")
        g.add_edge(a, b, 1.0)

        mc = MetabolicControl()
        result = mc.step(g, dt=1.0, skip_layers=set())
        assert result["edges_skipped"] == 0
        # Edge should have been processed
        assert g.get_weight(a, b) < 1.0
