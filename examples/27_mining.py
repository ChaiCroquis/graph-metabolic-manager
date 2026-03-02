#!/usr/bin/env python3
"""
Mining / Resource Extraction Network Example
===============================================

Simulates a mining and resource extraction network connecting
open pit operations, underground mines, processing plants,
transport systems, and exploration sites.

Scenario:
- 30 mining operation nodes across 5 categories
- 6 rare geological/safety pattern nodes (early warning signals
  for hazards — losing them means risks go undetected)
- 8 garbage nodes (exhausted pits, closed shafts)
- Consistency discovery identifies geological-similar
  patterns, enabling proactive hazard planning

The manager should:
1. Maintain active mining relationships under congestion
2. PROTECT rare geological signals (irreplaceable safety indicators)
3. Clean up exhausted pits and closed shaft records
4. Discover structurally similar geological vulnerabilities
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _runner import ScenarioConfig, run_industry_example

SCENARIO = ScenarioConfig(
    number=27,
    title="Mining / Resource Extraction Network",
    categories={
        "Open_Pit": [
            "Pit_Alpha", "Pit_Beta", "Pit_Gamma",
            "Strip_Mine_A", "Quarry_B", "Dredge_Op_C",
        ],
        "Underground": [
            "Shaft_Main_1", "Shaft_Ventilation_A", "Drift_Level_3",
            "Stope_Block_B", "Crosscut_C", "Winze_D",
        ],
        "Processing": [
            "Crusher_Primary", "Ball_Mill_A", "Flotation_Cell_B",
            "Leach_Pad_C", "Smelter_D", "Refinery_E",
        ],
        "Transport": [
            "Haul_Road_Main", "Conveyor_Belt_A", "Rail_Siding_B",
            "Load_Out_C", "Slurry_Pipeline_D", "Truck_Fleet_E",
        ],
        "Exploration": [
            "Drill_Site_1", "Drill_Site_2", "Core_Storage_A",
            "Geophysics_Camp_B", "Assay_Lab_C", "Survey_Base_D",
        ],
    },
    entity_normal="operation",
    entity_rare="geological_signal",
    entity_garbage="exhausted",
    rare_names=[
        "Rare_Earth_Deposit_Trace", "Seismic_Precursor_Faint",
        "Groundwater_Intrusion_Signal", "Ore_Grade_Anomaly",
        "Slope_Stability_Warning", "Methane_Pocket_Indicator",
    ],
    garbage_names=[
        "Exhausted_Pit_A1", "Exhausted_Pit_A2", "Closed_Shaft_B1",
        "Closed_Shaft_B2", "Abandoned_Drift_C", "Flooded_Level_D",
        "Depleted_Zone_E", "Reclaimed_Site_F",
    ],
    cross_links=[
        ("Open_Pit", "Processing"),
        ("Underground", "Processing"),
        ("Processing", "Transport"),
        ("Exploration", "Open_Pit"),
        ("Exploration", "Underground"),
    ],
    normal_label="Operation nodes",
    rare_label="Geological/safety signals",
    garbage_label="Exhausted/closed",
    scenario_a_desc="(Standard mining network optimization)",
    scenario_b_desc="(Critical geological signals preserved)",
    discovery_title="Geological Vulnerability Pattern Discovery",
    discovery_description="Finding operations with similar geological-risk profiles",
    discovery_conclusion="Structurally similar operations may share geological risks.\n  Use this for proactive hazard and safety planning.",
    loss_message="In mining, losing a geological signal\n  can lead to collapses, floods, or toxic gas events.",
)

if __name__ == "__main__":
    run_industry_example(SCENARIO)
