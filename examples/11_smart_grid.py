#!/usr/bin/env python3
"""
Smart Grid / Energy Network Example
======================================

Simulates an electrical power grid with substations, generators,
transmission lines, and monitoring points.

Scenario:
- 25 substations across 5 grid zones with heavy power flows
- 6 rare grid anomaly patterns (early warning signals of cascade
  failure that have occurred only once — must be preserved)
- 8 decommissioned monitoring points (old meters/sensors)
- Consistency discovery identifies grid sections with similar
  stress patterns, enabling preventive load balancing

The manager should:
1. Maintain power flow topology under load congestion
2. PROTECT rare anomaly records (cascade failure early warnings)
3. Clean up decommissioned monitoring data
4. Discover grid sections with similar vulnerability profiles
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _runner import ScenarioConfig, run_industry_example

SCENARIO = ScenarioConfig(
    number=11,
    title="Smart Grid / Energy Network",
    categories={
        "Zone_North": ["Sub_N01", "Sub_N02", "Sub_N03", "Sub_N04", "Sub_N05"],
        "Zone_South": ["Sub_S01", "Sub_S02", "Sub_S03", "Sub_S04", "Sub_S05"],
        "Zone_East": ["Sub_E01", "Sub_E02", "Sub_E03", "Sub_E04", "Sub_E05"],
        "Zone_West": ["Sub_W01", "Sub_W02", "Sub_W03", "Sub_W04", "Sub_W05"],
        "Zone_Central": ["Sub_C01", "Sub_C02", "Sub_C03", "Sub_C04", "Sub_C05"],
        "Generators": [
            "Solar_Farm", "Wind_Park", "Gas_Turbine",
            "Hydro_Plant", "Nuclear_Unit", "Battery_Storage",
        ],
    },
    entity_normal="substation",
    entity_rare="rare_anomaly",
    entity_garbage="decommissioned",
    rare_names=[
        "Voltage_Collapse_Precursor", "Frequency_Drift_Rare",
        "Phase_Imbalance_Unique", "Harmonic_Resonance_Grid",
        "Islanding_Near_Miss", "Transformer_Saturation_Event",
    ],
    garbage_names=[
        "Old_Meter_A1", "Old_Meter_A2", "Retired_SCADA_1",
        "Retired_SCADA_2", "Legacy_RTU_1", "Legacy_RTU_2",
        "Analog_Gauge_1", "Analog_Gauge_2",
    ],
    cross_links=[
        # Inter-zone tie lines
        ("Zone_North", "Zone_South"), ("Zone_North", "Zone_East"),
        ("Zone_North", "Zone_West"), ("Zone_North", "Zone_Central"),
        ("Zone_South", "Zone_East"), ("Zone_South", "Zone_West"),
        ("Zone_South", "Zone_Central"), ("Zone_East", "Zone_West"),
        ("Zone_East", "Zone_Central"), ("Zone_West", "Zone_Central"),
        # Generator connections to zones
        ("Generators", "Zone_North"), ("Generators", "Zone_South"),
        ("Generators", "Zone_East"), ("Generators", "Zone_West"),
        ("Generators", "Zone_Central"),
    ],
    normal_label="Substations",
    rare_label="Rare anomalies",
    garbage_label="Decommissioned",
    scenario_a_desc="(Standard grid data cleanup)",
    scenario_b_desc="(Anomaly records preserved)",
    discovery_title="Grid Vulnerability Discovery",
    discovery_description="Finding zones with similar stress patterns",
    discovery_conclusion="Zones with similar stress profiles may experience\n  similar cascade scenarios. Prioritize reinforcement.",
    loss_message="In power grids, a cascade failure like the 2003 Northeast\n  blackout affected 55 million people. Early warnings matter.",
    # Non-default parameters
    connect_prob=0.55,
    cross_link_prob=0.3,
    normal_weight_range=(0.6, 1.0),
    cross_weight_range=(0.15, 0.4),
    k_opt=5.0,
    alpha=1.6,
    prune_threshold=0.06,
)

if __name__ == "__main__":
    run_industry_example(SCENARIO)
