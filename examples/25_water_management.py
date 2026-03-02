#!/usr/bin/env python3
"""
Water / Wastewater Management Network Example
================================================

Simulates a water and wastewater management network connecting
treatment plants, pumping stations, reservoirs, distribution mains,
and monitoring wells.

Scenario:
- 30 infrastructure nodes across 5 categories
- 6 rare water quality pattern nodes (early warning signals
  for contamination — losing them means hazards go undetected)
- 8 garbage nodes (decommissioned wells, replaced pipes)
- Consistency discovery identifies infrastructure-similar
  patterns, enabling proactive maintenance planning

The manager should:
1. Maintain active water infrastructure relationships under congestion
2. PROTECT rare water quality signals (irreplaceable safety indicators)
3. Clean up decommissioned wells and replaced pipe records
4. Discover structurally similar infrastructure vulnerabilities
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _runner import ScenarioConfig, run_industry_example

SCENARIO = ScenarioConfig(
    number=25,
    title="Water / Wastewater Management Network",
    categories={
        "Treatment_Plants": [
            "WTP_Central", "WTP_North", "WWTP_South",
            "Desalination_A", "Reclamation_B", "Filtration_C",
        ],
        "Pumping_Stations": [
            "Pump_Station_1", "Pump_Station_2", "Booster_Pump_A",
            "Lift_Station_B", "Raw_Water_Pump_C", "High_Service_D",
        ],
        "Reservoirs": [
            "Reservoir_Main", "Reservoir_Hilltop", "Storage_Tank_A",
            "Clearwell_B", "Elevated_Tank_C", "Ground_Storage_D",
        ],
        "Distribution_Mains": [
            "Main_Trunk_East", "Main_Trunk_West", "Feeder_Line_A",
            "Service_Line_B", "Transmission_Main_C", "Lateral_D",
        ],
        "Monitoring_Wells": [
            "Monitor_Well_MW1", "Monitor_Well_MW2", "Sentinel_Well_A",
            "Piezometer_B", "Sampling_Point_C", "Compliance_Well_D",
        ],
    },
    entity_normal="infrastructure",
    entity_rare="quality_signal",
    entity_garbage="decommissioned",
    rare_names=[
        "PFAS_Trace_Novel", "Cryptosporidium_Signal",
        "Pipe_Corrosion_Precursor", "Algal_Bloom_Early",
        "Microplastic_Source_Faint", "Lead_Leach_Anomaly",
    ],
    garbage_names=[
        "Decommissioned_Well_A1", "Decommissioned_Well_A2", "Replaced_Pipe_B1",
        "Replaced_Pipe_B2", "Abandoned_Pump_C", "Sealed_Reservoir_D",
        "Removed_Hydrant_E", "Closed_Intake_F",
    ],
    cross_links=[
        ("Treatment_Plants", "Pumping_Stations"),
        ("Pumping_Stations", "Reservoirs"),
        ("Reservoirs", "Distribution_Mains"),
        ("Monitoring_Wells", "Treatment_Plants"),
        ("Distribution_Mains", "Monitoring_Wells"),
    ],
    normal_label="Infrastructure nodes",
    rare_label="Water quality signals",
    garbage_label="Decommissioned/replaced",
    scenario_a_desc="(Standard water infrastructure optimization)",
    scenario_b_desc="(Critical water quality signals preserved)",
    discovery_title="Infrastructure Vulnerability Pattern Discovery",
    discovery_description="Finding assets with similar infrastructure-risk profiles",
    discovery_conclusion="Structurally similar assets may share infrastructure risks.\n  Use this for proactive maintenance and compliance planning.",
    loss_message="In water management, losing a quality signal\n  can lead to public health crises affecting entire communities.",
)

if __name__ == "__main__":
    run_industry_example(SCENARIO)
