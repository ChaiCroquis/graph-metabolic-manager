"""
Graph Metabolic Manager — Public API re-export.

Intelligent graph data structure management with automatic pruning,
rarity protection, and hidden relationship discovery.

Patent claims: 1-50 (all claims via re-export)
Key formula: See individual modules for patent-specific formulas.

Usage:
    from graph_metabolic_manager import Graph, MetabolicControl, RarityProtection

    g = Graph()
    n1 = g.add_node("Product A")
    n2 = g.add_node("Product B")
    g.add_edge(n1, n2, weight=1.0)

    mc = MetabolicControl()
    mc.step(g, dt=1.0)

License:
    Source code: Apache License 2.0 (with Patent Exclusion)
    Patented algorithms: Commercial use requires a separate patent license
    See PATENT_NOTICE.md for details.
"""

from __future__ import annotations

__version__ = "0.2.1"

from ._logging import TRACE
from .consistency import (
    ConsistencyDiscovery,
    attribute_similarity,
    compute_structural_repr,
    consistency_score,
    relational_similarity,
)
from .graph import Graph, Node
from .manager import GraphMetabolicManager
from .meta_control import MetaControl, health_index, meta_update_amount
from .metabolic import MetabolicControl, decay_rate, update_weight
from .rarity import RarityProtection

__all__ = [
    "Graph",
    "Node",
    "MetabolicControl",
    "RarityProtection",
    "ConsistencyDiscovery",
    "MetaControl",
    "GraphMetabolicManager",
    "TRACE",
    "decay_rate",
    "update_weight",
    "compute_structural_repr",
    "consistency_score",
    "relational_similarity",
    "attribute_similarity",
    "health_index",
    "meta_update_amount",
]
