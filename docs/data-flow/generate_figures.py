#!/usr/bin/env python3
"""Generate all data-flow visualization figures for patent documentation.

Produces 10 PNG figures in docs/data-flow/figures/ using the actual
graph-metabolic-manager library with concrete numerical examples.

Usage:
    python docs/data-flow/generate_figures.py
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for CI/headless

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# --------------- Library imports (the actual library) ----------------
# Ensure the package is importable
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from graph_metabolic_manager import (
    Graph,
    GraphMetabolicManager,
    MetabolicControl,
    MetaControl,
    RarityProtection,
    compute_structural_repr,
    consistency_score,
    health_index,
    relational_similarity,
    attribute_similarity,
)
from graph_metabolic_manager.metabolic import (
    DEFAULT_ALPHA,
    DEFAULT_BETA,
    DEFAULT_GAMMA,
    DEFAULT_PRUNE_THRESHOLD,
    decay_rate,
    update_weight,
)
from graph_metabolic_manager.meta_control import (
    DEFAULT_K_OPT,
    DEFAULT_H_TARGET,
    meta_update_amount,
)
from graph_metabolic_manager.consistency import (
    DEFAULT_THETA_L,
    DEFAULT_THETA_U,
    DEFAULT_W_SYS,
    DEFAULT_W_REL,
    DEFAULT_W_ATTR,
    cosine_similarity,
    structural_diff_similarity,
    sign_agreement,
)

FIGURES_DIR = Path(__file__).resolve().parent / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# ---- Global style ----
plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.grid": True,
    "axes.grid.which": "both",
    "grid.alpha": 0.3,
    "font.size": 11,
})


# ====================================================================
# Helper: build a sample graph
# ====================================================================

def _build_sample_graph(seed: int = 42) -> tuple[Graph, list[int], list[int], list[int]]:
    """Build a 20-node sample graph with normal/truth/garbage nodes.

    Returns:
        (graph, normal_ids, truth_ids, garbage_ids)
    """
    rng = random.Random(seed)
    g = Graph()

    normal = [g.add_node(f"N{i}", node_type="normal") for i in range(10)]
    truth = [g.add_node(f"T{i}", node_type="truth") for i in range(4)]
    garbage = [g.add_node(f"G{i}", node_type="garbage") for i in range(6)]

    # Dense connections among normals
    for i in range(len(normal)):
        for j in range(i + 1, len(normal)):
            if rng.random() < 0.5:
                g.add_edge(normal[i], normal[j], rng.uniform(0.5, 1.0))

    # Truth nodes: sparse connections (degree=1 each)
    for tid in truth:
        partner = rng.choice(normal)
        if not g.has_edge(tid, partner):
            g.add_edge(tid, partner, rng.uniform(0.3, 0.7))

    # Garbage: isolated (no edges)
    return g, normal, truth, garbage


# ====================================================================
# Figure 1: Decay Rate Curve
# ====================================================================

def fig01_decay_rate_curve() -> None:
    """Plot lambda(C) = beta * (1 + gamma * C^alpha) for different alpha."""
    C = np.linspace(0, 20, 200)

    fig, ax = plt.subplots(figsize=(10, 6))

    for alpha, style, color in [(1.0, "--", "#2196F3"), (2.0, "-", "#F44336"), (3.0, "-.", "#4CAF50")]:
        lam = [decay_rate(c, alpha=alpha) for c in C]
        label_suffix = " (default)" if alpha == DEFAULT_ALPHA else ""
        ax.plot(C, lam, style, color=color, linewidth=2.5,
                label=f"alpha={alpha:.1f}{label_suffix}")

    # Concrete example points (default alpha=2.0)
    examples = [(2, decay_rate(2)), (5, decay_rate(5)), (10, decay_rate(10))]
    for c_val, lam_val in examples:
        ax.plot(c_val, lam_val, "ko", markersize=8, zorder=5)
        ax.annotate(f"C={c_val}  ->  lambda={lam_val:.3f}",
                    (c_val, lam_val), textcoords="offset points",
                    xytext=(12, 8), fontsize=10,
                    bbox=dict(boxstyle="round,pad=0.3", fc="lightyellow", ec="gray"))

    ax.set_xlabel("Congestion C = deg(u) + deg(v)", fontsize=13)
    ax.set_ylabel("Decay Rate lambda(C)", fontsize=13)
    ax.set_title("Figure 1: Adaptive Decay Rate  --  lambda(C) = beta(1 + gamma * C^alpha)\n"
                 f"beta={DEFAULT_BETA}, gamma={DEFAULT_GAMMA}", fontsize=14)
    ax.legend(fontsize=12)
    ax.set_xlim(0, 20)
    ax.set_ylim(bottom=0)

    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "01_decay_rate_curve.png", dpi=150)
    plt.close(fig)
    print("[OK] 01_decay_rate_curve.png")


# ====================================================================
# Figure 2: Weight Decay Timeline
# ====================================================================

def fig02_weight_decay_timeline() -> None:
    """Plot edge weight over time for different congestion levels."""
    steps = np.arange(0, 11)
    scenarios = [
        (2.0,  "#4CAF50", "Sparse (C=2)"),
        (5.0,  "#FF9800", "Medium (C=5)"),
        (10.0, "#F44336", "Dense (C=10)"),
    ]

    fig, ax = plt.subplots(figsize=(10, 6))

    for C, color, label in scenarios:
        lam = decay_rate(C)
        weights = [update_weight(1.0, lam, float(t)) for t in steps]
        ax.plot(steps, weights, "o-", color=color, linewidth=2.5, markersize=6, label=label)

        # Find step where weight first drops below threshold
        for t, w in zip(steps, weights):
            if w < DEFAULT_PRUNE_THRESHOLD:
                ax.annotate(f"Pruned at t={t}\n(w={w:.4f})",
                            (t, w), textcoords="offset points",
                            xytext=(10, 10), fontsize=9,
                            arrowprops=dict(arrowstyle="->", color=color),
                            bbox=dict(boxstyle="round,pad=0.3", fc="lightyellow"))
                break

    ax.axhline(y=DEFAULT_PRUNE_THRESHOLD, color="red", linestyle=":", linewidth=2,
               label=f"Prune Threshold = {DEFAULT_PRUNE_THRESHOLD}")

    ax.set_xlabel("Time Step (dt=1.0)", fontsize=13)
    ax.set_ylabel("Edge Weight w", fontsize=13)
    ax.set_title("Figure 2: Weight Decay  --  w(t) = w0 * exp(-lambda * t)\n"
                 f"alpha={DEFAULT_ALPHA}, beta={DEFAULT_BETA}, gamma={DEFAULT_GAMMA}",
                 fontsize=14)
    ax.legend(fontsize=11)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 1.05)

    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "02_weight_decay_timeline.png", dpi=150)
    plt.close(fig)
    print("[OK] 02_weight_decay_timeline.png")


# ====================================================================
# Figure 3: Metabolic Control Before/After
# ====================================================================

def fig03_metabolic_before_after() -> None:
    """Bar chart: graph size before vs after metabolic control."""
    g, normal, truth, garbage = _build_sample_graph()
    init_nodes = g.node_count()
    init_edges = g.edge_count()

    mc = MetabolicControl()
    for _ in range(120):
        mc.step(g, dt=1.0)

    final_nodes = g.node_count()
    final_edges = g.edge_count()

    fig, ax = plt.subplots(figsize=(8, 6))
    x = np.arange(2)
    w = 0.35

    before = [init_nodes, init_edges]
    after = [final_nodes, final_edges]

    bars1 = ax.bar(x - w / 2, before, w, label="Before (t=0)", color="#42A5F5", edgecolor="black")
    bars2 = ax.bar(x + w / 2, after, w, label="After (t=120)", color="#EF5350", edgecolor="black")

    ax.set_xticks(x)
    ax.set_xticklabels(["Nodes", "Edges"], fontsize=13)
    ax.set_ylabel("Count", fontsize=13)
    ax.set_title("Figure 3: Metabolic Control  --  Before vs After (120 steps)\n"
                 f"alpha={DEFAULT_ALPHA}, beta={DEFAULT_BETA}, prune_threshold={DEFAULT_PRUNE_THRESHOLD}",
                 fontsize=14)
    ax.legend(fontsize=12)

    # Value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h + 0.3,
                    str(int(h)), ha="center", fontsize=13, fontweight="bold")

    ax.set_ylim(0, max(before) * 1.2)

    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "03_metabolic_before_after.png", dpi=150)
    plt.close(fig)
    print("[OK] 03_metabolic_before_after.png")


# ====================================================================
# Figure 4: Rarity Protection Phase Timeline
# ====================================================================

def fig04_rarity_phase_timeline() -> None:
    """Timeline of 3 nodes through rarity protection phases."""
    # Simulate the phase state machine manually for visualization
    twait1, twait2 = 50, 50

    # Node A: spoke_up=True at t=40, survives
    # Node B: spoke_up=False, degree=0, removed
    # Node C: no protection (not rare)
    total_steps = 130

    node_a_phases = []
    node_b_phases = []
    node_c_phases = []

    for t in range(total_steps):
        # Node A: enters protection at t=5
        if t < 5:
            node_a_phases.append("normal")
        elif t < 5 + twait1:
            node_a_phases.append("phase1")
        elif t < 5 + twait1 + twait2:
            node_a_phases.append("phase2")
        else:
            node_a_phases.append("released")

        # Node B: enters protection at t=5
        if t < 5:
            node_b_phases.append("normal")
        elif t < 5 + twait1:
            node_b_phases.append("phase1")
        elif t < 5 + twait1 + twait2:
            node_b_phases.append("phase2")
        else:
            node_b_phases.append("removed")

        # Node C: never protected
        node_c_phases.append("normal")

    phase_colors = {
        "normal": "#E0E0E0",
        "phase1": "#42A5F5",
        "phase2": "#FFA726",
        "released": "#66BB6A",
        "removed": "#EF5350",
    }

    fig, axes = plt.subplots(3, 1, figsize=(14, 7), sharex=True)

    nodes_data = [
        ("Node A (truth, spoke_up=True)", node_a_phases),
        ("Node B (truth, spoke_up=False)", node_b_phases),
        ("Node C (normal, not rare)", node_c_phases),
    ]

    for ax, (label, phases) in zip(axes, nodes_data):
        for t, phase in enumerate(phases):
            ax.barh(0, 1, left=t, color=phase_colors[phase], edgecolor="none", height=0.6)
        ax.set_yticks([0])
        ax.set_yticklabels([label], fontsize=11)
        ax.set_xlim(0, total_steps)
        ax.grid(False)
        ax.set_axisbelow(True)
        ax.xaxis.grid(True, alpha=0.3)

    # Add vertical markers
    for ax in axes:
        ax.axvline(x=5, color="black", linestyle=":", linewidth=1.5, alpha=0.5)
        ax.axvline(x=5 + twait1, color="black", linestyle=":", linewidth=1.5, alpha=0.5)
        ax.axvline(x=5 + twait1 + twait2, color="black", linestyle=":", linewidth=1.5, alpha=0.5)

    axes[0].annotate("Enter\nProtection", (5, 0.35), fontsize=9, ha="center")
    axes[0].annotate(f"Phase1->2\n(Twait1={twait1})", (55, 0.35), fontsize=9, ha="center")
    axes[0].annotate(f"Finalize\n(Twait2={twait2})", (105, 0.35), fontsize=9, ha="center")

    axes[-1].set_xlabel("Time Step", fontsize=13)

    # Legend
    patches = [mpatches.Patch(color=c, label=l)
               for l, c in phase_colors.items()]
    fig.legend(handles=patches, loc="upper right", fontsize=10, ncol=5,
               bbox_to_anchor=(0.98, 1.0))

    fig.suptitle("Figure 4: Rarity Protection Phase Timeline\n"
                 f"Twait1={twait1}, Twait2={twait2}, rare_degree_max=1",
                 fontsize=14, y=1.04)

    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "04_rarity_phase_timeline.png", dpi=150,
                bbox_inches="tight")
    plt.close(fig)
    print("[OK] 04_rarity_phase_timeline.png")


# ====================================================================
# Figure 5: Rarity With vs Without Protection
# ====================================================================

def fig05_rarity_with_vs_without() -> None:
    """Bar chart: truth node survival with vs without rarity protection."""
    seed = 42

    # Without protection
    g1, _, truth1, _ = _build_sample_graph(seed)
    mgr1 = GraphMetabolicManager(
        g1, seed=seed, enable_rarity=False, enable_consistency=False,
        enable_meta=False, beta=0.03, prune_threshold=0.08,
    )
    mgr1.run(steps=120)
    survived_without = sum(1 for nid in truth1 if g1.has_node(nid))

    # With protection
    g2, _, truth2, _ = _build_sample_graph(seed)
    mgr2 = GraphMetabolicManager(
        g2, seed=seed, enable_rarity=True, enable_consistency=True,
        enable_meta=False, beta=0.03, prune_threshold=0.08,
        theta_l=0.35, theta_u=0.90,
    )
    mgr2.run(steps=120)
    survived_with = sum(1 for nid in truth2 if g2.has_node(nid))

    total_truth = len(truth1)

    fig, ax = plt.subplots(figsize=(8, 6))
    x = [0, 1]
    bars = ax.bar(x,
                  [survived_without, survived_with],
                  color=["#EF5350", "#66BB6A"],
                  edgecolor="black", width=0.5)

    ax.set_xticks(x)
    ax.set_xticklabels(["Without Protection", "With Protection"], fontsize=13)
    ax.set_ylabel("Truth Nodes Survived", fontsize=13)
    ax.set_title(f"Figure 5: Rarity Protection Effect  --  Truth Nodes ({total_truth} total)\n"
                 "120 steps, beta=0.03, prune=0.08", fontsize=14)

    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 0.1,
                f"{int(h)}/{total_truth}", ha="center", fontsize=15, fontweight="bold")

    ax.set_ylim(0, total_truth + 1)
    ax.axhline(y=total_truth, color="gray", linestyle=":", linewidth=1.5, alpha=0.5,
               label=f"Total Truth Nodes = {total_truth}")
    ax.legend(fontsize=11)

    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "05_rarity_with_vs_without.png", dpi=150)
    plt.close(fig)
    print("[OK] 05_rarity_with_vs_without.png")


# ====================================================================
# Figure 6: Consistency Score Breakdown
# ====================================================================

def fig06_consistency_score_breakdown() -> None:
    """Stacked bar chart showing S_sys, S_rel, S_attr weighted contributions."""
    # Create 3 pairs with known similarity profiles
    g = Graph()
    # Pair 1: High similarity (same structure, same type, shared neighbors)
    a1 = g.add_node("A1", node_type="sensor", category="IoT")
    b1 = g.add_node("B1", node_type="sensor", category="IoT")
    c1 = g.add_node("Hub1", node_type="hub")
    d1 = g.add_node("Hub2", node_type="hub")
    g.add_edge(a1, c1, 1.0)
    g.add_edge(a1, d1, 1.0)
    g.add_edge(b1, c1, 1.0)
    g.add_edge(b1, d1, 1.0)
    g.add_edge(a1, b1, 0.5)

    # Pair 2: Medium similarity (different structure, same type)
    a2 = g.add_node("A2", node_type="device")
    b2 = g.add_node("B2", node_type="device")
    e1 = g.add_node("E1", node_type="hub")
    e2 = g.add_node("E2", node_type="hub")
    e3 = g.add_node("E3", node_type="hub")
    g.add_edge(a2, e1, 1.0)
    g.add_edge(b2, e2, 1.0)
    g.add_edge(b2, e3, 1.0)

    # Pair 3: Low similarity (different everything)
    a3 = g.add_node("A3", node_type="alpha", tag="x")
    b3 = g.add_node("B3", node_type="beta", tag="y")
    f1 = g.add_node("F1", node_type="gamma")
    g.add_edge(a3, f1, 1.0)

    pairs = [
        ("High\n(same struct/type)", a1, b1),
        ("Medium\n(diff struct)", a2, b2),
        ("Low\n(different all)", a3, b3),
    ]

    s_sys_vals = []
    s_rel_vals = []
    s_attr_vals = []

    for label, nid_a, nid_b in pairs:
        r_a = compute_structural_repr(g.subgraph(nid_a, k_hop=2))
        r_b = compute_structural_repr(g.subgraph(nid_b, k_hop=2))

        s_cos = cosine_similarity(r_a, r_b)
        s_str = structural_diff_similarity(r_a, r_b)
        s_sgn = sign_agreement(r_a, r_b)
        s_sys = (s_cos + s_str + s_sgn) / 3.0

        s_rel = relational_similarity(g, nid_a, nid_b)
        s_attr = attribute_similarity(g, nid_a, nid_b)

        # Weighted contributions (not raw values)
        total_w = DEFAULT_W_SYS + DEFAULT_W_REL + DEFAULT_W_ATTR  # 10
        s_sys_vals.append(DEFAULT_W_SYS * s_sys / total_w)
        s_rel_vals.append(DEFAULT_W_REL * s_rel / total_w)
        s_attr_vals.append(DEFAULT_W_ATTR * s_attr / total_w)

    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(pairs))
    w = 0.5

    ax.bar(x, s_sys_vals, w, label=f"S_sys (w={DEFAULT_W_SYS}/10)", color="#42A5F5")
    ax.bar(x, s_rel_vals, w, bottom=s_sys_vals, label=f"S_rel (w={DEFAULT_W_REL}/10)", color="#FFA726")
    bottoms = [a + b for a, b in zip(s_sys_vals, s_rel_vals)]
    ax.bar(x, s_attr_vals, w, bottom=bottoms, label=f"S_attr (w={DEFAULT_W_ATTR}/10)", color="#66BB6A")

    # Sandwich threshold band
    ax.axhspan(DEFAULT_THETA_L, DEFAULT_THETA_U, alpha=0.15, color="green",
               label=f"Accept: [{DEFAULT_THETA_L}, {DEFAULT_THETA_U}]")
    ax.axhline(y=DEFAULT_THETA_L, color="green", linestyle="--", linewidth=1.5, alpha=0.7)
    ax.axhline(y=DEFAULT_THETA_U, color="green", linestyle="--", linewidth=1.5, alpha=0.7)

    # Total score labels
    for i in range(len(pairs)):
        total = s_sys_vals[i] + s_rel_vals[i] + s_attr_vals[i]
        status = "ACCEPT" if DEFAULT_THETA_L <= total <= DEFAULT_THETA_U else "REJECT"
        ax.text(i, total + 0.02, f"S={total:.3f}\n({status})",
                ha="center", fontsize=10, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels([p[0] for p in pairs], fontsize=11)
    ax.set_ylabel("Weighted Score Contribution", fontsize=13)
    ax.set_title("Figure 6: Consistency Score Breakdown\n"
                 f"S = ({DEFAULT_W_SYS}*S_sys + {DEFAULT_W_REL}*S_rel + {DEFAULT_W_ATTR}*S_attr) / 10",
                 fontsize=14)
    ax.legend(fontsize=10, loc="upper right")
    ax.set_ylim(0, 1.15)

    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "06_consistency_score_breakdown.png", dpi=150)
    plt.close(fig)
    print("[OK] 06_consistency_score_breakdown.png")


# ====================================================================
# Figure 7: Health Index Curve
# ====================================================================

def fig07_health_index_curve() -> None:
    """Plot H = 1 - |k_avg - k_opt| / k_opt."""
    k_avg = np.linspace(0, 15, 300)
    H = [health_index(k, DEFAULT_K_OPT) for k in k_avg]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(k_avg, H, "-", color="#1565C0", linewidth=3)

    # Target line
    ax.axhline(y=DEFAULT_H_TARGET, color="orange", linestyle="--", linewidth=2,
               label=f"H_target = {DEFAULT_H_TARGET}")

    # Optimal point
    ax.plot(DEFAULT_K_OPT, 1.0, "*", color="gold", markersize=20, zorder=5,
            markeredgecolor="black", markeredgewidth=1.5)
    ax.annotate(f"k_opt={DEFAULT_K_OPT}\nH=1.0 (perfect)",
                (DEFAULT_K_OPT, 1.0), textcoords="offset points",
                xytext=(40, -20), fontsize=11,
                arrowprops=dict(arrowstyle="->"),
                bbox=dict(boxstyle="round,pad=0.3", fc="lightyellow"))

    # Example points
    examples = [(3.0, "below"), (8.0, "above")]
    for k_ex, pos in examples:
        h_ex = health_index(k_ex, DEFAULT_K_OPT)
        ax.plot(k_ex, h_ex, "ko", markersize=8, zorder=5)
        offset_y = 15 if pos == "below" else 15
        ax.annotate(f"k_avg={k_ex:.0f}  ->  H={h_ex:.2f}",
                    (k_ex, h_ex), textcoords="offset points",
                    xytext=(15, offset_y), fontsize=10,
                    bbox=dict(boxstyle="round,pad=0.3", fc="lightyellow", ec="gray"))

    # Shade zones
    ax.axvspan(0, DEFAULT_K_OPT, alpha=0.05, color="red", label="Underdense zone")
    ax.axvspan(DEFAULT_K_OPT, 15, alpha=0.05, color="blue", label="Overdense zone")

    ax.set_xlabel("Average Degree k_avg", fontsize=13)
    ax.set_ylabel("Health Index H", fontsize=13)
    ax.set_title(f"Figure 7: Health Index  --  H = 1 - |k_avg - k_opt| / k_opt\n"
                 f"k_opt={DEFAULT_K_OPT}, H_target={DEFAULT_H_TARGET}", fontsize=14)
    ax.legend(fontsize=11)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 1.1)

    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "07_health_index_curve.png", dpi=150)
    plt.close(fig)
    print("[OK] 07_health_index_curve.png")


# ====================================================================
# Figure 8: Meta Control Convergence
# ====================================================================

def fig08_meta_convergence() -> None:
    """Dual-axis plot: health index and alpha over time."""
    random.seed(42)
    np.random.seed(42)

    g, _, _, _ = _build_sample_graph(42)
    mc = MetabolicControl()
    rp = RarityProtection()
    meta = MetaControl(k_opt=5.0, h_target=0.7)

    health_hist = []
    alpha_hist = []
    kavg_hist = []

    for t in range(100):
        info = meta.step(g)
        mc.alpha = meta.current_alpha
        mc.step(g, dt=1.0, protected=rp.protected)
        rp.update_phases(g, t)

        health_hist.append(info["H"])
        alpha_hist.append(info["alpha"])
        kavg_hist.append(info["k_avg"])

    fig, ax1 = plt.subplots(figsize=(12, 6))

    color_h = "#1565C0"
    color_a = "#F44336"

    ax1.set_xlabel("Time Step", fontsize=13)
    ax1.set_ylabel("Health Index H", fontsize=13, color=color_h)
    line_h = ax1.plot(health_hist, "-", color=color_h, linewidth=2, label="Health H")
    ax1.tick_params(axis="y", labelcolor=color_h)
    ax1.axhline(y=DEFAULT_H_TARGET, color=color_h, linestyle=":", linewidth=1.5, alpha=0.5)
    ax1.set_ylim(0, 1.1)

    ax2 = ax1.twinx()
    ax2.set_ylabel("Alpha (congestion sensitivity)", fontsize=13, color=color_a)
    line_a = ax2.plot(alpha_hist, "-", color=color_a, linewidth=2, label="Alpha")
    ax2.tick_params(axis="y", labelcolor=color_a)

    # Combined legend
    lines = line_h + line_a
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, fontsize=12, loc="center right")

    ax1.set_title("Figure 8: Meta Control Convergence\n"
                  f"k_opt={DEFAULT_K_OPT}, h_target={DEFAULT_H_TARGET}, "
                  f"eta=0.001, n=4, alpha range=[0.5, 3.0]", fontsize=14)

    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "08_meta_convergence.png", dpi=150)
    plt.close(fig)
    print("[OK] 08_meta_convergence.png")


# ====================================================================
# Figure 9: Hierarchy Processing Schedule
# ====================================================================

def fig09_hierarchy_schedule() -> None:
    """Heatmap: which layers are processed at each time step."""
    dt_edge, dt_core, dt_rare = 5, 3, 1
    steps = 16
    layers = ["rare", "core", "edge"]

    data = np.zeros((3, steps))
    for t in range(steps):
        # rare: dt=1, always processed
        data[0, t] = 1
        # core: dt=3
        if t % dt_core == 0:
            data[1, t] = 1
        # edge: dt=5
        if t % dt_edge == 0:
            data[2, t] = 1

    fig, ax = plt.subplots(figsize=(14, 4))

    cmap = plt.cm.colors.ListedColormap(["#E0E0E0", "#66BB6A"])
    ax.imshow(data, aspect="auto", cmap=cmap, interpolation="nearest")

    # Cell labels
    for i in range(3):
        for j in range(steps):
            text = "RUN" if data[i, j] == 1 else "SKIP"
            color = "white" if data[i, j] == 1 else "#999999"
            ax.text(j, i, text, ha="center", va="center",
                    fontsize=8, fontweight="bold", color=color)

    ax.set_xticks(range(steps))
    ax.set_xticklabels([str(t) for t in range(steps)], fontsize=10)
    ax.set_yticks(range(3))
    ax.set_yticklabels([f"{l}\n(dt={dt})" for l, dt in
                        zip(layers, [dt_rare, dt_core, dt_edge])],
                       fontsize=11)
    ax.set_xlabel("Time Step", fontsize=13)
    ax.set_title("Figure 9: Hierarchy Processing Schedule\n"
                 f"dt_rare={dt_rare} (every step), dt_core={dt_core}, dt_edge={dt_edge}",
                 fontsize=14)

    # Frequency summary
    freq_text = (f"Rare: {steps}/{steps} steps ({100:.0f}%)\n"
                 f"Core: {sum(1 for t in range(steps) if t % dt_core == 0)}/{steps} steps "
                 f"({sum(1 for t in range(steps) if t % dt_core == 0)/steps*100:.0f}%)\n"
                 f"Edge: {sum(1 for t in range(steps) if t % dt_edge == 0)}/{steps} steps "
                 f"({sum(1 for t in range(steps) if t % dt_edge == 0)/steps*100:.0f}%)")
    ax.text(steps + 0.5, 1, freq_text, fontsize=9, va="center",
            bbox=dict(boxstyle="round,pad=0.5", fc="lightyellow", ec="gray"))

    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "09_hierarchy_schedule.png", dpi=150,
                bbox_inches="tight")
    plt.close(fig)
    print("[OK] 09_hierarchy_schedule.png")


# ====================================================================
# Figure 10: Full Pipeline
# ====================================================================

def fig10_full_pipeline() -> None:
    """4-panel subplot: full pipeline metrics over 150 steps."""
    random.seed(42)
    np.random.seed(42)

    g, normal, truth, garbage = _build_sample_graph(42)
    mgr = GraphMetabolicManager(
        g, seed=42,
        enable_rarity=True,
        enable_consistency=True,
        enable_meta=True,
        k_opt=5.0,
        beta=0.03,
        prune_threshold=0.08,
        theta_l=0.35,
        theta_u=0.90,
    )

    results = mgr.run(steps=150)

    steps_x = [r["time"] for r in results]
    nodes_y = [r["nodes"] for r in results]
    edges_y = [r["edges"] for r in results]
    health_y = [r.get("health", 0) for r in results]
    alpha_y = [r.get("alpha", DEFAULT_ALPHA) for r in results]

    fig, axes = plt.subplots(4, 1, figsize=(14, 14), sharex=True)

    # (a) Nodes & Edges
    ax = axes[0]
    ax.plot(steps_x, nodes_y, "-", color="#1565C0", linewidth=2, label="Nodes")
    ax.plot(steps_x, edges_y, "-", color="#F44336", linewidth=2, label="Edges")
    ax.set_ylabel("Count", fontsize=12)
    ax.set_title("(a) Graph Size", fontsize=13)
    ax.legend(fontsize=11)

    # (b) Health
    ax = axes[1]
    ax.plot(steps_x, health_y, "-", color="#4CAF50", linewidth=2)
    ax.axhline(y=DEFAULT_H_TARGET, color="orange", linestyle="--", linewidth=1.5,
               label=f"H_target={DEFAULT_H_TARGET}")
    ax.set_ylabel("Health H", fontsize=12)
    ax.set_title("(b) Health Index", fontsize=13)
    ax.set_ylim(0, 1.1)
    ax.legend(fontsize=11)

    # (c) Alpha
    ax = axes[2]
    ax.plot(steps_x, alpha_y, "-", color="#FF5722", linewidth=2)
    ax.axhline(y=DEFAULT_ALPHA, color="gray", linestyle=":", linewidth=1.5,
               label=f"Initial alpha={DEFAULT_ALPHA}")
    ax.set_ylabel("Alpha", fontsize=12)
    ax.set_title("(c) Congestion Sensitivity Parameter", fontsize=13)
    ax.legend(fontsize=11)

    # (d) Protected nodes per step
    protected_y = [r.get("rare_protected", 0) for r in results]
    ax = axes[3]
    ax.fill_between(steps_x, protected_y, alpha=0.3, color="#9C27B0")
    ax.plot(steps_x, protected_y, "-", color="#9C27B0", linewidth=2)
    ax.set_ylabel("Protected Nodes", fontsize=12)
    ax.set_xlabel("Time Step", fontsize=13)
    ax.set_title("(d) Rarity-Protected Node Count", fontsize=13)

    fig.suptitle("Figure 10: Full Pipeline  --  GraphMetabolicManager (150 steps)\n"
                 "All 4 features enabled: Metabolic + Rarity + Consistency + Meta",
                 fontsize=15, y=1.01)

    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "10_full_pipeline.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("[OK] 10_full_pipeline.png")


# ====================================================================
# Main
# ====================================================================

def main() -> None:
    """Generate all 10 figures."""
    print(f"Saving figures to: {FIGURES_DIR}")
    print("-" * 50)

    fig01_decay_rate_curve()
    fig02_weight_decay_timeline()
    fig03_metabolic_before_after()
    fig04_rarity_phase_timeline()
    fig05_rarity_with_vs_without()
    fig06_consistency_score_breakdown()
    fig07_health_index_curve()
    fig08_meta_convergence()
    fig09_hierarchy_schedule()
    fig10_full_pipeline()

    print("-" * 50)
    print(f"Done! {len(list(FIGURES_DIR.glob('*.png')))} figures generated.")


if __name__ == "__main__":
    main()
