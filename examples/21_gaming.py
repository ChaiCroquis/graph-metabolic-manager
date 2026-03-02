#!/usr/bin/env python3
"""
Online Gaming Network Example
================================

Simulates an online gaming network connecting FPS, RPG, strategy,
sports, and casual player communities with their interactions.

Scenario:
- 30 player nodes across 5 categories
- 6 rare exploit/cheat pattern nodes (early warning signals
  for abuse — losing them means exploits go undetected)
- 8 garbage nodes (inactive players, banned accounts)
- Consistency discovery identifies behavior-similar anomaly
  patterns, enabling proactive anti-cheat measures

The manager should:
1. Maintain active player relationships under congestion
2. PROTECT rare exploit signals (irreplaceable cheat indicators)
3. Clean up inactive players and banned account records
4. Discover structurally similar behavioral anomalies
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _runner import ScenarioConfig, run_industry_example

SCENARIO = ScenarioConfig(
    number=21,
    title="Online Gaming Network",
    categories={
        "FPS_Players": [
            "Sniper_Ace", "Rusher_Max", "Support_Zen",
            "Flanker_Nova", "Anchor_Tank", "Entry_Blitz",
        ],
        "RPG_Players": [
            "Paladin_Sol", "Rogue_Shadow", "Mage_Arcane",
            "Healer_Grace", "Ranger_Wild", "Bard_Melody",
        ],
        "Strategy_Players": [
            "Commander_Rex", "Diplomat_Sage", "Builder_Stone",
            "Trader_Gold", "Spy_Cipher", "General_Iron",
        ],
        "Sports_Players": [
            "Striker_Fast", "Goalie_Wall", "Racer_Turbo",
            "Boxer_Fist", "Climber_Peak", "Swimmer_Wave",
        ],
        "Casual_Players": [
            "Puzzle_Mind", "Farm_Harvest", "Match3_Star",
            "Idle_Click", "Trivia_Brain", "Card_Dealer",
        ],
    },
    entity_normal="player",
    entity_rare="exploit_signal",
    entity_garbage="inactive",
    rare_names=[
        "Exploit_Pattern_Rare", "RMT_Signal_Faint",
        "Collusion_Trace", "Bug_Abuse_Novel",
        "Account_Sharing_Signal", "Latency_Manipulation_Trace",
    ],
    garbage_names=[
        "Inactive_Player_001", "Inactive_Player_002", "Banned_Account_X1",
        "Banned_Account_X2", "Abandoned_Guild_A", "Expired_Sub_B",
        "Deleted_Character_C", "Suspended_Clan_D",
    ],
    cross_links=[
        ("FPS_Players", "Strategy_Players"),
        ("RPG_Players", "Casual_Players"),
        ("Strategy_Players", "RPG_Players"),
        ("Sports_Players", "FPS_Players"),
        ("Casual_Players", "Sports_Players"),
    ],
    normal_label="Player nodes",
    rare_label="Exploit/cheat signals",
    garbage_label="Inactive/banned",
    scenario_a_desc="(Standard gaming network optimization)",
    scenario_b_desc="(Critical exploit signals preserved)",
    discovery_title="Behavioral Anomaly Pattern Discovery",
    discovery_description="Finding players with similar behavior-anomaly profiles",
    discovery_conclusion="Structurally similar players may share exploit patterns.\n  Use this for proactive anti-cheat and moderation planning.",
    loss_message="In online gaming, losing an exploit signal\n  can lead to widespread cheating undermining fair play.",
)

if __name__ == "__main__":
    run_industry_example(SCENARIO)
