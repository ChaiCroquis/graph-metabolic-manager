# Applicability and Scope of Validity / 適用範囲と検証の妥当範囲

This document states honestly what the 629-test verification suite does
and does not establish, and under what conditions the algorithm is
expected to provide value over baselines.

[日本語版はこちら](#日本語版)

---

## 1. What the test suite establishes

The 629-test suite (69 core + 560 patent verification across 28 industry
scenarios) establishes that:

- The four patent features (metabolic control, rarity protection,
  consistency discovery, meta control) are implemented correctly and
  behave as specified.
- When a graph is constructed such that **structurally rare nodes
  (low-weight, low-degree edges) coincide with the ground-truth
  "valuable" nodes**, the rarity protection mechanism preserves them
  and the metabolic control prunes the rest.
- The algorithm is deterministic, parameter-validated, and numerically
  stable across the 28 illustrative scenarios.

## 1.5. Real-data validation status (2026-05-10)

As of this writing, exactly **one** preregistered real-data validation
has been completed:

| ID | Dataset | Domain | Verdict | Notes |
|---|---|---|---|---|
| [F-001](VERIFIED_FINDINGS.md) | BattLeDIM L-Town | Water distribution / leak ranking | **INCONCLUSIVE** | Algorithm recall@50 = 0.061 vs Random 0.042; no preregistered success criterion met; baseline-sensitive |

The verdict reached via this single test is **not** "the algorithm
works on water networks". It is "on this single network with the
preregistered protocol, the algorithm is marginally above random
but does not decisively beat simple baselines". This is itself
useful information: it argues against retaining the unqualified
"Plausible" label on `#25 Water Management` (see §5 below) and
against generalizing the win-zone classification from
[`kdf-perovskite`](sync_with_kdf_perovskite.md) F-061 (non-scale-free
graphs) to all utility networks.

The full audit trail (preregistration, implementation, two
verifier-caught deviations, and how the discipline forced the verdict
through two wrong intermediate states to the correct INCONCLUSIVE)
is in [F-001](VERIFIED_FINDINGS.md).

## 2. What the test suite does NOT establish

The 28 industry scenarios are **synthetic graphs constructed by
[`tests/test_patent_verification.py`](../tests/test_patent_verification.py)**.
Specifically, [`_build_standard()`](../tests/test_patent_verification.py)
deliberately constructs graphs in which:

- "truth" nodes are added with **low-weight (0.04–0.10) edges** to a
  small number of normal nodes
- "normal" nodes are densely interconnected with **high-weight (0.5–1.0)
  edges**
- "garbage" nodes are added in complete isolation

This means the test scenarios encode the assumption that **structural
rareness ≡ task importance** by construction. The test suite therefore
does NOT establish:

- That real-world data in the 28 industries actually has this property
- That the algorithm outperforms baselines (Random, TopDegree, density-
  based methods) on real datasets
- That the algorithm is appropriate for any specific business problem
  in those industries

## 3. Decisive predictor of applicability

A sister project, `kdf-perovskite`, has applied the same theoretical
foundation to real data across many domains (graph pruning, LLM memory,
classical algorithm preprocessing, citation networks, financial fraud
detection, social networks, etc.). That project has established a
**decisive predictor** of when the algorithm provides value:

> The algorithm decisively beats Random / baselines **only when
> structural rareness in the graph is correlated with task importance**.

When this correlation does not hold, the algorithm typically performs
no better than Random, and in some cases worse than simple baselines
such as "keep the top-degree nodes."

## 4. Empirically known regions (from `kdf-perovskite`)

Each item below cites the specific `kdf-perovskite` finding ID
(`F-XXX`) that supports the claim. These IDs are the load-bearing
references that `docs/sync_with_kdf_perovskite.md` tracks for drift
detection.

### 4.1 Domains where the algorithm has been shown to work on real data

- Git commit archival when merge rate is below ~10% — rare merge
  commits are structurally rare AND historically important.
  (`kdf-perovskite` F-062, F-065, F-076)
- Long-conversation date/time recall — specific temporal facts are
  structurally isolated AND query-relevant.
  (`kdf-perovskite` F-057, F-058)
- Path-critical bottleneck detection on non-scale-free graphs (random
  graphs, planted-community graphs).
  (`kdf-perovskite` F-061)
- Orphan-node detection in personal knowledge management.
  (`kdf-perovskite` F-068 and earlier orphan-detection findings)

### 4.2 Domains where the algorithm has been shown NOT to work on real data

- **Scale-free networks where high-degree hubs are the important nodes**
  — citation networks, social influence detection, scale-free network
  analysis. Simple top-degree selection beats the algorithm.
  (`kdf-perovskite` F-061)
- **Density-based / feature-space anomaly detection** — financial fraud
  detection, Gaussian process inducing point selection, kernel SVM
  subset selection. The algorithm is no better than Random.
  (`kdf-perovskite` F-063, F-066, F-067)
- **General semantic retrieval** — query–document matching tasks
  (BEIR/SciFact-style). The algorithm completely fails (recall ≈ 0).
  (`kdf-perovskite` F-045)
- **Long-conversation general QA against modern memory systems** — the
  algorithm does not replace systems like Mem0 for general-purpose
  conversation memory.
  (`kdf-perovskite` F-053, F-054, F-055, F-056)
- **Citation interdisciplinary bridge detection** — recall 0% on real
  citation graphs.
  (`kdf-perovskite` F-075)
- **Metadata-minority detection where minority is semantic, not
  structural** — e.g. detecting cultural minorities by metadata.
  (`kdf-perovskite` F-047)

## 5. Honest classification of the 28 example scenarios

The example scripts in `examples/` are **illustrations of the
algorithm's mechanics on synthetic data**, not real-world validation.
The classification below indicates the author's current view of which
scenarios are likely to map to a structural-rareness-correlates-with-
importance pattern in real deployments. **None of the 28 scenarios
have been validated on real data within this repository.**

| # | Industry | Real-world applicability outlook |
|:---:|---|---|
| 01 | Basic | Illustrative only |
| 02 | E-Commerce | Unverified (depends on long-tail vs scale-free structure) |
| 03 | Knowledge Base | Unverified (general retrieval is known to fail in `kdf-perovskite`) |
| 04 | Medical (rare disease) | Unverified (metadata-minority cases are known to be ground-truth-type dependent) |
| 05 | Financial (fraud) | **Unlikely to apply** (feature-space anomaly detection is shown to fail in `kdf-perovskite`) |
| 06 | IoT Manufacturing | Unverified |
| 07 | Telecom | Unverified (telecom networks often scale-free; hub preservation may be more relevant) |
| 08 | Cybersecurity | Unverified (anomaly detection by feature space is known to fail) |
| 09 | Supply Chain | Plausible (path-critical bottleneck pattern) |
| 10 | Education | Unverified |
| 11 | Smart Grid | Plausible (path-critical pattern, non-scale-free) |
| 12 | Academic Citation | **Unlikely to apply** (`kdf-perovskite` shows recall ≈ 0 on real citation graphs) |
| 13 | Agriculture | Unverified |
| 14 | Legal | Unverified |
| 15 | HR | Unverified |
| 16 | Real Estate | Unverified |
| 17 | Insurance (actuarial) | Unverified (likely density-based anomaly, similar to financial) |
| 18 | Environmental | Unverified |
| 19 | Transportation | Plausible (path-critical) |
| 20 | Social Network | **Unlikely to apply** (scale-free; `kdf-perovskite` shows TopDegree dominates) |
| 21 | Gaming | Unverified |
| 22 | Media Advertising | Unverified (likely scale-free) |
| 23 | Aviation | Plausible (path-critical safety) |
| 24 | Pharma Manufacturing | Unverified |
| 25 | Water Management | Plausible but **single-test INCONCLUSIVE** (BattLeDIM L-Town, [F-001](VERIFIED_FINDINGS.md); marginally above min-TopDegree, below sum-TopDegree; n=33 leaks insufficient for statistical power) |
| 26 | Construction | Unverified |
| 27 | Mining | Unverified |
| 28 | Hospitality | Unverified |

Legend:
- **Unlikely to apply** — A direct or close analog has been empirically
  shown to fail in `kdf-perovskite`.
- Plausible — The structural pattern matches a domain where the
  algorithm has been shown to work.
- Unverified — No real-data evidence either way; the example is
  illustrative.

## 6. Recommended use

- **As a reference implementation of the patent claims** — the code is
  faithful to the specification and the tests demonstrate this.
- **As an educational tool** for understanding metabolic / rarity /
  consistency / meta-control mechanics on graphs.
- **As a starting point for evaluation** in a specific domain — but
  any real-world deployment should validate on real data with an
  appropriate baseline (Random, TopDegree, domain-specific method)
  before any claim of effectiveness is made.

This algorithm is **not** a general-purpose graph compression or
selection method. Its value is bounded by the structural-rareness ↔
importance correlation condition.

---

<a name="日本語版"></a>
## 日本語版

本ドキュメントは、629件のテストスイートが何を立証しており何を立証していないか、本アルゴリズムが価値を発揮することが期待される条件は何か、を率直に述べる。

### 1. テストスイートが立証していること

629件のテスト（コア69件 + 28業界シナリオ × 20テスト = 560件の特許検証）は以下を立証している。

- 特許の4要素（代謝制御・希少性保護・整合性発見・メタ制御）が仕様通りに実装され、規定どおりに動作する
- **構造的に稀少なノード（低weight・低次数）が ground-truth として "価値ある" ノードと一致するように構築されたグラフ** において、希少性保護機構がそれを保存し、代謝制御がそれ以外を剪定する
- 28シナリオ全てにわたり、決定論的・パラメータ検証済み・数値的に安定である

### 1.5. 実データ検証の状況(2026-05-10)

本書記載時点で、preregistered プロトコル経由で完了した実データ検証は
**1 件のみ**:

| ID | データセット | ドメイン | Verdict | 備考 |
|---|---|---|---|---|
| [F-001](VERIFIED_FINDINGS.md) | BattLeDIM L-Town | 配水網 / leak ranking | **INCONCLUSIVE** | recall@50 = 0.061 vs Random 0.042; preregistered 成功条件いずれも未達; ベースラインの取り方に sensitive |

この単発検証から得られる verdict は「水道網でアルゴリズムが機能する」
ではなく、「**この単一ネットワーク + preregistered プロトコルでは、
アルゴリズムは Random を僅かに超える程度で、シンプルなベースラインに
decisive に勝てない**」というもの。これ自体は有用な情報で、§5 の
`#25 Water Management` を無条件 "Plausible" にとどめる根拠を弱め、
[`kdf-perovskite`](sync_with_kdf_perovskite.md) F-061(non-scale-free
グラフでの win-zone)を utility 一般に generalize する正当性も弱める。

完全な監査記録(preregistration、実装、検証 agent が catch した2件の
逸脱、規律が誤った中間 verdict を2段経て正しい INCONCLUSIVE に着地
させた経緯)は [F-001](VERIFIED_FINDINGS.md) に honest に記録済み。

### 2. テストスイートが立証していないこと

28業界シナリオはすべて [`tests/test_patent_verification.py`](../tests/test_patent_verification.py) によって生成された **合成グラフ** である。具体的には [`_build_standard()`](../tests/test_patent_verification.py) が以下のように意図的に構築している。

- "truth" ノードは少数の normal ノードに対して **低 weight (0.04–0.10)** のエッジで接続される
- "normal" ノードどうしは **高 weight (0.5–1.0)** で密に接続される
- "garbage" ノードは完全に孤立した状態で追加される

これは「**構造的稀少性 ≡ 業務上の重要度**」という前提をシナリオ生成時に強制していることを意味する。したがって本テストスイートは以下を立証していない。

- 28業界の実データが実際にこの性質を持つこと
- 実データセット上で本アルゴリズムが Random / TopDegree / density-based 手法等のベースラインを上回ること
- これらの業界の特定の業務課題に本アルゴリズムが適切であること

### 3. 適性の決定的予測子

姉妹プロジェクト `kdf-perovskite` は同一の理論基盤を多領域の実データ（グラフ剪定・LLM memory・古典 algorithm 前処理・引用ネットワーク・金融 fraud 検出・SNS 等）に適用してきた。同プロジェクトでは本アルゴリズムが価値を発揮する条件として以下の **決定的予測子 (decisive predictor)** が確立されている。

> **構造的な稀少性が課題重要度と相関する条件下でのみ、本アルゴリズムは Random / ベースラインを決定的に上回る。**

この相関が成立しない場合、本アルゴリズムは典型的に Random と同等の性能となり、場合によっては「上位次数ノードを残す」のような単純なベースラインを下回る。

### 4. 実データで判明している適性領域（`kdf-perovskite` より）

各項目は支持する `kdf-perovskite` 知見 ID (`F-XXX`) を引用する。これらは
`docs/sync_with_kdf_perovskite.md` が drift 検出で追跡する load-bearing
参照である。

#### 4.1 実データで有効性が確認されている領域

- マージレートが約10%以下の git コミット archival（稀なマージコミットが構造的稀少 **かつ** 履歴的に重要）
  (`kdf-perovskite` F-062, F-065, F-076)
- 長期会話における日時情報の想起（特定の時間情報は構造的に孤立 **かつ** クエリ関連性高い）
  (`kdf-perovskite` F-057, F-058)
- non-scale-free グラフ（ランダム・planted-community 構造）における path-critical bottleneck 検出
  (`kdf-perovskite` F-061)
- パーソナル knowledge management における孤立ノード検出
  (`kdf-perovskite` F-068 ほか)

#### 4.2 実データで適性が確認されていない領域

- **scale-free ネットワークで高次数 hub が重要ノードである場合** — 引用ネットワーク・SNS 影響度・scale-free 分析。素直に上位次数を残す方が強い
  (`kdf-perovskite` F-061)
- **density-based / 特徴空間の anomaly detection** — 金融 fraud 検出・Gaussian process inducing point 選定・kernel SVM subset 選定。Random と同等
  (`kdf-perovskite` F-063, F-066, F-067)
- **一般的な semantic retrieval** — クエリ–文書マッチング（BEIR/SciFact 系）。recall ≈ 0 で完全に失敗
  (`kdf-perovskite` F-045)
- **長期会話の汎用 QA を Mem0 等の memory system 代替として用いる用途** — 一般用途では本アルゴリズムは Mem0 を置換できない
  (`kdf-perovskite` F-053, F-054, F-055, F-056)
- **引用ネットワークの interdisciplinary bridge 検出** — 実引用グラフで recall 0%
  (`kdf-perovskite` F-075)
- **構造的でなく semantic な metadata minority の検出** — 文化的少数派をメタデータで検出する等
  (`kdf-perovskite` F-047)

### 5. 28シナリオの率直な分類

`examples/` 以下のスクリプト群は **合成データ上でアルゴリズムの仕組みを示す illustration** であり、実世界での validation ではない。下記分類は、各シナリオが実運用で「構造的稀少性 ≡ 重要度」パターンに該当しそうか、についての著者の現時点の見解である。**28シナリオのいずれも、本リポジトリ内では実データで validation されていない**。

| # | 業界 | 実世界適性の見立て |
|:---:|---|---|
| 01 | Basic | illustration のみ |
| 02 | E-Commerce | 未検証（long-tail か scale-free かに依存） |
| 03 | Knowledge Base | 未検証（一般 retrieval は `kdf-perovskite` で失敗確認） |
| 04 | Medical (rare disease) | 未検証（metadata minority 系は ground-truth 型依存） |
| 05 | Financial (fraud) | **適用困難の可能性** （特徴空間 anomaly detection は `kdf-perovskite` で失敗確認） |
| 06 | IoT Manufacturing | 未検証 |
| 07 | Telecom | 未検証（scale-free 性が高い場合は hub 保持の方が適切） |
| 08 | Cybersecurity | 未検証（特徴空間 anomaly detection は失敗確認） |
| 09 | Supply Chain | 該当しそう（path-critical bottleneck パターン） |
| 10 | Education | 未検証 |
| 11 | Smart Grid | 該当しそう（path-critical、non-scale-free） |
| 12 | Academic Citation | **適用困難** （`kdf-perovskite` で実引用グラフ recall ≈ 0 確認） |
| 13 | Agriculture | 未検証 |
| 14 | Legal | 未検証 |
| 15 | HR | 未検証 |
| 16 | Real Estate | 未検証 |
| 17 | Insurance (actuarial) | 未検証（金融と同様 density-based の可能性） |
| 18 | Environmental | 未検証 |
| 19 | Transportation | 該当しそう（path-critical） |
| 20 | Social Network | **適用困難** （scale-free; `kdf-perovskite` で TopDegree が優位確認） |
| 21 | Gaming | 未検証 |
| 22 | Media Advertising | 未検証（scale-free の可能性） |
| 23 | Aviation | 該当しそう（path-critical safety） |
| 24 | Pharma Manufacturing | 未検証 |
| 25 | Water Management | 該当しそうだが **単発検証 INCONCLUSIVE**（BattLeDIM L-Town、[F-001](VERIFIED_FINDINGS.md); min-TopDegree より僅かに上、sum-TopDegree より下; n=33 leak で統計検出力不足） |
| 26 | Construction | 未検証 |
| 27 | Mining | 未検証 |
| 28 | Hospitality | 未検証 |

凡例:
- **適用困難（の可能性）** — `kdf-perovskite` で類似タスクが実データで失敗することが確認されている
- 該当しそう — `kdf-perovskite` で有効性が確認された構造パターンと一致する
- 未検証 — 実データの裏付けが両方向ともない（illustration として読むこと）

### 6. 推奨される使い方

- **特許請求項のリファレンス実装として** — コードは仕様に忠実であり、テストはそれを示している
- **教育用ツールとして** — グラフ上の代謝・希少性・整合性・メタ制御の動きを理解する
- **特定ドメインでの評価の出発点として** — ただし実運用での適用前には、必ず実データ上で適切なベースライン（Random・TopDegree・ドメイン固有手法）と比較することが必要

本アルゴリズムは **汎用的な** グラフ圧縮 / 選別手法ではない。「構造的稀少性 ↔ 重要度の相関」という条件にその価値は規定される。
