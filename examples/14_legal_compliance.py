#!/usr/bin/env python3
"""
Legal / Compliance Network Example
=====================================

Simulates a legal and regulatory compliance network connecting
contracts, IP filings, tax rulings, employment cases, and regulations.

Scenario:
- 30 legal document nodes across 5 practice areas
- 6 rare precedent nodes (novel rulings that reshape entire
  domains — losing them means missing critical legal shifts)
- 8 garbage nodes (expired regulations, superseded statutes)
- Consistency discovery identifies cross-domain legal principles
  that share structural similarity, enabling better risk mapping

The manager should:
1. Maintain active legal document relationships under congestion
2. PROTECT rare precedent nodes (irreplaceable legal signals)
3. Clean up expired regulations and superseded statutes
4. Discover structurally similar cross-domain legal principles
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _runner import ScenarioConfig, run_industry_example

SCENARIO = ScenarioConfig(
    number=14,
    title="Legal / Compliance Network",
    categories={
        "Contract_Law": ["Master_Agreement_A", "SaaS_Contract_1", "NDA_Template_B",
                         "Licensing_Deal_C", "Joint_Venture_D", "Franchise_Pact_E"],
        "IP_Law": ["Patent_Portfolio_1", "Trademark_Bundle_A", "Copyright_Case_B",
                    "Trade_Secret_C", "Design_Patent_D", "IP_Licensing_E"],
        "Tax_Law": ["Transfer_Pricing_A", "R_and_D_Credit_B", "Intl_Tax_Treaty_C",
                     "Estate_Tax_Plan_D", "Sales_Tax_Nexus_E", "Crypto_Tax_Rule_F"],
        "Employment_Law": ["Non_Compete_A", "Whistleblower_Case_B", "Union_Agreement_C",
                           "Remote_Work_Policy_D", "Exec_Compensation_E", "DEI_Compliance_F"],
        "Regulatory": ["FDA_Guidance_A", "SEC_Filing_B", "EPA_Standard_C",
                        "FCC_Rule_D", "OSHA_Compliance_E", "GDPR_Mapping_F"],
    },
    entity_normal="legal_doc",
    entity_rare="precedent",
    entity_garbage="expired_law",
    rare_names=[
        "Cross_Border_Precedent", "AI_Liability_Novel_Case",
        "Blockchain_Contract_First", "Privacy_Landmark_EU",
        "Antitrust_Rare_Ruling", "Environmental_Novel_Claim",
    ],
    garbage_names=[
        "Repealed_Statute_2015", "Superseded_Reg_A", "Vacated_Ruling_B",
        "Expired_Exemption_C", "Withdrawn_Guidance_D", "Overturned_Order_E",
        "Defunct_Treaty_F", "Archived_Advisory_G",
    ],
    cross_links=[
        ("Contract_Law", "IP_Law"),
        ("Tax_Law", "Regulatory"),
        ("Employment_Law", "Regulatory"),
        ("IP_Law", "Tax_Law"),
        ("Contract_Law", "Employment_Law"),
    ],
    normal_label="Legal document nodes",
    rare_label="Rare precedents",
    garbage_label="Expired/superseded",
    scenario_a_desc="(Standard legal document optimization)",
    scenario_b_desc="(Critical rare precedents preserved)",
    discovery_title="Cross-Domain Legal Principle Discovery",
    discovery_description="Finding legal areas with similar structural patterns",
    discovery_conclusion="Structurally similar legal areas may face analogous risks.\n  Use this for cross-practice compliance and risk mapping.",
    loss_message="In legal compliance, missing a novel precedent\n  can expose organizations to massive regulatory risk.",
)

if __name__ == "__main__":
    run_industry_example(SCENARIO)
