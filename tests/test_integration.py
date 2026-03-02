"""Tests for Integration: E-commerce scenario and GraphMetabolicManager."""

from __future__ import annotations

import random

import numpy as np

from graph_metabolic_manager import (
    Graph,
    GraphMetabolicManager,
    MetabolicControl,
    RarityProtection,
)


class TestECScenario:
    """ECScenario: E-Commerce product recommendation application."""

    def _run_ec(self) -> tuple[Graph, int, int, int]:
        """Build and run an EC simulation, returning final graph and initial counts."""
        random.seed(43)
        np.random.seed(43)
        g = Graph()

        popular = [g.add_node(f"Pop{i}") for i in range(15)]
        niche = [g.add_node(f"Niche{i}", node_type="truth") for i in range(5)]
        _seasonal = [g.add_node(f"Seasonal{i}", node_type="garbage") for i in range(5)]

        for i in range(len(popular)):
            for j in range(i + 1, len(popular)):
                if random.random() < 0.35:
                    g.add_edge(popular[i], popular[j], random.uniform(0.5, 1.0))
        for n in niche:
            g.add_edge(n, random.choice(popular), random.uniform(0.05, 0.15))

        n0 = g.node_count()
        ni0 = g.count_by_type("truth")
        ns0 = g.count_by_type("garbage")

        rp = RarityProtection()
        mc = MetabolicControl()
        for step in range(150):
            for nid in rp.identify_rare(g, step):
                rp.enter_protection(g, nid, step)
            for nid in list(rp.protected):
                if nid not in g.nodes:
                    continue
                nd = g.nodes[nid]
                if nd.phase == "phase1":
                    p = 0.7 if nd.node_type == "truth" else 0.005
                    if random.random() < p:
                        cands = [n for n in g.nodes if n != nid and g.degree(n) > 2]
                        if cands:
                            g.add_edge(nid, random.choice(cands), 0.5)
                            nd.spoke_up = True
            rp.update_phases(g, step)
            mc.step(g, dt=1.0, protected=rp.protected)

        return g, n0, ni0, ns0

    def test_niche_products_protected(self) -> None:
        g, _n0, _ni0, _ns0 = self._run_ec()
        assert g.count_by_type("truth") > 0

    def test_seasonal_products_cleaned(self) -> None:
        g, _n0, _ni0, ns0 = self._run_ec()
        assert g.count_by_type("garbage") < ns0

    def test_data_volume_optimized(self) -> None:
        g, n0, _ni0, _ns0 = self._run_ec()
        assert g.node_count() < n0


class TestManagerIntegration:
    """ManagerIntegration: unified GraphMetabolicManager end-to-end."""

    def _build_and_run(self) -> tuple[GraphMetabolicManager, int, int, list]:
        random.seed(42)
        g = Graph()
        for i in range(20):
            g.add_node(f"N{i}")
        for i in range(20):
            for j in range(i + 1, 20):
                if random.random() < 0.3:
                    g.add_edge(i, j, random.uniform(0.3, 1.0))
        n0 = g.node_count()
        e0 = g.edge_count()
        mgr = GraphMetabolicManager(g, seed=42)
        results = mgr.run(steps=50)
        return mgr, n0, e0, results

    def test_runs_without_error(self) -> None:
        _mgr, _n0, _e0, results = self._build_and_run()
        assert len(results) == 50

    def test_prunes_edges(self) -> None:
        mgr, _n0, e0, _results = self._build_and_run()
        assert mgr.graph.edge_count() < e0

    def test_summary_readable(self) -> None:
        mgr, _n0, _e0, _results = self._build_and_run()
        assert "GraphMetabolicManager" in mgr.summary()
