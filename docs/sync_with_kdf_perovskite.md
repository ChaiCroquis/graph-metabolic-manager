# Synchronization with `kdf-perovskite` / `kdf-perovskite` との同期

This document defines how this project's applicability claims stay
synchronized with the empirical findings of the sister project
`kdf-perovskite`, which shares the same theoretical foundation.

[日本語版はこちら](#日本語版)

---

## Why this exists

`graph-metabolic-manager` and `kdf-perovskite` implement the same core
theory in different languages and packaging:

| | `graph-metabolic-manager` | `kdf-perovskite` |
|---|---|---|
| Primary role | Reference implementation of the patent + 28-industry illustrations | Empirical validation of the theory on real datasets |
| Language | Python 3.10+ | Rust + Python bindings |
| Public-facing | Yes (PyPI / Streamlit / GitHub) | Internal / research-grade |
| Verification depth | Synthetic scenarios (629 tests) | F-001..F-086+ on real data |

A finding made in `kdf-perovskite` (e.g. "the algorithm fails on
scale-free citation graphs at recall 0%") directly affects what
`graph-metabolic-manager` may honestly claim about its 28 industry
examples. Without an explicit sync process, the two projects drift:
a `kdf-perovskite` retraction (e.g. F-044 → F-053) does not
automatically propagate, and a public-facing overclaim is the most
likely failure mode.

This document is the sync contract.

## Invariant

**Every time `docs/applicability.md` makes an empirical claim about
real-world applicability, it must cite the supporting
`kdf-perovskite` finding ID (`F-XXX`) inline.**

If a claim cannot be traced to a specific `F-XXX`, it is either
removed or relabeled as "未検証 / Unverified".

## Currently load-bearing `kdf-perovskite` findings

These are the `F-XXX` IDs that `docs/applicability.md` currently
depends on. If any of these is **retracted, narrowed, or replaced**
in `kdf-perovskite`, the corresponding line in `applicability.md`
must be updated.

### Findings supporting "where the algorithm works"

| ID | Topic | Used in `applicability.md` for |
|---|---|---|
| F-057 | LoCoMo temporal n=321, +10.6 pt p=0.0014 | Long-conversation date/time recall |
| F-058 | LoCoMo temporal × gpt-4.1-mini, +23.4 pt p=1.6×10⁻¹⁴ | Long-conversation date/time recall (model robustness) |
| F-061 | Classical algorithm revival — non-scale-free wins | Path-critical bottleneck on non-scale-free graphs |
| F-062 | B1 git commit pruning — merge 99.5% / tag 42% retained | Git archival when merge rate < 10% |
| F-065 | B1 cross-repo replication, 3 repos +25..+71pt | Git archival generality |
| F-068 | Analogy discovery 90% + negative control reject | Orphan-node detection |
| F-076 | Phase 2.5 git archival 4 repo expansion, merge-rate threshold confirmed | Git archival, merge-rate predictor |

### Findings supporting "where the algorithm does NOT work"

| ID | Topic | Used in `applicability.md` for |
|---|---|---|
| F-045 | BEIR SciFact recall 0.000 | General semantic retrieval failure |
| F-047 | PKM Welsh cultural minority — KDF below Random | Metadata-minority semantic detection failure |
| F-053 | Real KDF rerun, LongMemEval −23.8pt vs Mem0 (retracts F-044/F-049/F-050) | Long-conversation general QA, Mem0 not replaceable |
| F-054 | Real KDF @50% keep_rate, gap narrows but persists | Mem0-replacement narrative confirmed unrescued |
| F-055 | KDF+Mem0 hybrid tied with Mem0 alone | Hybrid does not rescue KDF on general QA |
| F-056 | LoCoMo narrative reasoning −24pt | Narrative reasoning failure |
| F-061 | Scale-free (BA, WS) — TopDegree wins | Scale-free social/citation network failure |
| F-063 | C5 GP inducing points — KDF doesn't help | Density-based failure (GP) |
| F-066 | B4 financial fraud archival — feature-space anomaly | Density-based failure (financial) |
| F-067 | C4 kernel SVM subset — Random tie, KMeans slight loss | Density-based failure (kernel SVM) |
| F-075 | Citation interdisciplinary bridge recall 0%, 3/3 LOSS | Citation network failure |

## Review process

### Trigger

A review is triggered whenever any of the following happens:

1. **Event-driven**: A new `F-XXX` is added to
   `kdf-perovskite/docs/VERIFIED_FINDINGS.md`, or an existing one is
   marked retracted (🚨), narrowed, or reclassified.
2. **Periodic**: Monthly, regardless of events. Read the latest
   `VERIFIED_FINDINGS.md` and check for changes since the last review.
3. **Pre-release**: Before any tagged release of
   `graph-metabolic-manager`, run the full review.

### Action

For each `F-XXX` listed in this document:

1. Open `kdf-perovskite/docs/VERIFIED_FINDINGS.md` and locate the
   finding by ID.
2. Verify that the title / verdict / sign of the result has not
   changed.
3. If the finding is retracted, narrowed, or replaced:
   - Find every line in `docs/applicability.md` that cites that ID.
   - Update the corresponding claim, OR replace the citation with
     the new ID, OR demote the claim to "Unverified".
4. If a *new* `F-XXX` introduces a domain not currently covered:
   - Decide whether it affects any of the 28 industry classifications
     in `applicability.md` §5.
   - If yes, update the table and add the new ID to this document's
     "Currently load-bearing" tables.

### Output

Each review produces a 1-line entry in the "Sync log" section below
(append-only). Empty reviews ("no change") still produce an entry.

## Sync log (append-only)

| Date | Reviewer | kdf-perovskite commit | Changes |
|---|---|---|---|
| 2026-05-10 | chai + Claude (initial setup) | 8dc6cd5ab268d0e0624faeb76c11bd836332e3a2 | Initial registration of F-045, F-047, F-053..F-058, F-061..F-068, F-075, F-076 as load-bearing |

## What this document does NOT do

- It does not validate `kdf-perovskite`'s findings — it trusts them as
  upstream truth (subject to that project's own verification).
- It does not automate the diff — the review is a human/Claude session
  task, not a CI check (a script could be added later if drift becomes
  frequent).
- It does not cover `kdf-perovskite` Layer B (genesis / cognitive-
  formalization) material — that is Vault-managed and out of scope
  for this Layer A repository.

---

<a name="日本語版"></a>
## 日本語版

本ドキュメントは、本プロジェクトの適用可能性に関する主張を、
同一の理論基盤を持つ姉妹プロジェクト `kdf-perovskite` の実データ
検証結果と同期させるための契約を定義する。

### なぜ必要か

`graph-metabolic-manager` と `kdf-perovskite` は同一のコア理論を
異なる言語・パッケージで実装している。

| | `graph-metabolic-manager` | `kdf-perovskite` |
|---|---|---|
| 主目的 | 特許のリファレンス実装 + 28業界 illustration | 理論を実データで実証 |
| 言語 | Python 3.10+ | Rust + Python bindings |
| 公開 | あり (PyPI / Streamlit / GitHub) | 内部 / research-grade |
| 検証深度 | 合成シナリオ (629テスト) | 実データで F-001..F-086+ |

`kdf-perovskite` で得られた知見（例: 「scale-free な引用グラフで
recall 0% で失敗」）は、`graph-metabolic-manager` が28業界の
example について率直に主張できる範囲に直接影響する。明示的な同期
プロセスがなければ二プロジェクトは drift し、`kdf-perovskite` 側の
撤回（例: F-044 → F-053）が伝搬せず、公開向けドキュメントの過剰
主張が発生する。本ドキュメントはその同期契約である。

### 不変条件

**`docs/applicability.md` が実世界適用性に関する empirical な主張を
する箇所は必ず、根拠となる `kdf-perovskite` 知見 ID (`F-XXX`) を
インラインで引用すること。**

特定の `F-XXX` に traceable でない主張は、削除するか「未検証 /
Unverified」に格下げする。

### 現在 load-bearing な `kdf-perovskite` 知見

`docs/applicability.md` が現状依存している `F-XXX` ID の一覧。
いずれかが `kdf-perovskite` で **撤回・narrowing・置換** された場合、
`applicability.md` の対応行を更新する必要がある。

#### 「有効な領域」を支持する知見

| ID | 内容 | `applicability.md` での用途 |
|---|---|---|
| F-057 | LoCoMo temporal n=321, +10.6 pt p=0.0014 | 長期会話の日時想起 |
| F-058 | LoCoMo temporal × gpt-4.1-mini, +23.4 pt p=1.6×10⁻¹⁴ | 日時想起の model robustness |
| F-061 | 古典 algorithm revival — non-scale-free で勝利 | non-scale-free graph での path-critical bottleneck |
| F-062 | B1 git commit pruning — merge 99.5% / tag 42% 保持 | merge rate <10% の git archival |
| F-065 | B1 cross-repo replication, 3 repo +25..+71pt | git archival の汎化 |
| F-068 | Analogy discovery 90% + negative control reject | 孤立ノード検出 |
| F-076 | Phase 2.5 git archival 4 repo 拡張、merge-rate threshold 確認 | git archival、merge-rate 予測子 |

#### 「適用困難な領域」を支持する知見

| ID | 内容 | `applicability.md` での用途 |
|---|---|---|
| F-045 | BEIR SciFact recall 0.000 | 一般 semantic retrieval 失敗 |
| F-047 | PKM Welsh cultural minority — KDF が Random 以下 | metadata minority semantic 検出失敗 |
| F-053 | Real KDF rerun, LongMemEval −23.8pt vs Mem0 (F-044/F-049/F-050 撤回) | 長期会話汎用 QA、Mem0 置換不可 |
| F-054 | Real KDF @50% keep_rate, gap 縮小も解消せず | Mem0 代替の narrative 再確認 |
| F-055 | KDF+Mem0 hybrid が Mem0 単独と同等 | hybrid でも一般 QA で KDF を救えない |
| F-056 | LoCoMo narrative reasoning −24pt | narrative reasoning 失敗 |
| F-061 | scale-free (BA, WS) — TopDegree が勝利 | scale-free 社会/引用ネットワーク失敗 |
| F-063 | C5 GP inducing points — KDF 機能せず | density-based 失敗 (GP) |
| F-066 | B4 金融 fraud archival — 特徴空間 anomaly | density-based 失敗 (金融) |
| F-067 | C4 kernel SVM subset — Random と tie、KMeans 微敗 | density-based 失敗 (kernel SVM) |
| F-075 | 引用 interdisciplinary bridge recall 0%, 3/3 LOSS | 引用ネットワーク失敗 |

### Review プロセス

#### トリガ

以下いずれかの場合に review を起動する。

1. **イベント駆動**: `kdf-perovskite/docs/VERIFIED_FINDINGS.md` に
   新規 `F-XXX` が追加されたとき、または既存知見が撤回 (🚨) /
   narrowing / 再分類されたとき
2. **周期**: 月次。イベントの有無に関わらず最新の
   `VERIFIED_FINDINGS.md` を読み、前回 review 以降の変更を確認
3. **リリース前**: `graph-metabolic-manager` の tag リリース前に
   完全 review を1回実施

#### アクション

本ドキュメントに掲載された各 `F-XXX` について以下を行う。

1. `kdf-perovskite/docs/VERIFIED_FINDINGS.md` で該当 ID を確認
2. タイトル / verdict / 結果の符号が変わっていないかを確認
3. 撤回・narrowing・置換されていた場合:
   - `docs/applicability.md` で該当 ID を引用している行を全て検索
   - 主張を更新する、新 ID で引用を差し替える、または「Unverified」に格下げ
4. *新規* `F-XXX` が現在カバーしていないドメインに該当する場合:
   - `applicability.md` §5 の28業界分類に影響するか判定
   - 影響あれば表を更新し、本ドキュメントの "Currently load-bearing"
     表に新 ID を追加

#### 出力

各 review は下記「Sync log」セクションに1行追記する（append-only）。
変更なしの review でも1行追記する。

### Sync log (append-only)

| 日付 | レビュアー | kdf-perovskite commit | 変更内容 |
|---|---|---|---|
| 2026-05-10 | chai + Claude (initial setup) | 8dc6cd5ab268d0e0624faeb76c11bd836332e3a2 | F-045, F-047, F-053..F-058, F-061..F-068, F-075, F-076 を load-bearing として初回登録 |

### 本ドキュメントが行わないこと

- `kdf-perovskite` の知見そのものを validate する責任は持たない（同
  プロジェクトの検証プロセスに従う）
- diff の自動化は行わない（人間 / Claude セッションでの review が前
  提。drift が頻発するようなら後日スクリプト化を検討）
- `kdf-perovskite` の Layer B（genesis / 認知形式化）材料は対象外。
  本リポジトリは Layer A のみを管理する
