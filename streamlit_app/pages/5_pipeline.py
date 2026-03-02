"""統合パイプライン (Full Pipeline) -- Interactive Demo Page."""

from __future__ import annotations

import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from graph_metabolic_manager import GraphMetabolicManager
from graph_metabolic_manager.metabolic import DEFAULT_ALPHA
from streamlit_app.components.graph_viz import (
    COLORS,
    LAYER_COLORS,
    apply_style,
    draw_graph,
)
from streamlit_app.components.sample_graphs import build_sample_graph

apply_style()

st.set_page_config(page_title="統合パイプライン", page_icon="🔬", layout="wide")
st.title("🔬 統合パイプライン (Full Pipeline)")

st.markdown("""
4つのコア機能 + 階層管理を統合したフルシミュレーションです。

**処理順序** (各ステップ):
1. メタ制御 → 2. アクティビティ更新 → 3. 階層レイヤー割当
→ 4. 希少性検出 → 5. 整合性発見 → 6. フェーズ更新 → 7. 代謝制御
""")

st.divider()

# ---- Sidebar ----
st.sidebar.header("代謝制御")
alpha = st.sidebar.slider("α", 0.5, 3.0, 2.0, 0.1, key="p_alpha")
beta = st.sidebar.slider("β", 0.01, 0.10, 0.03, 0.005, format="%.3f", key="p_beta")
gamma = st.sidebar.slider("γ", 0.0, 1.0, 0.5, 0.05, key="p_gamma")
prune = st.sidebar.slider("枝刈り閾値", 0.01, 0.20, 0.08, 0.01, key="p_prune")

st.sidebar.header("希少性保護")
twait1 = st.sidebar.slider("Twait1", 10, 100, 50, 5, key="p_tw1")
twait2 = st.sidebar.slider("Twait2", 10, 100, 50, 5, key="p_tw2")

st.sidebar.header("整合性発見")
theta_l = st.sidebar.slider("theta_L", 0.30, 0.90, 0.35, 0.05, key="p_tl")
theta_u = st.sidebar.slider("theta_U", 0.50, 1.00, 0.90, 0.05, key="p_tu")

st.sidebar.header("メタ制御")
k_opt = st.sidebar.slider("k_opt", 2.0, 10.0, 5.0, 0.5, key="p_kopt")
h_target = st.sidebar.slider("H_target", 0.50, 0.95, 0.70, 0.05, key="p_ht")

st.sidebar.header("階層管理")
dt_core = st.sidebar.slider("dt_core", 1, 10, 3, 1, key="p_dtc")
dt_edge = st.sidebar.slider("dt_edge", 1, 15, 5, 1, key="p_dte")
activity_th = st.sidebar.slider("activity_threshold", 0.3, 0.7, 0.5, 0.05, key="p_act")

st.sidebar.header("シミュレーション")
sim_steps = st.sidebar.slider("ステップ数", 50, 300, 150, 10, key="p_steps")

enable_meta = st.sidebar.checkbox("メタ制御", value=True, key="p_em")
enable_rarity = st.sidebar.checkbox("希少性保護", value=True, key="p_er")
enable_consistency = st.sidebar.checkbox("整合性発見", value=True, key="p_ec")
enable_hierarchy = st.sidebar.checkbox("階層管理", value=False, key="p_eh")

# ---- Run simulation with button ----
run_btn = st.button("🚀 シミュレーション実行", type="primary", use_container_width=True)

if run_btn or "pipeline_results" not in st.session_state:
    random.seed(42)
    np.random.seed(42)

    g, normal, truth, garbage = build_sample_graph(42)
    init_nodes = g.node_count()
    init_edges = g.edge_count()

    mgr = GraphMetabolicManager(
        g, seed=42,
        enable_rarity=enable_rarity,
        enable_consistency=enable_consistency,
        enable_meta=enable_meta,
        enable_hierarchy=enable_hierarchy,
        alpha=alpha, beta=beta, gamma=gamma, prune_threshold=prune,
        twait1=twait1, twait2=twait2,
        theta_l=theta_l, theta_u=theta_u,
        k_opt=k_opt, h_target=h_target,
        dt_core=dt_core, dt_edge=dt_edge,
        activity_threshold=activity_th,
    )

    results = mgr.run(steps=sim_steps)

    st.session_state["pipeline_results"] = results
    st.session_state["pipeline_graph"] = g
    st.session_state["pipeline_init"] = (init_nodes, init_edges)
    st.session_state["pipeline_discoveries"] = len(mgr.discoveries)

results = st.session_state.get("pipeline_results", [])
g = st.session_state.get("pipeline_graph")
init_info = st.session_state.get("pipeline_init", (20, 0))

if not results:
    st.info("「シミュレーション実行」ボタンを押してください。")
    st.stop()

# ================================================================
# Metrics
# ================================================================
init_nodes, init_edges = init_info
final_nodes = results[-1]["nodes"]
final_edges = results[-1]["edges"]
total_disc = st.session_state.get("pipeline_discoveries", 0)

col1, col2, col3, col4 = st.columns(4)
col1.metric("最終ノード数", final_nodes, delta=final_nodes - init_nodes)
col2.metric("最終エッジ数", final_edges, delta=final_edges - init_edges)
col3.metric("発見された隠れ関連", total_disc)
final_h = results[-1].get("health", 0)
col4.metric("最終 Health", f"{final_h:.3f}")

# ================================================================
# Chart 1: 4-Panel Dashboard
# ================================================================
st.subheader("1. パイプラインダッシュボード")

steps_x = [r["time"] for r in results]
nodes_y = [r["nodes"] for r in results]
edges_y = [r["edges"] for r in results]
health_y = [r.get("health", 0) for r in results]
alpha_y = [r.get("alpha", DEFAULT_ALPHA) for r in results]
protected_y = [r.get("rare_protected", 0) for r in results]

fig1, axes = plt.subplots(4, 1, figsize=(14, 12), sharex=True)

# (a) Nodes & Edges
ax = axes[0]
ax.plot(steps_x, nodes_y, "-", color=COLORS["primary"], linewidth=2, label="Nodes")
ax.plot(steps_x, edges_y, "-", color=COLORS["accent"], linewidth=2, label="Edges")
ax.set_ylabel("Count")
ax.set_title("(a) Graph Size")
ax.legend()

# (b) Health
ax = axes[1]
ax.plot(steps_x, health_y, "-", color=COLORS["success"], linewidth=2)
ax.axhline(y=h_target, color="orange", linestyle="--", linewidth=1.5,
           label=f"H_target={h_target}")
ax.set_ylabel("Health H")
ax.set_title("(b) Health Index")
ax.set_ylim(0, 1.1)
ax.legend()

# (c) Alpha
ax = axes[2]
ax.plot(steps_x, alpha_y, "-", color=COLORS["deep_orange"], linewidth=2)
ax.set_ylabel("Alpha")
ax.set_title("(c) Congestion Sensitivity")

# (d) Protected
ax = axes[3]
ax.fill_between(steps_x, protected_y, alpha=0.3, color=COLORS["purple"])
ax.plot(steps_x, protected_y, "-", color=COLORS["purple"], linewidth=2)
ax.set_ylabel("Protected Nodes")
ax.set_xlabel("Time Step")
ax.set_title("(d) Rarity-Protected Nodes")

fig1.suptitle(f"Full Pipeline ({sim_steps} steps)", fontsize=14, y=1.01)
fig1.tight_layout()
st.pyplot(fig1)
plt.close(fig1)

# ================================================================
# Chart 2: Hierarchy Schedule
# ================================================================
if enable_hierarchy:
    st.subheader("2. 階層処理スケジュール")

    sched_steps = min(16, sim_steps)
    layers = ["rare", "core", "edge"]
    dt_vals = [1, dt_core, dt_edge]
    data = np.zeros((3, sched_steps))

    for t in range(sched_steps):
        data[0, t] = 1  # rare: always
        if t % dt_core == 0:
            data[1, t] = 1
        if t % dt_edge == 0:
            data[2, t] = 1

    fig2, ax2 = plt.subplots(figsize=(14, 3.5))
    cmap = plt.cm.colors.ListedColormap(["#E0E0E0", "#66BB6A"])
    ax2.imshow(data, aspect="auto", cmap=cmap, interpolation="nearest")

    for i in range(3):
        for j in range(sched_steps):
            text = "RUN" if data[i, j] == 1 else "SKIP"
            color = "white" if data[i, j] == 1 else "#999999"
            ax2.text(j, i, text, ha="center", va="center",
                     fontsize=8, fontweight="bold", color=color)

    ax2.set_xticks(range(sched_steps))
    ax2.set_yticks(range(3))
    ax2.set_yticklabels([f"{l} (dt={dt})" for l, dt in zip(layers, dt_vals)])
    ax2.set_xlabel("Time Step")
    ax2.set_title(f"Hierarchy Schedule: dt_rare=1, dt_core={dt_core}, dt_edge={dt_edge}")
    fig2.tight_layout()
    st.pyplot(fig2)
    plt.close(fig2)

# ================================================================
# Chart 3: Final Network State
# ================================================================
st.subheader("3. 最終グラフ状態" if not enable_hierarchy else "3. 最終グラフ状態")

if g and g.node_count() > 0:
    fig3, ax3 = plt.subplots(figsize=(10, 7))
    color_mode = "layer" if enable_hierarchy else "type"
    draw_graph(g, ax3,
               title=f"Final State (t={sim_steps}): {g.node_count()} nodes, {g.edge_count()} edges",
               color_by=color_mode,
               highlight_protected=enable_rarity,
               seed=42)
    fig3.tight_layout()
    st.pyplot(fig3)
    plt.close(fig3)
else:
    st.warning("グラフが空になりました。パラメータを調整してください。")
