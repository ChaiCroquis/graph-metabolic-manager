#!/usr/bin/env python3
"""
Academic Citation Network Example
====================================

Simulates a research paper citation network where papers, authors,
and research topics form an evolving knowledge graph.

Scenario:
- 30 well-cited papers across 5 research fields
- 6 rare interdisciplinary papers (bridging distant fields with
  few citations but high novelty — must be preserved)
- 8 retracted/superseded papers (should be cleaned up)
- Consistency discovery identifies papers with similar citation
  structures, revealing hidden thematic connections

The manager should:
1. Maintain citation network under growing volume
2. PROTECT rare interdisciplinary papers (seeds of new fields)
3. Clean up retracted/superseded records
4. Discover structurally similar research clusters
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _runner import ScenarioConfig, run_industry_example

SCENARIO = ScenarioConfig(
    number=12,
    title="Academic Citation Network",
    categories={
        "Machine_Learning": [
            "Deep_Learning_Survey", "Transformer_Architecture",
            "GAN_Advances", "Reinforcement_Learning_Review",
            "Federated_Learning", "Neural_Architecture_Search",
        ],
        "Bioinformatics": [
            "Protein_Folding_2024", "Genome_Assembly_Method",
            "Drug_Target_Prediction", "Single_Cell_Analysis",
            "Metagenomics_Pipeline", "CRISPR_Optimization",
        ],
        "Quantum_Computing": [
            "Quantum_Error_Correction", "Variational_Algorithms",
            "Quantum_Supremacy_Exp", "Topological_Qubits",
            "Quantum_ML_Hybrid", "Quantum_Simulation_Review",
        ],
        "Climate_Science": [
            "Global_Warming_Model", "Ocean_Circulation_Study",
            "Carbon_Capture_Review", "Extreme_Weather_Predict",
            "Ice_Sheet_Dynamics", "Aerosol_Climate_Interaction",
        ],
        "Neuroscience": [
            "Brain_Connectome_Map", "Neural_Plasticity_Review",
            "Consciousness_Theory", "Memory_Consolidation",
            "Neurodegenerative_Markers", "Brain_Computer_Interface",
        ],
    },
    entity_normal="paper",
    entity_rare="interdisciplinary",
    entity_garbage="retracted",
    rare_names=[
        "Quantum_Biology_Bridge", "Neuro_Climate_Modeling",
        "AI_Consciousness_Theory", "Quantum_Genome_Analysis",
        "Climate_Neuroscience_Link", "Bio_Quantum_ML_Fusion",
    ],
    garbage_names=[
        "Retracted_Fraud_Study", "Superseded_Method_A",
        "Disproven_Hypothesis_1", "Withdrawn_Clinical_Trial",
        "Corrected_Then_Removed", "Plagiarized_Analysis",
        "Irreproducible_Result", "Outdated_Survey_2018",
    ],
    cross_links=[
        ("Machine_Learning", "Bioinformatics"),
        ("Machine_Learning", "Quantum_Computing"),
        ("Bioinformatics", "Neuroscience"),
        ("Climate_Science", "Machine_Learning"),
        ("Quantum_Computing", "Climate_Science"),
    ],
    normal_label="Well-cited papers",
    rare_label="Interdisciplinary",
    garbage_label="Retracted/superseded",
    scenario_a_desc="(Standard citation pruning by impact)",
    scenario_b_desc="(Interdisciplinary papers preserved)",
    discovery_title="Hidden Research Connection Discovery",
    discovery_description="Finding papers with similar citation structures",
    discovery_conclusion="These connections reveal emerging research themes\n  that span traditional field boundaries.",
    loss_message="In academia, today's obscure interdisciplinary paper\n  may be tomorrow's Nobel Prize-winning breakthrough.",
    # Non-default parameters
    cross_link_prob=0.35,
    cross_weight_range=(0.15, 0.4),
    k_opt=4.5,
)

if __name__ == "__main__":
    run_industry_example(SCENARIO)
