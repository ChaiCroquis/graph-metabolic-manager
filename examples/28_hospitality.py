#!/usr/bin/env python3
"""
Hospitality / Tourism Network Example
========================================

Simulates a hospitality and tourism network connecting hotels,
restaurants, attractions, transport hubs, and event venues.

Scenario:
- 30 hospitality nodes across 5 categories
- 6 rare demand/preference pattern nodes (early warning signals
  for market shifts — losing them means trends go undetected)
- 8 garbage nodes (closed venues, defunct tours)
- Consistency discovery identifies demand-similar
  patterns, enabling proactive capacity planning

The manager should:
1. Maintain active hospitality relationships under congestion
2. PROTECT rare demand signals (irreplaceable trend indicators)
3. Clean up closed venues and defunct tour records
4. Discover structurally similar demand vulnerabilities
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _runner import ScenarioConfig, run_industry_example

SCENARIO = ScenarioConfig(
    number=28,
    title="Hospitality / Tourism Network",
    categories={
        "Hotels": [
            "Grand_Hotel_A", "Boutique_Inn_B", "Resort_Coastal_C",
            "Budget_Lodge_D", "Business_Hotel_E", "Eco_Lodge_F",
        ],
        "Restaurants": [
            "Fine_Dining_1", "Casual_Bistro_A", "Street_Food_Hub_B",
            "Farm_Table_C", "Rooftop_Bar_D", "Fusion_Kitchen_E",
        ],
        "Attractions": [
            "Museum_Central", "Theme_Park_A", "Historic_Site_B",
            "Nature_Reserve_C", "Gallery_District_D", "Aquarium_E",
        ],
        "Transport_Hubs": [
            "Airport_Terminal_1", "Train_Station_Main", "Ferry_Port_A",
            "Bus_Depot_B", "Cruise_Terminal_C", "Cable_Car_D",
        ],
        "Event_Venues": [
            "Convention_Center", "Concert_Hall_A", "Stadium_B",
            "Exhibition_Ground_C", "Theater_District_D", "Festival_Site_E",
        ],
    },
    entity_normal="venue",
    entity_rare="demand_signal",
    entity_garbage="closed",
    rare_names=[
        "Emerging_Destination_Signal", "Guest_Preference_Niche",
        "Cultural_Shift_Indicator", "Overtourism_Precursor",
        "Service_Gap_Anomaly", "Seasonal_Reversal_Pattern",
    ],
    garbage_names=[
        "Closed_Venue_A1", "Closed_Venue_A2", "Defunct_Tour_B1",
        "Defunct_Tour_B2", "Shuttered_Hotel_C", "Bankrupt_Resort_D",
        "Cancelled_Festival_E", "Abandoned_Attraction_F",
    ],
    cross_links=[
        ("Transport_Hubs", "Hotels"),
        ("Hotels", "Restaurants"),
        ("Attractions", "Restaurants"),
        ("Event_Venues", "Hotels"),
        ("Transport_Hubs", "Attractions"),
    ],
    normal_label="Hospitality nodes",
    rare_label="Demand/trend signals",
    garbage_label="Closed/defunct",
    scenario_a_desc="(Standard hospitality network optimization)",
    scenario_b_desc="(Critical demand signals preserved)",
    discovery_title="Demand Pattern Discovery",
    discovery_description="Finding venues with similar demand-risk profiles",
    discovery_conclusion="Structurally similar venues may share demand patterns.\n  Use this for proactive capacity and marketing planning.",
    loss_message="In hospitality, losing a demand signal\n  can lead to over-investment or missed market opportunities.",
)

if __name__ == "__main__":
    run_industry_example(SCENARIO)
