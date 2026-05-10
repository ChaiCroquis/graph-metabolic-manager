# Phase B-1 Preregistration: BattLeDIM L-Town Validation

**Status**: PREREGISTRATION ONLY — no data downloaded, no code written, no result claimed.
**Author**: chai
**Date**: 2026-05-10
**Decision gate**: Implementation requires explicit user go-ahead after this document is reviewed.

[English summary at end](#english-summary)

---

## 1. 目的

`graph-metabolic-manager` の28業界 example はすべて合成データであり
([applicability.md](applicability.md))、実データ validation が無い。
Phase B-1 として **BattLeDIM L-Town(Cyprus 水道網ベンチマーク)**
での validation を着手するか否か、本ドキュメントで事前登録した
仮説・方法・成功/失敗基準に基づいて判断する。

本ドキュメントは **着手前に書く**。実装後に hypothesis を後付けで
narrowing する `post-hoc reframing` を構造的に防ぐ装置である
(kdf-perovskite memory `feedback_post_hoc_narrowing.md` 同等の
姿勢)。

## 2. データセット

| 項目 | 内容 |
|---|---|
| Source | Zenodo record [4017659](https://zenodo.org/records/4017659) (BattLeDIM 2020 L-Town) |
| ライセンス | Open (Zenodo CC) |
| 規模 | ~785 ノード(junction)/ ~905 パイプ(edge)/ 1年分 SCADA |
| Ground truth | 33 leak events、location + start/end time 付き |
| ハッシュ | ダウンロード時に取得して本書を update |

### Graph 変換(事前 commit)

- ノード = junction
- エッジ = pipe
- エッジ weight = **pipe length** を採用(diameter / age など他の選択肢があるが、length が "輸送 capacity と摩擦" の双方を捉える BattLeDIM 慣行に近い)
- 時系列 SCADA データは本 Phase では **使わない**(理由: 後述 §3 framing 制約)

## 3. Framing 制約(honest disclosure)

本アルゴリズムは **静的グラフ構造** に作用する。BattLeDIM の本来の
タスクは **時系列 SCADA からの leak detection** で、これは本アルゴリズム
の設計対象外である。本 Phase B-1 では以下の framing で評価する。

> **本 Phase で評価するもの**: 「static graph structure から、leak event
> が起きた pipe を高 ranking で識別できるか(criticality ranking)」

> **本 Phase で評価しないもの**: 「SCADA 時系列を入力とした real-time
> leak detection」

この区別は report 全体で明示し、「KDF が leak detection で BattLeDIM
benchmark を上回った」のような **誤読を生む書き方は禁止** とする。

## 4. 仮説

### H1(主仮説、事前登録)

> BattLeDIM L-Town の pipe を本アルゴリズムの structural rareness
> score で降順 sort したとき、上位 K 本に **実際に leak が起きた
> 33 本が含まれる割合 (recall@K)** は、以下の baseline を上回る:
> - B0 Random
> - B1 TopDegree(両端ノードの次数の小さい方)
> - B2 TopBetweenness(NetworkX edge betweenness centrality)

### H2(代替仮説、honest disclosure)

> 本アルゴリズムの ranking は betweenness centrality と統計的に区別
> 不能。

H2 が成立した場合、これは **失敗ではなく positioning 制約**:
"deterministic local approximation of betweenness" として定位される
(kdf-perovskite 風に言えば "decisive predictor は満たすが novel
detection ではない")。

### H3(失敗仮説、honest disclosure)

> 本アルゴリズムの ranking は Random と統計的に区別不能。または
> Random / TopDegree / TopBetweenness のいずれにも劣る。

H3 が成立した場合、`applicability.md` の "#25 Water Management →
Plausible" 判定は **撤回** し、F-XXX として水道網 leak ranking 失敗を
documented する(kdf-perovskite F-066 / F-075 と同列の honest negative)。

## 5. 評価プロトコル(事前 commit)

### 5.1 Pre-commit parameters

| 項目 | 値 |
|---|---|
| K(評価点) | 10, 25, 50, 100, 200(5点)|
| Primary metric | recall@K |
| Secondary metric | precision@K, AUC-PR(K-independent)|
| Statistical test | McNemar's exact paired test(algorithm vs 各 baseline)|
| 有意水準 | α = 0.05、Bonferroni correction(3 baseline)|
| seed | 42(全乱数源)|
| Algorithm steps | 100(`examples/01_basic_usage.py` 既定)|
| Algorithm parameters | デフォルト(alpha=2.0, beta, gamma 既定値、`tools` の hyperparameter search は **しない**)|

### 5.2 成功 / 失敗 判定基準

| 結果 | 判定 |
|---|---|
| Algorithm が **全 baseline を K=50 で +5pp 以上**、かつ少なくとも 1 baseline に対し p<0.05/3=0.0167 で有意に勝利 | **H1 採択 = success** |
| Algorithm が betweenness と tied、Random / TopDegree には勝利 | **H2 採択 = qualified success(positioning narrowing)** |
| Algorithm が betweenness と Random の中間、明確な勝者なし | **inconclusive、追加調査検討** |
| Algorithm が Random / TopDegree いずれかに敗北 | **H3 採択 = failure、F-XXX として記録** |

判定は **事前 commit した評価点(K=50)**で行う。事後に "K=N で勝った" と
別の K を採用する **post-hoc K-shopping は禁止**。

### 5.3 Baseline の再現性 commit

- B0 Random: `random.seed(42)` で 30 回試行、平均 ± 標準偏差
- B1 TopDegree: NetworkX `degree()` で deterministic
- B2 TopBetweenness: NetworkX `edge_betweenness_centrality()` で deterministic(ただし計算コスト O(VE)、L-Town 規模なら数秒)

### 5.4 独立検証

実装後、本セッションを終了して **fresh Claude session** を別途起動し
独立検証を依頼する。検証 agent は以下を確認する:

1. データハッシュが本書と一致するか
2. Graph 変換コードが §2 の commit と一致するか
3. 評価コードが §5.1-5.2 と一致するか(K, metric, test, α)
4. 結果数値の再現(seed 固定で複数回実行 → bit-exact 一致)
5. 上記から導かれる verdict が本書の判定基準を **後から書き換えていない** か

検証 agent の verdict は PASS / PASS_WITH_NOTES / FAIL のみ。
PASS_WITH_NOTES の場合、修正後に再検証。FAIL は実装やり直し。

### 5.5 報告 commit

- 結果は新規 `docs/VERIFIED_FINDINGS.md` の **F-001** として記録
- 結果が H1 / H2 / H3 のいずれであっても **同等の prominence で記録**
- `docs/applicability.md` の "#25 Water Management" 行を結果に応じて
  Plausible → Validated / Plausible → Falsified / Plausible のまま
  に更新(後二者は applicability 修正)
- `docs/sync_with_kdf_perovskite.md` の sync log に新 F-001 を登録
- README の "Verified on synthetic scenarios" 表記を「+ 1 real-world
  validation」に拡張するかは結果に応じて別判断(本書では commit しない)

## 6. Decision gate(実装着手前のチェックリスト)

実装着手は以下が **すべて Yes** のときのみ:

- [ ] hypothesis H1 が "ほぼ自明に通る" 設定になっていないか確認
      (= falsifiable か。例: K=200 で recall@K=1.0 になる設定では
      意味がない)
- [ ] BattLeDIM データを実際にダウンロードしてハッシュを記録できるか
- [ ] BattLeDIM benchmark の上位手法を baseline panel に含めるか:
      - **含める** = B3 として追加(例: 2020 winner の Vrachimis et al.)
      - **含めない** = "kdf-perovskite では BattLeDIM 上位手法と比較して
        いない" を applicability に明記
- [ ] User が implementation start を **明示的に承認** している
- [ ] 想定 work 量(3週間)を捻出できる scheduling

いずれかが No なら本書は shelved。プロジェクトは "honest synthetic-
only" の状態を維持する(`/contract` の高リスク規律は満たされて
いないので start しない)。

## 7. 本 Phase で行わないこと(scope clamp)

- PowerGraph(B-2)など他 dataset への展開
- アルゴリズム本体の修正・拡張
- Heterogeneous graph 拡張
- Hyperparameter search
- 時系列 SCADA を使った leak detection(framing 外)

これらが Phase B-1 の結果を見て必要になった場合、**別 preregistration
を書く**(本書を修正しない)。

## 8. リスク

| リスク | 内容 | 緩和 |
|---|---|---|
| Single-graph generalization | L-Town は1ネットワーク。"水道網一般" は主張不能 | "L-Town に限定した validation である" を結果報告で明示。B-2 で異 dataset replication 必須 |
| Ground-truth ラベルの偏り | 33 leak は L-Town の特定 sub-region に clustered している可能性 | データ取得後、leak の地理的分布を確認し報告に含める |
| BattLeDIM benchmark との比較公正性 | ベンチマーク手法は SCADA 入力前提、本アルゴリズムは静的 | §3 で framing 区別を明示済。比較は "同じ static problem 上での criticality ranking" として位置付け |
| 実装規模 | 3週間で予期せぬ pitfall | Decision gate で work 量を判定 |

## 9. 受領

本 preregistration は user が `c` (preregistration only)を選択した結果。
**本書を書いた段階では着手の決定は行われていない**。実装着手は §6 の
全項目を満たした上で別途 commit が必要。

---

<a name="english-summary"></a>
## English summary

This document **preregisters** the protocol for a possible Phase B-1
real-data validation of `graph-metabolic-manager` on the BattLeDIM
L-Town water-distribution-network benchmark. It does NOT commit to
running the validation; it commits to *how* the validation will be
run *if* it is run.

**Hypothesis H1** (primary): The algorithm's structural-rareness pipe
ranking achieves higher recall@K than Random, TopDegree, and
TopBetweenness baselines (K ∈ {10, 25, 50, 100, 200}, primary K=50,
+5pp threshold, McNemar p<0.0167 with Bonferroni correction).

**Hypothesis H2** (honest qualified-success): The algorithm ties with
betweenness centrality. This is not failure but positions the
algorithm as "deterministic local approximation of betweenness"
rather than novel detection.

**Hypothesis H3** (honest failure): The algorithm loses to Random or
TopDegree. This would falsify the "#25 Water Management → Plausible"
classification in `applicability.md` and be recorded as F-001 negative.

**Framing constraint**: This evaluates static criticality ranking,
NOT real-time SCADA-based leak detection. The latter is outside the
algorithm's design and out of scope.

**Pre-committed parameters**: seed=42, default algorithm params, no
hyperparameter search, K-shopping forbidden, independent verification
agent required, results published regardless of outcome.

**Decision gate** (§6): Implementation only proceeds if the user
explicitly approves AND the work commitment (~3 weeks) is feasible
AND the hypothesis is judged falsifiable AND BattLeDIM data hashes
can be recorded. Otherwise this document is shelved and the project
remains honestly "synthetic-only verified".
