"""Shared pytest fixtures for graph_metabolic_manager tests."""

from __future__ import annotations

import random

import numpy as np
import pytest

from graph_metabolic_manager import Graph


@pytest.fixture
def simple_graph() -> tuple[Graph, int, int, int]:
    """3-node, 2-edge graph for basic operation tests.

    Structure:  Alice --0.8-- Bob --0.5-- Charlie
    """
    g = Graph()
    a = g.add_node("Alice")
    b = g.add_node("Bob")
    c = g.add_node("Charlie")
    g.add_edge(a, b, 0.8)
    g.add_edge(b, c, 0.5)
    return g, a, b, c


@pytest.fixture
def dense_sparse_graph() -> tuple[Graph, list[int]]:
    """20-node graph with dense (0-9) and sparse (10-19) clusters.

    Used for MetabolicControl pruning tests.
    """
    random.seed(42)
    np.random.seed(42)
    g = Graph()
    nodes = [g.add_node(f"N{i}") for i in range(20)]

    # Dense cluster (nodes 0-9)
    for i in range(10):
        for j in range(i + 1, 10):
            if random.random() < 0.6:
                g.add_edge(nodes[i], nodes[j], random.uniform(0.3, 1.0))

    # Sparse cluster (nodes 10-19)
    for i in range(10, 20):
        for j in range(i + 1, 20):
            if random.random() < 0.15:
                g.add_edge(nodes[i], nodes[j], random.uniform(0.3, 1.0))

    return g, nodes


@pytest.fixture
def seeded_rng() -> None:
    """Fix random seeds for reproducibility."""
    random.seed(42)
    np.random.seed(42)
