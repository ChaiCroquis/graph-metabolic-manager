#!/usr/bin/env python3
"""
Media / Advertising Network Example
======================================

Simulates a media and advertising network connecting TV channels,
digital platforms, print media, radio stations, and streaming services.

Scenario:
- 30 media outlet nodes across 5 categories
- 6 rare audience/sentiment pattern nodes (early warning signals
  for market shifts — losing them means trends go undetected)
- 8 garbage nodes (ended campaigns, discontinued formats)
- Consistency discovery identifies audience-similar vulnerability
  patterns, enabling proactive campaign planning

The manager should:
1. Maintain active media relationships under congestion
2. PROTECT rare audience signals (irreplaceable trend indicators)
3. Clean up ended campaigns and discontinued format records
4. Discover structurally similar audience vulnerabilities
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _runner import ScenarioConfig, run_industry_example

SCENARIO = ScenarioConfig(
    number=22,
    title="Media / Advertising Network",
    categories={
        "TV_Channels": [
            "News_Channel_A", "Sports_TV_B", "Entertainment_C",
            "Documentary_Net", "Kids_Channel_D", "Lifestyle_TV_E",
        ],
        "Digital_Platforms": [
            "Social_Media_1", "Video_Platform_A", "Podcast_Hub_B",
            "Blog_Network_C", "Ad_Exchange_D", "Influencer_Net_E",
        ],
        "Print_Media": [
            "Daily_Paper_A", "Magazine_Weekly_B", "Trade_Journal_C",
            "Tabloid_D", "Academic_Press_E", "Local_Gazette_F",
        ],
        "Radio_Stations": [
            "FM_Pop_101", "AM_Talk_Radio", "Internet_Radio_A",
            "College_Radio_B", "News_Radio_C", "Music_FM_D",
        ],
        "Streaming_Services": [
            "Stream_Video_1", "Stream_Music_A", "Stream_Live_B",
            "Stream_Podcast_C", "Stream_Sports_D", "Stream_News_E",
        ],
    },
    entity_normal="outlet",
    entity_rare="audience_signal",
    entity_garbage="ended",
    rare_names=[
        "Micro_Segment_Emerging", "Ad_Fatigue_Precursor",
        "Cross_Platform_Anomaly", "Sentiment_Shift_Signal",
        "Viral_Seed_Pattern", "Brand_Safety_Trace",
    ],
    garbage_names=[
        "Ended_Campaign_Q1", "Ended_Campaign_Q2", "Discontinued_Format_A",
        "Discontinued_Format_B", "Cancelled_Show_C", "Pulled_Ad_D",
        "Expired_Sponsorship_E", "Defunct_Publisher_F",
    ],
    cross_links=[
        ("TV_Channels", "Digital_Platforms"),
        ("Print_Media", "Digital_Platforms"),
        ("Radio_Stations", "Streaming_Services"),
        ("Digital_Platforms", "Streaming_Services"),
        ("TV_Channels", "Streaming_Services"),
    ],
    normal_label="Media outlet nodes",
    rare_label="Audience/trend signals",
    garbage_label="Ended/discontinued",
    scenario_a_desc="(Standard media network optimization)",
    scenario_b_desc="(Critical audience signals preserved)",
    discovery_title="Audience Vulnerability Pattern Discovery",
    discovery_description="Finding outlets with similar audience-risk profiles",
    discovery_conclusion="Structurally similar outlets may share audience risks.\n  Use this for proactive campaign and brand safety planning.",
    loss_message="In media and advertising, losing an audience signal\n  can lead to wasted budgets and missed market opportunities.",
)

if __name__ == "__main__":
    run_industry_example(SCENARIO)
