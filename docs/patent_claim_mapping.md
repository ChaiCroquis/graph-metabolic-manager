# Patent Claim Mapping / 特許請求項マッピング

This document maps each example to the patent claims it demonstrates,
and traces each patent feature to its implementation in code.

[日本語版はこちら](#日本語版)

---

## Patent Information

- **Application No.**: 2026-027032 (Japan)
- **Title**: Data Structure Management System Using Rarity Protection and Consistency Discovery
- **Title (JP)**: 希少性保護及び整合性発見を用いたデータ構造管理システム
- **Claims**: 50 claims (48 system + 1 method + 1 program)

---

## Feature → Code Mapping

### Feature 1: Metabolic Control (Claims 1–10)

| Claim | Description | Code |
|:---:|---|---|
| 1 | Congestion-based decay rate λ(C) = β×(1+γ×C^α) | `metabolic.py` → `decay_rate()` |
| 2 | Exponential weight update w ← w×exp(−λ×dt) | `metabolic.py` → `update_weight()` |
| 3 | Local congestion C = deg(u) + deg(v) | `graph.py` → `local_congestion()` |
| 4 | Pruning when weight < threshold | `metabolic.py` → `MetabolicControl.step()` |
| 5–10 | Parameter configurations and variants | `metabolic.py` → constructor params |

### Feature 2: Rarity Protection (Claims 11–20)

| Claim | Description | Code |
|:---:|---|---|
| 11 | Identify rare nodes (low degree + truth type) | `rarity.py` → `identify_rare()` |
| 12 | Phase 1: Unconditional grace period (Twait1) | `rarity.py` → `enter_protection()` |
| 13 | Phase 2: Conditional observation (Twait2) | `rarity.py` → `update_phases()` |
| 14 | Protection set excludes nodes from pruning | `manager.py` → `step()` L158 |
| 15–20 | Phase transitions and removal criteria | `rarity.py` → `update_phases()` |

### Feature 3: Consistency Discovery (Claims 21–26)

| Claim | Description | Code |
|:---:|---|---|
| 21 | k-hop subgraph extraction | `consistency.py` → `_get_repr()` |
| 22 | Laplacian eigenvalue spectrum computation | `consistency.py` → `compute_structural_repr()` |
| 23 | Composite score S = 7×S_sys + 2×S_rel + 1×S_attr | `consistency.py` → `consistency_score()` |
| 24 | Sandwich threshold θ_L ≤ S ≤ θ_U | `consistency.py` → `discover()` |
| 25–26 | Edge creation for discovered relationships | `manager.py` → `step()` L144–148 |

### Feature 4: Meta Control (Claims 27–32)

| Claim | Description | Code |
|:---:|---|---|
| 27 | Health index H = 1 − |kAvg − kOpt| / kOpt | `meta_control.py` → `health_index()` |
| 28 | Update amount Δ = η × δk^n (n=4) | `meta_control.py` → `meta_update_amount()` |
| 29 | Alpha adjustment based on health vs target | `meta_control.py` → `MetaControl.step()` |
| 30 | Alpha bounded within [α_min, α_max] | `meta_control.py` → `step()` L159 |
| 31–32 | History recording and convergence | `meta_control.py` → `self.history` |

---

## Example → Patent Feature Matrix

✅ = Feature actively demonstrated with domain-specific meaning
○ = Feature enabled but not the primary focus

| # | Example | Industry | MC | RP | CD | Meta |
|:---:|---|---|:---:|:---:|:---:|:---:|
| 01 | Basic Usage | General | ✅ | ✅ | — | ○ |
| 02 | EC Recommendation | E-Commerce | ✅ | ✅ | — | ○ |
| 03 | Knowledge Base | Enterprise IT | ✅ | ✅ | ✅ | ○ |
| 04 | Medical Knowledge | Healthcare | ✅ | ✅ | ✅ | ○ |
| 05 | Financial Network | Finance | ✅ | ✅ | ✅ | ○ |
| 06 | IoT Manufacturing | Manufacturing | ✅ | ✅ | ✅ | ○ |
| 07 | Telecom Network | Telecommunications | ✅ | ✅ | ✅ | ○ |
| 08 | Cybersecurity | Security | ✅ | ✅ | ✅ | ○ |
| 09 | Supply Chain | Logistics | ✅ | ✅ | ✅ | ○ |
| 10 | Education Curriculum | Education | ✅ | ✅ | ✅ | ○ |
| 11 | Smart Grid | Energy | ✅ | ✅ | ✅ | ○ |
| 12 | Academic Citation | Research | ✅ | ✅ | ✅ | ○ |
| 13 | Agriculture Food Safety | Agriculture | ✅ | ✅ | ✅ | ○ |
| 14 | Legal Compliance | Legal | ✅ | ✅ | ✅ | ○ |
| 15 | HR Talent | Human Resources | ✅ | ✅ | ✅ | ○ |
| 16 | Real Estate | Real Estate | ✅ | ✅ | ✅ | ○ |
| 17 | Insurance Actuarial | Insurance | ✅ | ✅ | ✅ | ○ |
| 18 | Environmental Monitoring | Environmental | ✅ | ✅ | ✅ | ○ |
| 19 | Transportation | Transportation | ✅ | ✅ | ✅ | ○ |
| 20 | Social Network | Social Media | ✅ | ✅ | ✅ | ○ |
| 21 | Gaming | Gaming | ✅ | ✅ | ✅ | ○ |
| 22 | Media Advertising | Media | ✅ | ✅ | ✅ | ○ |
| 23 | Aviation | Aerospace | ✅ | ✅ | ✅ | ○ |
| 24 | Pharma Manufacturing | Pharmaceutical | ✅ | ✅ | ✅ | ○ |
| 25 | Water Management | Water/Utilities | ✅ | ✅ | ✅ | ○ |
| 26 | Construction | Construction | ✅ | ✅ | ✅ | ○ |
| 27 | Mining | Mining | ✅ | ✅ | ✅ | ○ |
| 28 | Hospitality | Hospitality | ✅ | ✅ | ✅ | ○ |

---

## Example → Claim Detail Mapping

### Example 01: Basic Usage

| Patent Feature | What it demonstrates |
|---|---|
| Metabolic Control (Cl.1–4) | Noise nodes pruned by congestion-based decay |
| Rarity Protection (Cl.11–14) | "RareGem" node survives despite 1 weak connection |

### Example 02: EC Recommendation

| Patent Feature | What it demonstrates |
|---|---|
| Metabolic Control (Cl.1–4) | Seasonal products pruned from recommendation graph |
| Rarity Protection (Cl.11–14) | Niche products preserved for specific customer segments |

### Example 03: Knowledge Base

| Patent Feature | What it demonstrates |
|---|---|
| Metabolic Control (Cl.1–4) | Obsolete documents removed from knowledge graph |
| Rarity Protection (Cl.11–14) | Legacy documents preserved despite rare access |
| Consistency Discovery (Cl.21–24) | Hidden cross-department document relationships found |

### Example 04: Medical Knowledge

| Patent Feature | What it demonstrates |
|---|---|
| Metabolic Control (Cl.1–4) | Deprecated drug candidates removed |
| Rarity Protection (Cl.11–14) | Orphan disease data preserved for research |
| Consistency Discovery (Cl.21–24) | Drug repurposing candidates identified via structural similarity |

### Example 05: Financial Network

| Patent Feature | What it demonstrates |
|---|---|
| Metabolic Control (Cl.1–4) | Dormant accounts archived |
| Rarity Protection (Cl.11–14) | Fraud signals preserved (shell companies, anomalous patterns) |
| Consistency Discovery (Cl.21–24) | Hidden links between suspicious and normal entities |

### Example 06: IoT Manufacturing

| Patent Feature | What it demonstrates |
|---|---|
| Metabolic Control (Cl.1–4) | Obsolete sensor data from decommissioned equipment removed |
| Rarity Protection (Cl.11–14) | Rare anomaly patterns (equipment failure precursors) preserved |
| Consistency Discovery (Cl.21–24) | Cross-equipment failure pattern discovery for predictive maintenance |

### Example 07: Telecom Network

| Patent Feature | What it demonstrates |
|---|---|
| Metabolic Control (Cl.1–4) | Legacy equipment nodes removed from network topology |
| Rarity Protection (Cl.11–14) | Backup relay routes preserved as failover paths |
| Consistency Discovery (Cl.21–24) | Structurally similar network segments identified |

### Example 08: Cybersecurity

| Patent Feature | What it demonstrates |
|---|---|
| Metabolic Control (Cl.1–4) | Stale/expired threat indicators cleaned up |
| Rarity Protection (Cl.11–14) | APT signals preserved despite minimal footprint |
| Consistency Discovery (Cl.21–24) | Hidden attack campaign connections revealed |

### Example 09: Supply Chain

| Patent Feature | What it demonstrates |
|---|---|
| Metabolic Control (Cl.1–4) | Defunct supplier records removed |
| Rarity Protection (Cl.11–14) | Sole-source critical suppliers preserved |
| Consistency Discovery (Cl.21–24) | Suppliers with similar vulnerability profiles identified |

### Example 10: Education Curriculum

| Patent Feature | What it demonstrates |
|---|---|
| Metabolic Control (Cl.1–4) | Discontinued courses removed from curriculum graph |
| Rarity Protection (Cl.11–14) | Interdisciplinary courses preserved |
| Consistency Discovery (Cl.21–24) | Courses with similar prerequisite structures found |

### Example 11: Smart Grid

| Patent Feature | What it demonstrates |
|---|---|
| Metabolic Control (Cl.1–4) | Decommissioned monitoring points removed |
| Rarity Protection (Cl.11–14) | Cascade failure precursor records preserved |
| Consistency Discovery (Cl.21–24) | Grid zones with similar vulnerability profiles identified |

### Example 12: Academic Citation

| Patent Feature | What it demonstrates |
|---|---|
| Metabolic Control (Cl.1–4) | Retracted/superseded papers removed from citation network |
| Rarity Protection (Cl.11–14) | Interdisciplinary field-bridging papers preserved |
| Consistency Discovery (Cl.21–24) | Hidden thematic connections across research fields |

### Example 13: Agriculture Food Safety

| Patent Feature | What it demonstrates |
|---|---|
| Metabolic Control (Cl.1–4) | Expired certifications and recalled batches removed |
| Rarity Protection (Cl.11–14) | Rare pest/disease trace signals preserved |
| Consistency Discovery (Cl.21–24) | Cross-region contamination risk patterns identified |

### Example 14: Legal Compliance

| Patent Feature | What it demonstrates |
|---|---|
| Metabolic Control (Cl.1–4) | Expired regulations and superseded statutes removed |
| Rarity Protection (Cl.11–14) | Rare cross-domain legal precedents preserved |
| Consistency Discovery (Cl.21–24) | Cross-domain legal principle connections found |

### Example 15: HR Talent

| Patent Feature | What it demonstrates |
|---|---|
| Metabolic Control (Cl.1–4) | Resigned employees and closed positions removed |
| Rarity Protection (Cl.11–14) | Rare cross-domain skill combinations preserved |
| Consistency Discovery (Cl.21–24) | Cross-department talent similarity patterns found |

### Example 16: Real Estate

| Patent Feature | What it demonstrates |
|---|---|
| Metabolic Control (Cl.1–4) | Sold/expired listings and demolished properties removed |
| Rarity Protection (Cl.11–14) | Rare unique property features preserved |
| Consistency Discovery (Cl.21–24) | Cross-zone structural similarity patterns found |

### Example 17: Insurance Actuarial

| Patent Feature | What it demonstrates |
|---|---|
| Metabolic Control (Cl.1–4) | Expired policies and settled claims removed |
| Rarity Protection (Cl.11–14) | Rare claim patterns preserved for risk modeling |
| Consistency Discovery (Cl.21–24) | Cross-product risk correlation patterns found |

### Example 18: Environmental Monitoring

| Patent Feature | What it demonstrates |
|---|---|
| Metabolic Control (Cl.1–4) | Decommissioned monitoring stations removed |
| Rarity Protection (Cl.11–14) | Rare species sightings and pollution patterns preserved |
| Consistency Discovery (Cl.21–24) | Cross-ecosystem structural similarity patterns found |

### Example 19: Transportation

| Patent Feature | What it demonstrates |
|---|---|
| Metabolic Control (Cl.1–4) | Defunct routes and closed facilities removed |
| Rarity Protection (Cl.11–14) | Rare bottleneck and alternative route signals preserved |
| Consistency Discovery (Cl.21–24) | Facilities with similar logistics vulnerability profiles identified |

### Example 20: Social Network

| Patent Feature | What it demonstrates |
|---|---|
| Metabolic Control (Cl.1–4) | Inactive/abandoned accounts removed |
| Rarity Protection (Cl.11–14) | Rare bridge users connecting distant communities preserved |
| Consistency Discovery (Cl.21–24) | Users with similar cross-community bridging profiles identified |

### Example 21: Gaming

| Patent Feature | What it demonstrates |
|---|---|
| Metabolic Control (Cl.1–4) | Banned/deleted accounts removed |
| Rarity Protection (Cl.11–14) | Rare cheat/exploit pattern signals preserved |
| Consistency Discovery (Cl.21–24) | Players with similar anomalous behavior profiles identified |

### Example 22: Media Advertising

| Patent Feature | What it demonstrates |
|---|---|
| Metabolic Control (Cl.1–4) | Discontinued campaigns and expired ad placements removed |
| Rarity Protection (Cl.11–14) | Rare emerging trend signals preserved |
| Consistency Discovery (Cl.21–24) | Media outlets with similar audience structure identified |

### Example 23: Aviation

| Patent Feature | What it demonstrates |
|---|---|
| Metabolic Control (Cl.1–4) | Retired/decommissioned components removed |
| Rarity Protection (Cl.11–14) | Rare fatigue crack propagation patterns preserved |
| Consistency Discovery (Cl.21–24) | Components with similar stress/failure profiles identified |

### Example 24: Pharma Manufacturing

| Patent Feature | What it demonstrates |
|---|---|
| Metabolic Control (Cl.1–4) | Expired batches and recalled products removed |
| Rarity Protection (Cl.11–14) | Rare contamination trace patterns preserved |
| Consistency Discovery (Cl.21–24) | Facilities with similar contamination risk profiles identified |

### Example 25: Water Management

| Patent Feature | What it demonstrates |
|---|---|
| Metabolic Control (Cl.1–4) | Decommissioned/replaced infrastructure assets removed |
| Rarity Protection (Cl.11–14) | Rare water quality anomaly signals preserved |
| Consistency Discovery (Cl.21–24) | Infrastructure assets with similar vulnerability profiles identified |

### Example 26: Construction

| Patent Feature | What it demonstrates |
|---|---|
| Metabolic Control (Cl.1–4) | Completed/demolished project records removed |
| Rarity Protection (Cl.11–14) | Rare structural defect pattern signals preserved |
| Consistency Discovery (Cl.21–24) | Building systems with similar defect risk profiles identified |

### Example 27: Mining

| Patent Feature | What it demonstrates |
|---|---|
| Metabolic Control (Cl.1–4) | Exhausted/closed mining operations removed |
| Rarity Protection (Cl.11–14) | Rare geological anomaly and safety signals preserved |
| Consistency Discovery (Cl.21–24) | Operations with similar geological risk profiles identified |

### Example 28: Hospitality

| Patent Feature | What it demonstrates |
|---|---|
| Metabolic Control (Cl.1–4) | Closed/defunct venues removed |
| Rarity Protection (Cl.11–14) | Rare demand pattern and cultural shift signals preserved |
| Consistency Discovery (Cl.21–24) | Venues with similar demand structure profiles identified |

---

<a name="日本語版"></a>
## 日本語版

### 特許情報

- **出願番号**: 特願2026-027032
- **発明の名称**: 希少性保護及び整合性発見を用いたデータ構造管理システム
- **請求項数**: 50項（システム48 + 方法1 + プログラム1）

### 特許要素 → コード対応表

| 特許要素 | 請求項 | 実装ファイル | 主要関数 |
|---|:---:|---|---|
| 代謝制御 | 1–10 | `metabolic.py` | `decay_rate()`, `update_weight()`, `MetabolicControl.step()` |
| 希少性保護 | 11–20 | `rarity.py` | `identify_rare()`, `enter_protection()`, `update_phases()` |
| 整合性発見 | 21–26 | `consistency.py` | `compute_structural_repr()`, `consistency_score()`, `discover()` |
| メタ制御 | 27–32 | `meta_control.py` | `health_index()`, `meta_update_amount()`, `MetaControl.step()` |

### サンプル → 特許要素 対応表

| # | 業界 | 代謝制御の意味 | 希少性保護の意味 | 整合性発見の意味 |
|:---:|---|---|---|---|
| 01 | 汎用 | ノイズノードの除去 | 希少ノードの生存 | — |
| 02 | EC/推薦 | 季節商品の整理 | ニッチ商品の保護 | — |
| 03 | ナレッジ管理 | 陳腐化文書の除去 | レガシー文書の保護 | 部門間の隠れた関連発見 |
| 04 | 医療/創薬 | 廃止薬候補の除去 | 希少疾患データの保護 | 薬剤リポジショニング候補の発見 |
| 05 | 金融/不正検知 | 休眠口座の整理 | 不正信号の保護 | 疑わしいエンティティの隠れた関連 |
| 06 | IoT/製造 | 廃棄センサーデータの除去 | 設備異常前兆の保護 | 設備間の異常パターン横展開 |
| 07 | 通信 | レガシー機器の除去 | バックアップ経路の保護 | 類似ネットワーク構造の発見 |
| 08 | サイバーセキュリティ | 期限切れ指標の除去 | APT信号の保護 | 攻撃キャンペーンの隠れた関連 |
| 09 | サプライチェーン | 取引停止先の除去 | 唯一供給元の保護 | 類似脆弱構造の発見 |
| 10 | 教育 | 廃止科目の除去 | 学際科目の保護 | 類似カリキュラム構造の発見 |
| 11 | エネルギー | 廃止計測点の除去 | カスケード障害前兆の保護 | 類似脆弱ゾーンの発見 |
| 12 | 学術 | 撤回論文の除去 | 学際論文の保護 | 分野横断テーマの発見 |
| 13 | 農業/食品安全 | 期限切れ認証の除去 | 病害虫痕跡シグナルの保護 | 地域間の汚染リスク類似構造発見 |
| 14 | 法務/コンプライアンス | 失効規制の除去 | 希少判例の保護 | 分野横断の法的原則発見 |
| 15 | HR/人材 | 退職者データの除去 | 希少スキル組合せの保護 | 部門間の人材類似性発見 |
| 16 | 不動産/都市計画 | 成約済みデータの除去 | 希少な物件特性の保護 | エリア間の構造類似発見 |
| 17 | 保険/アクチュアリー | 期限切れ契約の除去 | 希少な請求パターンの保護 | 商品間のリスク相関発見 |
| 18 | 環境モニタリング | 廃止観測点の除去 | 希少種・汚染パターンの保護 | 生態系間の類似構造発見 |
| 19 | 運輸/物流 | 廃止路線の除去 | ボトルネック信号の保護 | 類似脆弱構造の発見 |
| 20 | ソーシャルネットワーク | 非活性アカウントの除去 | ブリッジユーザーの保護 | コミュニティ間の類似構造発見 |
| 21 | オンラインゲーム | BANアカウントの除去 | チート信号の保護 | 類似異常行動パターンの発見 |
| 22 | メディア/広告 | 廃止キャンペーンの除去 | トレンド信号の保護 | 類似オーディエンス構造の発見 |
| 23 | 航空/宇宙 | 退役部品の除去 | 疲労亀裂信号の保護 | 類似応力プロファイルの発見 |
| 24 | 製薬製造 | 期限切れバッチの除去 | 汚染痕跡信号の保護 | 類似汚染リスク構造の発見 |
| 25 | 水道/下水 | 廃止設備の除去 | 水質異常信号の保護 | 類似インフラ脆弱性の発見 |
| 26 | 建設/インフラ | 解体物件の除去 | 構造欠陥信号の保護 | 類似欠陥リスク構造の発見 |
| 27 | 鉱業/資源 | 枯渇サイトの除去 | 地質異常信号の保護 | 類似地質リスク構造の発見 |
| 28 | 観光/ホスピタリティ | 閉鎖施設の除去 | 需要シフト信号の保護 | 類似需要構造の発見 |

### 全サンプルに共通する特許上の意義

1. **代謝制御**が解決する問題: データ構造が成長し続けると管理不能になる → 局所混雑度に基づく自動整理
2. **希少性保護**が解決する問題: 従来手法では低接続データから先に消える → 二段階審査で価値判断
3. **整合性発見**が解決する問題: 隠れた関連は人手では発見困難 → ラプラシアン固有値による構造類似性検出
4. **メタ制御**が解決する問題: 固定パラメータでは最適な管理が困難 → 健全性指標に基づくフィードバック制御
