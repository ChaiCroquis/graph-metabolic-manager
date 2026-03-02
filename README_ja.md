# Graph Metabolic Manager

[![CI](https://github.com/ChaiCroquis/graph-metabolic-manager/actions/workflows/ci.yml/badge.svg)](https://github.com/ChaiCroquis/graph-metabolic-manager/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

**グラフ型データ構造の自動管理 — 不要データの代謝・希少データの保護・隠れた関連の発見**

[English version](README.md)

---

## これは何？

Graph Metabolic Manager は、大規模グラフデータを自動管理する特許アルゴリズムのリファレンス実装です。
3つの問題を同時に解決します：

| 課題 | 解決策 | 方法 |
|---|---|---|
| データが増え続ける | **代謝制御** | 局所混雑度に基づくエッジの適応的減衰 |
| 価値あるデータの喪失 | **希少性保護** | 2フェーズレビューで孤立ノードを保護 |
| 見落とされた関連 | **整合性発見** | ラプラシアン固有値による構造的類似性分析 |

### 特徴

- **局所計算のみ** — グラフ全体の走査不要。各エッジは `deg(u) + deg(v)` だけで評価
- **スケーラブル** — 小規模グラフから数百万ノードまで対応
- **言語非依存** — 純粋なアルゴリズム。どの言語でも実装可能
- **検証済み** — 629テスト合格（28業界×特許4機能の560テスト含む）

---

## クイックスタート

```bash
# インストール（開発モード）
pip install -e .

# 依存パッケージのみインストール
pip install numpy
```

### 基本的な使い方

```python
from graph_metabolic_manager import Graph, GraphMetabolicManager

# グラフを作成
g = Graph()
n1 = g.add_node("商品A")
n2 = g.add_node("商品B")
n3 = g.add_node("希少な知見")
g.add_edge(n1, n2, weight=1.0)
g.add_edge(n1, n3, weight=0.1)

# マネージャーで一括管理
mgr = GraphMetabolicManager(g)
mgr.run(steps=100)
print(mgr.summary())
```

### 個別コンポーネントの使用

```python
from graph_metabolic_manager import Graph, MetabolicControl, RarityProtection

g = Graph()
n1 = g.add_node("商品A")
n2 = g.add_node("商品B")
n3 = g.add_node("希少な知見")
g.add_edge(n1, n2, weight=1.0)
g.add_edge(n1, n3, weight=0.1)

# 代謝制御（低価値エッジを自動枝刈り）
mc = MetabolicControl()
mc.step(g, dt=1.0)

# 希少性保護（希少ノードを削除から保護）
rp = RarityProtection()
rare_nodes = rp.identify_rare(g, t=0)
for nid in rare_nodes:
    rp.enter_protection(g, nid, t=0)
```

---

## アーキテクチャ

```
┌──────────────────────────────────────────────────────┐
│            GraphMetabolicManager — 7フェーズ処理       │
│                                                      │
│  Phase 1: メタ制御      → alphaパラメータ更新          │
│  Phase 2: 活動度計算    → node.activity更新           │
│  Phase 3: レイヤー割当  → edge / core / rare          │
│  Phase 4: 希少性識別    → 保護開始                     │
│  Phase 5: 整合性発見    → 新エッジ追加                 │
│  Phase 6: フェーズ更新  → 保護解除 or ノード削除       │
│  Phase 7: 代謝制御      → エッジ減衰 + 枝刈り         │
└──────────────────────────────────────────────────────┘
```

| コンポーネント | 特許請求項 | 役割 |
|---|---|---|
| MetabolicControl | 請求項 1-10 | 混雑度ベースの自動枝刈り |
| RarityProtection | 請求項 11-20 | 2フェーズレビューによる希少ノード保護 |
| ConsistencyDiscovery | 請求項 21-26 | ラプラシアン固有値による構造的類似性発見 |
| MetaControl | 請求項 27-32 | 健全性フィードバックループ |
| GraphMetabolicManager | 請求項 33-50 | 統合パイプライン（上記全てを連携） |

---

## 仕組み

### 1. 代謝制御（自動枝刈り）

各エッジの重みが局所混雑度に応じて指数的に減衰します：

```
減衰率:   λ(C) = β × (1 + γ × C^α)
重み更新: w ← w × exp(-λ × dt)
混雑度:   C = deg(u) + deg(v)
```

| パラメータ | デフォルト値 | 意味 |
|---|---|---|
| alpha (α) | 2.0 | 混雑度感度の指数 |
| beta (β) | 0.05 | 基底減衰率 |
| gamma (γ) | 0.5 | 混雑度のスケーリング |
| prune_threshold | 0.1 | エッジ削除の閾値 |

**具体例**（alpha=2.0）:

| 混雑度 C | 減衰率 λ | 意味 |
|---|---|---|
| C = 2（疎） | 0.15 | ゆっくり減衰 |
| C = 5（中） | 0.675 | 4ステップで閾値以下 |
| C = 10（密） | 2.55 | 1ステップでほぼゼロ |

### 2. 希少性保護（2フェーズレビュー）

孤立ノード（degree ≤ 1）を即座に削除せず、2段階で審査します：

```
Phase 1（Twait1 = 50ステップ）: 無条件猶予
  → エッジを獲得した → 保護成功
  → 獲得できない   → Phase 2 へ

Phase 2（Twait2 = 50ステップ）: 条件付き観察
  → まだ孤立 & エッジなし → 削除
  → エッジを獲得          → 保護解除（生存）
```

### 3. 整合性発見（隠れた関係の発見）

ラプラシアン固有値スペクトルで構造的な「指紋」を比較し、隠れた類似性を発見します：

```
1. k-hop部分グラフを抽出（k=2）
2. ラプラシアン固有値ベクトル（8次元）を計算
3. 複合スコアを算出:
   S = (7×S_sys + 2×S_rel + 1×S_attr) / 10
4. サンドイッチ閾値で判定:
   0.70 ≤ S ≤ 0.80 → ACCEPT（隠れた整合性を発見）
   S < 0.70 → 類似度不足
   S > 0.80 → 自明すぎ（発見の価値なし）
```

### 4. メタ制御（自動パラメータ調整）

グラフの「健全性」を監視し、代謝制御のパラメータを自動調整します：

```
健全性指標: H = 1 - |k_avg - k_opt| / k_opt
更新量:     Δ = η × δk^4（4乗則: 小偏差は無視、大偏差に急応答）
```

| パラメータ | デフォルト値 | 意味 |
|---|---|---|
| k_opt | 5.0 | 最適平均次数 |
| h_target | 0.7 | 目標健全性 |
| eta (η) | 0.001 | 学習率 |
| alpha_range | [0.5, 3.0] | αの調整範囲 |

---

## テスト

```bash
# 開発用依存パッケージのインストール
pip install -e ".[dev]"

# テスト実行
pytest tests/ -v
```

**629テスト** がコアアルゴリズムと特許機能を検証：

| カテゴリ | テスト数 | 状態 |
|---|---|---|
| グラフ基本操作 | 8 | 合格 |
| 数理モデル | 5 | 合格 |
| 代謝制御 | 4 | 合格 |
| 希少性保護 | 4 | 合格 |
| 整合性発見 | 16 | 合格 |
| メタ制御 | 4 | 合格 |
| 階層管理 | 13 | 合格 |
| 統合テスト | 6 | 合格 |
| TRACEログ | 9 | 合格 |
| **特許検証（28業界 × 20）** | **560** | **全合格** |

---

## 適用業界（28業界のサンプル）

各業界にそれぞれ実行可能なサンプルがあります：

| 業界 | ファイル | 保護対象 |
|---|---|---|
| 汎用 | `01_basic_usage.py` | 基本的な使い方 |
| EC・通販 | `02_ec_recommendation.py` | ニッチ商品 |
| 知識管理 | `03_knowledge_base.py` | レガシー文書 |
| 医療 | `04_medical_knowledge.py` | 希少疾患データ |
| 金融 | `05_financial_network.py` | 不正検知シグナル |
| IoT・製造 | `06_iot_manufacturing.py` | 設備異常の前兆 |
| 通信 | `07_telecom_network.py` | バックアップ経路 |
| サイバーセキュリティ | `08_cybersecurity.py` | APT脅威シグナル |
| サプライチェーン | `09_supply_chain.py` | 単一供給源 |
| 教育 | `10_education_curriculum.py` | 学際的カリキュラム |
| エネルギー | `11_smart_grid.py` | カスケード障害警告 |
| 学術研究 | `12_academic_citation.py` | 分野横断論文 |
| 農業・食品安全 | `13_agriculture_food_safety.py` | 病害虫トレース |
| 法務・コンプライアンス | `14_legal_compliance.py` | 希少判例 |
| 人材管理 | `15_hr_talent.py` | 希少スキル組合せ |
| 不動産 | `16_real_estate.py` | 特異物件特性 |
| 保険 | `17_insurance_actuarial.py` | 希少請求パターン |
| 環境監視 | `18_environmental_monitoring.py` | 希少種・イベント |
| 物流 | `19_transportation.py` | ルートボトルネック |
| SNS | `20_social_network.py` | ブリッジユーザー |
| ゲーム | `21_gaming.py` | チート検知 |
| メディア・広告 | `22_media_advertising.py` | 新興トレンド |
| 航空宇宙 | `23_aviation.py` | 疲労亀裂パターン |
| 製薬 | `24_pharma_manufacturing.py` | 汚染トレース |
| 上下水道 | `25_water_management.py` | 水質シグナル |
| 建設 | `26_construction.py` | 構造欠陥シグナル |
| 鉱業 | `27_mining.py` | 地質異常シグナル |
| 観光・ホスピタリティ | `28_hospitality.py` | 需要パターン |

```bash
# サンプルの実行
python examples/01_basic_usage.py
python examples/02_ec_recommendation.py
```

---

## データフロー可視化

具体的な数値で数式の入力→計算→出力を追跡できるドキュメントと図表です：

- **[処理フロー（数式トレース）](docs/data-flow/processing_flow.md)** — 全数式に具体値を代入したトレース
- **[図表ガイド（日本語解説）](docs/data-flow/figures_guide.md)** — 全10枚の図の入力・出力・読み方

| 図 | 内容 | 対応する請求項 |
|---|---|---|
| 図1 | 減衰率曲線 λ(C) — α=1,2,3の比較 | 請求項1-10 |
| 図2 | エッジ重み減衰タイムライン | 請求項1-10 |
| 図3 | 代謝制御 Before/After 棒グラフ | 請求項1-10 |
| 図4 | 希少性保護フェーズタイムライン | 請求項11-20 |
| 図5 | 保護あり/なし truthノード生存比較 | 請求項11-20 |
| 図6 | 整合性スコア分解 (7:2:1の重み) | 請求項21-26 |
| 図7 | 健全性指標 H の三角形カーブ | 請求項27-32 |
| 図8 | メタ制御の収束（H + α の時系列） | 請求項27-32 |
| 図9 | 階層処理スケジュール ヒートマップ | 請求項20-26 |
| 図10 | 統合パイプライン 150ステップ | 請求項33-50 |

```bash
# 図表の再生成
python docs/data-flow/generate_figures.py
```

---

## 論文シリーズ

技術論文（Qiita/Zenn/note 投稿向け）全6回:

| # | タイトル | 対象 |
|---|---|---|
| [00](docs/paper-series/00_シリーズ概要.md) | シリーズ概要 | 全体目次 |
| [01](docs/paper-series/01_概要編.md) | 概要編 — なぜグラフは太るのか | 問題定義と4機能 |
| [02](docs/paper-series/02_代謝制御編.md) | 代謝制御編 — O(1)/エッジの自動整理 | λ(C)の数式と計算例 |
| [03](docs/paper-series/03_希少性保護編.md) | 希少性保護編 — 2フェーズレビュー | 28業界の保護対象比較 |
| [04](docs/paper-series/04_整合性発見編.md) | 整合性発見編 — ラプラシアン固有値 | スコア計算の詳細 |
| [05](docs/paper-series/05_メタ制御編.md) | メタ制御編 — フィードバックと4乗則 | 制御理論との比較 |
| [06](docs/paper-series/06_検証編.md) | 検証編 — 629テストの実証評価 | 28業界×4機能の結果 |

---

## 特許情報

| 項目 | 内容 |
|---|---|
| 出願番号 | 特願2026-027032 |
| 発明の名称 | 希少性保護及び整合性発見を用いたデータ構造管理システム |
| IPC | G06F 16/21, G06F 16/906 |
| 請求項数 | 50項（システム48 + 方法1 + プログラム1） |
| 出願日 | 2026年2月24日 |

### ライセンス

ソースコードは **Apache License 2.0**（特許除外条項付き）で公開しています。

| 対象 | ライセンス | 費用 |
|---|---|---|
| ソースコード（著作権） | Apache 2.0 | 無料 |
| 特許アルゴリズム（商用利用） | 別途特許ライセンス | 要相談 |

- 学術研究・個人利用: 無料（Apache 2.0の範囲内）
- 商用利用（特許技術を含む製品・サービス）: 特許ライセンスが必要

詳細は [PATENT_NOTICE.md](PATENT_NOTICE.md) をご確認ください。

**ライセンス形態**:
- 独占ライセンス（分野限定の1社独占）
- 非独占ライセンス
- 分野限定ライセンス
- 技術サポート付きライセンス

**お問い合わせ**: garden.of.knowledge.chai@gmail.com

---

## プロジェクト構成

```
graph-metabolic-manager/
├── README.md                      # 英語版README
├── README_ja.md                   # 日本語版README（本ファイル）
├── LICENSE                        # Apache 2.0 + 特許除外条項
├── CHANGELOG.md                   # リリース履歴
├── PATENT_NOTICE.md               # 特許ライセンス情報
├── pyproject.toml                 # パッケージ設定
├── graph_metabolic_manager/       # コアライブラリ
│   ├── __init__.py                # 公開API（16シンボル）
│   ├── graph.py                   # グラフデータ構造
│   ├── metabolic.py               # 代謝制御（請求項1-10）
│   ├── rarity.py                  # 希少性保護（請求項11-20）
│   ├── consistency.py             # 整合性発見（請求項21-26）
│   ├── meta_control.py            # メタ制御（請求項27-32）
│   ├── manager.py                 # 統合マネージャー（請求項33-50）
│   └── _logging.py                # カスタムTRACEログレベル（level 5）
├── examples/                      # 28業界サンプル
├── tests/                         # 629テスト
├── benchmarks/                    # パフォーマンスベンチマーク
└── docs/                          # ドキュメント
    ├── data-flow/                 # データフロー可視化（図表10枚）
    │   ├── figures_guide.md       # 図表ガイド（日本語）
    │   ├── processing_flow.md     # 処理フロー（数式トレース）
    │   └── generate_figures.py    # 図表生成スクリプト
    └── paper-series/              # 技術論文シリーズ（全6回）
```

---

## コントリビューション

Issue や Pull Request を歓迎します。

コントリビューションは Apache License 2.0 の下でライセンスされます。
