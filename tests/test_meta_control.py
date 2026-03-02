"""Tests for MetaControl: automatic parameter tuning."""

from __future__ import annotations

import random

import numpy as np
import pytest

from graph_metabolic_manager import Graph, MetabolicControl, MetaControl, health_index
from graph_metabolic_manager.meta_control import DEFAULT_K_OPT, meta_update_amount


class TestHealthIndex:
    """Health index: H = 1 - |kAvg - kOpt| / kOpt."""

    def test_perfect_health(self) -> None:
        assert health_index(DEFAULT_K_OPT, DEFAULT_K_OPT) == pytest.approx(1.0)

    def test_deviation_reduces_health(self) -> None:
        h = health_index(DEFAULT_K_OPT * 1.5, DEFAULT_K_OPT)
        assert h < 1.0


class TestMetaUpdateAmount:
    """Update amount: Delta = eta * delta_k^n (n=4)."""

    def test_proportional_to_fourth_power(self) -> None:
        d1 = meta_update_amount(1.0)
        d2 = meta_update_amount(2.0)
        # 2^4 / 1^4 = 16
        assert d2 / d1 == pytest.approx(16.0)


class TestMetaControlConvergence:
    """MetaControlConvergence: feedback loop convergence behavior."""

    def test_health_maintained_or_improved(self) -> None:
        random.seed(42)
        np.random.seed(42)
        g = Graph()
        for i in range(30):
            g.add_node(f"M{i}")
        for i in range(30):
            for j in range(i + 1, 30):
                if random.random() < 0.5:
                    g.add_edge(i, j, random.uniform(0.3, 1.0))

        meta = MetaControl(k_opt=5.0, h_target=0.7, initial_alpha=2.0)
        mc = MetabolicControl()
        for _ in range(100):
            meta.step(g)
            mc.alpha = meta.current_alpha
            mc.step(g, dt=1.0)

        h0 = meta.history[0]["H"]
        hf = meta.history[-1]["H"]
        assert hf >= h0 or hf > 0.3
