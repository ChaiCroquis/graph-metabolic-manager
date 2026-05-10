# Patent Verification Report / 特許検証レポート

Systematic verification that all 28 industry examples correctly
implement and demonstrate the 4 core patent features.

[日本語版はこちら](#日本語版)

---

## Test Environment

- **Python**: 3.13.9
- **Platform**: Windows (win32)
- **pytest**: 9.0.2
- **Date**: 2026-02-28

---

## Test Summary

```
Total tests: 629 passed

  Core algorithm tests:      69 (9 test files)
  Patent verification tests: 560 (1 test file, 28 scenarios x 20 tests)
```

---

## Scope of Validity (read this first)

**The 28 industry scenarios are synthetic graphs.** The test generator
[`_build_standard()`](../tests/test_patent_verification.py) deliberately
constructs each scenario so that:

- "truth" nodes are connected with **low-weight (0.04–0.10), low-degree
  edges** to a small number of normal nodes
- "normal" nodes are densely interconnected with **high-weight (0.5–1.0)
  edges**
- "garbage" nodes are added in **complete isolation**

This means each scenario encodes the assumption that **structural
rareness ≡ task importance** by construction. The 560 patent
verification tests therefore demonstrate:

✅ The algorithm correctly preserves structurally rare nodes when
   structural rareness coincides with the ground-truth important nodes.

❌ They do NOT demonstrate that real-world data in the named industries
   actually has this property, nor that the algorithm outperforms
   baselines (Random, TopDegree, density-based methods) on real data
   in those industries.

A sister project, `kdf-perovskite`, has applied the same theoretical
foundation to real data across many domains and established a
**decisive predictor** of applicability: the algorithm decisively beats
baselines **only when structural rareness in the graph is correlated
with task importance**. Empirically known *failure* domains include
scale-free networks (citation, social), density-based anomaly
detection (financial fraud), general semantic retrieval, and metadata-
minority detection.

For the honest classification of the 28 example scenarios and the
empirically known applicability boundaries, see
[applicability.md](applicability.md).

The per-feature verification results below (Patent Features 1–4 and
Integration) should be read as **"the algorithm does what the patent
specifies on the constructed scenarios"**, not as cross-industry
real-world validation.

---

## Patent Feature 1: Metabolic Control (Claims 1–10)

**What is verified**: Congestion-based pruning correctly removes
garbage/isolated data while reducing overall graph size.

| Test | Description | Result |
|---|---|:---:|
| `test_garbage_nodes_pruned` | Garbage (isolated) nodes are removed by metabolic pruning | ✅ 28/28 |
| `test_graph_size_reduced` | Graph shrinks after metabolic management | ✅ 28/28 |
| `test_some_normal_nodes_survive` | Core data structure is preserved (not over-pruned) | ✅ 28/28 |

**Conclusion**: Metabolic control correctly differentiates between
garbage (isolated, no connections) and core data (connected, active).
All 28 industry scenarios demonstrate successful automatic pruning.

---

## Patent Feature 2: Rarity Protection (Claims 11–20)

**What is verified**: Two-phase review correctly preserves rare but
valuable nodes that would be destroyed by standard pruning.

| Test | Description | Result |
|---|---|:---:|
| `test_without_protection_truth_lost` | Truth nodes destroyed WITHOUT protection | ✅ 28/28 |
| `test_with_protection_truth_survives` | Truth nodes survive WITH protection | ✅ 28/28 |
| `test_protection_improves_survival` | Protection provides measurable improvement | ✅ 28/28 |
| `test_garbage_still_cleaned_with_protection` | Protection does NOT prevent garbage cleanup | ✅ 28/28 |

**Key finding**: In ALL 28 scenarios, without rarity protection,
truth nodes are partially or completely destroyed. With protection,
survival rate improves in every case. This proves the patent's claim
that rarity protection is necessary and effective.

**Detailed survival comparison**:

| # | Industry | Without Protection | With Protection | Improvement |
|:---:|---|:---:|:---:|:---:|
| 01 | General | partial loss | preserved | ✅ |
| 02 | E-Commerce | partial loss | preserved | ✅ |
| 03 | Knowledge Base | partial loss | preserved | ✅ |
| 04 | Medical | partial loss | preserved | ✅ |
| 05 | Financial | 0/6 (all lost) | preserved | ✅ |
| 06 | IoT Manufacturing | partial loss | preserved | ✅ |
| 07 | Telecom | 0/6 (all lost) | 4/6 preserved | ✅ |
| 08 | Cybersecurity | 0/6 (all lost) | 2/6 preserved | ✅ |
| 09 | Supply Chain | 0/6 (all lost) | 2/6 preserved | ✅ |
| 10 | Education | 0/6 (all lost) | 4/6 preserved | ✅ |
| 11 | Smart Grid | 0/6 (all lost) | 6/6 preserved | ✅ |
| 12 | Academic Citation | 0/6 (all lost) | 1/6 preserved | ✅ |
| 13 | Agriculture | partial loss | preserved | ✅ |
| 14 | Legal | partial loss | preserved | ✅ |
| 15 | HR | partial loss | preserved | ✅ |
| 16 | Real Estate | partial loss | preserved | ✅ |
| 17 | Insurance | partial loss | preserved | ✅ |
| 18 | Environmental | partial loss | preserved | ✅ |
| 19 | Transportation | 0/6 (all lost) | 1/6 preserved | ✅ |
| 20 | Social Network | 0/6 (all lost) | 2/6 preserved | ✅ |
| 21 | Gaming | 0/6 (all lost) | 2/6 preserved | ✅ |
| 22 | Media Advertising | 0/6 (all lost) | 2/6 preserved | ✅ |
| 23 | Aviation | 0/6 (all lost) | 1/6 preserved | ✅ |
| 24 | Pharma Manufacturing | 0/6 (all lost) | 1/6 preserved | ✅ |
| 25 | Water Management | 0/6 (all lost) | 2/6 preserved | ✅ |
| 26 | Construction | 0/6 (all lost) | 1/6 preserved | ✅ |
| 27 | Mining | 0/6 (all lost) | 2/6 preserved | ✅ |
| 28 | Hospitality | 0/6 (all lost) | 2/6 preserved | ✅ |

---

## Patent Feature 3: Consistency Discovery (Claims 21–26)

**What is verified**: Laplacian eigenvalue-based structural similarity
correctly discovers hidden connections between rare and normal nodes.

| Test | Description | Result |
|---|---|:---:|
| `test_discoveries_found` | At least one structural similarity found | ✅ 28/28 |
| `test_discovery_scores_valid` | All scores in [0, 1] range | ✅ 28/28 |
| `test_discovery_nodes_exist` | All discovered nodes exist in graph | ✅ 28/28 |
| `test_discovery_respects_threshold` | All scores within sandwich threshold [θ_L, θ_U] | ✅ 28/28 |

**Conclusion**: Consistency discovery produces valid, meaningful
structural similarities in all 28 industry scenarios. The sandwich
threshold correctly filters both too-dissimilar and trivially-similar
results.

---

## Patent Feature 4: Meta Control (Claims 27–32)

**What is verified**: Health-based feedback loop correctly monitors
graph state and dynamically adjusts system parameters.

| Test | Description | Result |
|---|---|:---:|
| `test_health_tracked` | Health index recorded for every step | ✅ 28/28 |
| `test_health_values_valid` | Health index H in [0, 1] | ✅ 28/28 |
| `test_alpha_within_bounds` | Alpha stays within [α_min, α_max] | ✅ 28/28 |
| `test_alpha_adjusts_dynamically` | Alpha changes from initial value | ✅ 28/28 |
| `test_health_history_contains_required_keys` | History records contain k_avg, k_opt, H, delta_k, alpha | ✅ 28/28 |

**Conclusion**: Meta control actively monitors and adjusts the system
in all scenarios. The 4th-power update rule provides stability
(small corrections for small deviations) while remaining responsive
(large corrections for large deviations).

---

## Integration: All Features Combined

**What is verified**: All 4 patent features function correctly
when combined in the full management pipeline.

| Test | Description | Result |
|---|---|:---:|
| `test_full_pipeline_runs` | Full pipeline completes without error | ✅ 28/28 |
| `test_full_pipeline_garbage_cleaned` | Garbage removed in full pipeline | ✅ 28/28 |
| `test_full_pipeline_truth_protected` | Truth nodes protected in full pipeline | ✅ 28/28 |
| `test_summary_readable` | Manager summary is human-readable | ✅ 28/28 |

---

## How to Reproduce

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Run full verification suite
pytest tests/test_patent_verification.py -v

# Run all tests (core + patent verification)
pytest tests/ -v

# Run specific patent feature tests
pytest tests/test_patent_verification.py -k "TestMetabolicControl" -v
pytest tests/test_patent_verification.py -k "TestRarityProtection" -v
pytest tests/test_patent_verification.py -k "TestConsistencyDiscovery" -v
pytest tests/test_patent_verification.py -k "TestMetaControl" -v
pytest tests/test_patent_verification.py -k "TestIntegrationAllFeatures" -v
```

---

<a name="日本語版"></a>
## 日本語版

### テスト環境

- **Python**: 3.13.9 / **pytest**: 9.0.2 / **実施日**: 2026-02-28

### テスト結果概要

```
総テスト数: 629 全パス

  コア機能テスト:     69件 (9ファイル)
  特許検証テスト:     560件 (28業界シナリオ × 20テスト)
```

### 検証の妥当範囲（先にお読みください）

**28業界シナリオはすべて合成グラフです。** テスト生成器
[`_build_standard()`](../tests/test_patent_verification.py) は各シナリオを
意図的に以下のように構築している。

- "truth" ノード: 少数の normal ノードに対して **低 weight (0.04–0.10)・低次数** で接続
- "normal" ノード: **高 weight (0.5–1.0)** で密に相互接続
- "garbage" ノード: **完全に孤立した状態** で追加

これは各シナリオが「**構造的稀少性 ≡ 業務上の重要度**」という前提を
構築時に強制していることを意味する。560件の特許検証テストは以下を
立証している。

✅ 構造的稀少性が ground-truth として価値あるノードと一致する場合に、
   本アルゴリズムが構造的に稀少なノードを正しく保護することを示す。

❌ 28業界の実データが実際にこの性質を持つこと、および同業界の実データ
   上で本アルゴリズムがベースライン（Random・TopDegree・density-based
   手法）を上回ることは、本テストでは立証されていない。

姉妹プロジェクト `kdf-perovskite` は同一の理論基盤を多領域の実データ
に適用しており、適性の **決定的予測子 (decisive predictor)** を確立して
いる。すなわち「**構造的稀少性が課題重要度と相関する条件下でのみ**、
本アルゴリズムは決定的にベースラインを上回る」。実データで失敗
することが判明している領域には、scale-free ネットワーク（引用・SNS）、
density-based anomaly detection（金融 fraud）、一般 semantic retrieval、
metadata minority 検出などがある。

28シナリオの率直な分類と実データで判明している適用境界については
[applicability.md](applicability.md) 参照。

下記の特許要素別検証結果（Patent Feature 1–4 と統合）は、**「特許仕様
通りに動作することを構築シナリオ上で確認した」** ものとして読まれるべき
であり、業界横断の実世界 validation ではない。

### 特許要素別の検証結果

#### 代謝制御（請求項1–10）: ✅ 全84テスト合格

| テスト | 検証内容 | 28業界 |
|---|---|:---:|
| ゴミノード除去 | 孤立ノードが代謝制御により除去される | ✅ 28/28 |
| グラフ縮小 | 管理後にグラフサイズが縮小する | ✅ 28/28 |
| 正常ノード生存 | コアデータ構造が過剰に刈り取られない | ✅ 28/28 |

#### 希少性保護（請求項11–20）: ✅ 全112テスト合格

| テスト | 検証内容 | 28業界 |
|---|---|:---:|
| 保護なし→消失 | 保護なしでは希少ノードが消失する | ✅ 28/28 |
| 保護あり→生存 | 保護ありでは希少ノードが生存する | ✅ 28/28 |
| 生存率改善 | 保護により測定可能な改善がある | ✅ 28/28 |
| ゴミは除去継続 | 保護中もゴミノードは正しく除去される | ✅ 28/28 |

**核心的知見**: 全28業界シナリオにおいて、希少性保護なしでは
価値ある希少データが消失し、保護ありでは生存率が改善された。
これは特許の「希少性保護の必要性と有効性」の主張を証明する。

#### 整合性発見（請求項21–26）: ✅ 全112テスト合格

| テスト | 検証内容 | 28業界 |
|---|---|:---:|
| パターン発見 | 構造的類似パターンが発見される | ✅ 28/28 |
| スコア妥当性 | 全スコアが[0,1]範囲内 | ✅ 28/28 |
| ノード実在性 | 発見されたノードがグラフ内に存在する | ✅ 28/28 |
| 閾値遵守 | サンドイッチ閾値[θ_L, θ_U]内 | ✅ 28/28 |

#### メタ制御（請求項27–32）: ✅ 全140テスト合格

| テスト | 検証内容 | 28業界 |
|---|---|:---:|
| 健全性記録 | 全ステップで健全性指標が記録される | ✅ 28/28 |
| 健全性値妥当性 | H値が[0,1]範囲内 | ✅ 28/28 |
| α値範囲 | αが設定範囲[α_min, α_max]内 | ✅ 28/28 |
| α動的調整 | αが初期値から変化する（フィードバック動作） | ✅ 28/28 |
| 履歴キー | 必要な全キー(k_avg, k_opt, H, delta_k, alpha)が含まれる | ✅ 28/28 |

#### 統合テスト（全機能連動）: ✅ 全112テスト合格

| テスト | 検証内容 | 28業界 |
|---|---|:---:|
| 完走 | 全機能ONでエラーなく完走する | ✅ 28/28 |
| ゴミ除去 | 全機能ONでゴミが除去される | ✅ 28/28 |
| 希少保護 | 全機能ONで希少ノードが保護される | ✅ 28/28 |
| サマリー | 管理サマリーが正常に出力される | ✅ 28/28 |

### 結論

**特許の全4要素（代謝制御・希少性保護・整合性発見・メタ制御）が、
全28業界の合成シナリオにおいて仕様通り正しく動作することを、560件の
自動テストで確認した。** これは特許請求項のリファレンス実装としての
正しさを示すものであり、各業界の実データに対する性能保証ではない。
実適用前には [applicability.md](applicability.md) を参照のこと。
