#!/usr/bin/env python3
"""
Pharmaceutical Manufacturing Network Example
===============================================

Simulates a pharmaceutical manufacturing network connecting API production,
formulation, packaging, quality control, and distribution facilities.

Scenario:
- 30 facility nodes across 5 categories
- 6 rare contamination pattern nodes (early warning signals
  for quality issues — losing them means defects go undetected)
- 8 garbage nodes (expired batches, recalled lots)
- Consistency discovery identifies contamination-similar
  patterns, enabling proactive quality planning

The manager should:
1. Maintain active manufacturing relationships under congestion
2. PROTECT rare contamination signals (irreplaceable quality indicators)
3. Clean up expired batches and recalled lot records
4. Discover structurally similar contamination vulnerabilities
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _runner import ScenarioConfig, run_industry_example

SCENARIO = ScenarioConfig(
    number=24,
    title="Pharmaceutical Manufacturing Network",
    categories={
        "API_Production": [
            "Synthesis_Reactor_A", "Fermentation_Tank_B", "Crystallizer_C",
            "Purification_Unit_D", "Drying_Chamber_E", "Milling_Station_F",
        ],
        "Formulation": [
            "Tablet_Press_1", "Capsule_Filler_A", "Coating_Pan_B",
            "Liquid_Mixer_C", "Ointment_Line_D", "Lyophilizer_E",
        ],
        "Packaging": [
            "Blister_Pack_Line_1", "Bottle_Fill_A", "Vial_Seal_B",
            "Cartoner_C", "Labeler_D", "Serialization_E",
        ],
        "Quality_Control": [
            "HPLC_Lab_1", "Micro_Lab_A", "Stability_Chamber_B",
            "Dissolution_Lab_C", "Particle_Counter_D", "Endotoxin_Lab_E",
        ],
        "Distribution": [
            "Cold_Chain_DC_1", "Ambient_Warehouse_A", "Regional_Hub_B",
            "Hospital_Depot_C", "Pharmacy_Dist_D", "Export_Center_E",
        ],
    },
    entity_normal="facility",
    entity_rare="contamination_signal",
    entity_garbage="expired",
    rare_names=[
        "Endotoxin_Trace_Rare", "Cross_Contamination_Signal",
        "Particle_Count_Anomaly", "Stability_Drift_Faint",
        "Sterility_Breach_Precursor", "Potency_Variation_Trace",
    ],
    garbage_names=[
        "Expired_Batch_2021A", "Expired_Batch_2021B", "Recalled_Lot_X1",
        "Recalled_Lot_X2", "Failed_Validation_C", "Rejected_Raw_Material_D",
        "Obsolete_Formula_E", "Withdrawn_Product_F",
    ],
    cross_links=[
        ("API_Production", "Formulation"),
        ("Formulation", "Packaging"),
        ("Quality_Control", "API_Production"),
        ("Quality_Control", "Formulation"),
        ("Packaging", "Distribution"),
    ],
    normal_label="Facility nodes",
    rare_label="Contamination signals",
    garbage_label="Expired/recalled",
    scenario_a_desc="(Standard pharma network optimization)",
    scenario_b_desc="(Critical contamination signals preserved)",
    discovery_title="Contamination Pattern Discovery",
    discovery_description="Finding facilities with similar contamination-risk profiles",
    discovery_conclusion="Structurally similar facilities may share contamination risks.\n  Use this for proactive quality and GMP compliance planning.",
    loss_message="In pharma manufacturing, losing a contamination signal\n  can lead to patient harm and massive product recalls.",
)

if __name__ == "__main__":
    run_industry_example(SCENARIO)
