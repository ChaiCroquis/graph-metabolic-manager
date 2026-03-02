#!/usr/bin/env python3
"""
Aviation / Aerospace Network Example
=======================================

Simulates an aviation and aerospace network connecting engine systems,
avionics, airframe components, landing gear, and hydraulic systems.

Scenario:
- 30 component nodes across 5 categories
- 6 rare failure-mode pattern nodes (early warning signals
  for defects — losing them means failures go undetected)
- 8 garbage nodes (retired components, superseded parts)
- Consistency discovery identifies failure-mode-similar
  patterns, enabling proactive maintenance planning

The manager should:
1. Maintain active component relationships under congestion
2. PROTECT rare failure-mode signals (irreplaceable safety indicators)
3. Clean up retired components and superseded part records
4. Discover structurally similar failure-mode vulnerabilities
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _runner import ScenarioConfig, run_industry_example

SCENARIO = ScenarioConfig(
    number=23,
    title="Aviation / Aerospace Network",
    categories={
        "Engines": [
            "Turbofan_CFM56", "Turbofan_GE90", "Turboprop_PW100",
            "APU_Unit_A", "Thrust_Reverser_B", "Nacelle_Assembly_C",
        ],
        "Avionics": [
            "FMS_Primary", "EFIS_Display_A", "Transponder_B",
            "Weather_Radar_C", "Autopilot_Unit_D", "Com_Radio_E",
        ],
        "Airframe": [
            "Fuselage_Section_1", "Wing_Box_Left", "Wing_Box_Right",
            "Empennage_Assy", "Flap_Assembly_A", "Spoiler_Panel_B",
        ],
        "Landing_Gear": [
            "Main_Gear_Left", "Main_Gear_Right", "Nose_Gear_Assy",
            "Brake_Unit_A", "Tire_Assembly_B", "Shock_Strut_C",
        ],
        "Hydraulics": [
            "Hyd_Pump_1", "Hyd_Pump_2", "Actuator_Aileron",
            "Actuator_Rudder", "Reservoir_Main", "Filter_Assy_A",
        ],
    },
    entity_normal="component",
    entity_rare="failure_signal",
    entity_garbage="retired",
    rare_names=[
        "Turbine_Micro_Crack_Signal", "Avionics_Glitch_Rare",
        "Composite_Delamination_Trace", "Hydraulic_Cavitation_Pattern",
        "Fatigue_Cycle_Anomaly", "Corrosion_Precursor_Faint",
    ],
    garbage_names=[
        "Retired_Component_A1", "Retired_Component_A2", "Superseded_Part_B1",
        "Superseded_Part_B2", "Scrapped_Engine_C", "Obsolete_Avionics_D",
        "Condemned_Gear_E", "Expired_Actuator_F",
    ],
    cross_links=[
        ("Engines", "Hydraulics"),
        ("Avionics", "Engines"),
        ("Airframe", "Landing_Gear"),
        ("Hydraulics", "Landing_Gear"),
        ("Avionics", "Airframe"),
    ],
    normal_label="Component nodes",
    rare_label="Failure-mode signals",
    garbage_label="Retired/superseded",
    scenario_a_desc="(Standard aviation component optimization)",
    scenario_b_desc="(Critical failure-mode signals preserved)",
    discovery_title="Failure-Mode Pattern Discovery",
    discovery_description="Finding components with similar failure-risk profiles",
    discovery_conclusion="Structurally similar components may share failure modes.\n  Use this for proactive maintenance and inspection planning.",
    loss_message="In aviation, losing a failure-mode signal\n  can lead to catastrophic in-flight failures.",
)

if __name__ == "__main__":
    run_industry_example(SCENARIO)
