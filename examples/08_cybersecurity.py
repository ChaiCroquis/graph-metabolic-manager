#!/usr/bin/env python3
"""
Cybersecurity Threat Intelligence Example
==========================================

Simulates a threat intelligence graph connecting indicators of
compromise (IoCs), attack techniques, and threat actors.

Scenario:
- 30 known threat indicators across 5 attack categories
- 6 rare APT (Advanced Persistent Threat) signals with minimal
  footprint that must NOT be pruned
- 8 stale indicators (expired, no longer relevant)
- Consistency discovery links APT signals to known attack
  patterns, revealing hidden campaign connections

The manager should:
1. Maintain the active threat indicator network
2. PROTECT rare APT signals (early warnings of targeted attacks)
3. Clean up expired indicators
4. Discover hidden connections between APT activity and known patterns
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _runner import ScenarioConfig, run_industry_example

SCENARIO = ScenarioConfig(
    number=8,
    title="Cybersecurity Threat Intelligence",
    categories={
        "Malware": [
            "Trojan_X", "Ransomware_Y", "Worm_Z",
            "Rootkit_A", "Spyware_B", "Dropper_C",
        ],
        "Phishing": [
            "Phish_Domain_1", "Phish_Domain_2", "Phish_Kit_A",
            "Phish_Kit_B", "Spoofed_Email_1", "Spoofed_Email_2",
        ],
        "Exploit": [
            "CVE_2025_001", "CVE_2025_002", "CVE_2025_003",
            "ZeroDay_Alpha", "ZeroDay_Beta", "MemCorrupt_1",
        ],
        "C2_Infra": [
            "C2_Server_1", "C2_Server_2", "C2_Server_3",
            "C2_Domain_A", "C2_Domain_B", "Proxy_Relay_1",
        ],
        "Lateral": [
            "PassHash_1", "CredDump_A", "PrivEsc_1",
            "PrivEsc_2", "TokenTheft_A", "Kerberoast_1",
        ],
    },
    entity_normal="indicator",
    entity_rare="apt_signal",
    entity_garbage="stale",
    rare_names=[
        "APT_Beacon_Faint", "APT_DNS_Tunnel_Rare",
        "APT_Cert_Anomaly", "APT_Timing_Pattern",
        "APT_Steganography_Trace", "APT_Supply_Chain_Implant",
    ],
    garbage_names=[
        "Expired_IP_1", "Expired_IP_2", "Old_Hash_A",
        "Old_Hash_B", "Revoked_Cert_1", "Revoked_Cert_2",
        "Dead_C2_Domain", "Sinkholed_Server",
    ],
    cross_links=[
        ("Phishing", "Malware"), ("Malware", "C2_Infra"),
        ("Exploit", "Lateral"), ("Lateral", "C2_Infra"),
        ("Exploit", "Malware"),
    ],
    normal_label="Known indicators",
    rare_label="APT signals",
    garbage_label="Stale indicators",
    scenario_a_desc="(Standard threat feed pruning)",
    scenario_b_desc="(APT signals preserved)",
    discovery_title="Hidden Campaign Discovery",
    discovery_description="Linking APT signals to known attack patterns",
    discovery_conclusion="These links suggest which APT activities may be part\n  of broader, coordinated attack campaigns.",
    loss_message="In cybersecurity, a missed APT signal can mean months\n  of undetected data exfiltration before discovery.",
    # Non-default parameters
    connect_prob=0.5,
    cross_weight_range=(0.2, 0.5),
    rare_weight_range=(0.03, 0.09),
    k_opt=5.0,
    alpha=2.0,
    beta=0.04,
    theta_l=0.50,
)

if __name__ == "__main__":
    run_industry_example(SCENARIO)
