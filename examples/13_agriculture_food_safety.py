#!/usr/bin/env python3
"""
Agriculture / Food Safety Network Example
============================================

Simulates an agriculture and food safety network connecting farms,
livestock operations, processing plants, distributors, and quality labs.

Scenario:
- 30 farm/processing nodes across 5 categories
- 6 rare pest/disease pattern nodes (early warning signals
  for contamination — losing them means outbreaks go undetected)
- 8 garbage nodes (expired certifications, recalled batches)
- Consistency discovery identifies cross-region contamination
  patterns, enabling proactive quarantine planning

The manager should:
1. Maintain active food supply relationships under congestion
2. PROTECT rare pest/disease signals (irreplaceable early warnings)
3. Clean up expired certifications and recalled batch records
4. Discover structurally similar contamination vulnerabilities
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _runner import ScenarioConfig, run_industry_example

SCENARIO = ScenarioConfig(
    number=13,
    title="Agriculture / Food Safety Network",
    categories={
        "Grain_Farms": ["Wheat_Farm_A", "Wheat_Farm_B", "Corn_Field_1",
                        "Rice_Paddy_X", "Soybean_Co", "Barley_Ranch"],
        "Livestock": ["Cattle_Ranch_A", "Poultry_Farm_1", "Dairy_Farm_B",
                      "Swine_Op_1", "Sheep_Station", "Aquaculture_1"],
        "Processing_Plants": ["Flour_Mill_1", "Meat_Packer_A", "Dairy_Proc_1",
                              "Canning_Plant", "Frozen_Food_Co", "Oil_Press_1"],
        "Distribution": ["Cold_Chain_Hub", "Warehouse_East", "Warehouse_West",
                         "Export_Terminal", "Retail_Dist_1", "Food_Bank_Net"],
        "Quality_Labs": ["FDA_Lab_Central", "State_Lab_A", "Private_QA_1",
                         "University_Lab", "Import_Test_Lab", "Micro_Lab_B"],
    },
    entity_normal="facility",
    entity_rare="pest_signal",
    entity_garbage="expired",
    rare_names=[
        "Aflatoxin_Trace_Signal", "Novel_Pathogen_Strain",
        "Pesticide_Residue_Anomaly", "Prion_Like_Signal",
        "Mycotoxin_Rare_Pattern", "Antibiotic_Resistant_Trace",
    ],
    garbage_names=[
        "Expired_Cert_2019", "Recalled_Batch_X1", "Revoked_License_A",
        "Contaminated_Lot_B", "Failed_Audit_C", "Closed_Farm_D",
        "Banned_Additive_E", "Withdrawn_Product_F",
    ],
    cross_links=[
        ("Grain_Farms", "Processing_Plants"),
        ("Livestock", "Processing_Plants"),
        ("Processing_Plants", "Distribution"),
        ("Quality_Labs", "Processing_Plants"),
        ("Quality_Labs", "Livestock"),
    ],
    normal_label="Farm/processing nodes",
    rare_label="Pest/disease signals",
    garbage_label="Expired/recalled",
    scenario_a_desc="(Standard food network optimization)",
    scenario_b_desc="(Critical pest/disease signals preserved)",
    discovery_title="Cross-Region Contamination Pattern Discovery",
    discovery_description="Finding facilities with similar contamination risk profiles",
    discovery_conclusion="Structurally similar facilities may share contamination risks.\n  Use this for proactive quarantine and inspection planning.",
    loss_message="In food safety, losing a contamination signal\n  can lead to widespread outbreaks affecting millions.",
)

if __name__ == "__main__":
    run_industry_example(SCENARIO)
