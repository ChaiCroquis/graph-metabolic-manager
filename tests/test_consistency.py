"""Tests for ConsistencyDiscovery: structural similarity."""

from __future__ import annotations

import pytest

from graph_metabolic_manager import (
    Graph,
    attribute_similarity,
    compute_structural_repr,
    consistency_score,
    relational_similarity,
)
from graph_metabolic_manager.consistency import (
    DEFAULT_THETA_L,
    DEFAULT_THETA_U,
    DEFAULT_W_ATTR,
    DEFAULT_W_REL,
    DEFAULT_W_SYS,
    cosine_similarity,
)


def _make_path(n: int = 5) -> Graph:
    """Create a path graph: P0 -- P1 -- ... -- P(n-1)."""
    g = Graph()
    for i in range(n):
        g.add_node(f"P{i}")
    for i in range(n - 1):
        g.add_edge(i, i + 1, 1.0)
    return g


def _make_star(n: int = 5) -> Graph:
    """Create a star graph: S0 at center, S1..S(n-1) as leaves."""
    g = Graph()
    for i in range(n):
        g.add_node(f"S{i}")
    for i in range(1, n):
        g.add_edge(0, i, 1.0)
    return g


class TestConsistencyDiscovery:
    """ConsistencyDiscovery: Laplacian eigenvalue-based structural similarity."""

    def test_same_structure_high_similarity(self) -> None:
        rp1 = compute_structural_repr(_make_path())
        rp2 = compute_structural_repr(_make_path())
        assert cosine_similarity(rp1, rp2) > 0.99

    def test_different_structure_lower_similarity(self) -> None:
        rp = compute_structural_repr(_make_path())
        rs = compute_structural_repr(_make_star())
        sim_pp = cosine_similarity(rp, rp)
        sim_ps = cosine_similarity(rp, rs)
        assert sim_ps < sim_pp

    def test_sandwich_threshold_values(self) -> None:
        assert pytest.approx(0.70) == DEFAULT_THETA_L
        assert pytest.approx(0.80) == DEFAULT_THETA_U

    def test_identical_score_rejected_as_trivial(self) -> None:
        rp = compute_structural_repr(_make_path())
        s = consistency_score(rp, rp)
        # Identical structures should score above theta_U (trivial match)
        assert not (DEFAULT_THETA_L <= s <= DEFAULT_THETA_U)

    def test_score_weight_ratio_7_2_1(self) -> None:
        assert DEFAULT_W_SYS == 7
        assert DEFAULT_W_REL == 2
        assert DEFAULT_W_ATTR == 1


class TestRelationalSimilarity:
    """RelationalSimilarity: Jaccard coefficient of neighborhoods."""

    def test_identical_neighborhoods(self) -> None:
        """Nodes sharing all neighbors should have similarity = 1.0."""
        g = Graph()
        a = g.add_node("A")
        b = g.add_node("B")
        c = g.add_node("C")
        d = g.add_node("D")
        # A and B both connect to C and D
        g.add_edge(a, c, 1.0)
        g.add_edge(a, d, 1.0)
        g.add_edge(b, c, 1.0)
        g.add_edge(b, d, 1.0)
        # A-B also connected (excluded from Jaccard)
        g.add_edge(a, b, 1.0)
        assert relational_similarity(g, a, b) == pytest.approx(1.0)

    def test_disjoint_neighborhoods(self) -> None:
        """Nodes with zero neighbor overlap should have similarity = 0.0."""
        g = Graph()
        a = g.add_node("A")
        b = g.add_node("B")
        c = g.add_node("C")
        d = g.add_node("D")
        g.add_edge(a, c, 1.0)
        g.add_edge(b, d, 1.0)
        assert relational_similarity(g, a, b) == pytest.approx(0.0)

    def test_partial_overlap(self) -> None:
        """Partial overlap gives Jaccard between 0 and 1."""
        g = Graph()
        a = g.add_node("A")
        b = g.add_node("B")
        c = g.add_node("C")  # shared
        d = g.add_node("D")  # only A
        e = g.add_node("E")  # only B
        g.add_edge(a, c, 1.0)
        g.add_edge(a, d, 1.0)
        g.add_edge(b, c, 1.0)
        g.add_edge(b, e, 1.0)
        # J = |{C}| / |{C,D,E}| = 1/3
        assert relational_similarity(g, a, b) == pytest.approx(1 / 3)

    def test_both_isolated(self) -> None:
        """Two isolated nodes have similarity 0.0."""
        g = Graph()
        a = g.add_node("A")
        b = g.add_node("B")
        assert relational_similarity(g, a, b) == pytest.approx(0.0)

    def test_result_in_range(self) -> None:
        """Result is always in [0, 1]."""
        g = _make_path(10)
        for i in range(10):
            for j in range(i + 1, 10):
                sim = relational_similarity(g, i, j)
                assert 0.0 <= sim <= 1.0


class TestAttributeSimilarity:
    """AttributeSimilarity: type match + metadata Jaccard."""

    def test_same_type_no_metadata(self) -> None:
        """Same type, no metadata → 1.0 (only type match counts)."""
        g = Graph()
        a = g.add_node("A", node_type="product")
        b = g.add_node("B", node_type="product")
        assert attribute_similarity(g, a, b) == pytest.approx(1.0)

    def test_different_type_no_metadata(self) -> None:
        """Different type, no metadata → 0.0."""
        g = Graph()
        a = g.add_node("A", node_type="product")
        b = g.add_node("B", node_type="user")
        assert attribute_similarity(g, a, b) == pytest.approx(0.0)

    def test_same_type_matching_metadata(self) -> None:
        """Same type + matching metadata → 1.0."""
        g = Graph()
        a = g.add_node("A", node_type="product", category="electronics")
        b = g.add_node("B", node_type="product", category="electronics")
        assert attribute_similarity(g, a, b) == pytest.approx(1.0)

    def test_same_type_partial_metadata(self) -> None:
        """Same type + partial metadata match → between 0.5 and 1.0."""
        g = Graph()
        a = g.add_node("A", node_type="product", color="red", size="L")
        b = g.add_node("B", node_type="product", color="red", size="M")
        # type_match = 1.0
        # metadata: color matches (1), size doesn't (0) → 1/2 = 0.5
        # (1.0 + 0.5) / 2 = 0.75
        assert attribute_similarity(g, a, b) == pytest.approx(0.75)

    def test_result_in_range(self) -> None:
        """Result is always in [0, 1]."""
        g = Graph()
        a = g.add_node("A", node_type="x", k1="v1")
        b = g.add_node("B", node_type="y", k2="v2")
        sim = attribute_similarity(g, a, b)
        assert 0.0 <= sim <= 1.0

    def test_missing_node(self) -> None:
        """Returns 0.0 if either node doesn't exist."""
        g = Graph()
        a = g.add_node("A")
        assert attribute_similarity(g, a, 999) == pytest.approx(0.0)
