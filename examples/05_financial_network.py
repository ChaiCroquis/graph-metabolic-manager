#!/usr/bin/env python3
"""
Financial Transaction Network Example
======================================

Simulates a financial transaction network used for fraud detection
and risk monitoring.

Scenario:
- 30 normal business entities with regular transaction patterns
- 6 suspicious entities (rare transaction patterns that might indicate
  emerging fraud schemes - must NOT be deleted)
- 8 inactive entities (dormant accounts, should be archived)
- Demonstrates how rarity protection preserves weak but critical
  fraud signals that traditional pruning would destroy

The manager should:
1. Maintain normal transaction relationships
2. PROTECT suspicious low-activity entities (early fraud signals)
3. Clean up truly inactive entities
4. Discover hidden connections between suspicious entities
"""

import logging
import random

from graph_metabolic_manager import (
    ConsistencyDiscovery,
    Graph,
    GraphMetabolicManager,
)

logging.basicConfig(level=logging.INFO, format="%(message)s")


def build_financial_network(seed: int = 42) -> tuple:
    """Build a simulated financial transaction network."""
    random.seed(seed)
    g = Graph()

    # Normal business entities organized by sector
    sectors = {
        "Manufacturing": 8,
        "Retail": 7,
        "Finance": 6,
        "Tech": 5,
        "Services": 4,
    }

    normal = []
    sector_nodes = {}
    for sector, count in sectors.items():
        sector_nodes[sector] = []
        for i in range(count):
            nid = g.add_node(
                f"{sector}_{i:02d}",
                node_type="normal",
                sector=sector,
                risk_level="low",
            )
            normal.append(nid)
            sector_nodes[sector].append(nid)

    # Intra-sector transactions (strong, frequent)
    for _sector, nodes in sector_nodes.items():
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                if random.random() < 0.5:
                    g.add_edge(nodes[i], nodes[j],
                               weight=random.uniform(0.5, 1.0))

    # Cross-sector transactions (weaker, less frequent)
    all_sectors = list(sector_nodes.keys())
    for i in range(len(all_sectors)):
        for j in range(i + 1, len(all_sectors)):
            for _ in range(3):
                a = random.choice(sector_nodes[all_sectors[i]])
                b = random.choice(sector_nodes[all_sectors[j]])
                if random.random() < 0.3:
                    g.add_edge(a, b, weight=random.uniform(0.1, 0.4))

    # Suspicious entities (weak signals of potential fraud)
    # These have very few transactions but they could be:
    # - Shell companies in layering schemes
    # - Early indicators of new fraud patterns
    # - Accounts being tested before large-scale fraud
    suspicious = []
    suspicious_names = [
        "ShellCo_Alpha", "ShellCo_Beta", "Offshore_X",
        "NewAccount_Unusual", "Pattern_Anomaly_1", "Pattern_Anomaly_2",
    ]
    for name in suspicious_names:
        nid = g.add_node(
            name,
            node_type="truth",
            risk_level="high",
        )
        # Each has exactly 1 weak transaction link
        target = random.choice(normal)
        g.add_edge(nid, target, weight=random.uniform(0.03, 0.10))
        suspicious.append(nid)

    # Inactive entities (truly dormant, safe to archive)
    inactive = []
    inactive_names = [
        "Dormant_Acct_1", "Dormant_Acct_2", "Closed_Biz_A",
        "Closed_Biz_B", "Expired_Entity_1", "Expired_Entity_2",
        "Deregistered_Co", "Abandoned_Acct",
    ]
    for name in inactive_names:
        nid = g.add_node(
            name,
            node_type="garbage",
            risk_level="none",
        )
        # No transactions (completely dormant)
        inactive.append(nid)

    return g, normal, suspicious, inactive


def main():
    print("=" * 60)
    print("  Example 5: Financial Transaction Network")
    print("=" * 60)

    g, normal, suspicious, inactive = build_financial_network()

    print("\nInitial transaction network:")
    print(f"  Normal entities:     {len(normal)} (regular transaction patterns)")
    print(f"  Suspicious entities: {len(suspicious)} (potential fraud signals)")
    print(f"  Inactive entities:   {len(inactive)} (dormant accounts)")
    print(f"  Total: {g.node_count()} nodes, {g.edge_count()} edges")
    print(f"  Average degree: {g.avg_degree():.2f}")

    # ----------------------------------------------------------
    # Scenario A: WITHOUT rarity protection (dangerous!)
    # ----------------------------------------------------------
    print("\n--- Scenario A: Without Rarity Protection ---")
    print("  (What happens with traditional pruning)")

    g_a, normal_a, suspicious_a, inactive_a = build_financial_network()
    mgr_a = GraphMetabolicManager(
        g_a, seed=42,
        enable_rarity=False,
        enable_meta=True,
        k_opt=4.0,
    )
    mgr_a.run(steps=120)

    susp_a = sum(1 for nid in suspicious_a if g_a.has_node(nid))
    inact_a = sum(1 for nid in inactive_a if g_a.has_node(nid))
    print(f"  Suspicious entities surviving: {susp_a}/{len(suspicious_a)}")
    print(f"  Inactive entities remaining:   {inact_a}/{len(inactive_a)}")
    if susp_a == 0:
        print("  [DANGER] ALL fraud signals were destroyed!")

    # ----------------------------------------------------------
    # Scenario B: WITH rarity protection
    # ----------------------------------------------------------
    print("\n--- Scenario B: With Rarity Protection ---")
    print("  (Fraud signals are preserved)")

    mgr = GraphMetabolicManager(
        g, seed=42,
        enable_rarity=True,
        enable_consistency=False,
        k_opt=4.0,
    )
    mgr.run(steps=150, verbose=True)

    susp_survived = sum(1 for nid in suspicious if g.has_node(nid))
    inact_survived = sum(1 for nid in inactive if g.has_node(nid))
    normal_survived = sum(1 for nid in normal if g.has_node(nid))

    print("\n  Results:")
    print(f"  Normal entities:     {normal_survived}/{len(normal)} remaining")
    print(f"  Suspicious entities: {susp_survived}/{len(suspicious)} PROTECTED")
    print(f"  Inactive entities:   {len(inactive) - inact_survived}/{len(inactive)} cleaned")

    # ----------------------------------------------------------
    # Part 2: Hidden connection discovery
    # ----------------------------------------------------------
    print("\n--- Part 2: Suspicious Connection Discovery ---")

    g2, normal2, suspicious2, _ = build_financial_network(seed=99)
    cd = ConsistencyDiscovery(theta_l=0.55, theta_u=0.85)
    discoveries = cd.discover(g2, rare_node_ids=suspicious2, candidate_ids=normal2)

    if discoveries:
        print(f"\n  Found {len(discoveries)} hidden connections:")
        for rare_id, cand_id, score in discoveries[:6]:
            r_label = g2.nodes[rare_id].label
            c_label = g2.nodes[cand_id].label
            print(f"    {r_label} <-> {c_label} (score: {score:.3f})")
        print("\n  These connections suggest which normal entities")
        print("  may be linked to suspicious activity patterns.")

    # ----------------------------------------------------------
    # Comparison
    # ----------------------------------------------------------
    print("\n--- Comparison ---")
    print(f"  Without protection: {susp_a}/{len(suspicious)} fraud signals preserved")
    print(f"  With protection:    {susp_survived}/{len(suspicious)} fraud signals preserved")
    improvement = susp_survived - susp_a
    if improvement > 0:
        print(f"  -> Rarity protection saved {improvement} critical fraud signals")
    print("\n  In fraud detection, a single missed pattern can mean")
    print("  millions in undetected losses.")

    print("\nDone!")


if __name__ == "__main__":
    main()
