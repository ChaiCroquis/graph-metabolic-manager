"""Tests for RarityProtection: multi-phase review."""

from __future__ import annotations

import random

import numpy as np

from graph_metabolic_manager import Graph, MetabolicControl, RarityProtection


def _run_simulation(with_protection: bool, seed: int = 42) -> dict:
    """Run a full simulation with or without rarity protection.

    Builds two communities (A, B) with truth and garbage nodes,
    then runs metabolic control for 120 steps.
    """
    random.seed(seed)
    np.random.seed(seed)
    g = Graph()

    # Communities
    comm_a = [g.add_node(f"A{i}") for i in range(20)]
    comm_b = [g.add_node(f"B{i}") for i in range(20)]
    for lst in (comm_a, comm_b):
        for i in range(len(lst)):
            for j in range(i + 1, len(lst)):
                if random.random() < 0.4:
                    g.add_edge(lst[i], lst[j], random.uniform(0.5, 1.0))
    for _ in range(5):
        g.add_edge(
            random.choice(comm_a),
            random.choice(comm_b),
            random.uniform(0.3, 0.6),
        )

    # Truth nodes (valuable but weakly connected)
    truth = []
    for i in range(10):
        nid = g.add_node(f"Truth{i}", node_type="truth")
        truth.append(nid)
        if random.random() < 0.5:
            g.add_edge(nid, random.choice(comm_a), random.uniform(0.05, 0.15))

    # Garbage nodes
    garbage = []
    for i in range(10):
        nid = g.add_node(f"Garb{i}", node_type="garbage")
        garbage.append(nid)
        if random.random() < 0.3 and len(garbage) > 1:
            tgt = random.choice(garbage[:-1])
            if tgt != nid:
                g.add_edge(nid, tgt, random.uniform(0.05, 0.1))

    n_truth = g.count_by_type("truth")
    n_garb = g.count_by_type("garbage")

    mc = MetabolicControl()
    rp = RarityProtection()

    if with_protection:
        for step in range(120):
            for nid in rp.identify_rare(g, step):
                rp.enter_protection(g, nid, step)
            # Discovery simulation
            for nid in list(rp.protected):
                if nid not in g.nodes:
                    continue
                nd = g.nodes[nid]
                if nd.phase != "phase1":
                    continue
                p = 0.8 if nd.node_type == "truth" else 0.02
                if random.random() < p:
                    cands = [n for n in g.nodes if n != nid and g.degree(n) > 2]
                    if cands:
                        g.add_edge(nid, random.choice(cands), 0.5)
                        nd.spoke_up = True
            rp.update_phases(g, step)
            mc.step(g, dt=1.0, protected=rp.protected)
    else:
        for _ in range(120):
            mc.step(g, dt=1.0)

    return {
        "truth_survived": g.count_by_type("truth"),
        "garbage_survived": g.count_by_type("garbage"),
        "truth_total": n_truth,
        "garbage_total": n_garb,
    }


class TestRarityProtection:
    """RarityProtection: multi-phase review system."""

    def test_without_protection_truth_lost(self) -> None:
        r = _run_simulation(False)
        assert r["truth_survived"] < r["truth_total"]

    def test_with_protection_truth_preserved(self) -> None:
        r0 = _run_simulation(False)
        r1 = _run_simulation(True)
        assert r1["truth_survived"] > r0["truth_survived"]

    def test_with_protection_garbage_removed(self) -> None:
        r = _run_simulation(True)
        assert r["garbage_survived"] < r["garbage_total"]

    def test_overall_score_improved(self) -> None:
        r0 = _run_simulation(False)
        r1 = _run_simulation(True)
        rate_t0 = r0["truth_survived"] / r0["truth_total"] * 100
        rate_t1 = r1["truth_survived"] / r1["truth_total"] * 100
        rate_g0 = (1 - r0["garbage_survived"] / r0["garbage_total"]) * 100
        rate_g1 = (1 - r1["garbage_survived"] / r1["garbage_total"]) * 100
        sc0 = (rate_t0 + rate_g0) / 2
        sc1 = (rate_t1 + rate_g1) / 2
        assert sc1 > sc0 + 10
