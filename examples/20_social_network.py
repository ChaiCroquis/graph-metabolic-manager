#!/usr/bin/env python3
"""
Social Network Analysis Example
==================================

Simulates a social network connecting tech, art, sports, science,
and music communities with members and their interactions.

Scenario:
- 30 community member nodes across 5 categories
- 6 rare cross-community bridge nodes (early warning signals
  for emerging trends — losing them means shifts go undetected)
- 8 garbage nodes (deleted accounts, banned bots)
- Consistency discovery identifies community-similar bridge
  patterns, enabling proactive trend analysis

The manager should:
1. Maintain active community relationships under congestion
2. PROTECT rare bridge signals (irreplaceable trend indicators)
3. Clean up deleted accounts and banned bot records
4. Discover structurally similar community bridges
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _runner import ScenarioConfig, run_industry_example

SCENARIO = ScenarioConfig(
    number=20,
    title="Social Network Analysis",
    categories={
        "Tech_Community": [
            "Dev_Alice", "Dev_Bob", "SysAdmin_Carol",
            "Designer_Dan", "PM_Eve", "DataSci_Frank",
        ],
        "Art_Community": [
            "Painter_Grace", "Sculptor_Hank", "Photographer_Iris",
            "Filmmaker_Jack", "Writer_Karen", "Musician_Leo",
        ],
        "Sports_Community": [
            "Coach_Mike", "Athlete_Nina", "Trainer_Oscar",
            "Analyst_Pam", "Scout_Quinn", "Physio_Ray",
        ],
        "Science_Community": [
            "Physicist_Sara", "Biologist_Tom", "Chemist_Uma",
            "Geologist_Vic", "Astronomer_Wendy", "Ecologist_Xander",
        ],
        "Music_Community": [
            "Producer_Yara", "DJ_Zane", "Vocalist_Amy",
            "Guitarist_Ben", "Drummer_Cleo", "Pianist_Derek",
        ],
    },
    entity_normal="member",
    entity_rare="bridge_signal",
    entity_garbage="removed",
    rare_names=[
        "Cross_Culture_Bridge", "Emerging_Influencer_Niche",
        "Underground_Movement_Seed", "Diaspora_Connector",
        "Whistleblower_Network_Trace", "Counter_Narrative_Origin",
    ],
    garbage_names=[
        "Deleted_Account_001", "Deleted_Account_002", "Banned_Bot_Alpha",
        "Banned_Bot_Beta", "Suspended_Troll_A", "Spam_Account_B",
        "Fake_Profile_C", "Inactive_Bot_D",
    ],
    cross_links=[
        ("Tech_Community", "Science_Community"),
        ("Art_Community", "Music_Community"),
        ("Sports_Community", "Science_Community"),
        ("Tech_Community", "Art_Community"),
        ("Music_Community", "Sports_Community"),
    ],
    normal_label="Community members",
    rare_label="Bridge/trend signals",
    garbage_label="Deleted/banned",
    scenario_a_desc="(Standard social network optimization)",
    scenario_b_desc="(Critical bridge signals preserved)",
    discovery_title="Community Bridge Pattern Discovery",
    discovery_description="Finding members with similar community-bridge profiles",
    discovery_conclusion="Structurally similar members may bridge communities.\n  Use this for proactive trend and influence analysis.",
    loss_message="In social networks, losing a bridge signal\n  can mean missing emerging movements and cultural shifts.",
)

if __name__ == "__main__":
    run_industry_example(SCENARIO)
