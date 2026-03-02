"""Graph visualization helpers for Streamlit demo pages."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from graph_metabolic_manager import Graph

try:
    import networkx as nx
except ImportError:
    nx = None  # type: ignore[assignment]

# ---- Color palette (consistent across all pages) ----
COLORS = {
    "primary": "#1565C0",
    "accent": "#F44336",
    "success": "#4CAF50",
    "warning": "#FF9800",
    "info": "#42A5F5",
    "error": "#EF5350",
    "purple": "#9C27B0",
    "deep_orange": "#FF5722",
    "gray": "#E0E0E0",
    "gold": "#FFD600",
}

NODE_TYPE_COLORS = {
    "normal": "#42A5F5",
    "truth": "#66BB6A",
    "garbage": "#EF5350",
    "hub": "#FFA726",
    "sensor": "#AB47BC",
    "device": "#26C6DA",
}

LAYER_COLORS = {
    "rare": "#9C27B0",
    "core": "#FF9800",
    "edge": "#BDBDBD",
}

PHASE_COLORS = {
    "normal": "#E0E0E0",
    "phase1": "#42A5F5",
    "phase2": "#FFA726",
    "released": "#66BB6A",
    "removed": "#EF5350",
}


def apply_style() -> None:
    """Apply the shared matplotlib style."""
    plt.rcParams.update({
        "figure.facecolor": "white",
        "axes.grid": True,
        "axes.grid.which": "both",
        "grid.alpha": 0.3,
        "font.size": 11,
    })


def to_networkx(graph: Graph) -> "nx.Graph":
    """Convert library Graph to NetworkX for visualization."""
    if nx is None:
        raise ImportError("networkx is required for graph visualization")
    G = nx.Graph()
    for nid, node in graph.nodes.items():
        G.add_node(
            nid,
            label=node.label,
            node_type=node.node_type,
            layer=node.layer,
            is_protected=node.is_protected,
            phase=node.phase,
        )
    for (u, v), w in graph.edges.items():
        G.add_edge(u, v, weight=w)
    return G


def draw_graph(
    graph: Graph,
    ax: plt.Axes,
    title: str = "",
    color_by: str = "type",
    highlight_protected: bool = False,
    seed: int = 42,
) -> None:
    """Draw a graph on the given matplotlib axes.

    Args:
        graph: The library Graph to draw.
        ax: Matplotlib axes to draw on.
        title: Title for the subplot.
        color_by: "type" for node_type coloring, "layer" for hierarchy layer.
        highlight_protected: Draw halos around protected nodes.
        seed: Layout seed for reproducibility.
    """
    if nx is None:
        ax.text(0.5, 0.5, "networkx not installed", ha="center", va="center")
        return

    G = to_networkx(graph)
    if len(G.nodes) == 0:
        ax.text(0.5, 0.5, "Empty graph", ha="center", va="center",
                transform=ax.transAxes, fontsize=12)
        ax.set_title(title)
        return

    pos = nx.spring_layout(G, seed=seed, k=1.5 / max(1, len(G.nodes) ** 0.5))

    # Node colors
    if color_by == "layer":
        node_colors = [
            LAYER_COLORS.get(G.nodes[n].get("layer", "edge"), "#BDBDBD")
            for n in G.nodes
        ]
    else:
        node_colors = [
            NODE_TYPE_COLORS.get(G.nodes[n].get("node_type", "normal"), "#42A5F5")
            for n in G.nodes
        ]

    # Edge widths based on weight
    weights = [G[u][v].get("weight", 1.0) for u, v in G.edges()]
    edge_widths = [max(0.5, w * 2) for w in weights]

    # Draw protected node halos first
    if highlight_protected:
        protected_nodes = [n for n in G.nodes if G.nodes[n].get("is_protected")]
        if protected_nodes:
            protected_colors = [
                PHASE_COLORS.get(G.nodes[n].get("phase", "phase1"), "#42A5F5")
                for n in protected_nodes
            ]
            nx.draw_networkx_nodes(
                G, pos, nodelist=protected_nodes,
                node_color=protected_colors, node_size=600,
                alpha=0.3, ax=ax,
            )

    # Draw main graph
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=300,
                           edgecolors="black", linewidths=0.5, ax=ax)
    nx.draw_networkx_edges(G, pos, width=edge_widths, alpha=0.6,
                           edge_color="#888888", ax=ax)
    labels = {n: G.nodes[n].get("label", str(n)) for n in G.nodes}
    nx.draw_networkx_labels(G, pos, labels, font_size=7, ax=ax)

    ax.set_title(title, fontsize=12)
    ax.axis("off")
