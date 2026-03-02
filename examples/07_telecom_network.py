#!/usr/bin/env python3
"""
Telecommunications Network Example
====================================

Simulates a telecommunications infrastructure where routers,
switches, and links form a large network topology.

Scenario:
- 25 core routers in 5 regional clusters with heavy traffic
- 6 rare alternative routes (backup paths through minor nodes
  that are critical during outages - must NOT be deleted)
- 8 decommissioned nodes (legacy equipment, should be removed)
- Consistency discovery identifies regions with structurally
  similar topology, enabling unified maintenance planning

The manager should:
1. Maintain core routing mesh under traffic-based congestion
2. PROTECT rare backup routes (they are the only failover paths)
3. Clean up decommissioned legacy nodes
4. Discover structurally similar network segments
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _runner import ScenarioConfig, run_industry_example

SCENARIO = ScenarioConfig(
    number=7,
    title="Telecommunications Network",
    categories={
        "Tokyo": [
            "Tokyo_Router_00", "Tokyo_Router_01", "Tokyo_Router_02",
            "Tokyo_Router_03", "Tokyo_Router_04", "Tokyo_Router_05",
        ],
        "Osaka": [
            "Osaka_Router_00", "Osaka_Router_01", "Osaka_Router_02",
            "Osaka_Router_03", "Osaka_Router_04",
        ],
        "Nagoya": [
            "Nagoya_Router_00", "Nagoya_Router_01", "Nagoya_Router_02",
            "Nagoya_Router_03", "Nagoya_Router_04",
        ],
        "Fukuoka": [
            "Fukuoka_Router_00", "Fukuoka_Router_01", "Fukuoka_Router_02",
            "Fukuoka_Router_03", "Fukuoka_Router_04",
        ],
        "Sapporo": [
            "Sapporo_Router_00", "Sapporo_Router_01",
            "Sapporo_Router_02", "Sapporo_Router_03",
        ],
    },
    entity_normal="core_router",
    entity_rare="backup_relay",
    entity_garbage="legacy",
    rare_names=[
        "Relay_Niigata", "Relay_Kanazawa", "Relay_Hiroshima",
        "Relay_Sendai", "Relay_Matsuyama", "Relay_Naha",
    ],
    garbage_names=[
        "Legacy_ATM_1", "Legacy_ATM_2", "Old_ISDN_Switch",
        "Retired_PBX_A", "Retired_PBX_B", "Analog_Relay_1",
        "Analog_Relay_2", "Decomm_Sat_Link",
    ],
    cross_links=[
        ("Tokyo", "Osaka"), ("Tokyo", "Nagoya"), ("Tokyo", "Fukuoka"),
        ("Tokyo", "Sapporo"), ("Osaka", "Nagoya"), ("Osaka", "Fukuoka"),
        ("Osaka", "Sapporo"), ("Nagoya", "Fukuoka"), ("Nagoya", "Sapporo"),
        ("Fukuoka", "Sapporo"),
    ],
    normal_label="Core routers",
    rare_label="Backup relays",
    garbage_label="Legacy equipment",
    scenario_a_desc="(Traditional network pruning)",
    scenario_b_desc="(Backup routes preserved)",
    discovery_title="Network Segment Similarity",
    discovery_description="Finding regions with similar topology",
    discovery_conclusion="Regions with similar topology can share\n  maintenance playbooks and failover procedures.",
    loss_message="In telecom, losing a backup route means a single\n  fiber cut can isolate an entire region.",
    # Non-default parameters
    connect_prob=0.6,
    cross_link_attempts=2,
    cross_link_prob=0.35,
    normal_weight_range=(0.6, 1.0),
    cross_weight_range=(0.2, 0.5),
    k_opt=4.5,
)

if __name__ == "__main__":
    run_industry_example(SCENARIO)
