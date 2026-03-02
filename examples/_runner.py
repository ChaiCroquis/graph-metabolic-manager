"""Shared runner for industry scenario examples (07-28).

Implements the common Scenario A / Scenario B / Consistency Discovery /
Comparison template used by all industry examples.  Each example file
provides only a ``ScenarioConfig`` dataclass with domain-specific labels,
node names, and tuning parameters.

This module is **not** a public API --- it exists solely to eliminate
~4,000 lines of duplicated template code across 22 example files.
"""

from __future__ import annotations

import logging
import random
import sys
from dataclasses import dataclass

from graph_metabolic_manager import (
    ConsistencyDiscovery,
    Graph,
    GraphMetabolicManager,
)

logging.basicConfig(
    level=logging.INFO, format="%(message)s", stream=sys.stdout,
)


# ------------------------------------------------------------------
# Configuration dataclass
# ------------------------------------------------------------------

@dataclass
class ScenarioConfig:
    """All domain-specific data for one industry example."""

    # ---- Identity ----
    number: int                            # Example number (7-28)
    title: str                             # e.g. "Telecommunications Network"

    # ---- Graph topology ----
    categories: dict[str, list[str]]       # Category name -> list of node names
    cross_links: list[tuple[str, str]]     # Cross-category link pairs

    # ---- Node labels ----
    entity_normal: str                     # entity tag for normal nodes
    entity_rare: str                       # entity tag for rare (truth) nodes
    entity_garbage: str                    # entity tag for garbage nodes
    rare_names: list[str]                  # 6 rare node names
    garbage_names: list[str]               # 8 garbage node names

    # ---- Display text ----
    normal_label: str                      # "Core routers"
    rare_label: str                        # "Backup relays"
    garbage_label: str                     # "Legacy equipment"
    scenario_a_desc: str = ""              # "(Traditional network pruning)"
    scenario_b_desc: str = ""              # "(Backup routes preserved)"
    discovery_title: str = ""              # Part 2 heading
    discovery_description: str = ""        # Part 2 subtitle
    discovery_conclusion: str = ""         # Part 2 closing remark
    loss_message: str = ""                 # Comparison closing remark

    # ---- Graph generation parameters ----
    connect_prob: float = 0.45             # Intra-category edge probability
    cross_link_attempts: int = 3           # Random links per cross-link pair
    cross_link_prob: float = 0.4           # Probability of each cross link
    normal_weight_range: tuple[float, float] = (0.5, 1.0)
    cross_weight_range: tuple[float, float] = (0.2, 0.6)
    rare_weight_range: tuple[float, float] = (0.04, 0.10)

    # ---- Manager parameters ----
    k_opt: float = 4.0
    alpha: float = 1.8
    beta: float = 0.03
    prune_threshold: float = 0.08
    steps_a: int = 120
    steps_b: int = 150

    # ---- Consistency discovery parameters ----
    theta_l: float = 0.55
    theta_u: float = 0.85


# ------------------------------------------------------------------
# Graph builder
# ------------------------------------------------------------------

def build_scenario_graph(
    cfg: ScenarioConfig,
    seed: int = 42,
) -> tuple[Graph, list[int], list[int], list[int]]:
    """Build a graph from *cfg*.

    Returns:
        (graph, normal_ids, rare_ids, garbage_ids)
    """
    random.seed(seed)
    g = Graph()

    # --- Normal nodes (by category) ---
    normal_ids: list[int] = []
    cat_nodes: dict[str, list[int]] = {}
    for cat, names in cfg.categories.items():
        cat_nodes[cat] = []
        for name in names:
            nid = g.add_node(
                name,
                node_type="normal",
                entity=cfg.entity_normal,
                category=cat,
            )
            normal_ids.append(nid)
            cat_nodes[cat].append(nid)

    # --- Intra-category edges ---
    for _cat, nodes in cat_nodes.items():
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                if random.random() < cfg.connect_prob:
                    g.add_edge(
                        nodes[i], nodes[j],
                        weight=random.uniform(*cfg.normal_weight_range),
                    )

    # --- Cross-category links ---
    for cat_a, cat_b in cfg.cross_links:
        for _ in range(cfg.cross_link_attempts):
            a = random.choice(cat_nodes[cat_a])
            b = random.choice(cat_nodes[cat_b])
            if random.random() < cfg.cross_link_prob:
                g.add_edge(a, b, weight=random.uniform(*cfg.cross_weight_range))

    # --- Rare (truth) nodes ---
    rare_ids: list[int] = []
    for name in cfg.rare_names:
        nid = g.add_node(name, node_type="truth", entity=cfg.entity_rare)
        target = random.choice(normal_ids)
        g.add_edge(nid, target, weight=random.uniform(*cfg.rare_weight_range))
        rare_ids.append(nid)

    # --- Garbage nodes ---
    garbage_ids: list[int] = []
    for name in cfg.garbage_names:
        nid = g.add_node(name, node_type="garbage", entity=cfg.entity_garbage)
        garbage_ids.append(nid)

    return g, normal_ids, rare_ids, garbage_ids


# ------------------------------------------------------------------
# Full example runner
# ------------------------------------------------------------------

def run_industry_example(cfg: ScenarioConfig) -> None:
    """Execute the standard Scenario A / B / Discovery / Comparison template."""

    n_cats = len(cfg.categories)

    # === Banner ===
    print("=" * 60)
    print(f"  Example {cfg.number}: {cfg.title}")
    print("=" * 60)

    g, normal_ids, rare_ids, garbage_ids = build_scenario_graph(cfg)

    print(f"\nInitial {cfg.title.lower()} graph:")
    print(f"  {cfg.normal_label}:{' ' * max(1, 22 - len(cfg.normal_label))}"
          f"{len(normal_ids)} ({n_cats} categories)")
    print(f"  {cfg.rare_label}:{' ' * max(1, 22 - len(cfg.rare_label))}"
          f"{len(rare_ids)} (irreplaceable)")
    print(f"  {cfg.garbage_label}:{' ' * max(1, 22 - len(cfg.garbage_label))}"
          f"{len(garbage_ids)} (to clean)")
    print(f"  Total: {g.node_count()} nodes, {g.edge_count()} edges")
    print(f"  Average degree: {g.avg_degree():.2f}")

    # === Scenario A: WITHOUT rarity protection ===
    print("\n--- Scenario A: Without Rarity Protection ---")
    if cfg.scenario_a_desc:
        print(f"  {cfg.scenario_a_desc}")

    g_a, _, rare_a, _ = build_scenario_graph(cfg)
    mgr_a = GraphMetabolicManager(
        g_a, seed=42,
        enable_rarity=False,
        enable_meta=True,
        k_opt=cfg.k_opt,
    )
    mgr_a.run(steps=cfg.steps_a)

    rare_a_surv = sum(1 for nid in rare_a if g_a.has_node(nid))
    print(f"  {cfg.rare_label} surviving: {rare_a_surv}/{len(rare_ids)}")
    if rare_a_surv == 0:
        print(f"  [DANGER] ALL {cfg.rare_label.lower()} lost!")

    # === Scenario B: WITH rarity protection ===
    print("\n--- Scenario B: With Rarity Protection ---")
    if cfg.scenario_b_desc:
        print(f"  {cfg.scenario_b_desc}")

    mgr = GraphMetabolicManager(
        g, seed=42,
        enable_rarity=True,
        enable_consistency=False,
        k_opt=cfg.k_opt,
        alpha=cfg.alpha,
        beta=cfg.beta,
        prune_threshold=cfg.prune_threshold,
    )
    mgr.run(steps=cfg.steps_b, verbose=True)

    rare_survived = sum(1 for nid in rare_ids if g.has_node(nid))
    garbage_survived = sum(1 for nid in garbage_ids if g.has_node(nid))
    normal_survived = sum(1 for nid in normal_ids if g.has_node(nid))

    print("\n  Results:")
    print(f"  {cfg.normal_label}: {normal_survived}/{len(normal_ids)} remaining")
    print(f"  {cfg.rare_label}:  {rare_survived}/{len(rare_ids)} PROTECTED")
    print(f"  {cfg.garbage_label}: "
          f"{len(garbage_ids) - garbage_survived}/{len(garbage_ids)} cleaned")

    # === Part 2: Consistency discovery ===
    if cfg.discovery_title:
        print(f"\n--- Part 2: {cfg.discovery_title} ---")
        if cfg.discovery_description:
            print(f"  ({cfg.discovery_description})")

        g2, normal2, rare2, _ = build_scenario_graph(cfg, seed=99)
        cd = ConsistencyDiscovery(
            theta_l=cfg.theta_l, theta_u=cfg.theta_u, k_hop=2,
        )
        discoveries = cd.discover(
            g2, rare_node_ids=rare2, candidate_ids=normal2,
        )

        if discoveries:
            print(f"\n  Found {len(discoveries)} structural similarities:")
            seen: set[tuple[str, str]] = set()
            count = 0
            for r_id, n_id, score in discoveries:
                if count >= 6:
                    break
                r_label = g2.nodes[r_id].label
                n_label = g2.nodes[n_id].label
                key = (r_label, n_label)
                if key not in seen:
                    seen.add(key)
                    print(f"    {r_label} <-> {n_label} "
                          f"(similarity: {score:.3f})")
                    count += 1
            if cfg.discovery_conclusion:
                print(f"\n  {cfg.discovery_conclusion}")
        else:
            print("\n  No structural similarities detected.")

    # === Comparison ===
    print("\n--- Comparison ---")
    print(f"  Without protection: {rare_a_surv}/{len(rare_ids)} "
          f"{cfg.rare_label.lower()}")
    print(f"  With protection:    {rare_survived}/{len(rare_ids)} "
          f"{cfg.rare_label.lower()}")
    improvement = rare_survived - rare_a_surv
    if improvement > 0:
        print(f"  -> Rarity protection saved {improvement} "
              f"{cfg.rare_label.lower()}")
    if cfg.loss_message:
        print(f"\n  {cfg.loss_message}")

    print("\nDone!")
