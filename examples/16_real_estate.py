#!/usr/bin/env python3
"""
Real Estate / Urban Planning Network Example
===============================================

Simulates a real estate and urban planning network connecting
properties, development zones, and infrastructure assets.

Scenario:
- 30 property/area nodes across 5 urban zones
- 6 rare property feature nodes (unique site characteristics
  that define once-in-a-generation opportunities — losing them
  means missing critical development insights)
- 8 garbage nodes (sold/expired listings, demolished properties)
- Consistency discovery identifies cross-zone structural
  similarities, enabling smarter zoning and development

The manager should:
1. Maintain active property relationships under congestion
2. PROTECT rare property feature signals (irreplaceable insights)
3. Clean up sold listings and demolished property records
4. Discover structurally similar cross-zone development patterns
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _runner import ScenarioConfig, run_industry_example

SCENARIO = ScenarioConfig(
    number=16,
    title="Real Estate / Urban Planning Network",
    categories={
        "Downtown": ["Office_Tower_A", "Retail_Block_B", "Condo_High_C",
                      "Parking_Garage_D", "Hotel_Prime_E", "Mixed_Use_F"],
        "Suburban": ["Single_Family_A", "Strip_Mall_B", "School_District_C",
                      "Community_Center_D", "Townhome_Dev_E", "Park_Land_F"],
        "Industrial": ["Warehouse_A", "Factory_Zone_B", "Logistics_Park_C",
                        "Data_Center_D", "Power_Substation_E", "Rail_Yard_F"],
        "Waterfront": ["Marina_Complex_A", "Pier_Development_B", "Beach_Resort_C",
                        "Fishery_Dock_D", "Coastal_Condo_E", "Boardwalk_F"],
        "University": ["Student_Housing_A", "Research_Park_B", "Campus_Retail_C",
                        "Innovation_Hub_D", "Athletic_Complex_E", "Library_Quad_F"],
    },
    entity_normal="property",
    entity_rare="rare_feature",
    entity_garbage="inactive_listing",
    rare_names=[
        "Heritage_Building_Potential", "Underground_River_Site",
        "Transit_Hub_Adjacent", "Green_Corridor_Unique",
        "Mixed_Use_Pioneer", "Disaster_Resilient_Design",
    ],
    garbage_names=[
        "Sold_Listing_2022", "Expired_Lease_A", "Demolished_Bldg_B",
        "Condemned_Site_C", "Abandoned_Lot_D", "Rezoned_Parcel_E",
        "Foreclosed_Unit_F", "Withdrawn_Permit_G",
    ],
    cross_links=[
        ("Downtown", "Suburban"),
        ("Industrial", "Waterfront"),
        ("University", "Downtown"),
        ("Suburban", "Industrial"),
        ("Waterfront", "University"),
    ],
    normal_label="Property/area nodes",
    rare_label="Rare property features",
    garbage_label="Inactive listings",
    scenario_a_desc="(Standard property portfolio optimization)",
    scenario_b_desc="(Critical rare property features preserved)",
    discovery_title="Cross-Zone Structural Similarity Discovery",
    discovery_description="Finding properties with similar development potential",
    discovery_conclusion="Structurally similar zones may share development potential.\n  Use this for zoning strategy and investment prioritization.",
    loss_message="In real estate, losing sight of a unique property feature\n  can mean missing multi-million dollar development potential.",
)

if __name__ == "__main__":
    run_industry_example(SCENARIO)
