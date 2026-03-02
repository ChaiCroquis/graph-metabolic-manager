"""代謝制御 (Metabolic Control) -- Interactive Demo Page."""

from __future__ import annotations

import copy
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from graph_metabolic_manager import MetabolicControl, decay_rate, update_weight
from streamlit_app.components.graph_viz import (
    COLORS,
    apply_style,
    draw_graph,
)
from streamlit_app.components.sample_graphs import build_sample_graph

apply_style()

# ---- Page config ----
st.set_page_config(page_title="代謝制御", page_icon="🔄", layout="wide")
st.title("🔄 代謝制御 (Metabolic Control)")

st.latex(r"\lambda(C) = \beta \cdot (1 + \gamma \cdot C^{\alpha})")
st.latex(r"w(t) = w_0 \cdot e^{-\lambda \cdot t}")

st.markdown("""
混雑した領域（次数の高いノード同士）のエッジほど速く減衰し、
疎な領域のエッジは保持されます。局所的な統計量のみで計算するため、
大規模グラフにもスケールします。
""")

st.divider()

# ---- Sidebar ----
st.sidebar.header("パラメータ設定")

alpha = st.sidebar.slider(
    "α — 混雑感度指数",
    min_value=0.5, max_value=3.0, value=2.0, step=0.1,
    help="大きいほど混雑領域の減衰が急激になります",
)
beta = st.sidebar.slider(
    "β — 基本減衰率",
    min_value=0.01, max_value=0.10, value=0.05, step=0.005,
    format="%.3f",
    help="全エッジに共通の最低減衰率",
)
gamma = st.sidebar.slider(
    "γ — 混雑スケーリング係数",
    min_value=0.0, max_value=1.0, value=0.5, step=0.05,
    help="混雑項の影響度を制御します",
)
prune_threshold = st.sidebar.slider(
    "枝刈り閾値",
    min_value=0.01, max_value=0.20, value=0.10, step=0.01,
    help="この値を下回ったエッジは除去されます",
)
sim_steps = st.sidebar.slider(
    "シミュレーション ステップ数",
    min_value=10, max_value=200, value=120, step=10,
)

# ================================================================
# Chart 1: Decay Rate Curve
# ================================================================
st.subheader("1. 減衰率曲線")
st.markdown(f"現在の設定: α={alpha}, β={beta:.3f}, γ={gamma}")

C_range = np.linspace(0, 20, 200)

fig1, ax1 = plt.subplots(figsize=(10, 5))

# User's alpha (main line)
lam_user = [decay_rate(c, alpha=alpha, beta=beta, gamma=gamma) for c in C_range]
ax1.plot(C_range, lam_user, "-", color=COLORS["accent"], linewidth=2.5,
         label=f"alpha={alpha:.1f} (current)")

# Reference lines
for ref_alpha, style, color in [(1.0, "--", COLORS["info"]), (3.0, "-.", COLORS["success"])]:
    if abs(ref_alpha - alpha) > 0.05:
        lam_ref = [decay_rate(c, alpha=ref_alpha, beta=beta, gamma=gamma) for c in C_range]
        ax1.plot(C_range, lam_ref, style, color=color, linewidth=1.5, alpha=0.5,
                 label=f"alpha={ref_alpha:.1f} (ref)")

# Example points
for c_val in [2, 5, 10]:
    lam_val = decay_rate(c_val, alpha=alpha, beta=beta, gamma=gamma)
    ax1.plot(c_val, lam_val, "ko", markersize=8, zorder=5)
    ax1.annotate(f"C={c_val} -> lambda={lam_val:.3f}",
                 (c_val, lam_val), textcoords="offset points",
                 xytext=(12, 8), fontsize=9,
                 bbox=dict(boxstyle="round,pad=0.3", fc="lightyellow", ec="gray"))

ax1.set_xlabel("Congestion C = deg(u) + deg(v)")
ax1.set_ylabel("Decay Rate lambda(C)")
ax1.set_title("Adaptive Decay Rate Curve")
ax1.legend()
ax1.set_xlim(0, 20)
ax1.set_ylim(bottom=0)
fig1.tight_layout()
st.pyplot(fig1)
plt.close(fig1)

# ================================================================
# Chart 2: Weight Decay Timeline
# ================================================================
st.subheader("2. エッジ重みの時間推移")

steps_range = np.arange(0, 11)
scenarios = [
    (2.0, COLORS["success"], "Sparse (C=2)"),
    (5.0, COLORS["warning"], "Medium (C=5)"),
    (10.0, COLORS["accent"], "Dense (C=10)"),
]

fig2, ax2 = plt.subplots(figsize=(10, 5))

for C_val, color, label in scenarios:
    lam = decay_rate(C_val, alpha=alpha, beta=beta, gamma=gamma)
    weights = [update_weight(1.0, lam, float(t)) for t in steps_range]
    ax2.plot(steps_range, weights, "o-", color=color, linewidth=2.5,
             markersize=6, label=label)

    for t, w in zip(steps_range, weights):
        if w < prune_threshold:
            ax2.annotate(f"Pruned t={t}\n(w={w:.4f})",
                         (t, w), textcoords="offset points",
                         xytext=(10, 10), fontsize=8,
                         arrowprops=dict(arrowstyle="->", color=color),
                         bbox=dict(boxstyle="round,pad=0.2", fc="lightyellow"))
            break

ax2.axhline(y=prune_threshold, color="red", linestyle=":", linewidth=2,
            label=f"Prune Threshold = {prune_threshold}")
ax2.set_xlabel("Time Step (dt=1.0)")
ax2.set_ylabel("Edge Weight w")
ax2.set_title("Weight Decay Over Time")
ax2.legend()
ax2.set_xlim(0, 10)
ax2.set_ylim(0, 1.05)
fig2.tight_layout()
st.pyplot(fig2)
plt.close(fig2)

# ================================================================
# Chart 3: Before/After Simulation
# ================================================================
st.subheader("3. シミュレーション結果 (Before/After)")

g_orig, normal, truth, garbage = build_sample_graph(42)
# Deep copy for simulation
import pickle
g_sim = pickle.loads(pickle.dumps(g_orig))

mc = MetabolicControl(alpha=alpha, beta=beta, gamma=gamma,
                      prune_threshold=prune_threshold)
for _ in range(sim_steps):
    mc.step(g_sim, dt=1.0)

init_nodes = g_orig.node_count()
init_edges = g_orig.edge_count()
final_nodes = g_sim.node_count()
final_edges = g_sim.edge_count()

# Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("初期ノード数", init_nodes)
col2.metric("最終ノード数", final_nodes, delta=final_nodes - init_nodes)
col3.metric("初期エッジ数", init_edges)
col4.metric("最終エッジ数", final_edges, delta=final_edges - init_edges)

# Bar chart
fig3, ax3 = plt.subplots(figsize=(8, 5))
x = np.arange(2)
w_bar = 0.35
bars1 = ax3.bar(x - w_bar / 2, [init_nodes, init_edges], w_bar,
                label="Before (t=0)", color=COLORS["info"], edgecolor="black")
bars2 = ax3.bar(x + w_bar / 2, [final_nodes, final_edges], w_bar,
                label=f"After (t={sim_steps})", color=COLORS["error"], edgecolor="black")

ax3.set_xticks(x)
ax3.set_xticklabels(["Nodes", "Edges"])
ax3.set_ylabel("Count")
ax3.set_title(f"Metabolic Control: Before vs After ({sim_steps} steps)")
ax3.legend()

for bars in [bars1, bars2]:
    for bar in bars:
        h = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width() / 2, h + 0.3,
                 str(int(h)), ha="center", fontsize=12, fontweight="bold")

ax3.set_ylim(0, max(init_nodes, init_edges) * 1.2)
fig3.tight_layout()
st.pyplot(fig3)
plt.close(fig3)

# ================================================================
# Chart 4: Network Visualization (Before/After)
# ================================================================
st.subheader("4. ネットワーク構造の変化")

fig4, (ax4a, ax4b) = plt.subplots(1, 2, figsize=(14, 6))
draw_graph(g_orig, ax4a, title=f"Before (t=0): {init_nodes} nodes, {init_edges} edges",
           seed=42)
draw_graph(g_sim, ax4b, title=f"After (t={sim_steps}): {final_nodes} nodes, {final_edges} edges",
           seed=42)
fig4.tight_layout()
st.pyplot(fig4)
plt.close(fig4)
