#!/usr/bin/env python3
"""
Environmental Monitoring Network Example
===========================================

Simulates an environmental monitoring network connecting sensor
stations, wildlife trackers, and ecosystem observation points.

Scenario:
- 30 monitoring nodes across 5 ecosystem types
- 6 rare species/event observation nodes (early signals of
  ecological shifts — losing them means missing critical
  environmental changes before they become irreversible)
- 8 garbage nodes (decommissioned stations, invalid readings)
- Consistency discovery identifies cross-ecosystem pattern
  similarities, enabling proactive conservation planning

The manager should:
1. Maintain active monitoring relationships under congestion
2. PROTECT rare observation signals (irreplaceable ecological data)
3. Clean up decommissioned station and invalid reading records
4. Discover structurally similar cross-ecosystem patterns
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _runner import ScenarioConfig, run_industry_example

SCENARIO = ScenarioConfig(
    number=18,
    title="Environmental Monitoring Network",
    categories={
        "Forest": ["Old_Growth_Station_A", "Canopy_Sensor_B", "Soil_Monitor_C",
                    "Wildlife_Cam_D", "Tree_Ring_Lab_E", "Fungal_Net_Sensor_F"],
        "Wetland": ["Marsh_Gauge_A", "Bird_Colony_Cam_B", "Water_Quality_C",
                     "Amphibian_Tracker_D", "Peat_Depth_Sensor_E", "Reed_Bed_F"],
        "Coastal": ["Tide_Station_A", "Reef_Monitor_B", "Seagrass_Cam_C",
                     "Mangrove_Sensor_D", "Shore_Erosion_E", "Marine_Buoy_F"],
        "Mountain": ["Alpine_Weather_A", "Glacier_Gauge_B", "Snow_Pack_C",
                      "Raptor_Nest_Cam_D", "Treeline_Monitor_E", "Rock_Slide_F"],
        "Urban_Park": ["Air_Quality_A", "Noise_Monitor_B", "Pollinator_Cam_C",
                        "Urban_Stream_D", "Green_Roof_Sensor_E", "Bat_Detector_F"],
    },
    entity_normal="station",
    entity_rare="rare_observation",
    entity_garbage="defunct_station",
    rare_names=[
        "New_Species_Sighting", "Migration_Pattern_Shift",
        "Pollution_Source_Unknown", "Microplastic_Novel_Path",
        "Coral_Bleaching_Precursor", "Invasive_Species_Early",
    ],
    garbage_names=[
        "Decommissioned_Station_A", "Invalid_Reading_Batch_B",
        "Broken_Sensor_Array_C", "Flooded_Data_Logger_D",
        "Vandalized_Camera_E", "Expired_Calibration_F",
        "Corrupted_Dataset_G", "Abandoned_Buoy_H",
    ],
    cross_links=[
        ("Forest", "Wetland"),
        ("Wetland", "Coastal"),
        ("Mountain", "Forest"),
        ("Urban_Park", "Wetland"),
        ("Coastal", "Mountain"),
    ],
    normal_label="Monitoring stations",
    rare_label="Rare observations",
    garbage_label="Defunct stations",
    scenario_a_desc="(Standard monitoring network optimization)",
    scenario_b_desc="(Critical rare observations preserved)",
    discovery_title="Cross-Ecosystem Pattern Discovery",
    discovery_description="Finding ecosystems with similar stress indicators",
    discovery_conclusion="Structurally similar ecosystems may face correlated threats.\n  Use this for proactive conservation and early warning systems.",
    loss_message="In environmental monitoring, losing a rare observation\n  can mean missing the window to prevent irreversible damage.",
)

if __name__ == "__main__":
    run_industry_example(SCENARIO)
