#!/usr/bin/env python3
"""
Transportation / Logistics Network Example
=============================================

Simulates a transportation and logistics network connecting rail systems,
maritime operations, aviation hubs, trucking fleets, and warehouse facilities.

Scenario:
- 30 logistics nodes across 5 categories
- 6 rare safety/anomaly pattern nodes (early warning signals
  for incidents — losing them means accidents go undetected)
- 8 garbage nodes (retired routes, decommissioned assets)
- Consistency discovery identifies route-similar vulnerability
  patterns, enabling proactive safety planning

The manager should:
1. Maintain active logistics relationships under congestion
2. PROTECT rare safety signals (irreplaceable early warnings)
3. Clean up retired routes and decommissioned asset records
4. Discover structurally similar route vulnerabilities
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _runner import ScenarioConfig, run_industry_example

SCENARIO = ScenarioConfig(
    number=19,
    title="Transportation / Logistics Network",
    categories={
        "Rail": ["Rail_Hub_East", "Rail_Hub_West", "Rail_Freight_1",
                 "Rail_Passenger_A", "Rail_Switch_Yard", "Rail_Depot_B"],
        "Maritime": ["Port_Alpha", "Port_Beta", "Container_Terminal_1",
                     "Bulk_Carrier_Dock", "Tanker_Berth_A", "Shipyard_Main"],
        "Aviation": ["Airport_Hub_1", "Cargo_Airport_A", "Regional_Air_B",
                     "Heliport_Central", "Air_Freight_Hub", "Charter_Base_C"],
        "Trucking": ["Truck_Fleet_A", "Truck_Fleet_B", "LTL_Hub_1",
                     "FTL_Depot_East", "Drayage_Op_A", "Last_Mile_Hub"],
        "Warehouse": ["DC_Northeast", "DC_Southeast", "DC_Midwest",
                      "Cold_Storage_1", "Cross_Dock_A", "Fulfillment_West"],
    },
    entity_normal="facility",
    entity_rare="safety_signal",
    entity_garbage="retired",
    rare_names=[
        "Near_Miss_Signal", "Fatigue_Pattern_Rare",
        "Weather_Anomaly_Precursor", "Route_Deviation_Trace",
        "Cargo_Integrity_Signal", "Bridge_Stress_Anomaly",
    ],
    garbage_names=[
        "Retired_Route_47", "Retired_Route_82", "Decommissioned_Crane_A",
        "Decommissioned_Vessel_B", "Closed_Terminal_C", "Abandoned_Depot_D",
        "Scrapped_Locomotive_E", "Defunct_Carrier_F",
    ],
    cross_links=[
        ("Rail", "Warehouse"),
        ("Maritime", "Warehouse"),
        ("Aviation", "Warehouse"),
        ("Trucking", "Warehouse"),
        ("Maritime", "Rail"),
    ],
    normal_label="Logistics nodes",
    rare_label="Safety signals",
    garbage_label="Retired/decommissioned",
    scenario_a_desc="(Standard logistics network optimization)",
    scenario_b_desc="(Critical safety signals preserved)",
    discovery_title="Route Vulnerability Pattern Discovery",
    discovery_description="Finding facilities with similar route-risk profiles",
    discovery_conclusion="Structurally similar facilities may share route risks.\n  Use this for proactive safety and routing planning.",
    loss_message="In transportation, losing a safety signal\n  can lead to catastrophic incidents affecting thousands.",
)

if __name__ == "__main__":
    run_industry_example(SCENARIO)
