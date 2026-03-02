#!/usr/bin/env python3
"""
Insurance / Actuarial Network Example
========================================

Simulates an insurance and actuarial network connecting policies,
risk models, claim records, and product lines.

Scenario:
- 30 policy/risk nodes across 5 product lines
- 6 rare claim pattern nodes (anomalous signals indicating
  emerging risks — losing them means blind spots in underwriting)
- 8 garbage nodes (expired policies, settled claims)
- Consistency discovery identifies cross-product risk similarity,
  enabling portfolio-wide risk correlation analysis

The manager should:
1. Maintain active policy/risk relationships under congestion
2. PROTECT rare claim pattern signals (irreplaceable risk insights)
3. Clean up expired policy and settled claim records
4. Discover structurally similar cross-product risk patterns
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _runner import ScenarioConfig, run_industry_example

SCENARIO = ScenarioConfig(
    number=17,
    title="Insurance / Actuarial Network",
    categories={
        "Auto": ["Fleet_Policy_A", "Rideshare_Risk_B", "Commercial_Auto_C",
                  "Personal_Auto_D", "Motorcycle_Niche_E", "Telematics_Pool_F"],
        "Home": ["Coastal_Home_A", "Wildfire_Zone_B", "Flood_Plain_C",
                  "Urban_Condo_D", "Rural_Estate_E", "Rental_Property_F"],
        "Life": ["Term_Life_A", "Whole_Life_B", "Variable_Universal_C",
                  "Group_Life_D", "Key_Person_E", "Annuity_Product_F"],
        "Health": ["Group_Health_A", "Individual_Plan_B", "Medicare_Supp_C",
                    "Dental_Vision_D", "Critical_Illness_E", "Telehealth_F"],
        "Commercial": ["Cyber_Liability_A", "Directors_Officers_B", "Workers_Comp_C",
                        "Professional_Liability_D", "Property_Comm_E", "Marine_Cargo_F"],
    },
    entity_normal="policy",
    entity_rare="claim_pattern",
    entity_garbage="expired_policy",
    rare_names=[
        "Pandemic_Cascading_Claim", "Cyber_Physical_Crossover",
        "Climate_Novel_Event", "Multi_Policy_Fraud_Signal",
        "Longevity_Risk_Anomaly", "Catastrophe_Bond_Trigger",
    ],
    garbage_names=[
        "Expired_Policy_2020", "Settled_Claim_A", "Lapsed_Coverage_B",
        "Cancelled_Endorsement_C", "Voided_Binder_D", "Closed_Reserve_E",
        "Terminated_Reinsurance_F", "Archived_Actuarial_G",
    ],
    cross_links=[
        ("Auto", "Commercial"),
        ("Home", "Commercial"),
        ("Life", "Health"),
        ("Health", "Commercial"),
        ("Auto", "Home"),
    ],
    normal_label="Policy/risk nodes",
    rare_label="Rare claim patterns",
    garbage_label="Expired/settled",
    scenario_a_desc="(Standard actuarial model optimization)",
    scenario_b_desc="(Critical rare claim patterns preserved)",
    discovery_title="Cross-Product Risk Similarity Discovery",
    discovery_description="Finding product lines with correlated risk profiles",
    discovery_conclusion="Structurally similar products may share tail-risk exposure.\n  Use this for portfolio diversification and reinsurance planning.",
    loss_message="In insurance, missing an emerging claim pattern\n  can lead to catastrophic under-reserving and insolvency.",
)

if __name__ == "__main__":
    run_industry_example(SCENARIO)
