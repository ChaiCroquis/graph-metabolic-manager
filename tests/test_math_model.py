"""Tests for MathModel: decay rate and weight update formulas."""

from __future__ import annotations

import math

import pytest

from graph_metabolic_manager import decay_rate, update_weight
from graph_metabolic_manager.metabolic import DEFAULT_BETA, DEFAULT_GAMMA


class TestDecayRate:
    """Decay rate: lambda(C) = beta * (1 + gamma * C^alpha)."""

    def test_monotonically_increasing(self) -> None:
        vals = [decay_rate(float(c)) for c in range(20)]
        assert all(vals[i] <= vals[i + 1] for i in range(len(vals) - 1))

    def test_crowded_higher_than_sparse(self) -> None:
        assert decay_rate(10.0) > decay_rate(2.0)

    def test_formula_accuracy(self) -> None:
        lam = decay_rate(5.0, alpha=2.0)
        expected = DEFAULT_BETA * (1 + DEFAULT_GAMMA * 25.0)
        assert lam == pytest.approx(expected)


class TestWeightUpdate:
    """Weight update: w_new = w * exp(-lambda * dt)."""

    def test_exponential_decay(self) -> None:
        w0 = 1.0
        lam = decay_rate(5.0)
        w1 = update_weight(w0, lam, 1.0)
        w2 = update_weight(w1, lam, 1.0)
        assert w1 == pytest.approx(w0 * math.exp(-lam))
        assert w2 == pytest.approx(w0 * math.exp(-lam * 2))

    def test_crowded_edges_decay_faster(self) -> None:
        ws = update_weight(1.0, decay_rate(2.0), 5.0)
        wd = update_weight(1.0, decay_rate(10.0), 5.0)
        assert wd < ws
