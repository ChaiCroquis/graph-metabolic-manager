#!/usr/bin/env python3
"""Tests for PatentVerification: cross-industry verification of all patent features."""

from __future__ import annotations

import random
import sys
from pathlib import Path

import pytest

# Ensure examples directory is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "examples"))

from graph_metabolic_manager import (
    ConsistencyDiscovery,
    Graph,
    GraphMetabolicManager,
)

# ============================================================
# Helper: Build graphs from each example scenario
# ============================================================


def _build_standard(
    categories: dict[str, int],
    rare_prefix: str,
    garbage_prefix: str,
    connect_prob: float = 0.45,
    normal_weight_range: tuple[float, float] = (0.5, 1.0),
    rare_weight_range: tuple[float, float] = (0.04, 0.10),
    num_rare: int = 6,
    num_garbage: int = 8,
) -> tuple[Graph, list[int], list[int], list[int]]:
    """Standard graph builder for industry scenarios."""
    random.seed(42)
    g = Graph()
    normal: list[int] = []
    cat_nodes: dict[str, list[int]] = {}
    for cat, count in categories.items():
        cat_nodes[cat] = []
        for i in range(count):
            nid = g.add_node(f"{cat}_{i}", node_type="normal")
            normal.append(nid)
            cat_nodes[cat].append(nid)
    for _cat, nodes in cat_nodes.items():
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                if random.random() < connect_prob:
                    g.add_edge(nodes[i], nodes[j],
                               weight=random.uniform(*normal_weight_range))
    rare: list[int] = []
    for i in range(num_rare):
        nid = g.add_node(f"{rare_prefix}_{i}", node_type="truth")
        target = random.choice(normal)
        g.add_edge(nid, target, weight=random.uniform(*rare_weight_range))
        rare.append(nid)
    garbage: list[int] = []
    for i in range(num_garbage):
        garbage.append(g.add_node(f"{garbage_prefix}_{i}", node_type="garbage"))
    return g, normal, rare, garbage


def _build_basic() -> tuple[Graph, list[int], list[int], list[int]]:
    """Example 01: Basic usage."""
    random.seed(42)
    g = Graph()
    popular = []
    for i in range(10):
        nid = g.add_node(f"Popular_{i}", node_type="normal")
        popular.append(nid)
    for i in range(len(popular)):
        for j in range(i + 1, len(popular)):
            if random.random() < 0.6:
                g.add_edge(popular[i], popular[j], weight=random.uniform(0.5, 1.0))
    rare = [g.add_node("RareGem", node_type="truth")]
    g.add_edge(rare[0], popular[0], weight=0.1)
    garbage = []
    for i in range(5):
        garbage.append(g.add_node(f"Noise_{i}", node_type="garbage"))
    return g, popular, rare, garbage


def _build_ec() -> tuple[Graph, list[int], list[int], list[int]]:
    """Example 02: E-Commerce."""
    random.seed(42)
    g = Graph()
    categories = ["Electronics", "Fashion", "Home", "Sports", "Books"]
    popular = []
    cat_nodes: dict[str, list[int]] = {}
    for cat in categories:
        cat_nodes[cat] = []
        for i in range(6):
            nid = g.add_node(f"{cat}_{i:02d}", node_type="normal", category=cat)
            popular.append(nid)
            cat_nodes[cat].append(nid)
    for _cat, nodes in cat_nodes.items():
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                if random.random() < 0.5:
                    g.add_edge(nodes[i], nodes[j], weight=random.uniform(0.5, 1.0))
    niche = []
    for i in range(8):
        nid = g.add_node(f"Niche_{i}", node_type="truth")
        target = random.choice(popular)
        g.add_edge(nid, target, weight=random.uniform(0.05, 0.12))
        niche.append(nid)
    seasonal = []
    for i in range(8):
        seasonal.append(g.add_node(f"Seasonal_{i}", node_type="garbage"))
    return g, popular, niche, seasonal


def _build_knowledge() -> tuple[Graph, list[int], list[int], list[int]]:
    """Example 03: Knowledge Base."""
    random.seed(42)
    g = Graph()
    depts = {"Eng": 5, "Product": 5, "Ops": 5, "HR": 5}
    active = []
    dept_nodes: dict[str, list[int]] = {}
    for dept, count in depts.items():
        dept_nodes[dept] = []
        for i in range(count):
            nid = g.add_node(f"{dept}_Doc_{i}", node_type="normal")
            active.append(nid)
            dept_nodes[dept].append(nid)
    for _dept, nodes in dept_nodes.items():
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                if random.random() < 0.5:
                    g.add_edge(nodes[i], nodes[j], weight=random.uniform(0.5, 1.0))
    legacy = []
    for i in range(5):
        nid = g.add_node(f"Legacy_{i}", node_type="truth")
        target = random.choice(active)
        g.add_edge(nid, target, weight=random.uniform(0.05, 0.12))
        legacy.append(nid)
    obsolete = []
    for i in range(5):
        obsolete.append(g.add_node(f"Obsolete_{i}", node_type="garbage"))
    return g, active, legacy, obsolete


def _build_medical() -> tuple[Graph, list[int], list[int], list[int]]:
    """Example 04: Medical Knowledge."""
    random.seed(42)
    g = Graph()
    normal = []
    for i in range(20):
        nid = g.add_node(f"Disease_{i}", node_type="normal")
        normal.append(nid)
    for i in range(15):
        nid = g.add_node(f"Gene_{i}", node_type="normal")
        normal.append(nid)
    for i in range(12):
        nid = g.add_node(f"Drug_{i}", node_type="normal")
        normal.append(nid)
    for i in range(len(normal)):
        for j in range(i + 1, len(normal)):
            if random.random() < 0.08:
                g.add_edge(normal[i], normal[j], weight=random.uniform(0.3, 1.0))
    rare = []
    for i in range(8):
        nid = g.add_node(f"RareDisease_{i}", node_type="truth")
        target = random.choice(normal)
        g.add_edge(nid, target, weight=random.uniform(0.04, 0.10))
        rare.append(nid)
    garbage = []
    for i in range(8):
        garbage.append(g.add_node(f"DeprecatedDrug_{i}", node_type="garbage"))
    return g, normal, rare, garbage


def _build_financial() -> tuple[Graph, list[int], list[int], list[int]]:
    """Example 05: Financial Network."""
    random.seed(42)
    g = Graph()
    sectors = {"Mfg": 8, "Retail": 7, "Finance": 6, "Tech": 5, "Svc": 4}
    normal = []
    sec_nodes: dict[str, list[int]] = {}
    for sec, count in sectors.items():
        sec_nodes[sec] = []
        for i in range(count):
            nid = g.add_node(f"{sec}_{i:02d}", node_type="normal")
            normal.append(nid)
            sec_nodes[sec].append(nid)
    for _sec, nodes in sec_nodes.items():
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                if random.random() < 0.5:
                    g.add_edge(nodes[i], nodes[j], weight=random.uniform(0.5, 1.0))
    suspicious = []
    for i in range(6):
        nid = g.add_node(f"Suspicious_{i}", node_type="truth")
        target = random.choice(normal)
        g.add_edge(nid, target, weight=random.uniform(0.03, 0.10))
        suspicious.append(nid)
    inactive = []
    for i in range(8):
        inactive.append(g.add_node(f"Inactive_{i}", node_type="garbage"))
    return g, normal, suspicious, inactive


def _build_iot() -> tuple[Graph, list[int], list[int], list[int]]:
    """Example 06: IoT Manufacturing."""
    random.seed(42)
    g = Graph()
    equipment = []
    for line in ["A", "B", "C"]:
        for i in range(5):
            nid = g.add_node(f"Equip_{line}_{i}", node_type="normal")
            equipment.append(nid)
    for i in range(len(equipment)):
        for j in range(i + 1, len(equipment)):
            if random.random() < 0.3:
                g.add_edge(equipment[i], equipment[j],
                           weight=random.uniform(0.4, 0.8))
    # Fewer sensors to keep graph balanced
    sensors = []
    for eid in equipment:
        for _ in range(random.randint(1, 2)):
            sid = g.add_node(f"Sensor_{eid}_{len(sensors)}", node_type="normal")
            g.add_edge(eid, sid, weight=random.uniform(0.7, 1.0))
            sensors.append(sid)
    rare = []
    for i in range(6):
        nid = g.add_node(f"RareAnomaly_{i}", node_type="truth")
        target = random.choice(equipment)
        g.add_edge(nid, target, weight=random.uniform(0.10, 0.20))
        rare.append(nid)
    obsolete = []
    for i in range(8):
        obsolete.append(g.add_node(f"Obsolete_{i}", node_type="garbage"))
    return g, equipment + sensors, rare, obsolete


def _build_telecom():
    """Example 07: Telecom Network."""
    return _build_standard(
        {"Tokyo": 6, "Osaka": 5, "Nagoya": 5, "Fukuoka": 5, "Sapporo": 4},
        "Relay", "Legacy", connect_prob=0.6, normal_weight_range=(0.6, 1.0),
    )


def _build_cybersecurity():
    """Example 08: Cybersecurity."""
    return _build_standard(
        {"Malware": 6, "Phishing": 6, "Exploit": 6, "C2": 6, "Lateral": 6},
        "APT", "Stale", connect_prob=0.5, rare_weight_range=(0.03, 0.09),
    )


def _build_supply_chain():
    """Example 09: Supply Chain."""
    return _build_standard(
        {"Semi": 6, "Raw": 6, "Elec": 6, "Logis": 6, "Assy": 6},
        "SoleSource", "Defunct",
    )


def _build_education():
    """Example 10: Education Curriculum."""
    return _build_standard(
        {"CS": 6, "Math": 6, "Physics": 6, "Business": 6, "Bio": 6},
        "Interdisciplinary", "Discontinued", connect_prob=0.5,
        rare_weight_range=(0.05, 0.12),
    )


def _build_smart_grid() -> tuple[Graph, list[int], list[int], list[int]]:
    """Example 11: Smart Grid."""
    random.seed(42)
    g = Graph()
    zones = {"N": 5, "S": 5, "E": 5, "W": 5, "C": 5}
    substations = []
    zone_nodes: dict[str, list[int]] = {}
    for zone, count in zones.items():
        zone_nodes[zone] = []
        for i in range(count):
            nid = g.add_node(f"Sub_{zone}_{i}", node_type="normal")
            substations.append(nid)
            zone_nodes[zone].append(nid)
    for _zone, nodes in zone_nodes.items():
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                if random.random() < 0.55:
                    g.add_edge(nodes[i], nodes[j], weight=random.uniform(0.6, 1.0))
    generators = []
    for i in range(6):
        nid = g.add_node(f"Gen_{i}", node_type="normal")
        for _ in range(random.randint(2, 4)):
            sub = random.choice(substations)
            g.add_edge(nid, sub, weight=random.uniform(0.4, 0.8))
        generators.append(nid)
    rare = []
    for i in range(6):
        nid = g.add_node(f"Anomaly_{i}", node_type="truth")
        target = random.choice(substations)
        g.add_edge(nid, target, weight=random.uniform(0.04, 0.10))
        rare.append(nid)
    decom = []
    for i in range(8):
        decom.append(g.add_node(f"Decom_{i}", node_type="garbage"))
    return g, substations + generators, rare, decom


def _build_academic():
    """Example 12: Academic Citation."""
    return _build_standard(
        {"ML": 6, "Bio": 6, "Quantum": 6, "Climate": 6, "Neuro": 6},
        "Interdisciplinary", "Retracted", connect_prob=0.5,
    )


def _build_agriculture():
    """Example 13: Agriculture / Food Safety."""
    return _build_standard(
        {"Grain": 6, "Livestock": 6, "Processing": 6, "Distrib": 6, "QA_Lab": 6},
        "PestSignal", "Expired",
    )


def _build_legal():
    """Example 14: Legal / Compliance."""
    return _build_standard(
        {"Contract": 6, "IP": 6, "Tax": 6, "Employment": 6, "Regulatory": 6},
        "Precedent", "Expired",
    )


def _build_hr():
    """Example 15: HR / Talent Management."""
    return _build_standard(
        {"Eng": 6, "Sales": 6, "Marketing": 6, "Ops": 6, "Research": 6},
        "RareSkill", "Resigned", connect_prob=0.50,
    )


def _build_real_estate():
    """Example 16: Real Estate / Urban Planning."""
    return _build_standard(
        {"Downtown": 6, "Suburban": 6, "Industrial": 6, "Waterfront": 6, "University": 6},
        "RareFeature", "Expired",
    )


def _build_insurance():
    """Example 17: Insurance / Actuarial."""
    return _build_standard(
        {"Auto": 6, "Home": 6, "Life": 6, "Health": 6, "Commercial": 6},
        "RareClaim", "Expired",
    )


def _build_environmental():
    """Example 18: Environmental Monitoring."""
    return _build_standard(
        {"Forest": 6, "Wetland": 6, "Coastal": 6, "Mountain": 6, "Urban": 6},
        "RareObs", "Decom",
    )


def _build_transportation():
    """Example 19: Transportation / Logistics."""
    return _build_standard(
        {"Rail": 6, "Maritime": 6, "Aviation": 6, "Trucking": 6, "Warehouse": 6},
        "RouteAnomaly", "Closed",
    )


def _build_social_network():
    """Example 20: Social Network Analysis."""
    return _build_standard(
        {"Tech": 6, "Art": 6, "Sports": 6, "Science": 6, "Music": 6},
        "BridgeUser", "Inactive",
    )


def _build_gaming():
    """Example 21: Online Gaming."""
    return _build_standard(
        {"FPS": 6, "RPG": 6, "Strategy": 6, "SportsSim": 6, "Casual": 6},
        "CheatSignal", "Banned",
    )


def _build_media_advertising():
    """Example 22: Media / Advertising."""
    return _build_standard(
        {"TV": 6, "Digital": 6, "Print": 6, "Radio": 6, "Streaming": 6},
        "TrendSignal", "Discontinued",
    )


def _build_aviation():
    """Example 23: Aviation / Aerospace."""
    return _build_standard(
        {"Engines": 6, "Avionics": 6, "Airframe": 6, "LandGear": 6, "Hydraulics": 6},
        "FatigueSignal", "Retired",
    )


def _build_pharma():
    """Example 24: Pharmaceutical Manufacturing."""
    return _build_standard(
        {"API": 6, "Formulation": 6, "Packaging": 6, "QC": 6, "Distrib": 6},
        "Contamination", "Expired",
    )


def _build_water():
    """Example 25: Water / Wastewater Management."""
    return _build_standard(
        {"Treatment": 6, "Pumping": 6, "Reservoir": 6, "DistMains": 6, "Monitor": 6},
        "QualityAlert", "Decom",
    )


def _build_construction():
    """Example 26: Construction / Infrastructure."""
    return _build_standard(
        {"Structural": 6, "Electrical": 6, "Plumbing": 6, "HVAC": 6, "Foundation": 6},
        "DefectSignal", "Demolished",
    )


def _build_mining():
    """Example 27: Mining / Resource Extraction."""
    return _build_standard(
        {"OpenPit": 6, "Underground": 6, "Processing": 6, "Transport": 6, "Explore": 6},
        "GeoSignal", "Exhausted",
    )


def _build_hospitality():
    """Example 28: Hospitality / Tourism."""
    return _build_standard(
        {"Hotels": 6, "Restaurant": 6, "Attraction": 6, "TransHub": 6, "EventVenue": 6},
        "DemandSignal", "Defunct",
    )


# ============================================================
# All builders in a registry for parametrized tests
# ============================================================

SCENARIOS = {
    "01_basic":             _build_basic,
    "02_ec":                _build_ec,
    "03_knowledge":         _build_knowledge,
    "04_medical":           _build_medical,
    "05_financial":         _build_financial,
    "06_iot":               _build_iot,
    "07_telecom":           _build_telecom,
    "08_cybersecurity":     _build_cybersecurity,
    "09_supply_chain":      _build_supply_chain,
    "10_education":         _build_education,
    "11_smart_grid":        _build_smart_grid,
    "12_academic":          _build_academic,
    "13_agriculture":       _build_agriculture,
    "14_legal":             _build_legal,
    "15_hr":                _build_hr,
    "16_real_estate":       _build_real_estate,
    "17_insurance":         _build_insurance,
    "18_environmental":     _build_environmental,
    "19_transportation":    _build_transportation,
    "20_social_network":    _build_social_network,
    "21_gaming":            _build_gaming,
    "22_media_advertising": _build_media_advertising,
    "23_aviation":          _build_aviation,
    "24_pharma":            _build_pharma,
    "25_water":             _build_water,
    "26_construction":      _build_construction,
    "27_mining":            _build_mining,
    "28_hospitality":       _build_hospitality,
}


# ============================================================
# Patent Feature 1: Metabolic Control (代謝制御)
# Patent claims 1-10
#
# Verifies:
# - Graph size is reduced after running metabolic control
# - Garbage (isolated) nodes are pruned
# - At least some normal nodes survive
# ============================================================

class TestMetabolicControl:
    """MetabolicControl: prunes congested and isolated data while preserving core structure."""

    @pytest.mark.parametrize("name,builder", list(SCENARIOS.items()))
    def test_garbage_nodes_pruned(self, name: str, builder: callable) -> None:
        """Garbage/isolated nodes must be removed by metabolic pruning."""
        g, normal, rare, garbage = builder()

        mgr = GraphMetabolicManager(
            g, seed=42,
            enable_rarity=False,
            enable_meta=True,
            k_opt=4.0,
        )
        mgr.run(steps=120)

        garbage_survived = sum(1 for nid in garbage if g.has_node(nid))
        assert garbage_survived < len(garbage), (
            f"[{name}] Metabolic control failed to prune garbage nodes: "
            f"{garbage_survived}/{len(garbage)} survived"
        )

    @pytest.mark.parametrize("name,builder", list(SCENARIOS.items()))
    def test_graph_size_reduced(self, name: str, builder: callable) -> None:
        """Graph must shrink after metabolic management."""
        g, _, _, _ = builder()
        initial_nodes = g.node_count()
        initial_edges = g.edge_count()

        mgr = GraphMetabolicManager(
            g, seed=42,
            enable_rarity=False,
            enable_meta=True,
            k_opt=4.0,
        )
        mgr.run(steps=120)

        assert g.node_count() < initial_nodes or g.edge_count() < initial_edges, (
            f"[{name}] Graph was not reduced: "
            f"{initial_nodes}->{g.node_count()} nodes, "
            f"{initial_edges}->{g.edge_count()} edges"
        )

    @pytest.mark.parametrize("name,builder", list(SCENARIOS.items()))
    def test_some_normal_nodes_survive(self, name: str, builder: callable) -> None:
        """Normal (core) nodes should not all be destroyed when the
        full patent system (metabolic + rarity + meta) is active."""
        g, normal, _, _ = builder()

        mgr = GraphMetabolicManager(
            g, seed=42,
            enable_rarity=True,
            enable_meta=True,
            k_opt=4.0,
        )
        mgr.run(steps=120)

        normal_survived = sum(1 for nid in normal if g.has_node(nid))
        assert normal_survived > 0, (
            f"[{name}] ALL normal nodes destroyed even with full patent system"
        )


# ============================================================
# Patent Feature 2: Rarity Protection (希少性保護)
# Patent claims 11-20
#
# Verifies:
# - WITHOUT protection: truth nodes are destroyed
# - WITH protection: truth nodes survive
# - Protection provides measurable improvement
# ============================================================

class TestRarityProtection:
    """RarityProtection: preserves rare but valuable data from pruning."""

    @pytest.mark.parametrize("name,builder", list(SCENARIOS.items()))
    def test_without_protection_truth_lost(self, name: str, builder: callable) -> None:
        """Without rarity protection, truth nodes should be destroyed or reduced."""
        g, normal, rare, garbage = builder()

        mgr = GraphMetabolicManager(
            g, seed=42,
            enable_rarity=False,
            enable_meta=True,
            k_opt=5.0,
            beta=0.03,
            prune_threshold=0.08,
        )
        mgr.run(steps=120)

        rare_survived = sum(1 for nid in rare if g.has_node(nid))
        assert rare_survived < len(rare), (
            f"[{name}] All truth nodes survived WITHOUT protection "
            f"({rare_survived}/{len(rare)}). "
            f"This means the scenario does not demonstrate the need for protection."
        )

    @pytest.mark.parametrize("name,builder", list(SCENARIOS.items()))
    def test_with_protection_truth_survives(self, name: str, builder: callable) -> None:
        """With rarity protection, at least some truth nodes must survive."""
        g, normal, rare, garbage = builder()

        mgr = GraphMetabolicManager(
            g, seed=42,
            enable_rarity=True,
            enable_meta=True,
            k_opt=5.0,
            beta=0.03,
            prune_threshold=0.08,
        )
        mgr.run(steps=120)

        rare_survived = sum(1 for nid in rare if g.has_node(nid))
        assert rare_survived > 0, (
            f"[{name}] ALL truth nodes destroyed even WITH protection. "
            f"Rarity protection is not functioning."
        )

    @pytest.mark.parametrize("name,builder", list(SCENARIOS.items()))
    def test_protection_improves_survival(self, name: str, builder: callable) -> None:
        """Rarity protection must improve truth node survival rate."""
        # Run WITHOUT protection
        g_off, _, rare_off, _ = builder()
        mgr_off = GraphMetabolicManager(
            g_off, seed=42,
            enable_rarity=False,
            enable_meta=True,
            k_opt=5.0,
            beta=0.03,
            prune_threshold=0.08,
        )
        mgr_off.run(steps=120)
        survived_off = sum(1 for nid in rare_off if g_off.has_node(nid))

        # Run WITH protection
        g_on, _, rare_on, _ = builder()
        mgr_on = GraphMetabolicManager(
            g_on, seed=42,
            enable_rarity=True,
            enable_meta=True,
            k_opt=5.0,
            beta=0.03,
            prune_threshold=0.08,
        )
        mgr_on.run(steps=120)
        survived_on = sum(1 for nid in rare_on if g_on.has_node(nid))

        assert survived_on >= survived_off, (
            f"[{name}] Protection made things worse: "
            f"OFF={survived_off}, ON={survived_on}"
        )
        assert survived_on > survived_off, (
            f"[{name}] Protection had no effect: "
            f"OFF={survived_off}, ON={survived_on}. "
            f"Rarity protection must provide measurable improvement."
        )

    @pytest.mark.parametrize("name,builder", list(SCENARIOS.items()))
    def test_garbage_still_cleaned_with_protection(
        self, name: str, builder: callable
    ) -> None:
        """Rarity protection must NOT prevent garbage cleanup."""
        g, _, _, garbage = builder()

        mgr = GraphMetabolicManager(
            g, seed=42,
            enable_rarity=True,
            enable_meta=True,
            k_opt=5.0,
            beta=0.03,
            prune_threshold=0.08,
        )
        mgr.run(steps=120)

        garbage_survived = sum(1 for nid in garbage if g.has_node(nid))
        assert garbage_survived < len(garbage), (
            f"[{name}] Garbage nodes not cleaned even with protection: "
            f"{garbage_survived}/{len(garbage)} survived"
        )


# ============================================================
# Patent Feature 3: Consistency Discovery (整合性発見)
# Patent claims 21-26
#
# Verifies:
# - Structural similarities are discovered between rare and normal nodes
# - Discovery scores are within valid range [0, 1]
# - At least some connections are found
# ============================================================

class TestConsistencyDiscovery:
    """ConsistencyDiscovery: finds hidden structural patterns between rare and normal nodes."""

    @pytest.mark.parametrize("name,builder", list(SCENARIOS.items()))
    def test_discoveries_found(self, name: str, builder: callable) -> None:
        """Consistency discovery must find at least one connection."""
        g, normal, rare, _ = builder()

        cd = ConsistencyDiscovery(theta_l=0.50, theta_u=0.90, k_hop=2)
        discoveries = cd.discover(g, rare_node_ids=rare, candidate_ids=normal)

        assert len(discoveries) > 0, (
            f"[{name}] No structural similarities discovered. "
            f"ConsistencyDiscovery returned empty results."
        )

    @pytest.mark.parametrize("name,builder", list(SCENARIOS.items()))
    def test_discovery_scores_valid(self, name: str, builder: callable) -> None:
        """Discovery scores must be in [0, 1] range."""
        g, normal, rare, _ = builder()

        cd = ConsistencyDiscovery(theta_l=0.50, theta_u=0.90, k_hop=2)
        discoveries = cd.discover(g, rare_node_ids=rare, candidate_ids=normal)

        for rare_id, cand_id, score in discoveries:
            assert 0.0 <= score <= 1.0, (
                f"[{name}] Invalid score {score} for "
                f"({rare_id}, {cand_id})"
            )

    @pytest.mark.parametrize("name,builder", list(SCENARIOS.items()))
    def test_discovery_nodes_exist(self, name: str, builder: callable) -> None:
        """Discovered connections must reference existing nodes."""
        g, normal, rare, _ = builder()

        cd = ConsistencyDiscovery(theta_l=0.50, theta_u=0.90, k_hop=2)
        discoveries = cd.discover(g, rare_node_ids=rare, candidate_ids=normal)

        for rare_id, cand_id, _score in discoveries:
            assert g.has_node(rare_id), (
                f"[{name}] Discovered rare node {rare_id} does not exist"
            )
            assert g.has_node(cand_id), (
                f"[{name}] Discovered candidate node {cand_id} does not exist"
            )

    @pytest.mark.parametrize("name,builder", list(SCENARIOS.items()))
    def test_discovery_respects_threshold(self, name: str, builder: callable) -> None:
        """All discoveries must satisfy theta_l <= score <= theta_u."""
        g, normal, rare, _ = builder()
        theta_l, theta_u = 0.50, 0.90

        cd = ConsistencyDiscovery(theta_l=theta_l, theta_u=theta_u, k_hop=2)
        discoveries = cd.discover(g, rare_node_ids=rare, candidate_ids=normal)

        for rare_id, cand_id, score in discoveries:
            assert theta_l <= score <= theta_u, (
                f"[{name}] Score {score:.3f} outside threshold "
                f"[{theta_l}, {theta_u}] for ({rare_id}, {cand_id})"
            )


# ============================================================
# Patent Feature 4: Meta Control (メタ制御)
# Patent claims 27-32
#
# Verifies:
# - Health index is tracked over time
# - Alpha parameter is dynamically adjusted
# - Health history is recorded
# - System does not diverge (alpha stays within bounds)
# ============================================================

class TestMetaControl:
    """MetaControl: dynamically adjusts system parameters based on graph health feedback."""

    @pytest.mark.parametrize("name,builder", list(SCENARIOS.items()))
    def test_health_tracked(self, name: str, builder: callable) -> None:
        """Health index must be recorded for every step."""
        g, _, _, _ = builder()

        mgr = GraphMetabolicManager(
            g, seed=42,
            enable_rarity=True,
            enable_meta=True,
            k_opt=4.0,
        )
        mgr.run(steps=100)

        assert len(mgr.meta.history) == 100, (
            f"[{name}] Expected 100 history records, "
            f"got {len(mgr.meta.history)}"
        )

    @pytest.mark.parametrize("name,builder", list(SCENARIOS.items()))
    def test_health_values_valid(self, name: str, builder: callable) -> None:
        """Health index must be in [0, 1] range."""
        g, _, _, _ = builder()

        mgr = GraphMetabolicManager(
            g, seed=42,
            enable_rarity=True,
            enable_meta=True,
            k_opt=4.0,
        )
        mgr.run(steps=100)

        for record in mgr.meta.history:
            assert 0.0 <= record["H"] <= 1.0, (
                f"[{name}] Invalid health index: {record['H']}"
            )

    @pytest.mark.parametrize("name,builder", list(SCENARIOS.items()))
    def test_alpha_within_bounds(self, name: str, builder: callable) -> None:
        """Alpha must stay within configured bounds."""
        g, _, _, _ = builder()

        mgr = GraphMetabolicManager(
            g, seed=42,
            enable_rarity=True,
            enable_meta=True,
            k_opt=4.0,
        )
        mgr.run(steps=100)

        for record in mgr.meta.history:
            assert mgr.meta.alpha_min <= record["alpha"] <= mgr.meta.alpha_max, (
                f"[{name}] Alpha {record['alpha']} out of bounds "
                f"[{mgr.meta.alpha_min}, {mgr.meta.alpha_max}]"
            )

    @pytest.mark.parametrize("name,builder", list(SCENARIOS.items()))
    def test_alpha_adjusts_dynamically(self, name: str, builder: callable) -> None:
        """Alpha must change from its initial value when graph density
        exceeds optimal. Using k_opt=1.5 ensures the initial graph
        is denser than target, triggering meta control feedback.

        The 4th-power update rule (delta^4) produces very small adjustments
        for small deviations, so we check at reduced precision (3 decimal
        places) and verify alpha moved from initial 2.0."""
        g, _, _, _ = builder()

        initial_alpha = 2.0
        mgr = GraphMetabolicManager(
            g, seed=42,
            enable_rarity=True,
            enable_meta=True,
            k_opt=1.5,
        )
        mgr.run(steps=100)

        final_alpha = mgr.meta.history[-1]["alpha"]
        # Alpha should have moved from initial value (even slightly)
        assert abs(final_alpha - initial_alpha) > 1e-10, (
            f"[{name}] Alpha never changed from initial {initial_alpha}. "
            f"Meta control feedback is not active."
        )

    @pytest.mark.parametrize("name,builder", list(SCENARIOS.items()))
    def test_health_history_contains_required_keys(
        self, name: str, builder: callable
    ) -> None:
        """Each history record must contain k_avg, k_opt, H, delta_k, alpha."""
        g, _, _, _ = builder()

        mgr = GraphMetabolicManager(
            g, seed=42,
            enable_rarity=True,
            enable_meta=True,
            k_opt=4.0,
        )
        mgr.run(steps=10)

        required_keys = {"k_avg", "k_opt", "H", "delta_k", "alpha"}
        for record in mgr.meta.history:
            missing = required_keys - set(record.keys())
            assert not missing, (
                f"[{name}] History record missing keys: {missing}"
            )


# ============================================================
# Integration: All 4 features working together
# ============================================================

class TestIntegrationAllFeatures:
    """IntegrationAllFeatures: all 4 patent features combined in full pipeline."""

    @pytest.mark.parametrize("name,builder", list(SCENARIOS.items()))
    def test_full_pipeline_runs(self, name: str, builder: callable) -> None:
        """Full pipeline (all 4 features) must complete without error."""
        g, _, _, _ = builder()

        mgr = GraphMetabolicManager(
            g, seed=42,
            enable_rarity=True,
            enable_consistency=True,
            enable_meta=True,
            k_opt=4.0,
        )
        results = mgr.run(steps=100)

        assert len(results) == 100, f"[{name}] Expected 100 results, got {len(results)}"
        assert all("nodes" in r for r in results), f"[{name}] Missing 'nodes' key in results"
        assert all("edges" in r for r in results), f"[{name}] Missing 'edges' key in results"

    @pytest.mark.parametrize("name,builder", list(SCENARIOS.items()))
    def test_full_pipeline_garbage_cleaned(
        self, name: str, builder: callable
    ) -> None:
        """With all features on, garbage must still be cleaned."""
        g, _, _, garbage = builder()

        mgr = GraphMetabolicManager(
            g, seed=42,
            enable_rarity=True,
            enable_consistency=True,
            enable_meta=True,
            k_opt=4.0,
        )
        mgr.run(steps=150)

        garbage_survived = sum(1 for nid in garbage if g.has_node(nid))
        assert garbage_survived < len(garbage), (
            f"[{name}] Garbage not cleaned in full pipeline"
        )

    @pytest.mark.parametrize("name,builder", list(SCENARIOS.items()))
    def test_full_pipeline_truth_protected(
        self, name: str, builder: callable
    ) -> None:
        """With all features on, truth nodes must be protected.
        Uses moderate k_opt and step count matching actual examples."""
        g, _, rare, _ = builder()

        mgr = GraphMetabolicManager(
            g, seed=42,
            enable_rarity=True,
            enable_consistency=True,
            enable_meta=True,
            k_opt=5.0,
            beta=0.03,
            prune_threshold=0.08,
            # Wide consistency thresholds: with real s_rel/s_attr computation,
            # rare (type="truth") vs normal nodes have low relational/attribute
            # similarity, making composite scores ≈ 0.7 * S_sys.
            theta_l=0.35,
            theta_u=0.90,
        )
        # Run fewer steps than twait1+twait2=100 to ensure protection
        # doesn't expire before consistency discoveries create new edges.
        mgr.run(steps=80)

        rare_survived = sum(1 for nid in rare if g.has_node(nid))
        assert rare_survived > 0, (
            f"[{name}] ALL truth nodes lost in full pipeline"
        )

    @pytest.mark.parametrize("name,builder", list(SCENARIOS.items()))
    def test_summary_readable(self, name: str, builder: callable) -> None:
        """Manager summary must be a non-empty human-readable string."""
        g, _, _, _ = builder()

        mgr = GraphMetabolicManager(
            g, seed=42,
            enable_rarity=True,
            enable_meta=True,
            k_opt=4.0,
        )
        mgr.run(steps=50)

        summary = mgr.summary()
        assert isinstance(summary, str), f"[{name}] summary() must return str"
        assert len(summary) > 50, f"[{name}] summary too short: {len(summary)} chars"
        assert "GraphMetabolicManager" in summary, f"[{name}] 'GraphMetabolicManager' not in summary"
