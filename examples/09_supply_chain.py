#!/usr/bin/env python3
"""
Supply Chain Network Example
==============================

Simulates a global supply chain network connecting suppliers,
manufacturers, distributors, and logistics hubs.

Scenario:
- 30 established suppliers across 5 material categories
- 6 sole-source critical suppliers (the ONLY source for rare
  materials --- losing them means production halts)
- 8 defunct suppliers (bankrupt or exited the market)
- Consistency discovery identifies suppliers with similar
  risk profiles, enabling diversification planning

The manager should:
1. Maintain active supply relationships under congestion
2. PROTECT sole-source suppliers (irreplaceable supply paths)
3. Clean up defunct supplier records
4. Discover structurally similar supply chain vulnerabilities
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _runner import ScenarioConfig, run_industry_example

SCENARIO = ScenarioConfig(
    number=9,
    title="Supply Chain Network",
    categories={
        "Semiconductors": ["Chip_Fab_A", "Chip_Fab_B", "Chip_Fab_C",
                           "Wafer_Co_1", "Wafer_Co_2", "Packaging_X"],
        "Raw_Materials": ["Steel_Mill_1", "Steel_Mill_2", "Aluminum_Co",
                          "Copper_Mine_A", "Rare_Earth_Co", "Polymer_Inc"],
        "Electronics": ["PCB_Maker_1", "PCB_Maker_2", "Capacitor_Co",
                        "Resistor_Co", "Connector_Inc", "Display_Corp"],
        "Logistics": ["Shipping_Global", "Freight_Asia", "Rail_Europe",
                      "Air_Cargo_1", "Trucking_NA", "Port_Hub_1"],
        "Assembly": ["OEM_Plant_A", "OEM_Plant_B", "OEM_Plant_C",
                     "Contract_Mfg_1", "Contract_Mfg_2", "Test_Facility"],
    },
    entity_normal="supplier",
    entity_rare="sole_source",
    entity_garbage="defunct",
    rare_names=[
        "Gallium_Nitride_Only", "Cobalt_Refiner_Sole",
        "Specialty_Resin_Unique", "Precision_Bearing_Only",
        "Medical_Grade_Titanium", "Aerospace_Alloy_Sole",
    ],
    garbage_names=[
        "Bankrupt_Mfg_A", "Bankrupt_Mfg_B", "Exited_Chip_Co",
        "Closed_Warehouse", "Dissolved_Logistics", "Merged_Away_Inc",
        "Sanctioned_Supplier", "Recalled_Parts_Co",
    ],
    cross_links=[
        ("Raw_Materials", "Semiconductors"),
        ("Semiconductors", "Electronics"),
        ("Electronics", "Assembly"),
        ("Logistics", "Assembly"),
        ("Raw_Materials", "Electronics"),
    ],
    normal_label="Established suppliers",
    rare_label="Sole-source critical",
    garbage_label="Defunct suppliers",
    scenario_a_desc="(Standard supply chain optimization)",
    scenario_b_desc="(Critical sole-source suppliers preserved)",
    discovery_title="Supply Chain Vulnerability Discovery",
    discovery_description="Finding suppliers with similar risk profiles",
    discovery_conclusion=(
        "Structurally similar suppliers may share risks.\n"
        "  Use this for diversification and contingency planning."
    ),
    loss_message=(
        "In supply chains, losing visibility of a sole-source\n"
        "  supplier can halt production lines worth $M/day."
    ),
)

if __name__ == "__main__":
    run_industry_example(SCENARIO)
