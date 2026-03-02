"""
Meta Control — Automatic parameter tuning via feedback loop.

Monitors the graph's health (average degree vs. optimal degree) and
dynamically adjusts the metabolic control's sensitivity parameter (alpha)
to maintain a balanced graph density.

Patent claims: 27-32

Key concepts:
- Health index: H = 1 - |kAvg - kOpt| / kOpt
- Update amount: Delta = eta * delta_k^n (n=4: rapid response to deviation)
- If H < target: increase alpha (more aggressive pruning)
- If H >= target: decrease alpha (ease off)
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from ._logging import TRACE

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .graph import Graph


# ------------------------------------------------------------------
# Default parameters (Patent specification)
# ------------------------------------------------------------------
DEFAULT_K_OPT = 5.0       # Optimal average degree
DEFAULT_H_TARGET = 0.7    # Target health index
DEFAULT_ETA = 0.001       # Learning rate
DEFAULT_META_N = 4         # Exponent for update amount (4th power)
DEFAULT_ALPHA_MIN = 0.5    # Minimum alpha
DEFAULT_ALPHA_MAX = 3.0    # Maximum alpha


# ------------------------------------------------------------------
# Mathematical functions
# ------------------------------------------------------------------

def health_index(k_avg: float, k_opt: float) -> float:
    """Compute the graph health index.

    Formula: H = 1 - |kAvg - kOpt| / kOpt

    H = 1.0 when average degree equals optimal.
    H = 0.0 when deviation equals optimal degree.

    Args:
        k_avg: Current average degree.
        k_opt: Optimal (target) average degree.

    Returns:
        Health index in [0, 1].
    """
    if k_opt == 0:
        return 0.0
    return max(0.0, 1.0 - abs(k_avg - k_opt) / k_opt)


def meta_update_amount(
    delta_k: float, eta: float = DEFAULT_ETA, n: int = DEFAULT_META_N
) -> float:
    """Compute the parameter update amount.

    Formula: Delta = eta * delta_k^n

    Using n=4 (4th power) means:
    - Small deviations -> tiny updates (stable)
    - Large deviations -> rapid corrections (responsive)

    Args:
        delta_k: Deviation from optimal degree (k_avg - k_opt).
        eta: Learning rate.
        n: Exponent (default 4).

    Returns:
        Update amount Delta.
    """
    return eta * (delta_k ** n)


# ------------------------------------------------------------------
# MetaControl class
# ------------------------------------------------------------------

class MetaControl:
    """Automatic parameter tuning via health-based feedback loop.

    Monitors the graph's average degree and adjusts the metabolic
    control's alpha parameter to maintain target density:

    - Graph too dense (H < target): increase alpha -> more pruning
    - Graph at target (H >= target): decrease alpha -> less pruning

    The 4th-power update rule ensures stability under small fluctuations
    while responding quickly to large imbalances.

    Args:
        k_opt: Optimal average degree (default 5.0).
        h_target: Target health index (default 0.7).
        eta: Learning rate (default 0.001).
        n: Update exponent (default 4).
        alpha_min: Minimum alpha value (default 0.5).
        alpha_max: Maximum alpha value (default 3.0).
        initial_alpha: Starting alpha value (default 2.0).

    Example:
        >>> meta = MetaControl()
        >>> mc = MetabolicControl()
        >>> for t in range(100):
        ...     info = meta.step(graph)
        ...     mc.alpha = meta.current_alpha
        ...     mc.step(graph, dt=1.0)
    """

    def __init__(
        self,
        k_opt: float = DEFAULT_K_OPT,
        h_target: float = DEFAULT_H_TARGET,
        eta: float = DEFAULT_ETA,
        n: int = DEFAULT_META_N,
        alpha_min: float = DEFAULT_ALPHA_MIN,
        alpha_max: float = DEFAULT_ALPHA_MAX,
        initial_alpha: float = 2.0,
    ):
        if k_opt <= 0:
            raise ValueError(f"k_opt must be positive, got {k_opt}")
        if not 0 <= h_target <= 1:
            raise ValueError(f"h_target must be in [0, 1], got {h_target}")
        if eta <= 0:
            raise ValueError(f"eta must be positive, got {eta}")
        if n < 1:
            raise ValueError(f"n must be >= 1, got {n}")
        if alpha_min >= alpha_max:
            raise ValueError(f"alpha_min must be < alpha_max, got {alpha_min} >= {alpha_max}")
        self.k_opt = k_opt
        self.h_target = h_target
        self.eta = eta
        self.n = n
        self.alpha_min = alpha_min
        self.alpha_max = alpha_max
        self.current_alpha = initial_alpha
        self.history: list[dict[str, float]] = []

    def step(self, graph: Graph) -> dict[str, float]:
        """Execute one meta-control step.

        Measures graph health and updates alpha accordingly.

        Args:
            graph: The graph to monitor.

        Returns:
            Dict with: k_avg, k_opt, H, delta_k, alpha.
        """
        k_avg = graph.avg_degree()
        H = health_index(k_avg, self.k_opt)
        delta_k = max(0.0, k_avg - self.k_opt)

        delta = meta_update_amount(delta_k, self.eta, self.n)
        old_alpha = self.current_alpha
        if self.h_target > H:
            self.current_alpha += delta
            direction = "+Delta"
        else:
            self.current_alpha -= delta * 0.5
            direction = "-Delta*0.5"

        self.current_alpha = max(self.alpha_min, min(self.alpha_max, self.current_alpha))

        if logger.isEnabledFor(TRACE):
            logger.log(
                TRACE,
                "meta: k_avg=%.4f, k_opt=%.4f, "
                "H=1-|%.4f-%.4f|/%.4f=%.4f, h_target=%.4f, "
                "deltak=%.4f, Delta=%.6f*%.4f^%d=%.6f, "
                "alpha: %.4f -> %.4f (%s) "
                "[clamped to [%.2f,%.2f]]",
                k_avg, self.k_opt,
                k_avg, self.k_opt, self.k_opt, H, self.h_target,
                delta_k, self.eta, delta_k, self.n, delta,
                old_alpha, self.current_alpha, direction,
                self.alpha_min, self.alpha_max,
            )

        record = {
            "k_avg": k_avg,
            "k_opt": self.k_opt,
            "H": H,
            "delta_k": delta_k,
            "alpha": self.current_alpha,
        }
        self.history.append(record)
        logger.debug("Meta: H=%.3f, alpha=%.3f (k_avg=%.2f, k_opt=%.2f)", H, self.current_alpha, k_avg, self.k_opt)
        return record
