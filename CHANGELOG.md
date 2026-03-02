# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [0.2.1] - 2026-03-02

### Changed

- **License**: MIT → Apache License 2.0 with Patent Exclusion clause
  - Apache 2.0 Section 3 (patent grant) explicitly excludes Claims 1-50
    of Japanese Patent Application No. 2026-027032
  - Resolves ambiguity between MIT's "without restriction" and patent rights
  - `PATENT_NOTICE.md` updated with dual licensing structure explanation

### Added

- **Technical paper series** (`docs/paper-series/`, 6 articles)
  - Part 1: Overview — problem definition and 4-component architecture
  - Part 2: Metabolic control — adaptive decay with O(1)/edge
  - Part 3: Rarity protection — two-phase review with 28-industry comparison
  - Part 4: Consistency discovery — Laplacian eigenvalues and sandwich threshold
  - Part 5: Meta control — health index and 4th-power feedback rule
  - Part 6: Verification — 28 industries x 629 tests empirical evaluation

---

## [0.2.0] - 2026-03-01

### Added

- **Hierarchy layer system** (`manager.py`)
  - Differential processing intervals per layer (dt_edge=5, dt_core=3, dt_rare=1)
  - Activity-based automatic layer promotion (edge → core)
  - `enable_hierarchy` parameter in `GraphMetabolicManager`
  - `_update_activity()` — Exponential moving average activity tracking
  - `_update_layers()` — Automatic layer assignment based on activity scores
  - `_compute_skip_layers()` — Per-step layer skip logic

- **Enhanced consistency discovery** (`consistency.py`)
  - `relational_similarity()` — Jaccard coefficient of neighborhoods
  - `attribute_similarity()` — Type match + metadata overlap scoring
  - Composite score: S = (7×S_sys + 2×S_rel + 1×S_attr) / 10
  - Per-pair auto-computation of s_rel and s_attr when not overridden

- **Hierarchy layer tests** (`tests/test_hierarchy.py`)
  - 13 tests covering layer assignment, skip logic, activity tracking

- **Custom TRACE log level** (`_logging.py`)
  - TRACE level (5) below DEBUG (10) for patent formula visibility
  - Per-edge decay formula traces in `metabolic.py` (Claims 1–10)
  - Phase transition traces in `rarity.py` (Claims 11–20)
  - Composite score breakdown traces in `consistency.py` (Claims 21–26)
  - Health feedback loop traces in `meta_control.py` (Claims 27–32)
  - Step orchestration traces in `manager.py`
  - Enable with `logging.basicConfig(level=5)`

- **Parameter validation** — `ValueError` in all constructors
  - `MetabolicControl`: alpha > 0, beta >= 0, gamma >= 0
  - `RarityProtection`: twait1 > 0, twait2 > 0
  - `ConsistencyDiscovery`: theta_l/theta_u in [0,1], theta_l <= theta_u
  - `MetaControl`: k_opt > 0, h_target in [0,1], alpha_min < alpha_max
  - `Graph.add_edge`: no self-loops, endpoints must exist, weight >= 0

- **TRACE logging tests** (`tests/test_trace_logging.py`)
  - 9 tests covering level registration, output, and public API

### Changed

- **Examples 07–28 consolidated** — Shared runner `examples/_runner.py`
  eliminates ~3,800 lines of duplicated template code.  Each example is
  now a thin `ScenarioConfig` data file (~45–60 lines).
- **Test builders consolidated** — `_build_standard()` factory function
  in `test_patent_verification.py` replaces 20 identical builder functions.
- **Improved type annotations** across all core modules:
  - `dict` → `dict[str, int]`, `dict[str, float]`, `dict[str, Any]`, etc.
  - `Node.metadata: dict` → `dict[str, object]`
  - `ConsistencyDiscovery._repr_cache: dict` → `dict[int, np.ndarray]`
- `GraphMetabolicManager.step()` → `dict[str, Any]` return type
- `GraphMetabolicManager.run()` → `list[dict[str, Any]]` return type

### Removed

- `tests/test_all.py` — Deprecated aggregate test file, superseded by
  individual pytest-based test modules.

---

## [0.1.0] - 2026-02-28

### Added

- **Core library** (`graph_metabolic_manager/`)
  - `Graph` — Graph data structure with node/edge management
  - `MetabolicControl` — Congestion-based adaptive edge decay (Patent Claims 1–10)
  - `RarityProtection` — Two-phase review for rare node preservation (Patent Claims 11–20)
  - `ConsistencyDiscovery` — Laplacian eigenvalue structural similarity (Patent Claims 21–26)
  - `MetaControl` — Health-based feedback loop for parameter tuning (Patent Claims 27–32)
  - `GraphMetabolicManager` — Unified interface combining all components

- **28 industry examples** (`examples/`)
  - 01: Basic Usage
  - 02: E-Commerce Recommendation
  - 03: Enterprise Knowledge Base
  - 04: Medical Knowledge Graph
  - 05: Financial Transaction Network
  - 06: IoT / Manufacturing Sensor Network
  - 07: Telecommunications Network
  - 08: Cybersecurity Threat Intelligence
  - 09: Supply Chain Network
  - 10: Education / Curriculum Network
  - 11: Smart Grid / Energy Network
  - 12: Academic Citation Network
  - 13: Agriculture / Food Safety
  - 14: Legal / Compliance
  - 15: HR / Talent Management
  - 16: Real Estate / Urban Planning
  - 17: Insurance / Actuarial
  - 18: Environmental Monitoring
  - 19: Transportation / Logistics
  - 20: Social Network Analysis
  - 21: Online Gaming
  - 22: Media / Advertising
  - 23: Aviation / Aerospace
  - 24: Pharmaceutical Manufacturing
  - 25: Water / Wastewater Management
  - 26: Construction / Infrastructure
  - 27: Mining / Resource Extraction
  - 28: Hospitality / Tourism

- **629 tests** (`tests/`)
  - 69 core algorithm tests (9 test files)
  - 560 patent verification tests (28 industries × 20 tests)

- **Documentation** (`docs/`)
  - Algorithm overview
  - Examples guide (28 industry scenarios)
  - Patent claim mapping (claims ↔ code ↔ examples)
  - Verification report

- **Benchmarks** (`benchmarks/`)
  - Scalability profiling script (100 → 100,000 nodes)

- **Development tooling**
  - GitHub Actions CI (Python 3.10–3.13, ruff + mypy + pytest)
  - PEP 561 `py.typed` marker
  - ruff, mypy, pytest configuration in `pyproject.toml`

### Patent

- Japanese Patent Application No. 2026-027032
- "Data Structure Management System Using Rarity Protection and Consistency Discovery"
- Filed: February 24, 2026
- 50 claims (48 system + 1 method + 1 program)
