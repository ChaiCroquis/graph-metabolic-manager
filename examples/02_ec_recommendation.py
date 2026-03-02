#!/usr/bin/env python3
"""
E-Commerce Recommendation Graph Example
========================================

Simulates a product recommendation graph for an e-commerce site.

Scenario:
- 30 popular products with many cross-recommendations
- 8 niche products that are valuable to specific customer segments
- 8 seasonal products that are out-of-season and should be cleaned up

The manager should:
1. Prune stale seasonal product connections
2. Protect niche products from deletion
3. Maintain healthy recommendation density
"""

import logging
import random

from graph_metabolic_manager import Graph, GraphMetabolicManager

logging.basicConfig(level=logging.INFO, format="%(message)s")


def build_ec_graph(seed: int = 42) -> tuple:
    """Build a simulated e-commerce recommendation graph."""
    random.seed(seed)
    g = Graph()

    # Popular products: densely interconnected
    popular = []
    categories = ["Electronics", "Books", "Clothing", "Home", "Sports"]
    for cat in categories:
        for i in range(6):
            nid = g.add_node(
                f"{cat}_{i}",
                node_type="normal",
                category=cat,
            )
            popular.append(nid)

    # Add recommendation edges within and across categories
    for i in range(len(popular)):
        for j in range(i + 1, len(popular)):
            # Higher probability within same category
            same_cat = (i // 6) == (j // 6)
            prob = 0.5 if same_cat else 0.08
            if random.random() < prob:
                weight = random.uniform(0.5, 1.0) if same_cat else random.uniform(0.2, 0.5)
                g.add_edge(popular[i], popular[j], weight=weight)

    # Niche products: valuable but few connections
    niche = []
    niche_names = [
        "Vintage_Vinyl_Player", "Artisan_Tea_Set", "Handmade_Journal",
        "Organic_Yoga_Mat", "Rare_Board_Game", "Custom_Fountain_Pen",
        "Heritage_Knife_Set", "Limited_Art_Print",
    ]
    for name in niche_names:
        nid = g.add_node(name, node_type="truth")
        # Each niche product has 1 weak connection to a popular item
        target = random.choice(popular)
        g.add_edge(nid, target, weight=random.uniform(0.05, 0.15))
        niche.append(nid)

    # Seasonal products: out-of-season, should be pruned
    seasonal = []
    seasonal_names = [
        "Xmas_Ornament", "Summer_Sandals", "Valentine_Chocolate",
        "Halloween_Costume", "Easter_Basket", "Spring_Planter",
        "Winter_Coat_Sale", "Back_to_School_Kit",
    ]
    for name in seasonal_names:
        nid = g.add_node(name, node_type="garbage")
        # No connections (out of season = isolated)
        seasonal.append(nid)

    return g, popular, niche, seasonal


def main():
    print("=" * 60)
    print("  Example 2: E-Commerce Recommendation Graph")
    print("=" * 60)

    g, popular, niche, seasonal = build_ec_graph()

    print("\nInitial state:")
    print(f"  Popular products:  {len(popular)} (densely connected)")
    print(f"  Niche products:    {len(niche)} (1 weak connection each)")
    print(f"  Seasonal products: {len(seasonal)} (isolated, out of season)")
    print(f"  Total: {g.node_count()} nodes, {g.edge_count()} edges")
    print(f"  Average degree: {g.avg_degree():.2f}")

    # Run metabolic management
    mgr = GraphMetabolicManager(
        g,
        seed=42,
        enable_rarity=True,
        enable_consistency=False,  # Keep it simple for this example
        # Tuning for EC scenario
        alpha=2.0,
        beta=0.05,
        prune_threshold=0.1,
        k_opt=5.0,
    )

    print("\nRunning 150 steps...")
    mgr.run(steps=150, verbose=True)

    # Analyze results
    print(f"\n{'=' * 60}")
    print("  Results")
    print(f"{'=' * 60}")

    niche_survived = sum(1 for nid in niche if g.has_node(nid))
    seasonal_survived = sum(1 for nid in seasonal if g.has_node(nid))
    popular_survived = sum(1 for nid in popular if g.has_node(nid))

    print(f"\n  Popular products remaining:  {popular_survived}/{len(popular)}")
    print(f"  Niche products protected:    {niche_survived}/{len(niche)}")
    print(f"  Seasonal products cleaned:   {len(seasonal) - seasonal_survived}/{len(seasonal)}")
    print(f"\n  Total: {g.node_count()} nodes, {g.edge_count()} edges")
    print(f"  Average degree: {g.avg_degree():.2f}")

    # Evaluate
    print("\n  --- Evaluation ---")
    if niche_survived > 0:
        print(f"  [OK] Niche products were protected ({niche_survived}/{len(niche)} survived)")
    else:
        print("  [!!] Niche products were lost!")

    if seasonal_survived < len(seasonal):
        print(f"  [OK] Seasonal products were cleaned up ({len(seasonal) - seasonal_survived}/{len(seasonal)} removed)")
    else:
        print("  [!!] Seasonal products were not cleaned!")

    print(f"\n  Total edges pruned: {mgr.metabolic.total_pruned_edges}")
    print(f"  Total nodes pruned: {mgr.metabolic.total_pruned_nodes}")

    if mgr.meta.history:
        print(f"  Health: {mgr.meta.history[0]['H']:.3f} -> {mgr.meta.history[-1]['H']:.3f}")

    print("\nDone!")


if __name__ == "__main__":
    main()
