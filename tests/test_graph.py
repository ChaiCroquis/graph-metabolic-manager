"""Tests for Graph: basic node/edge operations and local statistics."""

from __future__ import annotations

import pytest


class TestGraphBasics:
    """Graph: node/edge CRUD and local statistics."""

    def test_nodes_created(self, simple_graph: tuple) -> None:
        g, _a, _b, _c = simple_graph
        assert g.node_count() == 3

    def test_has_node(self, simple_graph: tuple) -> None:
        g, a, _b, _c = simple_graph
        assert g.has_node(a)
        assert not g.has_node(99)

    def test_edges_created(self, simple_graph: tuple) -> None:
        g, _a, _b, _c = simple_graph
        assert g.edge_count() == 2

    def test_has_edge(self, simple_graph: tuple) -> None:
        g, a, b, c = simple_graph
        assert g.has_edge(a, b)
        assert not g.has_edge(a, c)

    def test_edge_weight(self, simple_graph: tuple) -> None:
        g, a, b, _c = simple_graph
        assert g.get_weight(a, b) == pytest.approx(0.8)

    def test_degree(self, simple_graph: tuple) -> None:
        g, a, b, _c = simple_graph
        assert g.degree(b) == 2
        assert g.degree(a) == 1

    def test_local_congestion(self, simple_graph: tuple) -> None:
        """C = deg(u) + deg(v)."""
        g, a, b, _c = simple_graph
        # deg(a)=1, deg(b)=2 -> C=3
        assert g.local_congestion(a, b) == pytest.approx(3.0)

    def test_node_removal(self, simple_graph: tuple) -> None:
        g, _a, _b, c = simple_graph
        g.remove_node(c)
        assert g.node_count() == 2
        assert g.edge_count() == 1
