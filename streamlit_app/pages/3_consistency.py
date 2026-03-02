"""整合性発見 (Consistency Discovery) -- Interactive Demo Page."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from graph_metabolic_manager import (
    ConsistencyDiscovery,
    attribute_similarity,
    compute_structural_repr,
    consistency_score,
    relational_similarity,
)
from graph_metabolic_manager.consistency import (
    cosine_similarity,
    sign_agreement,
    structural_diff_similarity,
)
from streamlit_app.components.graph_viz import (
    COLORS,
    apply_style,
    draw_graph,
)
from streamlit_app.components.sample_graphs import build_consistency_graph

apply_style()

st.set_page_config(page_title="整合性発見", page_icon="🔍", layout="wide")
st.title("🔍 整合性発見 (Consistency Discovery)")

st.latex(
    r"S = \frac{W_{sys} \cdot S_{sys} + W_{rel} \cdot S_{rel} + W_{attr} \cdot S_{attr}}"
    r"{W_{sys} + W_{rel} + W_{attr}}"
)

st.markdown("""
ノード間の **構造的類似性** を3つの指標で測定し、
隠れた関係性を発見します。

- **S_sys** (重み7): ラプラシアン固有値による構造的類似度
- **S_rel** (重み2): 近傍ノードのJaccard係数
- **S_attr** (重み1): ノードタイプ・メタデータの一致度

「低すぎず高すぎない」サンドイッチ閾値で、
自明でない有意な関係だけを抽出します。
""")

st.divider()

# ---- Sidebar ----
st.sidebar.header("パラメータ設定")

theta_l = st.sidebar.slider(
    "theta_L — 下限閾値",
    min_value=0.30, max_value=0.90, value=0.70, step=0.05,
    help="これ未満のスコアは類似性不足として棄却",
)
theta_u = st.sidebar.slider(
    "theta_U — 上限閾値",
    min_value=0.50, max_value=1.00, value=0.80, step=0.05,
    help="これ超のスコアは自明すぎるとして棄却",
)
k_hop = st.sidebar.slider(
    "k-hop — 近傍半径",
    min_value=1, max_value=4, value=2, step=1,
    help="部分グラフ抽出時のホップ数",
)
dim = st.sidebar.slider(
    "dim — 構造表現の次元数",
    min_value=4, max_value=16, value=8, step=2,
    help="固有値ベクトルの次元数",
)

if theta_l > theta_u:
    st.sidebar.warning("theta_L は theta_U 以下にしてください。")

# ================================================================
# Chart 1: Score Breakdown
# ================================================================
st.subheader("1. スコア分解 (Stacked Bar)")

g, pairs = build_consistency_graph()

w_sys, w_rel, w_attr = 7, 2, 1
total_w = w_sys + w_rel + w_attr

s_sys_vals = []
s_rel_vals = []
s_attr_vals = []
total_scores = []

for label, nid_a, nid_b in pairs:
    r_a = compute_structural_repr(g.subgraph(nid_a, k_hop=k_hop), dim=dim)
    r_b = compute_structural_repr(g.subgraph(nid_b, k_hop=k_hop), dim=dim)

    s_cos = cosine_similarity(r_a, r_b)
    s_str = structural_diff_similarity(r_a, r_b)
    s_sgn = sign_agreement(r_a, r_b)
    s_sys = (s_cos + s_str + s_sgn) / 3.0

    s_rel = relational_similarity(g, nid_a, nid_b)
    s_attr_val = attribute_similarity(g, nid_a, nid_b)

    s_sys_vals.append(w_sys * s_sys / total_w)
    s_rel_vals.append(w_rel * s_rel / total_w)
    s_attr_vals.append(w_attr * s_attr_val / total_w)
    total_scores.append(s_sys_vals[-1] + s_rel_vals[-1] + s_attr_vals[-1])

fig1, ax1 = plt.subplots(figsize=(10, 5))
x = np.arange(len(pairs))
w_bar = 0.5

ax1.bar(x, s_sys_vals, w_bar, label=f"S_sys (w={w_sys}/10)", color=COLORS["info"])
ax1.bar(x, s_rel_vals, w_bar, bottom=s_sys_vals,
        label=f"S_rel (w={w_rel}/10)", color=COLORS["warning"])
bottoms = [a + b for a, b in zip(s_sys_vals, s_rel_vals)]
ax1.bar(x, s_attr_vals, w_bar, bottom=bottoms,
        label=f"S_attr (w={w_attr}/10)", color=COLORS["success"])

# Sandwich threshold band
ax1.axhspan(theta_l, theta_u, alpha=0.15, color="green",
            label=f"Accept: [{theta_l:.2f}, {theta_u:.2f}]")
ax1.axhline(y=theta_l, color="green", linestyle="--", linewidth=1.5, alpha=0.7)
ax1.axhline(y=theta_u, color="green", linestyle="--", linewidth=1.5, alpha=0.7)

for i in range(len(pairs)):
    status = "ACCEPT" if theta_l <= total_scores[i] <= theta_u else "REJECT"
    ax1.text(i, total_scores[i] + 0.02, f"S={total_scores[i]:.3f}\n({status})",
             ha="center", fontsize=10, fontweight="bold")

ax1.set_xticks(x)
ax1.set_xticklabels([p[0] for p in pairs])
ax1.set_ylabel("Weighted Score Contribution")
ax1.set_title("Consistency Score Breakdown")
ax1.legend(fontsize=9, loc="upper right")
ax1.set_ylim(0, 1.15)
fig1.tight_layout()
st.pyplot(fig1)
plt.close(fig1)

# ================================================================
# Chart 2: Eigenvalue Spectrum Comparison
# ================================================================
st.subheader("2. 固有値スペクトル比較")

# Use the first pair (highest similarity) for visualization
pair_idx = st.selectbox(
    "比較するペアを選択",
    options=list(range(len(pairs))),
    format_func=lambda i: pairs[i][0].replace("\n", " "),
    index=0,
)

label, nid_a, nid_b = pairs[pair_idx]
r_a = compute_structural_repr(g.subgraph(nid_a, k_hop=k_hop), dim=dim)
r_b = compute_structural_repr(g.subgraph(nid_b, k_hop=k_hop), dim=dim)

fig2, (ax2a, ax2b) = plt.subplots(1, 2, figsize=(12, 4))

x_dim = np.arange(len(r_a))
ax2a.bar(x_dim, r_a, color=COLORS["info"], alpha=0.8)
ax2a.set_title(f"Node {g.nodes[nid_a].label} Eigenvalues")
ax2a.set_xlabel("Dimension")
ax2a.set_ylabel("Value")

ax2b.bar(x_dim, r_b, color=COLORS["accent"], alpha=0.8)
ax2b.set_title(f"Node {g.nodes[nid_b].label} Eigenvalues")
ax2b.set_xlabel("Dimension")

# Make y-axes consistent
y_max = max(max(abs(r_a)), max(abs(r_b))) * 1.2 if len(r_a) > 0 else 1.0
for ax in [ax2a, ax2b]:
    ax.set_ylim(-y_max, y_max)

fig2.suptitle(f"Laplacian Eigenvalue Spectrum (dim={dim}, k_hop={k_hop})", fontsize=12)
fig2.tight_layout()
st.pyplot(fig2)
plt.close(fig2)

# Show similarity sub-scores
s_cos = cosine_similarity(r_a, r_b)
s_str = structural_diff_similarity(r_a, r_b)
s_sgn = sign_agreement(r_a, r_b)
col1, col2, col3 = st.columns(3)
col1.metric("Cosine Similarity", f"{s_cos:.4f}")
col2.metric("Structural Diff Similarity", f"{s_str:.4f}")
col3.metric("Sign Agreement", f"{s_sgn:.4f}")

# ================================================================
# Chart 3: Network with Discovered Edges
# ================================================================
st.subheader("3. 発見された隠れエッジ")

st.markdown(f"theta_L={theta_l:.2f}, theta_U={theta_u:.2f} でConsistencyDiscoveryを実行")

cd = ConsistencyDiscovery(theta_l=theta_l, theta_u=theta_u)
# Get all node IDs that could be rare
all_ids = list(g.nodes.keys())
discoveries = cd.discover(g, all_ids)

if discoveries:
    st.success(f"{len(discoveries)} 個の隠れ関係を発見しました。")
    for rare_id, cand_id, score in discoveries:
        st.markdown(
            f"- **{g.nodes[rare_id].label}** ↔ **{g.nodes[cand_id].label}** "
            f"(score={score:.4f})"
        )
else:
    st.info("現在の閾値設定では隠れ関係は発見されませんでした。theta_L/theta_Uを調整してみてください。")

fig3, ax3 = plt.subplots(figsize=(10, 7))
draw_graph(g, ax3, title="Consistency Discovery Network", seed=42)
fig3.tight_layout()
st.pyplot(fig3)
plt.close(fig3)
