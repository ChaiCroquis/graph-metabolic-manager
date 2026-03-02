#!/usr/bin/env python3
"""
HR / Talent Management Network Example
=========================================

Simulates an HR and talent management network connecting employees,
roles, and skill profiles across multiple departments.

Scenario:
- 30 employee/role nodes across 5 departments
- 6 rare cross-disciplinary skill combination nodes (unique
  talent signals — losing them means missing key hires)
- 8 garbage nodes (resigned employees, closed positions)
- Consistency discovery identifies cross-department talent
  similarity, enabling strategic workforce planning

The manager should:
1. Maintain active talent relationships under congestion
2. PROTECT rare skill combination signals (irreplaceable talent insights)
3. Clean up resigned employee and closed position records
4. Discover structurally similar cross-department talent profiles
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _runner import ScenarioConfig, run_industry_example

SCENARIO = ScenarioConfig(
    number=15,
    title="HR / Talent Management Network",
    categories={
        "Engineering": ["Senior_Dev_A", "Backend_Lead_B", "Frontend_Eng_C",
                        "DevOps_Eng_D", "QA_Lead_E", "Architect_F"],
        "Sales": ["Account_Exec_A", "Sales_Dir_B", "BDR_Rep_C",
                   "Enterprise_Rep_D", "Channel_Mgr_E", "Sales_Ops_F"],
        "Marketing": ["Content_Lead_A", "SEO_Specialist_B", "Brand_Mgr_C",
                       "Growth_Hacker_D", "PR_Director_E", "Analytics_Mgr_F"],
        "Operations": ["Supply_Chain_A", "Procurement_B", "Facilities_Mgr_C",
                        "Project_Mgr_D", "Process_Eng_E", "Logistics_Lead_F"],
        "Research": ["Data_Scientist_A", "ML_Engineer_B", "Research_Dir_C",
                      "Lab_Tech_D", "Statistician_E", "Research_Analyst_F"],
    },
    entity_normal="employee",
    entity_rare="rare_skill",
    entity_garbage="inactive",
    rare_names=[
        "ML_Plus_Biology", "Quantum_Finance_Hybrid",
        "Design_Plus_DataScience", "Legal_Plus_AI",
        "Hardware_Plus_ML", "Linguistics_Plus_Security",
    ],
    garbage_names=[
        "Resigned_Eng_2023", "Closed_Role_Sales_A", "Terminated_Ops_B",
        "Retired_Director_C", "Departed_Analyst_D", "Cancelled_Req_E",
        "Frozen_Position_F", "Eliminated_Role_G",
    ],
    cross_links=[
        ("Engineering", "Research"),
        ("Sales", "Marketing"),
        ("Operations", "Engineering"),
        ("Marketing", "Research"),
        ("Sales", "Operations"),
    ],
    normal_label="Employee/role nodes",
    rare_label="Rare skill combos",
    garbage_label="Inactive records",
    scenario_a_desc="(Standard talent pool optimization)",
    scenario_b_desc="(Critical rare skill signals preserved)",
    discovery_title="Cross-Department Talent Similarity Discovery",
    discovery_description="Finding roles with similar structural talent profiles",
    discovery_conclusion="Structurally similar roles may benefit from talent sharing.\n  Use this for internal mobility and cross-training programs.",
    loss_message="In talent management, losing rare cross-disciplinary\n  skill signals can mean missing transformative hires.",
    connect_prob=0.50,
)

if __name__ == "__main__":
    run_industry_example(SCENARIO)
