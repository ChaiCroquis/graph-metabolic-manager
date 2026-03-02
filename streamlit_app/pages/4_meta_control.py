"""メタ制御 (Meta Control) -- Interactive Demo Page."""

from __future__ import annotations

import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from graph_metabolic_manager import (
    MetabolicControl,
    MetaControl,
    RarityProtection,
    health_index,
)
from streamlit_app.components.graph_viz import COLORS, apply_style
from streamlit_app.components.sample_graphs import build_sample_graph

apply_style()

st.set_page_config(page_title="メタ制御", page_icon="⚖️", layout="wide")
st.title("⚖️ メタ制御 (Meta Control)")

st.latex(r"H = 1 - \frac{|k_{avg} - k_{opt}|}{k_{opt}}")
st.latex(r"\Delta\alpha = \eta \cdot \delta_k^n")

st.markdown("""
グラフの **健全性指標 H** を監視し、
目標値に近づくようにパラメータ α を自動調整するフィードバックループです。

- H が低い → α を増加（枝刈り強化 → 密度低下）
- H が高い → α を減少（枝刈り緩和 → 密度維持）
""")

st.divider()

# ---- Sidebar ----
st.sidebar.header("パラメータ設定")

k_opt = st.sidebar.slider(
    "k_opt — 最適平均次数",
    min_value=2.0, max_value=10.0, value=5.0, step=0.5,
    help="グラフがこの平均次数のときH=1.0（最健全）",
)
h_target = st.sidebar.slider(
    "H_target — 目標ヘルスインデックス",
    min_value=0.50, max_value=0.95, value=0.70, step=0.05,
    help="Hがこの値を下回ると調整が活発化",
)
eta = st.sidebar.slider(
    "η — 学習率",
    min_value=0.0001, max_value=0.0100, value=0.0010, step=0.0001,
    format="%.4f",
    help="α更新量のスケーリング係数",
)
n_exp = st.sidebar.slider(
    "n — 更新量指数",
    min_value=2, max_value=6, value=4, step=1,
    help="大きいほど大きな偏差に敏感に反応",
)
sim_steps = st.sidebar.slider(
    "シミュレーション ステップ数",
    min_value=50, max_value=300, value=100, step=10,
)

# ================================================================
# Chart 1: Health Index Curve
# ================================================================
st.subheader("1. 健全性指標曲線")

k_avg_range = np.linspace(0, 15, 300)
H_vals = [health_index(k, k_opt) for k in k_avg_range]

fig1, ax1 = plt.subplots(figsize=(10, 5))
ax1.plot(k_avg_range, H_vals, "-", color=COLORS["primary"], linewidth=3)

# Target line
ax1.axhline(y=h_target, color="orange", linestyle="--", linewidth=2,
            label=f"H_target = {h_target}")

# Optimal point
ax1.plot(k_opt, 1.0, "*", color=COLORS["gold"], markersize=20, zorder=5,
         markeredgecolor="black", markeredgewidth=1.5)
ax1.annotate(f"k_opt={k_opt}\nH=1.0",
             (k_opt, 1.0), textcoords="offset points",
             xytext=(40, -20), fontsize=10,
             arrowprops=dict(arrowstyle="->"),
             bbox=dict(boxstyle="round,pad=0.3", fc="lightyellow"))

# Example points
for k_ex in [k_opt * 0.6, k_opt * 1.6]:
    if 0 < k_ex < 15:
        h_ex = health_index(k_ex, k_opt)
        ax1.plot(k_ex, h_ex, "ko", markersize=8, zorder=5)
        ax1.annotate(f"k={k_ex:.1f} -> H={h_ex:.2f}",
                     (k_ex, h_ex), textcoords="offset points",
                     xytext=(15, 15), fontsize=9,
                     bbox=dict(boxstyle="round,pad=0.3", fc="lightyellow", ec="gray"))

# Shade zones
ax1.axvspan(0, k_opt, alpha=0.05, color="red", label="Underdense")
ax1.axvspan(k_opt, 15, alpha=0.05, color="blue", label="Overdense")

ax1.set_xlabel("Average Degree k_avg")
ax1.set_ylabel("Health Index H")
ax1.set_title(f"Health Index: H = 1 - |k_avg - k_opt| / k_opt  (k_opt={k_opt})")
ax1.legend()
ax1.set_xlim(0, 15)
ax1.set_ylim(0, 1.1)
fig1.tight_layout()
st.pyplot(fig1)
plt.close(fig1)

# ================================================================
# Chart 2: Convergence Dual-Axis Plot
# ================================================================
st.subheader("2. 収束プロット (Health + Alpha)")

random.seed(42)
np.random.seed(42)

g, _, _, _ = build_sample_graph(42)
mc = MetabolicControl()
rp = RarityProtection()
meta = MetaControl(k_opt=k_opt, h_target=h_target, eta=eta, n=n_exp)

health_hist = []
alpha_hist = []
kavg_hist = []

for t in range(sim_steps):
    info = meta.step(g)
    mc.alpha = meta.current_alpha
    mc.step(g, dt=1.0, protected=rp.protected)
    rp.update_phases(g, t)

    health_hist.append(info["H"])
    alpha_hist.append(info["alpha"])
    kavg_hist.append(info["k_avg"])

fig2, ax2_left = plt.subplots(figsize=(12, 5))

color_h = COLORS["primary"]
color_a = COLORS["accent"]

ax2_left.set_xlabel("Time Step")
ax2_left.set_ylabel("Health Index H", color=color_h)
line_h = ax2_left.plot(health_hist, "-", color=color_h, linewidth=2, label="Health H")
ax2_left.tick_params(axis="y", labelcolor=color_h)
ax2_left.axhline(y=h_target, color=color_h, linestyle=":", linewidth=1.5, alpha=0.5)
ax2_left.set_ylim(0, 1.1)

ax2_right = ax2_left.twinx()
ax2_right.set_ylabel("Alpha", color=color_a)
line_a = ax2_right.plot(alpha_hist, "-", color=color_a, linewidth=2, label="Alpha")
ax2_right.tick_params(axis="y", labelcolor=color_a)

lines = line_h + line_a
labels = [l.get_label() for l in lines]
ax2_left.legend(lines, labels, fontsize=11, loc="center right")

ax2_left.set_title(
    f"Meta Control Convergence  (k_opt={k_opt}, H_target={h_target}, eta={eta}, n={n_exp})"
)
fig2.tight_layout()
st.pyplot(fig2)
plt.close(fig2)

# ================================================================
# Chart 3: k_avg Trajectory
# ================================================================
st.subheader("3. 平均次数 k_avg の推移")

fig3, ax3 = plt.subplots(figsize=(12, 4))
ax3.plot(kavg_hist, "-", color=COLORS["success"], linewidth=2, label="k_avg")
ax3.axhline(y=k_opt, color="orange", linestyle="--", linewidth=2,
            label=f"k_opt = {k_opt}")
ax3.set_xlabel("Time Step")
ax3.set_ylabel("Average Degree")
ax3.set_title("Average Degree Over Time")
ax3.legend()
ax3.set_ylim(bottom=0)
fig3.tight_layout()
st.pyplot(fig3)
plt.close(fig3)

# Summary metrics
st.divider()
col1, col2, col3 = st.columns(3)
col1.metric("最終 Health", f"{health_hist[-1]:.3f}" if health_hist else "N/A")
col2.metric("最終 Alpha", f"{alpha_hist[-1]:.3f}" if alpha_hist else "N/A")
col3.metric("最終 k_avg", f"{kavg_hist[-1]:.2f}" if kavg_hist else "N/A")
