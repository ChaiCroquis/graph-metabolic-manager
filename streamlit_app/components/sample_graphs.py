"""Sample graph builders for Streamlit demo pages."""

from __future__ import annotations

import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from graph_metabolic_manager import Graph


def build_sample_graph(
    seed: int = 42,
) -> tuple[Graph, list[int], list[int], list[int]]:
    """Build a 20-node sample graph with normal/truth/garbage nodes.

    Returns:
        (graph, normal_ids, truth_ids, garbage_ids)
    """
    rng = random.Random(seed)
    g = Graph()

    normal = [g.add_node(f"N{i}", node_type="normal") for i in range(10)]
    truth = [g.add_node(f"T{i}", node_type="truth") for i in range(4)]
    garbage = [g.add_node(f"G{i}", node_type="garbage") for i in range(6)]

    # Dense connections among normals
    for i in range(len(normal)):
        for j in range(i + 1, len(normal)):
            if rng.random() < 0.5:
                g.add_edge(normal[i], normal[j], rng.uniform(0.5, 1.0))

    # Truth nodes: sparse connections (degree=1 each)
    for tid in truth:
        partner = rng.choice(normal)
        if not g.has_edge(tid, partner):
            g.add_edge(tid, partner, rng.uniform(0.3, 0.7))

    # Garbage: isolated (no edges)
    return g, normal, truth, garbage


def build_consistency_graph() -> tuple[Graph, list[tuple[str, int, int]]]:
    """Build a graph for consistency score demonstrations.

    Returns:
        (graph, pairs) where pairs is [(label, nid_a, nid_b), ...]
    """
    g = Graph()

    # Pair 1: High similarity (same structure, same type, shared neighbors)
    a1 = g.add_node("A1", node_type="sensor", category="IoT")
    b1 = g.add_node("B1", node_type="sensor", category="IoT")
    c1 = g.add_node("Hub1", node_type="hub")
    d1 = g.add_node("Hub2", node_type="hub")
    g.add_edge(a1, c1, 1.0)
    g.add_edge(a1, d1, 1.0)
    g.add_edge(b1, c1, 1.0)
    g.add_edge(b1, d1, 1.0)
    g.add_edge(a1, b1, 0.5)

    # Pair 2: Medium similarity (different structure, same type)
    a2 = g.add_node("A2", node_type="device")
    b2 = g.add_node("B2", node_type="device")
    e1 = g.add_node("E1", node_type="hub")
    e2 = g.add_node("E2", node_type="hub")
    e3 = g.add_node("E3", node_type="hub")
    g.add_edge(a2, e1, 1.0)
    g.add_edge(b2, e2, 1.0)
    g.add_edge(b2, e3, 1.0)

    # Pair 3: Low similarity (different everything)
    a3 = g.add_node("A3", node_type="alpha", tag="x")
    b3 = g.add_node("B3", node_type="beta", tag="y")
    f1 = g.add_node("F1", node_type="gamma")
    g.add_edge(a3, f1, 1.0)

    pairs = [
        ("High\n(same struct/type)", a1, b1),
        ("Medium\n(diff struct)", a2, b2),
        ("Low\n(different all)", a3, b3),
    ]
    return g, pairs
