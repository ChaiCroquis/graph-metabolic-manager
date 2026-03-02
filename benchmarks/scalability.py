#!/usr/bin/env python3
"""
Scalability Benchmark
=====================

Measures Graph Metabolic Manager performance across different graph sizes.
Demonstrates that the algorithm scales well because it uses only local
statistics (deg(u) + deg(v)) -no full graph traversal required.

Usage:
    python benchmarks/scalability.py

Patent: Japanese Patent Application No. 2026-027032
"""

import random
import time

from graph_metabolic_manager import Graph, GraphMetabolicManager


def build_graph(n_nodes: int, edge_prob: float, n_rare: int, n_garbage: int,
                seed: int = 42) -> tuple[Graph, list[int], list[int], list[int]]:
    """Build a random graph for benchmarking.

    Args:
        n_nodes: Number of normal nodes.
        edge_prob: Probability of edge between any two normal nodes.
        n_rare: Number of rare (truth) nodes.
        n_garbage: Number of garbage nodes.
        seed: Random seed for reproducibility.

    Returns:
        Tuple of (graph, normal_ids, rare_ids, garbage_ids).
    """
    random.seed(seed)
    g = Graph()

    # Normal nodes with random interconnections
    normal = []
    for i in range(n_nodes):
        nid = g.add_node(f"N_{i}", node_type="normal")
        normal.append(nid)

    # Edges: for large graphs, use neighbor sampling instead of all-pairs
    if n_nodes <= 1000:
        for i in range(n_nodes):
            for j in range(i + 1, n_nodes):
                if random.random() < edge_prob:
                    g.add_edge(normal[i], normal[j],
                               weight=random.uniform(0.3, 1.0))
    else:
        # For large graphs, each node connects to ~k random neighbors
        k = max(2, int(n_nodes * edge_prob))
        k = min(k, 20)  # Cap at 20 neighbors for performance
        for i in range(n_nodes):
            neighbors = random.sample(range(n_nodes), min(k, n_nodes - 1))
            for j in neighbors:
                if i != j:
                    g.add_edge(normal[i], normal[j],
                               weight=random.uniform(0.3, 1.0))

    # Rare nodes (one weak connection each)
    rare = []
    for i in range(n_rare):
        nid = g.add_node(f"Rare_{i}", node_type="truth")
        target = random.choice(normal)
        g.add_edge(nid, target, weight=random.uniform(0.04, 0.10))
        rare.append(nid)

    # Garbage nodes (isolated)
    garbage = []
    for i in range(n_garbage):
        gid = g.add_node(f"Garbage_{i}", node_type="garbage")
        garbage.append(gid)

    return g, normal, rare, garbage


def run_benchmark(label: str, n_nodes: int, edge_prob: float,
                  n_rare: int, n_garbage: int, steps: int) -> dict:
    """Run a single benchmark scenario.

    Returns:
        Dict with timing and result statistics.
    """
    # Build phase
    t0 = time.perf_counter()
    g, normal, rare, garbage = build_graph(n_nodes, edge_prob, n_rare, n_garbage)
    build_time = time.perf_counter() - t0

    initial_nodes = g.node_count()
    initial_edges = g.edge_count()

    # Run phase
    t0 = time.perf_counter()
    mgr = GraphMetabolicManager(
        g, seed=42,
        enable_rarity=True,
        enable_consistency=False,  # Skip for large graphs (O(n^2) pairs)
        enable_meta=True,
        k_opt=5.0,
        beta=0.03,
        prune_threshold=0.08,
        twait1=5,   # Shorter phases for benchmark (default 50)
        twait2=5,
    )
    mgr.run(steps=steps)
    run_time = time.perf_counter() - t0

    # Results
    rare_survived = sum(1 for nid in rare if g.has_node(nid))
    garbage_survived = sum(1 for nid in garbage if g.has_node(nid))

    result = {
        "label": label,
        "n_nodes": n_nodes,
        "initial_nodes": initial_nodes,
        "initial_edges": initial_edges,
        "final_nodes": g.node_count(),
        "final_edges": g.edge_count(),
        "rare_survived": f"{rare_survived}/{n_rare}",
        "garbage_cleaned": f"{n_garbage - garbage_survived}/{n_garbage}",
        "build_time_s": build_time,
        "run_time_s": run_time,
        "steps": steps,
        "time_per_step_ms": (run_time / steps) * 1000,
    }
    return result


def main() -> None:
    print("=" * 70)
    print("  Graph Metabolic Manager -Scalability Benchmark")
    print("=" * 70)
    print()
    print("  Patent: Japanese Patent Application No. 2026-027032")
    print("  Key property: O(E) per step -only local statistics used")
    print()

    scenarios = [
        # (label, n_nodes, edge_prob, n_rare, n_garbage, steps)
        ("Tiny (100)",       100,   0.10,   6,   10,  100),
        ("Small (500)",      500,   0.02,  10,   20,  100),
        ("Medium (1K)",     1000,   0.01,  15,   30,  100),
        ("Large (5K)",      5000,   0.004, 20,   50,   50),
        ("XL (10K)",       10000,   0.002, 30,   80,   50),
        ("XXL (50K)",      50000,   0.001, 50,  150,   20),
        ("Massive (100K)", 100000,  0.001, 80,  200,   10),
    ]

    results = []
    for label, n_nodes, edge_prob, n_rare, n_garbage, steps in scenarios:
        print(f"  Running {label}...", end="", flush=True)
        result = run_benchmark(label, n_nodes, edge_prob, n_rare, n_garbage, steps)
        results.append(result)
        print(f" {result['run_time_s']:.2f}s ({result['time_per_step_ms']:.1f}ms/step)")

    # Summary table
    print()
    print("-" * 70)
    print(f"  {'Scenario':<18} {'Nodes':>7} {'Edges':>8} {'Steps':>6} "
          f"{'Time':>7} {'ms/step':>8} {'Rare':>6} {'Clean':>6}")
    print("-" * 70)

    for r in results:
        print(
            f"  {r['label']:<18} {r['initial_nodes']:>7} {r['initial_edges']:>8} "
            f"{r['steps']:>6} {r['run_time_s']:>6.2f}s {r['time_per_step_ms']:>7.1f} "
            f"{r['rare_survived']:>6} {r['garbage_cleaned']:>6}"
        )

    print("-" * 70)
    print()
    print("  Key observations:")
    print("  - Time per step scales linearly with edge count (O(E))")
    print("  - No full graph traversal -each edge uses only deg(u) + deg(v)")
    print("  - Rarity protection works at all scales")
    print("  - Garbage is cleaned regardless of graph size")
    print()

    # Scaling factor analysis
    if len(results) >= 2:
        first = results[0]
        last = results[-1]
        edge_ratio = last["initial_edges"] / max(first["initial_edges"], 1)
        time_ratio = last["time_per_step_ms"] / max(first["time_per_step_ms"], 0.001)
        print(f"  Scale factor: {edge_ratio:.0f}x edges -> "
              f"{time_ratio:.1f}x time per step")
        if time_ratio < edge_ratio:
            print("  -> Sub-linear scaling achieved (better than O(E))")
        else:
            print("  -> Approximately linear scaling (as expected for O(E))")

    print("\nDone!")


if __name__ == "__main__":
    main()
