#!/usr/bin/env python3
"""
Basic Usage Example
===================

Shows how to use GraphMetabolicManager with a simple graph.
Demonstrates: automatic pruning, rarity protection, and health monitoring.
"""

import logging

from graph_metabolic_manager import Graph, GraphMetabolicManager

logging.basicConfig(level=logging.INFO, format="%(message)s")


def main():
    print("=" * 60)
    print("  Example 1: Basic Usage")
    print("=" * 60)

    # ----------------------------------------------------------
    # 1. Build a graph
    # ----------------------------------------------------------
    g = Graph()

    # Create a densely connected cluster (popular items)
    popular = []
    for i in range(10):
        nid = g.add_node(f"Popular_{i}")
        popular.append(nid)
    for i in range(len(popular)):
        for j in range(i + 1, len(popular)):
            g.add_edge(popular[i], popular[j], weight=0.8)

    # Create a few loosely connected nodes (rare but valuable)
    rare_valuable = g.add_node("RareGem", node_type="truth")
    g.add_edge(rare_valuable, popular[0], weight=0.1)

    # Create some noise nodes (should be pruned)
    for i in range(5):
        nid = g.add_node(f"Noise_{i}", node_type="garbage")
        # No connections -> will be identified as rare then pruned

    print(f"\nInitial graph: {g.node_count()} nodes, {g.edge_count()} edges")
    print(f"  Popular nodes: {len(popular)}")
    print("  Rare valuable: 1")
    print("  Noise nodes: 5")

    # ----------------------------------------------------------
    # 2. Run the manager
    # ----------------------------------------------------------
    mgr = GraphMetabolicManager(g, seed=42)

    print("\nRunning 120 steps of metabolic management...")
    mgr.run(steps=120, verbose=True)

    # ----------------------------------------------------------
    # 3. Check results
    # ----------------------------------------------------------
    print(f"\n{mgr.summary()}")

    # Did the rare gem survive?
    gem_survived = g.has_node(rare_valuable)
    print(f"\n  Rare gem survived? {'Yes!' if gem_survived else 'No'}")

    # How many noise nodes remain?
    noise_remaining = g.count_by_type("garbage")
    print(f"  Noise nodes remaining: {noise_remaining}")

    # Health history
    if mgr.meta.history:
        h_start = mgr.meta.history[0]["H"]
        h_end = mgr.meta.history[-1]["H"]
        print(f"\n  Health: {h_start:.3f} -> {h_end:.3f}")

    print("\nDone!")


if __name__ == "__main__":
    main()
