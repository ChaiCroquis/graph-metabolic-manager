"""Graph Metabolic Manager -- Interactive Demo (Home Page)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st

st.set_page_config(
    page_title="Graph Metabolic Manager Demo",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🧬 Graph Metabolic Manager")
st.subheader("インタラクティブデモ")

st.markdown("""
グラフ（ネットワーク）データ構造を **生物の代謝のように** 自動管理するライブラリです。

左のサイドバーから各機能のデモページに移動できます。
""")

st.divider()

# ---- 4 Core Features ----
st.markdown("### 4つのコア機能")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    #### 🔄 代謝制御 (Metabolic Control)
    混雑した領域のエッジを自動的に減衰・除去します。

    `λ(C) = β(1 + γ·C^α)`

    ---

    #### 🔍 整合性発見 (Consistency Discovery)
    隠れた関係性を固有値解析で自動検出します。

    `S = (7·S_sys + 2·S_rel + 1·S_attr) / 10`
    """)

with col2:
    st.markdown("""
    #### 🛡️ 希少性保護 (Rarity Protection)
    少数派ノードを2フェーズで保護します。

    `Phase1(猶予) → Phase2(観察) → 解放/削除`

    ---

    #### ⚖️ メタ制御 (Meta Control)
    グラフの健全性を監視し、パラメータを自動調整します。

    `H = 1 - |k_avg - k_opt| / k_opt`
    """)

st.divider()

# ---- Navigation ----
st.markdown("### ページ一覧")

pages = [
    ("1️⃣ 代謝制御", "パラメータを変えて減衰曲線やグラフの変化をリアルタイムで確認"),
    ("2️⃣ 希少性保護", "保護フェーズのタイムラインと保護効果を可視化"),
    ("3️⃣ 整合性発見", "スコア分解と隠れエッジの発見を体験"),
    ("4️⃣ メタ制御", "健全性フィードバックループの収束を観察"),
    ("5️⃣ 統合パイプライン", "全機能を組み合わせたシミュレーション"),
]

for name, desc in pages:
    st.markdown(f"**{name}** — {desc}")

st.divider()

# ---- Links ----
st.markdown("### リンク")
st.markdown("""
- 📦 [GitHub Repository](https://github.com/ChaiCroquis/graph-metabolic-manager)
- 📄 特許出願: 特願2026-027032
- 📜 License: Apache 2.0 (with Patent Exclusion)
""")

# ---- Sidebar ----
st.sidebar.markdown("### Graph Metabolic Manager")
st.sidebar.markdown("v0.2.1")
st.sidebar.markdown("---")
st.sidebar.markdown("左のメニューからページを選択してください。")
