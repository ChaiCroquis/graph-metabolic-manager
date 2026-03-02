#!/usr/bin/env python3
"""
Construction / Infrastructure Network Example
================================================

Simulates a construction and infrastructure network connecting
structural, electrical, plumbing, HVAC, and foundation systems.

Scenario:
- 30 building system nodes across 5 categories
- 6 rare structural defect pattern nodes (early warning signals
  for failures — losing them means defects go undetected)
- 8 garbage nodes (completed projects, demolished structures)
- Consistency discovery identifies defect-pattern-similar
  connections, enabling proactive inspection planning

The manager should:
1. Maintain active building system relationships under congestion
2. PROTECT rare defect signals (irreplaceable safety indicators)
3. Clean up completed projects and demolished structure records
4. Discover structurally similar defect-pattern vulnerabilities
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _runner import ScenarioConfig, run_industry_example

SCENARIO = ScenarioConfig(
    number=26,
    title="Construction / Infrastructure Network",
    categories={
        "Structural": [
            "Steel_Frame_A", "Concrete_Core_B", "Beam_Assembly_C",
            "Column_Grid_D", "Truss_System_E", "Shear_Wall_F",
        ],
        "Electrical": [
            "Main_Panel_1", "Sub_Panel_A", "Generator_Backup",
            "Transformer_B", "Conduit_Run_C", "Switchgear_D",
        ],
        "Plumbing": [
            "Main_Riser_1", "Branch_Line_A", "Drain_Stack_B",
            "Water_Heater_C", "Fire_Sprinkler_D", "Backflow_Prev_E",
        ],
        "HVAC": [
            "AHU_Central", "Chiller_Plant_A", "Boiler_Room_B",
            "Duct_Main_C", "VAV_Box_D", "Cooling_Tower_E",
        ],
        "Foundation": [
            "Pile_Group_1", "Mat_Foundation_A", "Caisson_B",
            "Grade_Beam_C", "Retaining_Wall_D", "Footing_Pad_E",
        ],
    },
    entity_normal="system",
    entity_rare="defect_signal",
    entity_garbage="completed",
    rare_names=[
        "Concrete_Crack_Propagation", "Rebar_Corrosion_Trace",
        "Settlement_Anomaly_Faint", "Seismic_Vulnerability_Signal",
        "Moisture_Intrusion_Precursor", "Load_Distribution_Anomaly",
    ],
    garbage_names=[
        "Completed_Project_A1", "Completed_Project_A2", "Demolished_Structure_B1",
        "Demolished_Structure_B2", "Condemned_Building_C", "Razed_Wing_D",
        "Removed_Addition_E", "Vacated_Floor_F",
    ],
    cross_links=[
        ("Foundation", "Structural"),
        ("Structural", "Electrical"),
        ("Structural", "Plumbing"),
        ("Electrical", "HVAC"),
        ("Plumbing", "HVAC"),
    ],
    normal_label="Building system nodes",
    rare_label="Defect pattern signals",
    garbage_label="Completed/demolished",
    scenario_a_desc="(Standard construction network optimization)",
    scenario_b_desc="(Critical defect signals preserved)",
    discovery_title="Defect Pattern Discovery",
    discovery_description="Finding systems with similar defect-risk profiles",
    discovery_conclusion="Structurally similar systems may share defect patterns.\n  Use this for proactive inspection and remediation planning.",
    loss_message="In construction, losing a defect signal\n  can lead to structural failures endangering occupants.",
)

if __name__ == "__main__":
    run_industry_example(SCENARIO)
