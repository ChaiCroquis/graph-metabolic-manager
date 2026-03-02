#!/usr/bin/env python3
"""
Medical Knowledge Graph Example
================================

Simulates a disease-gene-drug knowledge graph used in drug discovery.

Scenario:
- 20 well-known diseases with established gene/drug connections
- 8 rare diseases (few connections but critically important)
- 8 deprecated drug candidates (failed clinical trials)
- Consistency discovery finds potential drug repurposing candidates
  by detecting structural similarity between rare and common diseases

The manager should:
1. Maintain well-established medical knowledge connections
2. Protect rare disease data from deletion (orphan diseases matter!)
3. Clean up deprecated drug candidates
4. Discover potential drug repurposing opportunities
"""

import logging
import random

from graph_metabolic_manager import (
    ConsistencyDiscovery,
    Graph,
    GraphMetabolicManager,
)

logging.basicConfig(level=logging.INFO, format="%(message)s")


def build_medical_graph(seed: int = 42) -> tuple:
    """Build a simulated medical knowledge graph."""
    random.seed(seed)
    g = Graph()

    # Common diseases with well-known gene/drug connections
    diseases = []
    disease_names = [
        "Type2_Diabetes", "Hypertension", "Asthma", "Depression",
        "Alzheimer", "Breast_Cancer", "Lung_Cancer", "Arthritis",
        "Heart_Failure", "COPD", "Hepatitis_B", "HIV",
        "Parkinson", "Epilepsy", "Migraine", "Osteoporosis",
        "Anemia", "Thyroid_Disorder", "Psoriasis", "Crohn_Disease",
    ]
    for name in disease_names:
        nid = g.add_node(name, node_type="normal", entity="disease")
        diseases.append(nid)

    # Genes associated with diseases
    genes = []
    gene_names = [
        "BRCA1", "TP53", "EGFR", "KRAS", "APOE", "TNF",
        "IL6", "VEGF", "HER2", "ACE", "BRAF", "JAK2",
        "PTEN", "RB1", "MYC",
    ]
    for name in gene_names:
        nid = g.add_node(name, node_type="normal", entity="gene")
        genes.append(nid)

    # Approved drugs
    drugs = []
    drug_names = [
        "Metformin", "Lisinopril", "Salbutamol", "Fluoxetine",
        "Donepezil", "Tamoxifen", "Pembrolizumab", "Methotrexate",
        "Enalapril", "Tiotropium", "Entecavir", "Dolutegravir",
    ]
    for name in drug_names:
        nid = g.add_node(name, node_type="normal", entity="drug")
        drugs.append(nid)

    # Disease-gene connections (established knowledge)
    for disease in diseases:
        n_genes = random.randint(2, 5)
        for gene in random.sample(genes, min(n_genes, len(genes))):
            g.add_edge(disease, gene, weight=random.uniform(0.5, 1.0))

    # Disease-drug connections (approved treatments)
    for _i, disease in enumerate(diseases):
        n_drugs = random.randint(1, 3)
        for drug in random.sample(drugs, min(n_drugs, len(drugs))):
            g.add_edge(disease, drug, weight=random.uniform(0.4, 0.9))

    # Gene-drug connections (known mechanisms)
    for gene in genes:
        if random.random() < 0.4:
            drug = random.choice(drugs)
            g.add_edge(gene, drug, weight=random.uniform(0.3, 0.7))

    # Rare diseases (orphan diseases - few connections but critical)
    rare_diseases = []
    rare_names = [
        "Gaucher_Disease", "Fabry_Disease", "Huntington",
        "ALS", "Progeria", "Sickle_Cell_Rare_Variant",
        "Niemann_Pick", "Pompe_Disease",
    ]
    for name in rare_names:
        nid = g.add_node(name, node_type="truth", entity="rare_disease")
        # Each rare disease has only 1 weak gene connection
        gene = random.choice(genes)
        g.add_edge(nid, gene, weight=random.uniform(0.05, 0.15))
        rare_diseases.append(nid)

    # Deprecated drug candidates (failed clinical trials)
    deprecated = []
    deprecated_names = [
        "FailedDrug_A", "FailedDrug_B", "FailedDrug_C",
        "FailedDrug_D", "Withdrawn_X", "Withdrawn_Y",
        "Toxic_Compound_1", "Toxic_Compound_2",
    ]
    for name in deprecated_names:
        nid = g.add_node(name, node_type="garbage", entity="deprecated_drug")
        # No connections (removed from active research)
        deprecated.append(nid)

    return g, diseases, genes, drugs, rare_diseases, deprecated


def main():
    print("=" * 60)
    print("  Example 4: Medical Knowledge Graph")
    print("=" * 60)

    g, diseases, genes, drugs, rare_diseases, deprecated = build_medical_graph()

    print("\nInitial knowledge graph:")
    print(f"  Common diseases:   {len(diseases)}")
    print(f"  Genes:             {len(genes)}")
    print(f"  Approved drugs:    {len(drugs)}")
    print(f"  Rare diseases:     {len(rare_diseases)} (orphan diseases)")
    print(f"  Deprecated drugs:  {len(deprecated)} (failed trials)")
    print(f"  Total: {g.node_count()} nodes, {g.edge_count()} edges")
    print(f"  Average degree: {g.avg_degree():.2f}")

    # ----------------------------------------------------------
    # Part 1: Metabolic management
    # ----------------------------------------------------------
    print("\n--- Part 1: Knowledge Graph Maintenance (150 steps) ---")

    mgr = GraphMetabolicManager(
        g,
        seed=42,
        enable_rarity=True,
        enable_consistency=False,
        k_opt=6.0,
        alpha=1.8,
        beta=0.03,
    )

    mgr.run(steps=150, verbose=True)

    rare_survived = sum(1 for nid in rare_diseases if g.has_node(nid))
    deprecated_survived = sum(1 for nid in deprecated if g.has_node(nid))
    diseases_survived = sum(1 for nid in diseases if g.has_node(nid))
    genes_survived = sum(1 for nid in genes if g.has_node(nid))
    drugs_survived = sum(1 for nid in drugs if g.has_node(nid))

    print("\n  Results:")
    print(f"  Common diseases:  {diseases_survived}/{len(diseases)} remaining")
    print(f"  Genes:            {genes_survived}/{len(genes)} remaining")
    print(f"  Drugs:            {drugs_survived}/{len(drugs)} remaining")
    print(f"  Rare diseases:    {rare_survived}/{len(rare_diseases)} PROTECTED")
    print(f"  Deprecated drugs: {len(deprecated) - deprecated_survived}/{len(deprecated)} cleaned")

    # ----------------------------------------------------------
    # Part 2: Drug repurposing discovery
    # ----------------------------------------------------------
    print("\n--- Part 2: Drug Repurposing Discovery ---")
    print("  (Finding rare diseases with similar gene profiles to common ones)")

    g2, diseases2, genes2, drugs2, rare2, _ = build_medical_graph(seed=99)

    cd = ConsistencyDiscovery(theta_l=0.55, theta_u=0.85, k_hop=2)
    discoveries = cd.discover(g2, rare_node_ids=rare2, candidate_ids=diseases2)

    if discoveries:
        print(f"\n  Found {len(discoveries)} potential repurposing connections:")
        for rare_id, common_id, score in discoveries[:8]:
            rare_label = g2.nodes[rare_id].label
            common_label = g2.nodes[common_id].label
            print(f"    {rare_label} <-> {common_label} (score: {score:.3f})")
        print("\n  These suggest that treatments for the common diseases")
        print("  might be investigated for the rare diseases.")
    else:
        print("\n  No direct matches found in current threshold range.")

    # ----------------------------------------------------------
    # Evaluation
    # ----------------------------------------------------------
    print("\n--- Evaluation ---")
    if rare_survived > 0:
        print(f"  [OK] Rare disease data protected ({rare_survived}/{len(rare_diseases)})")
        print("       Orphan diseases preserved for future research")
    else:
        print("  [!!] Rare disease data lost!")

    if deprecated_survived < len(deprecated):
        print(f"  [OK] Deprecated drugs cleaned ({len(deprecated) - deprecated_survived}/{len(deprecated)})")
    else:
        print("  [!!] Deprecated drugs not cleaned!")

    print("\nDone!")


if __name__ == "__main__":
    main()
