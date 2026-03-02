"""希少性保護 (Rarity Protection) -- Interactive Demo Page."""

from __future__ import annotations

import pickle
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from graph_metabolic_manager import GraphMetabolicManager
from streamlit_app.components.graph_viz import (
    PHASE_COLORS,
    apply_style,
    draw_graph,
)
from streamlit_app.components.sample_graphs import build_sample_graph

apply_style()

st.set_page_config(page_title="希少性保護", page_icon="🛡️", layout="wide")
st.title("🛡️ 希少性保護 (Rarity Protection)")

st.markdown("""
次数が低い（つながりの少ない）希少ノードを、即座に削除せず
**2フェーズの保護期間** を設けて観察します。
""")

st.latex(r"\text{Normal} \xrightarrow{\text{identify}} \text{Phase1 (猶予)} "
         r"\xrightarrow{T_{wait1}} \text{Phase2 (観察)} "
         r"\xrightarrow{T_{wait2}} \text{Release / Remove}")

st.divider()

# ---- Sidebar ----
st.sidebar.header("パラメータ設定")

twait1 = st.sidebar.slider(
    "Twait1 — Phase1 猶予期間",
    min_value=10, max_value=100, value=50, step=5,
    help="Phase1（無条件保護）の持続ステップ数",
)
twait2 = st.sidebar.slider(
    "Twait2 — Phase2 観察期間",
    min_value=10, max_value=100, value=50, step=5,
    help="Phase2（条件付き観察）の持続ステップ数",
)
rare_degree = st.sidebar.slider(
    "希少判定の最大次数",
    min_value=0, max_value=3, value=1, step=1,
    help="この次数以下のノードが希少と判定されます",
)
beta_rarity = st.sidebar.slider(
    "β — 基本減衰率",
    min_value=0.01, max_value=0.10, value=0.03, step=0.005,
    format="%.3f",
)
prune_rarity = st.sidebar.slider(
    "枝刈り閾値",
    min_value=0.01, max_value=0.20, value=0.08, step=0.01,
)

# ================================================================
# Chart 1: Phase Timeline
# ================================================================
st.subheader("1. フェーズ遷移タイムライン")
st.markdown(f"Twait1={twait1}, Twait2={twait2}")

total_steps = 10 + twait1 + twait2 + 20

# Simulate phase state machine manually
node_a_phases = []  # spoke_up=True at t=~40, survives
node_b_phases = []  # spoke_up=False, removed
node_c_phases = []  # Not rare

enter_t = 5
for t in range(total_steps):
    if t < enter_t:
        node_a_phases.append("normal")
    elif t < enter_t + twait1:
        node_a_phases.append("phase1")
    elif t < enter_t + twait1 + twait2:
        node_a_phases.append("phase2")
    else:
        node_a_phases.append("released")

    if t < enter_t:
        node_b_phases.append("normal")
    elif t < enter_t + twait1:
        node_b_phases.append("phase1")
    elif t < enter_t + twait1 + twait2:
        node_b_phases.append("phase2")
    else:
        node_b_phases.append("removed")

    node_c_phases.append("normal")

fig1, axes = plt.subplots(3, 1, figsize=(14, 6), sharex=True)

nodes_data = [
    ("Node A (truth, spoke_up=True)", node_a_phases),
    ("Node B (truth, spoke_up=False)", node_b_phases),
    ("Node C (normal, not rare)", node_c_phases),
]

for ax, (label, phases) in zip(axes, nodes_data):
    for t, phase in enumerate(phases):
        ax.barh(0, 1, left=t, color=PHASE_COLORS[phase], edgecolor="none", height=0.6)
    ax.set_yticks([0])
    ax.set_yticklabels([label], fontsize=10)
    ax.set_xlim(0, total_steps)
    ax.grid(False)
    ax.xaxis.grid(True, alpha=0.3)

for ax in axes:
    ax.axvline(x=enter_t, color="black", linestyle=":", linewidth=1.5, alpha=0.5)
    ax.axvline(x=enter_t + twait1, color="black", linestyle=":", linewidth=1.5, alpha=0.5)
    ax.axvline(x=enter_t + twait1 + twait2, color="black", linestyle=":", linewidth=1.5, alpha=0.5)

axes[0].annotate("Enter\nProtection", (enter_t, 0.35), fontsize=8, ha="center")
axes[0].annotate(f"Phase1->2\n(Tw1={twait1})", (enter_t + twait1, 0.35), fontsize=8, ha="center")
axes[0].annotate(f"Finalize\n(Tw2={twait2})", (enter_t + twait1 + twait2, 0.35),
                 fontsize=8, ha="center")

axes[-1].set_xlabel("Time Step")

patches = [mpatches.Patch(color=c, label=l) for l, c in PHASE_COLORS.items()]
fig1.legend(handles=patches, loc="upper right", fontsize=9, ncol=5,
            bbox_to_anchor=(0.98, 1.0))
fig1.suptitle("Rarity Protection Phase Timeline", fontsize=13, y=1.02)
fig1.tight_layout()
st.pyplot(fig1)
plt.close(fig1)

# ================================================================
# Chart 2: With vs Without Protection
# ================================================================
st.subheader("2. 保護あり / なし比較")

seed = 42

# Without protection
g1, _, truth1, _ = build_sample_graph(seed)
mgr1 = GraphMetabolicManager(
    g1, seed=seed, enable_rarity=False, enable_consistency=False,
    enable_meta=False, beta=beta_rarity, prune_threshold=prune_rarity,
)
mgr1.run(steps=120)
survived_without = sum(1 for nid in truth1 if g1.has_node(nid))

# With protection
g2, _, truth2, _ = build_sample_graph(seed)
mgr2 = GraphMetabolicManager(
    g2, seed=seed, enable_rarity=True, enable_consistency=True,
    enable_meta=False, beta=beta_rarity, prune_threshold=prune_rarity,
    twait1=twait1, twait2=twait2,
    theta_l=0.35, theta_u=0.90,
)
mgr2.run(steps=120)
survived_with = sum(1 for nid in truth2 if g2.has_node(nid))

total_truth = len(truth1)

col1, col2 = st.columns(2)
col1.metric("保護なし — truthノード生存数",
            f"{survived_without}/{total_truth}",
            delta=f"{survived_without - total_truth}")
col2.metric("保護あり — truthノード生存数",
            f"{survived_with}/{total_truth}",
            delta=f"+{survived_with - survived_without}" if survived_with > survived_without else "0")

fig2, ax2 = plt.subplots(figsize=(8, 5))
bars = ax2.bar(
    [0, 1],
    [survived_without, survived_with],
    color=[PHASE_COLORS["removed"], PHASE_COLORS["released"]],
    edgecolor="black", width=0.5,
)
ax2.set_xticks([0, 1])
ax2.set_xticklabels(["Without Protection", "With Protection"])
ax2.set_ylabel("Truth Nodes Survived")
ax2.set_title(f"Truth Node Survival ({total_truth} total, 120 steps)")

for bar in bars:
    h = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width() / 2, h + 0.1,
             f"{int(h)}/{total_truth}", ha="center", fontsize=14, fontweight="bold")

ax2.set_ylim(0, total_truth + 1)
ax2.axhline(y=total_truth, color="gray", linestyle=":", linewidth=1.5, alpha=0.5)
fig2.tight_layout()
st.pyplot(fig2)
plt.close(fig2)

# ================================================================
# Chart 3: Network with Protected Nodes
# ================================================================
st.subheader("3. 保護ノードのネットワーク表示")

g3, _, truth3, _ = build_sample_graph(seed)
mgr3 = GraphMetabolicManager(
    g3, seed=seed, enable_rarity=True, enable_consistency=False,
    enable_meta=False, beta=beta_rarity, prune_threshold=prune_rarity,
    twait1=twait1, twait2=twait2,
)
# Run to middle of phase1
mid_step = min(twait1 // 2 + 10, 60)
mgr3.run(steps=mid_step)

fig3, ax3 = plt.subplots(figsize=(10, 7))
draw_graph(g3, ax3,
           title=f"Step {mid_step}: Protected Nodes Highlighted",
           highlight_protected=True, seed=42)
fig3.tight_layout()
st.pyplot(fig3)
plt.close(fig3)
