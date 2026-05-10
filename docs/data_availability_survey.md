# Real-World Dataset Availability Survey / 実世界データセット入手可能性調査

This document is a **research-only** survey of public datasets that
could be used to validate the algorithm in the 28 industry scenarios
of `examples/`. **No data has been downloaded, no validation has been
run.** This is a precursor to any future real-data validation work.

[日本語版はこちら](#日本語版)

---

## Purpose

The 28 industry examples in `examples/` are synthetic illustrations
(see [applicability.md](applicability.md)). To convert any of them
from "Plausible" or "Unverified" to validated, real-world data is
required. This document surveys what is actually obtainable.

**Scope rule**: Industries with no usable public dataset are
**skipped, not padded** — listed in Section 2 with one short line
each.

## Methodology

- Web search across Kaggle, SNAP, OpenML, UCI ML, AWS Open Data,
  government open-data portals (data.gov, EU Open Data),
  papers-with-code, arXiv dataset releases, domain-specific
  repositories (BattLeDIM, NASA, NTSB, etc.)
- Filter to datasets that are graph-structured (or cleanly
  convertible) AND have or can derive ground-truth labels for
  "rare-but-important" nodes
- License and accessibility checked best-effort from web sources;
  re-verify before any actual use
- Cross-referenced against `kdf-perovskite` empirical findings
  (F-XXX) to flag where overlap or already-falsified territory exists

## Section 1: Datasets found (industries with at least one candidate)

| # | Industry | Dataset | URL | License | Size | Graph-structured? | Ground-truth for "rare-but-important"? | Notes |
|---|---|---|---|---|---|---|---|---|
| 02 | E-Commerce | SNAP Amazon co-purchase (com-Amazon, amazon0312) | https://snap.stanford.edu/data/com-Amazon.html | Public / academic | Medium-Large (~262k–402k nodes, 0.8M–1.2M edges) | Yes (product co-purchase undirected) | ⚠️ Derivable — Amazon category labels exist as ground-truth communities; "long-tail / niche" requires deriving rarity from category size + degree percentile | Distinct from MovieLens (already used by `kdf-perovskite`). Co-purchase graphs not scale-free in the same sense as citations, so not directly F-061/F-075 territory. Worth empirical test. |
| 03 | Knowledge Base | Hetionet (integrated biomedical KG) | https://het.io/ | CC0 | Medium (47k nodes, 2.25M edges, 11 node types, 24 edge types) | Yes (heterogeneous KG) | ⚠️ Derivable — node-type labels but no built-in "legacy/cross-department" label; cross-domain bridge framing is researcher-defined | Overlaps thematically with FB15K-237 (already used by `kdf-perovskite`). Compare results before claiming novelty. |
| 03 | Knowledge Base | MOOCCube (Coursera+EDX+XuetangX) | http://moocdata.cn/ | Academic, registration | Medium (706 courses, 114k concepts, 199k users, 8M behaviors) | Yes (concept-course-video-user heterogeneous) | ⚠️ Derivable — concept-prerequisite edges exist; cross-disciplinary nodes derivable from cluster bridging | Doubles as KB and Education industries. Wikipedia-linked entities give external grounding. |
| 04 | Medical / pharma | Hetionet (rare-disease drug repositioning) | https://het.io/ | CC0 | (same as above) | Yes | ✅ Direct (Disease nodes carry rare-disease flags via DO/Orphanet ontology) | Distinct from PPI cancer gene network (`kdf-perovskite` falsified on hub-biased labels). Multiple node types → structural rareness ≠ degree alone. **Strong candidate.** |
| 04 | Medical / pharma | Orphanet / Orphadata | https://www.orphadata.com/ | Custom academic, free for research | Medium (~6,000+ rare diseases with gene/phenotype/epidemiology) | Convertible (relational tables → KG via HPO/ORDO ontologies) | ✅ Direct (every disease in scope is rare by definition; gene-disease links labeled) | Tabular by default; needs hands-on verification for graph conversion effort. |
| 06 | IoT Manufacturing | NASA C-MAPSS turbofan degradation | https://www.nasa.gov/intelligent-systems-division/ (also via Kaggle) | NASA Open Data | Small-Medium (21 sensors × hundreds of engine units × cycles) | **Convertible only** (sensor co-correlation or temporal precursor graph; not natively graph) | ⚠️ Derivable — RUL labels exist; precursor windowing is researcher-defined | Not natively a graph dataset. NASA-HTTP (already used by `kdf-perovskite`) is logs; this is sensor time-series. Graph construction effort non-trivial. |
| 06 | IoT Manufacturing | SECOM (UCI) | https://archive.ics.uci.edu/ml/datasets/SECOM | Public domain | Small (1567 obs, 590 features, 104 fails ≈ 6.6% positive) | **Tabular, not graph** | ⚠️ Derivable — fail/pass label exists; graph requires building feature-correlation or sensor-topology graph | Imbalance ratio ~14:1 matches "rare important" pattern, but density-based detection works fine here → likely F-066 territory (`kdf-perovskite` falsified). |
| 07 | Telecommunications | Internet Topology Zoo | https://topology-zoo.org/ | Free for academic use | Small-Medium (250+ ISP topologies, tens to hundreds of nodes each) | Yes (router/PoP-level graph, manually traced from operator maps) | ⚠️ Derivable — no explicit "backup route" label, but bridges/articulation points are computable as ground-truth bottlenecks | Path-critical bottlenecks in non-scale-free ISP topologies match the algorithm's win zone (F-061 non-scale-free side). **Strong candidate.** |
| 07 | Telecommunications | CAIDA ITDK | https://www.caida.org/catalog/datasets/internet-topology-data-kit/ | Free, registration / data > 1yr public | Large (millions of routers/AS-level edges) | Yes | ❌ No ground-truth importance label out of the box; betweenness synthesis required | AS-level scale-free → likely TopDegree-wins regime (F-061). Router-level less so. |
| 08 | Cybersecurity | DARPA OpTC | https://github.com/FiveDirections/OpTC-data | Public (DARPA release) | Very large (17.4B events, 1000 hosts, 6 days, ~1TB compressed JSON) | Yes (provenance graph: processes/files/sockets nodes, syscalls edges) | ✅ Direct (red-team attack ground truth marks malicious nodes/edges; rare relative to benign traffic) | Provenance graphs are exactly the "rare-but-structurally-anomalous" target pattern. **Strong candidate**, but data volume requires significant pre-processing. |
| 08 | Cybersecurity | DARPA TC E3/E5 | (request-access via TC PI list / GitHub mirrors) | Restricted, request access | Large | Yes | ✅ Direct | Older than OpTC, more APT-focused. Hands-on accessibility verification needed. |
| 09 | Supply Chain | SupplyGraph (Bangladesh FMCG) | https://github.com/ciol-researchlab/SupplyGraph , https://huggingface.co/datasets/azminetoushikwasi/SupplyGraph | Open | Very small (41 nodes, 684 edges, 5 categories, 25 plants) | Yes (product/plant/storage heterogeneous) | ⚠️ Derivable — node features include production/sales/delivery; "single-source supplier" computable from edge structure | Only realistic public supply-chain graph dataset found. **Size is borderline trivial — flag.** Single-source supplier = articulation point detection, in the algorithm's win zone if non-scale-free. |
| 10 | Education | MOOCCube | http://moocdata.cn/ | Academic | Medium | Yes (concept-prerequisite + course-video-user) | ⚠️ Derivable — prerequisite edges exist; cross-disciplinary requires defining clusters first | Same as #03 entry. Cross-disciplinary concept = bridge node = structural-rareness target. Plausible win zone if prerequisite graph is non-scale-free. |
| 11 | Smart Grid / energy | PowerGraph (figshare) | https://figshare.com/articles/dataset/PowerGraph/22820534 | Open (figshare default CC) | Medium (IEEE24/39/118 + UK + Texas 2000-bus, with PF/OPF/cascade labels) | Yes (bus-line graph) | ✅ Direct (cascade-failure outcome labels per scenario; line-criticality identifiable) | Power grids are non-scale-free with clear path-critical bottlenecks → matches the algorithm's documented win zone. **Strong candidate.** |
| 11 | Smart Grid / energy | Texas A&M Electric Grid Test Cases | https://electricgrids.engr.tamu.edu/electric-grid-test-cases/ | Open (academic) | Medium-Large (up to 24,000-bus Midwest case) | Yes | ⚠️ Derivable — physics-based criticality requires running simulations | Companion to PowerGraph; raw topology only, no cascade labels. |
| 13 | Agriculture / food safety | USGS Pesticide Use | https://www.kaggle.com/datasets/usgs/pesticide-use | Public domain (US gov) | Medium (county-level time series, 1992–) | **Convertible only** (county-pesticide bipartite or county-county similarity graph) | ❌ No direct "contamination event" label | Tabular, not natively graph. Other agriculture results (CCMT, IP102) are image-classification only. **Borderline skip.** |
| 14 | Legal / compliance | Caselaw Access Project + CourtListener | https://case.law , https://www.courtlistener.com/ | CC0 (CAP) / open API (CourtListener) | Large (~6.5–6.7M U.S. opinions, 1658–2018) | Yes (case-citation directed graph) | ⚠️ Derivable — Supreme Court Database (SCDB) gives issue-area/dissent labels; "rare clause" requires text mining; precedent-importance derivable from later citation patterns | Citation networks are typically scale-free → kdf F-075 (OpenAlex citations) territory where TopDegree wins. However legal citations are bounded by precedent doctrine and may behave differently. **Hands-on verification needed.** |
| 14 | Legal / compliance | LePaRD (judicial citations to precedent) | https://arxiv.org/html/2311.09356v3 | Per arXiv release | Large (millions of citation passages) | Yes (citation graph w/ context) | ⚠️ Derivable | Same scale-free caveat as above. |
| 15 | HR / talent | ESCO (EU skills/occupations taxonomy) | https://esco.ec.europa.eu/en/use-esco/download | Free, EC license (re-use permitted) | Medium (~3,000 occupations, 13,000+ skills, multilingual; RDF/JSON-LD) | Yes (occupation-skill bipartite + hierarchies) | ✅ Direct (skill rarity from occupation incidence; "essential vs optional" labeled) | Skill graph is hierarchical/sparse, not scale-free. Niche skill = low-incidence node connected to few occupations = structural rareness; "important" via essential-skill flag. **Strong candidate.** |
| 15 | HR / talent | O*NET | https://www.onetcenter.org/database.html | Public domain | Medium | Convertible (occupation-task-skill tables → graph) | ✅ Direct (importance/level ratings per skill per occupation) | Tabular by default but well-documented schema. |
| 17 | Insurance / actuarial | Kaggle Auto/Vehicle insurance fraud datasets (multiple) | https://www.kaggle.com/datasets/shivamb/vehicle-claim-fraud-detection (and similar) | Kaggle (varies, mostly CC0/Open Database) | Small (~15k rows typical) | **Tabular, not graph** | ✅ Direct (fraud binary label, ~6% positive) | Density-based anomaly detection works well → likely F-066 territory (`kdf-perovskite` falsified). **Recommend skip OR explicit replication of the falsification.** |
| 18 | Environmental monitoring | GBIF / eBird Observation Dataset | https://www.gbif.org/dataset/4fa7b334-ce0d-4e88-aaae-2e0c138d049e | CC-BY / CC-BY-NC (per dataset) | Very large (>1.3B occurrence records) | Convertible (species-location bipartite or species-species co-occurrence) | ✅ Direct (IUCN red-list / regional rarity per species; rare species in unusual locations = "rare AND important") | Co-occurrence graphs typically NOT scale-free at species level. Strong candidate but graph construction is researcher-defined. |
| 19 | Transportation | DIMACS USA road network (9th Implementation Challenge) | http://www.diag.uniroma1.it/~challenge9/ ; https://networkrepository.com/road-road-usa.php | Free academic | Very large (~24M nodes, 58M edges full USA) | Yes (planar road graph) | ⚠️ Derivable — no built-in importance label; betweenness centrality / max-flow bottleneck are derivable ground truth | Road networks are explicitly non-scale-free planar graphs with clear path bottlenecks → canonical win zone (matches "Path-critical bottlenecks in non-scale-free graphs" from `kdf-perovskite`). **Strong candidate.** |
| 19 | Transportation | OpenStreetMap-derived city/country graphs (osmnx, Geofabrik) | https://www.openstreetmap.org/ ; https://download.geofabrik.de/ | ODbL | Very large | Yes | ⚠️ Derivable | Same character as DIMACS, more current. |
| 20 | Social Network | SNAP Reddit hyperlink / user interaction networks | https://snap.stanford.edu/data/web-RedditNetworks.html | Free academic | Medium-Large (millions of edges) | Yes | ⚠️ Derivable — subreddit ground-truth communities exist; "niche community" = small dense cluster | Scale-free → matches `kdf-perovskite` F-061 (algorithm fails on scale-free social networks where hubs dominate). **Listing for completeness; expected to falsify, not validate.** |
| 20 | Social Network | SNAP LiveJournal w/ ground-truth communities | https://snap.stanford.edu/data/com-LiveJournal.html | Free academic | Large (~4M nodes, 35M edges) | Yes | ✅ Direct (user-declared groups as ground-truth communities) | Same caveat — scale-free degree distribution. F-061 territory. |
| 23 | Aviation | NASA ASRS (Aviation Safety Reporting System) | https://asrs.arc.nasa.gov/search/database.html ; data.gov mirror | Public (NASA / data.gov) | Large (>1M textual reports since 1976) | **Convertible only** (incident-aircraft-airport-anomaly_code multi-relational graph requires construction) | ✅ Direct (Anomaly category codes per report; severity proxies available) | Anomaly codes are categorical and rare codes are semantically meaningful. Could yield a heterogeneous incident graph. **Hands-on verification needed.** |
| 23 | Aviation | NTSB Aviation Accident Database | https://www.ntsb.gov/ | Public domain | Medium (records since 1962) | Convertible (aircraft/manufacturer/cause-code graph) | ✅ Direct (cause-code labels, severity, fatality) | Same flag as ASRS. |
| 24 | Pharma Manufacturing (rare side-effect signals) | FDA FAERS via openFDA | https://open.fda.gov/data/faers/ | Public domain (US gov) | Very large (>20M reports) | Convertible (drug-event bipartite graph; or drug-drug co-occurrence) | ✅ Direct (drug-AE pair frequencies, rare AEs identifiable; serious-AE flags per report) | Bipartite drug-AE graph is non-scale-free per-drug, and rare AEs are exactly the importance target. Distinct from PPI gene network (`kdf-perovskite` falsified) — different graph topology. **Strong candidate.** |
| 25 | Water Management | BattLeDIM L-Town (Cyprus WDN benchmark) | https://zenodo.org/records/4017659 ; https://battledim.ucy.ac.cy/ | Open (Zenodo CC) | Small-Medium (L-Town: ~785 nodes, 905 pipes, 1 year SCADA) | Yes (pipe-junction graph + sensor time-series on nodes) | ✅ Direct (leak event ground-truth labels with timestamps and locations) | Water distribution = planar non-scale-free utility graph with critical paths — same regime as power grid and roads. **Strong candidate.** |
| 25 | Water Management | EPANET example networks | https://www.epa.gov/water-research/epanet | Public domain (US EPA) | Small (test networks) | Yes | ❌ No event labels (purely topology + simulation) | Companion only. |
| 27 | Mining | USGS MRDS + USMIN | https://mrdata.usgs.gov/ | Public domain (US gov) | Large (hundreds of thousands of deposit records globally) | Convertible (deposit-commodity-geology bipartite/heterogeneous graph) | ⚠️ Derivable — commodity rarity per region is computable; "geological anomaly" requires geochemical data layer | Tabular/spatial by default; graph construction is researcher-defined. |
| 27 | Mining | Global Copper Deposit Dataset (Wang 2026, Geoscience Data Journal) | https://rmets.onlinelibrary.wiley.com/doi/10.1002/gdj3.70040 | Open (per Wiley GDJ) | Medium | Convertible | ⚠️ Derivable | Domain-specific. |
| 28 | Hospitality | HotelRec (TripAdvisor 50M reviews) | https://github.com/Diego999/HotelRec | Academic, request access | Very large (~50M reviews, 1.85k–4.3k hotels variants) | Convertible (user-hotel bipartite review graph) | ⚠️ Derivable — sub-rating dimensions exist; "rare guest preference" requires clustering rating profiles | Closest to MovieLens (`kdf-perovskite` already used). Likely behaves similarly. |
| 22 | Media Advertising | Criteo 1TB / CriteoPrivateAd / Avazu CTR | https://ailab.criteo.com/ressources/ ; Avazu Kaggle | Open (research) | Very large (1TB / 4B events; Avazu ~40M impressions) | **Tabular, not natively graph** | ❌ No graph-natural rare-importance label; CTR is a continuous ad-click target | Building a user-ad-publisher graph is researcher-defined. CTR distributions are heavy-tailed but the target ("important niche audience") is not a structural property. **Likely weak fit.** |

## Section 2: Skipped industries (no usable public dataset found)

- **#01 Basic / general** — Explicitly illustrative, not a real domain.
- **#05 Financial (fraud)** — Kaggle has many fraud datasets (PaySim,
  IEEE-CIS, credit-card) but they are tabular feature-vector
  classification, and `kdf-perovskite` has falsified the algorithm in
  this density-based regime (F-066). No public *graph-structured*
  financial fraud dataset with rare-but-structurally-important labels
  found beyond Elliptic Bitcoin Transactions (hub-dominated). Skipped
  to avoid duplicating F-066.
- **#16 Real Estate** — Kaggle Zillow datasets are tabular property
  records with price targets, not graphs. No public real-estate
  transaction or geographic-similarity graph dataset with
  "outlier-important" labels found.
- **#21 Gaming** — MMORPG public datasets exist (WoW Avatar History,
  Glitch auction data, Clash Royale) but are predominantly tabular
  logs, none with native graph structure and a "rare-important"
  ground-truth label.
- **#26 Construction** — All construction-defect datasets found (BD3,
  MBDD2025, SODA) are RGB image computer-vision datasets for defect
  classification, not graphs. BIMCompNet has IFC-graph modality but
  is for component classification, not defect-rarity detection.

## Strongest candidates (priority recommendations)

For any future real-data validation work (Phase B), the candidates
most aligned with the algorithm's documented win zone (path-critical,
non-scale-free, structurally rare ≡ important) are:

| Rank | Industry | Dataset | Why it fits |
|---|---|---|---|
| 1 | #11 Smart Grid | PowerGraph | Direct cascade labels, non-scale-free, path-critical |
| 2 | #19 Transportation | DIMACS USA road | Canonical non-scale-free planar, betweenness ground truth derivable |
| 3 | #25 Water Management | BattLeDIM L-Town | Direct leak labels, planar utility graph |
| 4 | #07 Telecommunications | Internet Topology Zoo | Many small non-scale-free ISP topologies, articulation-point ground truth |
| 5 | #08 Cybersecurity | DARPA OpTC | Direct red-team labels, provenance graph captures structural anomaly |
| 6 | #04 Medical / pharma | Hetionet | Direct rare-disease flags, multi-type → structural rareness ≠ degree |
| 7 | #15 HR / talent | ESCO | Direct skill-essentiality labels, sparse non-scale-free taxonomy |
| 8 | #24 Pharma Mfg (FAERS) | FDA FAERS | Direct rare-AE labels, bipartite non-hub-dominated |

Industries listed in Section 1 but **not** in this strongest-candidates
list either overlap heavily with `kdf-perovskite` already-falsified
domains (#14, #20) or require non-trivial graph-construction work
where the rare-important framing is researcher-defined (#02, #03,
#06, #13, #18, #23, #27, #28, #22).

## Caveats

- **Tabular-not-graph flag**: Several entries marked `Convertible`
  are not natively graphs. Graph construction effort is non-trivial
  and the choice of edges encodes researcher assumptions. Honest
  validation must report graph-construction details.
- **Ground-truth interpretability**: `⚠️ Derivable` means a label
  exists but its alignment with "rare-but-important" depends on
  framing. Hands-on inspection of label distributions is required
  before claiming validation.
- **License re-verification**: License notes are best-effort from
  web search. Re-verify directly with the source before any download.
- **Already-falsified overlap**: Where `kdf-perovskite` has already
  established a result (F-XXX), running the same dataset here adds
  little. Listings in scale-free / density-based domains (#14, #17,
  #20) are included for completeness but are expected to reproduce
  failure, not validate success.

## What this document does NOT do

- It does not download, evaluate, or validate any dataset.
- It does not commit to running a Phase B validation in any of these
  industries — that is a separate decision.
- It does not establish that the algorithm will succeed on any of
  these datasets — only that the data is reachable to find out.

---

<a name="日本語版"></a>
## 日本語版

本ドキュメントは、`examples/` の28業界シナリオを実データで検証する
ために使える可能性のある **公開データセットの調査記録** である。
**実データはダウンロードしておらず、validation も実施していない**。
将来的に実データ検証 (Phase B) を行う際の前段階の調査である。

### 目的

`examples/` の28業界 example はすべて合成データの illustration である
（[applicability.md](applicability.md) 参照）。これらを「該当しそう
(Plausible)」「未検証 (Unverified)」から validated に格上げするには
実データが必要。本ドキュメントは「実際に手に入るのか」を調べる。

**スコープルール**: 公開データセットが見当たらない業界は **水増し
せずスキップ** し、Section 2 に1行で理由を記す。

### 調査範囲（再掲）

- Kaggle / SNAP / OpenML / UCI ML / AWS Open Data / 各国オープンデータ
  ポータル / papers-with-code / arXiv / ドメイン固有リポジトリ
  (BattLeDIM / NASA / NTSB 等)
- 「グラフ構造（または cleanly convertible）」 **かつ**
  「rare-but-important の ground-truth ラベルが存在/導出可能」を満たす
  もの
- ライセンス・入手方法は web 検索ベース。実利用前に必ず一次情報で
  再確認すること
- `kdf-perovskite` 知見 (F-XXX) と重複・反証済み領域は明示

### Section 1 / Section 2 / 強候補リスト

英語版（上）の内容と同じ。28業界の調査結果を以下の3区分で整理：

#### Section 1: 候補ありの業界（上記英語版テーブルを参照）

22業界に少なくとも1つの候補データセットが見つかった。

#### Section 2: スキップされた業界

公開データが見当たらず、調査を打ち切った業界:

- **#01 Basic / general** — illustration のみ
- **#05 Financial (fraud)** — Kaggle の fraud データはほぼ tabular で、
  `kdf-perovskite` F-066 で既に density-based として反証済み。グラフ
  構造の金融 fraud 公開データは見当たらず（Elliptic Bitcoin は hub-
  dominated）
- **#16 Real Estate** — Zillow 等は tabular property 価格予測。グラフ
  構造の real-estate 公開データは見当たらず
- **#21 Gaming** — MMORPG の公開データはあるが tabular log 中心、
  rare-important ground-truth ラベルを持つグラフは見当たらず
- **#26 Construction** — defect 検出データは画像分類用が中心、グラフ
  でない

#### 強候補（Phase B の優先順位）

実データ検証を行う場合、本アルゴリズムの win zone（path-critical /
non-scale-free / 構造的稀少性 ≡ 重要度）と最も一致する候補:

1. **#11 Smart Grid — PowerGraph** （cascade ラベル、non-scale-free、path-critical）
2. **#19 Transportation — DIMACS USA road** （canonical non-scale-free、betweenness 導出可能）
3. **#25 Water Management — BattLeDIM L-Town** （直接 leak ラベル、planar utility graph）
4. **#07 Telecommunications — Internet Topology Zoo** （多数の small non-scale-free ISP、articulation point 導出可）
5. **#08 Cybersecurity — DARPA OpTC** （直接 red-team ラベル、provenance graph）
6. **#04 Medical / pharma — Hetionet** （直接 rare-disease フラグ、multi-type で「構造的稀少 ≠ 次数」）
7. **#15 HR / talent — ESCO** （直接 skill-essentiality ラベル、sparse non-scale-free taxonomy）
8. **#24 Pharma Mfg — FDA FAERS** （直接 rare-AE ラベル、bipartite で hub-dominated でない）

Section 1 にあって本リストにない業界は、`kdf-perovskite` で既に反証
された領域 (#14, #20) か、graph 構築の研究者依存度が高く rare-
important framing が自明でない (#02, #03, #06, #13, #18, #23, #27,
#28, #22) のいずれか。

### 注意事項

- **Tabular-not-graph フラグ**: `Convertible` 表記の項目は natively
  graph ではない。エッジ定義は研究者依存で、validation 時には graph
  構築の詳細を率直に開示する必要がある
- **Ground-truth の解釈**: `⚠️ Derivable` はラベルは存在するが
  「rare-but-important」との整合は framing 次第。実利用前にラベル分布
  の hands-on 確認が必要
- **ライセンス再確認**: web 検索ベースの best-effort。一次情報で再確認
- **反証済み領域**: `kdf-perovskite` で結論が出ている領域 (F-XXX) で
  同じことをしても新規性は薄い。scale-free / density-based 系
  (#14, #17, #20) の listing は「網羅性のため」であって「validate
  推奨」ではない

### 本ドキュメントが行わないこと

- データセットのダウンロード・評価・validation
- いずれかの業界での Phase B 実施の commit
- これらのデータで本アルゴリズムが成功する保証
