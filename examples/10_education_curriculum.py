#!/usr/bin/env python3
"""
Education / Curriculum Network Example
========================================

Simulates a university curriculum and learning resource network
where courses, topics, and study materials form a knowledge graph.

Scenario:
- 30 mainstream courses across 5 departments with strong prerequisites
- 6 rare interdisciplinary courses (unique cross-department bridges
  that serve small but important student populations)
- 8 discontinued courses (no longer offered)
- Consistency discovery identifies courses with similar prerequisite
  structures, enabling curriculum optimization

The manager should:
1. Maintain prerequisite and corequisite relationships
2. PROTECT rare interdisciplinary courses (they serve unique needs)
3. Clean up discontinued course records
4. Discover courses with similar structures for pathway optimization
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _runner import ScenarioConfig, run_industry_example

SCENARIO = ScenarioConfig(
    number=10,
    title="Education / Curriculum Network",
    categories={
        "CS": [
            "CS_Intro_Programming", "CS_Data_Structures", "CS_Algorithms",
            "CS_Databases", "CS_OS_Systems", "CS_Networks",
        ],
        "Math": [
            "Math_Calculus_I", "Math_Calculus_II", "Math_Linear_Algebra",
            "Math_Probability", "Math_Statistics", "Math_Discrete_Math",
        ],
        "Physics": [
            "Physics_Mechanics", "Physics_Electromagnetism", "Physics_Thermodynamics",
            "Physics_Quantum_Intro", "Physics_Optics", "Physics_Lab_Methods",
        ],
        "Business": [
            "Business_Accounting_101", "Business_Marketing", "Business_Finance_Intro",
            "Business_Management", "Business_Economics", "Business_Strategy",
        ],
        "Biology": [
            "Biology_Cell_Biology", "Biology_Genetics", "Biology_Ecology",
            "Biology_Biochemistry", "Biology_Microbiology", "Biology_Evolution",
        ],
    },
    entity_normal="course",
    entity_rare="interdisciplinary",
    entity_garbage="discontinued",
    rare_names=[
        "BioInformatics_Seminar", "Computational_Finance",
        "Physics_of_Music", "Eco_Data_Science",
        "Neuro_Economics", "Quantum_Computing_Intro",
    ],
    garbage_names=[
        "COBOL_Programming", "Typewriter_Skills", "Slide_Rule_Lab",
        "Punchcard_Systems", "Fortran_77_Intro", "Analog_Computing",
        "Vacuum_Tube_Design", "Teletype_Workshop",
    ],
    cross_links=[
        ("Math", "CS"), ("Math", "Physics"),
        ("CS", "Business"), ("Biology", "CS"),
        ("Physics", "Biology"),
    ],
    normal_label="Mainstream courses",
    rare_label="Interdisciplinary",
    garbage_label="Discontinued",
    scenario_a_desc="(Standard curriculum pruning)",
    scenario_b_desc="(Interdisciplinary courses preserved)",
    discovery_title="Curriculum Structure Discovery",
    discovery_description="Finding courses with similar prerequisite structures",
    discovery_conclusion="Courses with similar structures can share\n  teaching materials and assessment frameworks.",
    loss_message="In education, losing an interdisciplinary course means\n  closing pathways for students with unique career goals.",
    # Non-default parameters
    cross_link_prob=0.35,
    cross_weight_range=(0.2, 0.5),
    rare_weight_range=(0.05, 0.12),
    k_opt=4.5,
    alpha=1.5,
)

if __name__ == "__main__":
    run_industry_example(SCENARIO)
