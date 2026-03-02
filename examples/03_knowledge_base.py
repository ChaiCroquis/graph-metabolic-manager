#!/usr/bin/env python3
"""
Enterprise Knowledge Base Example
==================================

Simulates a corporate knowledge base where documents, expertise areas,
and team members are connected in a graph.

Scenario:
- 20 active documents with cross-references
- 5 legacy documents (outdated but historically important)
- 5 obsolete documents (truly outdated, should be archived)
- Demonstrates consistency discovery: finding hidden relationships
  between documents that share structural patterns

The manager should:
1. Maintain active document connections
2. Protect legacy documents from deletion
3. Archive obsolete documents
4. Discover hidden relationships between documents
"""

import logging
import random

from graph_metabolic_manager import (
    ConsistencyDiscovery,
    Graph,
    GraphMetabolicManager,
)

logging.basicConfig(level=logging.INFO, format="%(message)s")


def build_knowledge_graph(seed: int = 42) -> tuple:
    """Build a simulated corporate knowledge base graph."""
    random.seed(seed)
    g = Graph()

    # Active documents organized by department
    departments = {
        "Engineering": ["API_Design", "Architecture", "Testing_Guide", "Deploy_Process", "Code_Review"],
        "Product": ["Roadmap", "User_Research", "Feature_Spec", "Analytics", "Competitors"],
        "Operations": ["Runbook", "Incident_Response", "Monitoring", "SLA_Policy", "On_Call"],
        "HR": ["Onboarding", "Benefits", "Performance_Review", "Team_Structure", "Culture_Guide"],
    }

    active = []
    dept_nodes = {}
    for dept, docs in departments.items():
        dept_nodes[dept] = []
        for doc_name in docs:
            nid = g.add_node(f"{dept}/{doc_name}", node_type="normal", department=dept)
            active.append(nid)
            dept_nodes[dept].append(nid)

    # Cross-references within departments (strong)
    for _dept, nodes in dept_nodes.items():
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                if random.random() < 0.6:
                    g.add_edge(nodes[i], nodes[j], weight=random.uniform(0.5, 1.0))

    # Cross-references between departments (weaker)
    all_depts = list(dept_nodes.keys())
    for i in range(len(all_depts)):
        for j in range(i + 1, len(all_depts)):
            nodes_a = dept_nodes[all_depts[i]]
            nodes_b = dept_nodes[all_depts[j]]
            for _ in range(2):
                a, b = random.choice(nodes_a), random.choice(nodes_b)
                g.add_edge(a, b, weight=random.uniform(0.1, 0.3))

    # Legacy documents: important but rarely accessed
    legacy = []
    legacy_names = [
        "Original_Architecture_v1", "Founding_Principles",
        "First_Incident_Postmortem", "Legacy_API_Docs", "Company_History",
    ]
    for name in legacy_names:
        nid = g.add_node(name, node_type="truth")
        # One weak connection to current docs
        target = random.choice(active)
        g.add_edge(nid, target, weight=random.uniform(0.05, 0.12))
        legacy.append(nid)

    # Obsolete documents: truly outdated
    obsolete = []
    obsolete_names = [
        "Deprecated_Tool_Manual", "Old_Vendor_Contract",
        "Removed_Feature_Spec", "Outdated_Compliance", "Dead_Project_Plan",
    ]
    for name in obsolete_names:
        nid = g.add_node(name, node_type="garbage")
        # No connections (completely irrelevant)
        obsolete.append(nid)

    return g, active, legacy, obsolete


def main():
    print("=" * 60)
    print("  Example 3: Enterprise Knowledge Base")
    print("=" * 60)

    g, active, legacy, obsolete = build_knowledge_graph()

    print("\nInitial knowledge base:")
    print(f"  Active documents:   {len(active)} (cross-referenced)")
    print(f"  Legacy documents:   {len(legacy)} (historically important)")
    print(f"  Obsolete documents: {len(obsolete)} (should be archived)")
    print(f"  Total: {g.node_count()} nodes, {g.edge_count()} edges")

    # ----------------------------------------------------------
    # Part 1: Run metabolic management
    # ----------------------------------------------------------
    print("\n--- Part 1: Metabolic Management (150 steps) ---")

    mgr = GraphMetabolicManager(
        g,
        seed=42,
        enable_rarity=True,
        enable_consistency=False,
        k_opt=4.0,  # Knowledge bases tend to be sparser
    )

    mgr.run(steps=150, verbose=True)

    legacy_survived = sum(1 for nid in legacy if g.has_node(nid))
    obsolete_survived = sum(1 for nid in obsolete if g.has_node(nid))

    print("\n  Results:")
    print(f"  Legacy docs protected: {legacy_survived}/{len(legacy)}")
    print(f"  Obsolete docs cleaned: {len(obsolete) - obsolete_survived}/{len(obsolete)}")
    print(f"  Remaining: {g.node_count()} nodes, {g.edge_count()} edges")

    # ----------------------------------------------------------
    # Part 2: Consistency Discovery demonstration
    # ----------------------------------------------------------
    print("\n--- Part 2: Consistency Discovery ---")

    # Build a fresh graph for demonstration
    g2, active2, _, _ = build_knowledge_graph(seed=99)

    cd = ConsistencyDiscovery(theta_l=0.60, theta_u=0.85)

    # Pick a few nodes to analyze
    sample_nodes = active2[:5]
    other_nodes = active2[5:]

    print("\n  Analyzing structural similarity between documents...")
    discoveries = cd.discover(g2, rare_node_ids=sample_nodes, candidate_ids=other_nodes)

    if discoveries:
        print(f"\n  Found {len(discoveries)} potential hidden relationships:")
        for rare_id, cand_id, score in discoveries[:5]:
            rare_label = g2.nodes[rare_id].label
            cand_label = g2.nodes[cand_id].label
            print(f"    {rare_label} <-> {cand_label} (score: {score:.3f})")
    else:
        print("\n  No hidden relationships found in the sandwich threshold range.")
        print("  This means documents are either very similar or very different.")

    print("\nDone!")


if __name__ == "__main__":
    main()
