# Examples Guide

This guide explains what each example demonstrates, what problem it addresses, and who would benefit from it.

[日本語版はこちら](#日本語版)

---

## Overview

All examples follow the same pattern:

1. Build a domain-specific graph with realistic data
2. Run Graph Metabolic Manager to automatically maintain it
3. Show what was preserved, what was cleaned, and what was discovered

Each example can be run independently:

```bash
pip install -e .
python examples/01_basic_usage.py
```

---

## 01: Basic Usage

**File**: `examples/01_basic_usage.py`

**What it demonstrates**: The simplest possible use of GraphMetabolicManager. Creates a small graph with popular nodes, one rare valuable node, and noise nodes, then runs the manager.

**Key result**:
- Noise nodes removed (5 → 0)
- Rare valuable node survives thanks to rarity protection

**Who should read this**: Anyone getting started with the library.

---

## 02: E-Commerce Recommendation

**File**: `examples/02_ec_recommendation.py`

**Problem**: Product recommendation graphs grow indefinitely. Seasonal products go stale, but niche products serving specific customer segments must not be lost.

**Simulation**:
- 30 popular products (densely cross-recommended)
- 8 niche products (few recommendations but valuable to specific customers)
- 8 seasonal products (out-of-season, should be cleaned up)

**Key result**:
- Niche products protected: 5/8 survive
- Seasonal products removed: 8/8 cleaned
- Overall graph density optimized

**Who should read this**: Engineers building recommendation systems, product catalog managers, e-commerce platform teams.

**Applicable to**: Any system with product-to-product or user-to-product relationship graphs — retail, media, content platforms.

---

## 03: Enterprise Knowledge Base

**File**: `examples/03_knowledge_base.py`

**Problem**: Corporate knowledge bases accumulate documents over years. New documents are added but outdated ones are rarely removed. Meanwhile, historically important documents (founding principles, original architecture decisions) risk being buried or deleted.

**Simulation**:
- 20 active documents across 4 departments (Engineering, Product, Operations, HR)
- 5 legacy documents (historically important but rarely accessed)
- 5 obsolete documents (truly outdated, safe to archive)
- Part 2: Consistency Discovery finds hidden cross-department relationships

**Key result**:
- Legacy documents protected: 4/5 survive
- Obsolete documents archived: 5/5 cleaned
- Hidden relationships discovered: 70 cross-department connections found

**Who should read this**: Knowledge management teams, IT departments managing document systems, developers building search or wiki platforms.

**Applicable to**: Enterprise wikis, FAQ systems, documentation platforms, any system where information accumulates over time.

---

## 04: Medical Knowledge Graph

**File**: `examples/04_medical_knowledge.py`

**Problem**: Medical knowledge graphs connect diseases, genes, and drugs. Rare diseases have very few data points — traditional pruning methods delete them first. But rare disease data is often the most scientifically valuable.

**Simulation**:
- 20 common diseases with established gene/drug connections
- 15 genes and 12 approved drugs (well-connected)
- 8 rare diseases (orphan diseases — only 1 weak gene connection each)
- 8 deprecated drug candidates (failed clinical trials)
- Part 2: Consistency Discovery identifies potential drug repurposing candidates

**Key result**:
- Rare disease data protected: 5/8 survive
- Deprecated drugs cleaned: 8/8 removed
- Drug repurposing candidates identified: 105 potential connections

**Who should read this**: Bioinformatics engineers, drug discovery researchers, teams building medical knowledge graphs.

**Applicable to**: Any biomedical knowledge base, clinical data management, drug-target interaction databases.

**Why rarity protection matters here**: In rare diseases, a single data point about a gene-disease association could lead to a treatment breakthrough. Traditional pruning (TTL, LRU, threshold-based) removes low-connectivity nodes first — exactly the nodes that represent rare diseases.

---

## 05: Financial Transaction Network

**File**: `examples/05_financial_network.py`

**Problem**: Financial transaction networks are monitored for fraud. Suspicious entities (shell companies, unusual accounts) have very few transactions — they are deliberately low-profile. Traditional graph pruning destroys these weak signals.

**Simulation**:
- 30 normal business entities across 5 sectors
- 6 suspicious entities (potential fraud signals — shell companies, anomalous patterns)
- 8 inactive entities (dormant accounts, safe to archive)
- **Scenario A**: Without rarity protection (traditional approach)
- **Scenario B**: With rarity protection
- Part 2: Hidden connection discovery between suspicious and normal entities

**Key result**:
- **Without protection: 0/6 fraud signals survive (all destroyed)**
- With protection: 3/6 fraud signals preserved
- Inactive accounts cleaned: 8/8 removed
- Hidden suspicious connections discovered: 44 connections

**Who should read this**: AML (anti-money laundering) engineers, fraud detection teams, financial risk analysts.

**Applicable to**: Transaction monitoring, sanctions screening, insurance fraud detection, any system where rare patterns indicate risk.

**Why this example is critical**: The side-by-side comparison (Scenario A vs B) demonstrates that conventional graph maintenance actively destroys the very signals that fraud detection depends on. Rarity protection solves this by treating low-connectivity entities as "potentially important" rather than "probably noise."

---

## 06: IoT / Manufacturing Sensor Network

**File**: `examples/06_iot_manufacturing.py`

**Problem**: Factory sensor networks generate massive amounts of data. Equipment anomalies that appear only once or twice are often discarded as noise during data cleanup. But these rare signals can be early warnings of equipment failure.

**Simulation**:
- 15 pieces of equipment across 3 production lines
- 53 sensors (temperature, vibration, pressure, current, noise)
- 6 known alert patterns (well-established failure modes)
- 6 rare anomaly patterns (early warning signals seen only once)
- 8 obsolete sensor readings (from decommissioned equipment)
- Part 2: Predictive maintenance — discovering which equipment might share anomaly patterns

**Key result**:
- Rare anomaly signals protected: 4/6 survive
- Obsolete data cleaned: 8/8 removed
- Predictive maintenance connections: 78 cross-equipment patterns discovered

**Who should read this**: IoT platform engineers, predictive maintenance teams, factory automation engineers.

**Applicable to**: Any IoT environment — manufacturing, energy, transportation, building management — where sensor data is continuously generated and rare patterns have diagnostic value.

**Cost context**: In manufacturing, a single unplanned equipment stoppage can cost $10K–$100K+ per hour. Preserving rare anomaly signals enables earlier detection and prevention.

---

## 07: Telecommunications Network

**File**: `examples/07_telecom_network.py`

**Problem**: Telecommunications networks accumulate routing data as equipment is added. Legacy equipment records persist, but rare backup relay routes — the only failover paths during outages — risk being pruned due to low daily traffic.

**Simulation**:
- 25 core routers across 5 regional clusters (Tokyo, Osaka, Nagoya, Fukuoka, Sapporo)
- 6 backup relay nodes (failover paths through minor cities)
- 8 decommissioned legacy equipment nodes
- **Scenario A**: Without rarity protection → all backup routes lost
- **Scenario B**: With rarity protection → backup routes preserved
- Part 2: Structural similarity identifies regions with similar topology

**Key result**:
- Without protection: 0/6 backup routes survive
- With protection: 4/6 backup routes preserved
- Legacy equipment cleaned: 8/8 removed
- Structural similarities found: 13 cross-region topology matches

**Who should read this**: Network engineers, telecom infrastructure teams, NOC operators.

**Applicable to**: Any network topology management — ISPs, enterprise WANs, CDNs, mesh networks.

---

## 08: Cybersecurity Threat Intelligence

**File**: `examples/08_cybersecurity.py`

**Problem**: Threat intelligence graphs grow constantly with new indicators. Expired indicators should be removed, but APT (Advanced Persistent Threat) signals — extremely faint traces of targeted attacks — must not be lost. Traditional pruning destroys these weak signals first.

**Simulation**:
- 30 known threat indicators across 5 attack categories (Malware, Phishing, Exploit, C2 Infrastructure, Lateral Movement)
- 6 rare APT signals (faint indicators of targeted attacks)
- 8 stale/expired indicators
- Part 2: Hidden campaign connection discovery

**Key result**:
- Without protection: 0/6 APT signals survive
- With protection: 2/6 APT signals preserved
- Stale indicators cleaned: 8/8 removed
- Hidden campaign links: 64 connections discovered

**Who should read this**: SOC analysts, threat intelligence teams, CISO offices, SIEM engineers.

**Applicable to**: Threat intelligence platforms, SIEM systems, incident response, vulnerability management.

---

## 09: Supply Chain Network

**File**: `examples/09_supply_chain.py`

**Problem**: Supply chain networks grow with new supplier relationships. Defunct suppliers should be removed, but sole-source critical suppliers — the ONLY source for certain rare materials — must be tracked. Losing visibility of these suppliers means production can halt without warning.

**Simulation**:
- 30 established suppliers across 5 categories (Semiconductors, Raw Materials, Electronics, Logistics, Assembly)
- 6 sole-source critical suppliers (irreplaceable supply paths)
- 8 defunct suppliers (bankrupt or exited)
- Part 2: Supply chain vulnerability pattern discovery

**Key result**:
- Without protection: 0/6 sole-source suppliers tracked
- With protection: 2/6 sole-source suppliers preserved
- Defunct suppliers cleaned: 8/8 removed
- Risk-similar connections: 18 vulnerability patterns found

**Who should read this**: Supply chain managers, procurement teams, risk analysts, operations leaders.

**Applicable to**: Any multi-tier supply chain — automotive, electronics, pharmaceuticals, aerospace.

---

## 10: Education / Curriculum Network

**File**: `examples/10_education_curriculum.py`

**Problem**: University curriculum graphs accumulate courses over decades. Discontinued courses should be removed, but rare interdisciplinary courses — serving small but unique student populations — are at risk. These cross-department bridges enable career paths that no single department can provide.

**Simulation**:
- 30 mainstream courses across 5 departments (CS, Math, Physics, Business, Biology)
- 6 interdisciplinary courses (Bioinformatics, Computational Finance, Physics of Music, etc.)
- 8 discontinued courses (COBOL Programming, Typewriter Skills, etc.)
- Part 2: Curriculum structure similarity discovery

**Key result**:
- Without protection: 0/6 interdisciplinary courses survive
- With protection: 4/6 interdisciplinary courses preserved
- Discontinued courses cleaned: 8/8 removed
- Structural similarities: 65 cross-department patterns found

**Who should read this**: Academic administrators, curriculum designers, EdTech platform builders.

**Applicable to**: University course management, online learning platforms, corporate training systems.

---

## 11: Smart Grid / Energy Network

**File**: `examples/11_smart_grid.py`

**Problem**: Power grid monitoring generates massive data. Decommissioned monitoring points should be removed, but rare anomaly records — early warnings of cascade failures that occurred only once in history — must be preserved. Losing these records means the grid is blind to repeat scenarios.

**Simulation**:
- 25 substations across 5 grid zones with 6 generators
- 6 rare anomaly patterns (Voltage Collapse Precursor, Frequency Drift, Phase Imbalance, etc.)
- 8 decommissioned monitoring points
- Part 2: Grid zone vulnerability pattern discovery

**Key result**:
- Without protection: 0/6 anomaly records survive
- With protection: 6/6 anomaly records preserved
- Decommissioned data cleaned: 8/8 removed
- Vulnerability patterns: 26 cross-zone similarities found

**Who should read this**: Grid operators, utility engineers, SCADA administrators, energy regulators.

**Applicable to**: Power grids, water distribution, gas pipelines, any critical infrastructure monitoring.

---

## 12: Academic Citation Network

**File**: `examples/12_academic_citation.py`

**Problem**: Citation networks grow as new papers are published. Retracted and superseded papers should be removed, but rare interdisciplinary papers — bridging distant research fields with few citations today — must be preserved. These are often the seeds of entirely new research areas.

**Simulation**:
- 30 well-cited papers across 5 fields (Machine Learning, Bioinformatics, Quantum Computing, Climate Science, Neuroscience)
- 6 interdisciplinary papers (Quantum Biology Bridge, Neuro-Climate Modeling, AI Consciousness Theory, etc.)
- 8 retracted/superseded papers
- Part 2: Hidden thematic connection discovery across fields

**Key result**:
- Without protection: 0/6 interdisciplinary papers survive
- With protection: 1/6 interdisciplinary papers preserved
- Retracted papers cleaned: 8/8 removed
- Thematic connections: 48 cross-field links discovered

**Who should read this**: Research librarians, academic database administrators, scientometrics researchers.

**Applicable to**: Citation databases, research portals, systematic review tools, academic search engines.

---

## 13: Agriculture / Food Safety

**File**: `examples/13_agriculture_food_safety.py`

**Problem**: Agriculture monitoring generates data about pest patterns and disease signals. Rare contamination traces (e.g., novel pathogen strains, rare mycotoxin patterns) have very few occurrences but are critical early warnings.

**Simulation**:
- 30 farm/processing nodes across 5 categories
- 6 rare pest/disease signals
- 8 expired/recalled items

**Key result**:
- Without protection: 0/6 pest signals survive
- With protection: 2/6 pest signals preserved
- Expired/recalled items cleaned: 8/8 removed

**Who should read this**: Agricultural technology teams, food safety regulators, supply chain traceability engineers.

**Applicable to**: Farm management, food traceability, phytosanitary monitoring.

---

## 14: Legal / Compliance

**File**: `examples/14_legal_compliance.py`

**Problem**: Legal knowledge bases accumulate documents. Expired regulations should be removed, but rare legal precedents bridging multiple domains are at risk.

**Simulation**:
- 30 legal documents across 5 areas
- 6 rare precedent nodes
- 8 expired regulations

**Key result**:
- Without protection: 0/6 precedents survive
- With protection: 1/6 precedents preserved
- Expired regulations cleaned: 8/8 removed

**Who should read this**: Legal technology teams, compliance officers, legal research platforms.

**Applicable to**: Case law databases, regulatory compliance systems, contract management.

---

## 15: HR / Talent Management

**File**: `examples/15_hr_talent.py`

**Problem**: HR networks track employee skills and roles. Rare cross-domain skill combinations (e.g., ML+Biology, Legal+AI) are at risk of being lost when employees leave.

**Simulation**:
- 30 employee/role nodes across 5 departments
- 6 rare skill combinations
- 8 resigned/closed positions

**Key result**:
- Without protection: 0/6 skill signals survive
- With protection: 3/6 skill signals preserved
- Resigned/closed cleaned: 8/8 removed

**Who should read this**: HR analytics teams, talent acquisition, workforce planning.

**Applicable to**: Skills databases, internal mobility platforms, organizational network analysis.

---

## 16: Real Estate / Urban Planning

**File**: `examples/16_real_estate.py`

**Problem**: Property networks accumulate listings. Sold/expired should be removed, but rare property features (heritage buildings, unique zoning) must be preserved.

**Simulation**:
- 30 property/area nodes across 5 zones
- 6 rare feature nodes
- 8 sold/expired listings

**Key result**:
- Without protection: 0/6 features survive
- With protection: 1/6 features preserved
- Sold/expired cleaned: 8/8 removed

**Who should read this**: PropTech developers, urban planners, real estate analytics teams.

**Applicable to**: Property listing platforms, urban development databases, land use planning.

---

## 17: Insurance / Actuarial

**File**: `examples/17_insurance_actuarial.py`

**Problem**: Insurance networks track claim patterns. Expired policies should be removed, but rare claim patterns (pandemic cascading, cyber-physical crossover) are critical for risk modeling.

**Simulation**:
- 30 policy/risk nodes across 5 product lines
- 6 rare claim patterns
- 8 expired policies

**Key result**:
- Without protection: 0/6 patterns survive
- With protection: 2/6 patterns preserved
- Expired policies cleaned: 8/8 removed

**Who should read this**: Actuaries, risk modelers, InsurTech teams, underwriting analytics.

**Applicable to**: Claims analytics, risk assessment platforms, reinsurance modeling.

---

## 18: Environmental Monitoring

**File**: `examples/18_environmental_monitoring.py`

**Problem**: Environmental monitoring generates data from many stations. Decommissioned stations should be removed, but rare species sightings and unusual pollution patterns must be preserved.

**Simulation**:
- 30 monitoring nodes across 5 ecosystems
- 6 rare observation signals
- 8 decommissioned stations

**Key result**:
- Without protection: 0/6 observations survive
- With protection: 1/6 observations preserved
- Decommissioned stations cleaned: 8/8 removed

**Who should read this**: Environmental scientists, conservation agencies, pollution monitoring teams.

**Applicable to**: Biodiversity databases, pollution monitoring networks, climate observation systems.

---

## 19: Transportation / Logistics

**File**: `examples/19_transportation.py`

**Problem**: Transportation networks accumulate routing data. Defunct routes should be removed, but rare bottleneck signals and alternative routing paths with minimal daily traffic must be preserved.

**Simulation**:
- 30 facility nodes across 5 categories (Rail, Maritime, Aviation, Trucking, Warehouse)
- 6 rare bottleneck/route signals
- 8 closed/defunct routes

**Key result**:
- Without protection: 0/6 route signals survive
- With protection: 1/6 route signals preserved
- Closed routes cleaned: 8/8 removed

**Who should read this**: Logistics engineers, fleet managers, transportation planners.

**Applicable to**: Freight networks, last-mile delivery, multimodal transport optimization.

---

## 20: Social Network Analysis

**File**: `examples/20_social_network.py`

**Problem**: Social networks grow as users interact. Inactive accounts should be cleaned up, but rare bridge users connecting disparate communities are at risk.

**Simulation**:
- 30 community members across 5 groups (Tech, Art, Sports, Science, Music)
- 6 rare bridge users connecting distant communities
- 8 inactive/abandoned accounts

**Key result**:
- Without protection: 0/6 bridge users survive
- With protection: 2/6 bridge users preserved
- Inactive accounts cleaned: 8/8 removed

**Who should read this**: Social media engineers, community managers, network analysts.

**Applicable to**: Social platforms, community detection, influence analysis.

---

## 21: Online Gaming

**File**: `examples/21_gaming.py`

**Problem**: Gaming platforms track player interactions. Banned accounts should be removed, but rare cheating pattern signals and emerging exploit indicators must be preserved.

**Simulation**:
- 30 player nodes across 5 genres (FPS, RPG, Strategy, Sports, Casual)
- 6 rare cheat/exploit signals
- 8 banned/deleted accounts

**Key result**:
- Without protection: 0/6 cheat signals survive
- With protection: 2/6 cheat signals preserved
- Banned accounts cleaned: 8/8 removed

**Who should read this**: Game security teams, anti-cheat engineers, player behavior analysts.

**Applicable to**: Online gaming platforms, matchmaking systems, player behavior analytics.

---

## 22: Media / Advertising

**File**: `examples/22_media_advertising.py`

**Problem**: Media networks accumulate advertising data. Discontinued campaigns should be removed, but rare emerging trend signals are at risk.

**Simulation**:
- 30 media outlet nodes across 5 channels (TV, Digital, Print, Radio, Streaming)
- 6 rare trend/audience signals
- 8 discontinued/expired campaigns

**Key result**:
- Without protection: 0/6 trend signals survive
- With protection: 2/6 trend signals preserved
- Discontinued campaigns cleaned: 8/8 removed

**Who should read this**: AdTech engineers, media planners, audience analytics teams.

**Applicable to**: Advertising platforms, media buying, audience segmentation, cross-channel analytics.

---

## 23: Aviation / Aerospace

**File**: `examples/23_aviation.py`

**Problem**: Aviation maintenance networks track component relationships. Retired components should be removed, but rare fatigue crack propagation patterns are critical safety signals.

**Simulation**:
- 30 component nodes across 5 systems (Engines, Avionics, Airframe, Landing Gear, Hydraulics)
- 6 rare fatigue/failure precursor signals
- 8 retired/decommissioned components

**Key result**:
- Without protection: 0/6 fatigue signals survive
- With protection: 1/6 fatigue signals preserved
- Retired components cleaned: 8/8 removed

**Who should read this**: Aviation maintenance engineers, MRO teams, airworthiness analysts.

**Applicable to**: Aircraft maintenance, MRO operations, airworthiness management, defense systems.

---

## 24: Pharmaceutical Manufacturing

**File**: `examples/24_pharma_manufacturing.py`

**Problem**: Pharma manufacturing networks track quality data. Expired batches should be removed, but rare contamination trace patterns are critical for GMP compliance.

**Simulation**:
- 30 facility nodes across 5 areas (API Production, Formulation, Packaging, QC, Distribution)
- 6 rare contamination signals
- 8 expired/recalled products

**Key result**:
- Without protection: 0/6 contamination signals survive
- With protection: 1/6 contamination signals preserved
- Expired/recalled cleaned: 8/8 removed

**Who should read this**: QA/QC teams, GMP compliance officers, pharma manufacturing engineers.

**Applicable to**: GMP manufacturing, batch record management, deviation tracking, quality systems.

---

## 25: Water / Wastewater Management

**File**: `examples/25_water_management.py`

**Problem**: Water infrastructure networks track asset data. Decommissioned assets should be removed, but rare water quality anomaly signals (e.g., PFAS contamination traces) are critical for public health.

**Simulation**:
- 30 infrastructure nodes across 5 types (Treatment Plants, Pumping Stations, Reservoirs, Distribution Mains, Monitoring Wells)
- 6 rare water quality signals
- 8 decommissioned/replaced assets

**Key result**:
- Without protection: 0/6 quality signals survive
- With protection: 2/6 quality signals preserved
- Decommissioned assets cleaned: 8/8 removed

**Who should read this**: Water utility engineers, environmental compliance teams, infrastructure planners.

**Applicable to**: Water treatment, wastewater management, infrastructure asset management, regulatory compliance.

---

## 26: Construction / Infrastructure

**File**: `examples/26_construction.py`

**Problem**: Construction networks track building system relationships. Completed/demolished projects should be removed, but rare structural defect patterns are critical safety signals.

**Simulation**:
- 30 building system nodes across 5 disciplines (Structural, Electrical, Plumbing, HVAC, Foundation)
- 6 rare defect pattern signals
- 8 completed/demolished projects

**Key result**:
- Without protection: 0/6 defect signals survive
- With protection: 1/6 defect signals preserved
- Completed/demolished cleaned: 8/8 removed

**Who should read this**: Structural engineers, building inspectors, construction project managers.

**Applicable to**: Building information modeling (BIM), structural health monitoring, construction defect tracking.

---

## 27: Mining / Resource Extraction

**File**: `examples/27_mining.py`

**Problem**: Mining networks track operational data. Exhausted sites should be removed, but rare geological anomaly signals (e.g., rare earth deposits, seismic precursors) are critical for safety and discovery.

**Simulation**:
- 30 operation nodes across 5 areas (Open Pit, Underground, Processing, Transport, Exploration)
- 6 rare geological/safety signals
- 8 exhausted/closed operations

**Key result**:
- Without protection: 0/6 geological signals survive
- With protection: 2/6 geological signals preserved
- Exhausted/closed cleaned: 8/8 removed

**Who should read this**: Mining engineers, geologists, safety officers, resource planners.

**Applicable to**: Mining operations, geological surveys, mineral exploration, mine safety systems.

---

## 28: Hospitality / Tourism

**File**: `examples/28_hospitality.py`

**Problem**: Hospitality networks track venue and demand data. Closed venues should be removed, but rare demand pattern signals (emerging destinations, cultural shifts) are critical for strategic planning.

**Simulation**:
- 30 hospitality nodes across 5 sectors (Hotels, Restaurants, Attractions, Transport Hubs, Event Venues)
- 6 rare demand/trend signals
- 8 closed/defunct venues

**Key result**:
- Without protection: 0/6 demand signals survive
- With protection: 2/6 demand signals preserved
- Closed venues cleaned: 8/8 removed

**Who should read this**: Hospitality executives, tourism planners, revenue managers.

**Applicable to**: Hotel management, destination marketing, event planning, tourism analytics.

---

## Choosing the Right Example

| Your domain | Start with | Then explore |
|---|---|---|
| Getting started | 01 Basic Usage | Any that matches your field |
| E-commerce / Recommendations | 02 EC Recommendation | 01 for API basics |
| Enterprise IT / Knowledge management | 03 Knowledge Base | 04 for graph analysis patterns |
| Healthcare / Biotech | 04 Medical Knowledge | 03 for knowledge graph patterns |
| Finance / Risk / Compliance | 05 Financial Network | 08 for threat detection patterns |
| Manufacturing / IoT | 06 IoT Manufacturing | 11 for infrastructure patterns |
| Telecommunications / Networking | 07 Telecom Network | 11 for infrastructure patterns |
| Cybersecurity / Threat Intelligence | 08 Cybersecurity | 05 for rare signal patterns |
| Supply Chain / Logistics | 09 Supply Chain | 06 for sensor/monitoring patterns |
| Education / EdTech | 10 Education Curriculum | 03 for knowledge graph patterns |
| Energy / Utilities | 11 Smart Grid | 06 for IoT monitoring patterns |
| Research / Academia | 12 Academic Citation | 04 for knowledge graph patterns |
| Agriculture / Food Safety | 13 Agriculture Food Safety | 09 for supply chain patterns |
| Legal / Compliance | 14 Legal Compliance | 05 for risk signal patterns |
| HR / Talent Management | 15 HR Talent | 10 for network analysis patterns |
| Real Estate / Urban Planning | 16 Real Estate | 03 for knowledge graph patterns |
| Insurance / Actuarial | 17 Insurance Actuarial | 05 for financial patterns |
| Environmental Monitoring | 18 Environmental Monitoring | 06 for sensor/monitoring patterns |
| Transportation / Logistics | 19 Transportation | 09 for supply chain patterns |
| Social Media / Networks | 20 Social Network | 08 for rare signal patterns |
| Gaming / Online platforms | 21 Gaming | 08 for rare signal patterns |
| Media / Advertising | 22 Media Advertising | 05 for trend detection |
| Aviation / Aerospace | 23 Aviation | 06 for sensor/monitoring patterns |
| Pharmaceutical / GMP | 24 Pharma Manufacturing | 06 for quality monitoring |
| Water / Utilities | 25 Water Management | 11 for infrastructure patterns |
| Construction / Building | 26 Construction | 11 for infrastructure patterns |
| Mining / Resources | 27 Mining | 06 for sensor/monitoring patterns |
| Hospitality / Tourism | 28 Hospitality | 09 for supply chain patterns |

---

<a name="日本語版"></a>
## 日本語版

### 各Exampleの概要

| # | ファイル | 業界 | 解決する課題 |
|---|---|---|---|
| 01 | `01_basic_usage.py` | 汎用 | ライブラリの基本的な使い方 |
| 02 | `02_ec_recommendation.py` | EC/推薦 | 推薦グラフの膨張。ニッチ商品の保護と季節商品の整理 |
| 03 | `03_knowledge_base.py` | ナレッジ管理 | 社内文書の蓄積。レガシー文書の保護と部門間の隠れた関連発見 |
| 04 | `04_medical_knowledge.py` | 医療/創薬 | 希少疾患データの保護。ドラッグリポジショニング候補の発見 |
| 05 | `05_financial_network.py` | 金融/不正検知 | 不正検知の弱いシグナルが従来手法で全滅する問題 |
| 06 | `06_iot_manufacturing.py` | IoT/製造 | 設備異常の前兆信号の保護。予知保全パターンの横展開 |
| 07 | `07_telecom_network.py` | 通信 | バックアップ経路の保護。類似ネットワーク構造の発見 |
| 08 | `08_cybersecurity.py` | サイバーセキュリティ | APT信号の保護。攻撃キャンペーンの隠れた関連発見 |
| 09 | `09_supply_chain.py` | サプライチェーン | 唯一供給元の保護。類似脆弱構造の発見 |
| 10 | `10_education_curriculum.py` | 教育 | 学際科目の保護。類似カリキュラム構造の発見 |
| 11 | `11_smart_grid.py` | エネルギー | カスケード障害前兆の保護。類似脆弱ゾーンの発見 |
| 12 | `12_academic_citation.py` | 学術 | 学際論文の保護。分野横断テーマの発見 |
| 13 | `13_agriculture_food_safety.py` | 農業/食品安全 | 病害虫痕跡シグナルの保護。地域間の汚染リスク類似構造発見 |
| 14 | `14_legal_compliance.py` | 法務/コンプライアンス | 希少判例の保護。分野横断の法的原則発見 |
| 15 | `15_hr_talent.py` | HR/人材 | 希少スキル組合せの保護。部門間の人材類似性発見 |
| 16 | `16_real_estate.py` | 不動産/都市計画 | 希少な物件特性の保護。エリア間の構造類似発見 |
| 17 | `17_insurance_actuarial.py` | 保険/アクチュアリー | 希少な請求パターンの保護。商品間のリスク相関発見 |
| 18 | `18_environmental_monitoring.py` | 環境モニタリング | 希少種・汚染パターンの保護。生態系間の類似構造発見 |
| 19 | `19_transportation.py` | 運輸/物流 | ボトルネック信号の保護と廃止路線の整理 |
| 20 | `20_social_network.py` | ソーシャルネットワーク | ブリッジユーザーの保護と非活性アカウントの整理 |
| 21 | `21_gaming.py` | オンラインゲーム | チート信号の保護とBANアカウントの整理 |
| 22 | `22_media_advertising.py` | メディア/広告 | トレンド信号の保護と廃止キャンペーンの整理 |
| 23 | `23_aviation.py` | 航空/宇宙 | 疲労信号の保護と退役部品の整理 |
| 24 | `24_pharma_manufacturing.py` | 製薬製造 | 汚染信号の保護と期限切れバッチの整理 |
| 25 | `25_water_management.py` | 水道/下水 | 水質異常信号の保護と廃止設備の整理 |
| 26 | `26_construction.py` | 建設/インフラ | 欠陥信号の保護と解体物件の整理 |
| 27 | `27_mining.py` | 鉱業/資源 | 地質信号の保護と枯渇サイトの整理 |
| 28 | `28_hospitality.py` | 観光/ホスピタリティ | 需要信号の保護と閉鎖施設の整理 |

### 共通して示していること

1. **従来手法（TTL/LRU/閾値削除）では、接続が少ないデータから先に消える**
2. **しかし「接続が少ない ≠ 価値が低い」** — 希少疾患、不正信号、異常前兆はすべて低接続
3. **本技術の希少性保護により、ゴミは除去しつつ価値あるデータを守れる**
4. **さらに整合性発見により、まだ知られていない関連を自動で見つけられる**

### 実行方法

```bash
pip install -e .

# 基本的な使い方
python examples/01_basic_usage.py

# 全Example実行
python examples/02_ec_recommendation.py
python examples/03_knowledge_base.py
python examples/04_medical_knowledge.py
python examples/05_financial_network.py
python examples/06_iot_manufacturing.py
python examples/07_telecom_network.py
python examples/08_cybersecurity.py
python examples/09_supply_chain.py
python examples/10_education_curriculum.py
python examples/11_smart_grid.py
python examples/12_academic_citation.py
python examples/13_agriculture_food_safety.py
python examples/14_legal_compliance.py
python examples/15_hr_talent.py
python examples/16_real_estate.py
python examples/17_insurance_actuarial.py
python examples/18_environmental_monitoring.py
python examples/19_transportation.py
python examples/20_social_network.py
python examples/21_gaming.py
python examples/22_media_advertising.py
python examples/23_aviation.py
python examples/24_pharma_manufacturing.py
python examples/25_water_management.py
python examples/26_construction.py
python examples/27_mining.py
python examples/28_hospitality.py
```
