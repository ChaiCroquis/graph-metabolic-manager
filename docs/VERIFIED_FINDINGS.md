# Verified Findings — graph-metabolic-manager

This document records empirical findings about the graph-metabolic-
manager algorithm on real-world data. Each entry has a unique ID
(`F-001`, `F-002`, …) and is **append-only after independent
verification**.

ID namespace is local to this project. The sister project
[`kdf-perovskite`](sync_with_kdf_perovskite.md) maintains its own
`F-XXX` namespace; cross-references between the two are explicit.

A finding is "verified" only after:

1. Implementation matches a preregistered protocol (no post-hoc
   reframing).
2. An independent Claude session has reviewed the code, data hashes,
   metrics, and verdict against the preregistration.
3. The verdict is recorded against the preregistered criteria, even
   when uncomfortable.

---

## F-001 (VERIFIED) BattLeDIM L-Town leak-pipe ranking — INCONCLUSIVE single-network result

**Status**: VERIFIED (independent verifier verdict: PASS_WITH_NOTES, all
notes addressed in this revision).
**Date**: 2026-05-10
**Preregistration**: [docs/phase_b1_battledim_preregistration.md](phase_b1_battledim_preregistration.md)
**Implementation**: [phase_b1_battledim/run.py](../phase_b1_battledim/run.py) (sha256 `ca926192...`)
**Raw results**: [phase_b1_battledim/results/results.json](../phase_b1_battledim/results/results.json) (sha256 `e121b944...`)
**Data hashes**: [data/battledim/HASHES.sha256](../data/battledim/HASHES.sha256)

### Summary

The graph-metabolic-manager algorithm, run with default parameters
(seed=42, 100 steps) and the preregistered structural-rareness
score, was applied to the BattLeDIM L-Town water distribution network
(785 nodes, 905 pipes) with the 33-pipe leak ground truth from
2018+2019. Against the **literal preregistration baseline panel**
(B0 Random, B1 TopDegree as `min` of endpoint degrees per
preregistration §4 H1, B2 TopBetweenness), the algorithm **slightly
exceeds all baselines but falls short of every preregistered success
criterion**. Per preregistration §5.2 strict reading, the verdict is
**INCONCLUSIVE**.

### Key numbers

| Method | recall@10 | recall@25 | **recall@50 (primary)** | recall@100 | recall@200 |
|---|---:|---:|---:|---:|---:|
| **algorithm** | 0.000 | 0.000 | **0.061** | 0.121 | 0.242 |
| **B1 TopDegree (min, literal preregistration)** | 0.000 | 0.000 | **0.000** | 0.061 | 0.182 |
| TopDegree (sum, supplementary — see Note 1 below) | 0.000 | 0.030 | 0.091 | 0.091 | 0.182 |
| B2 TopBetweenness | 0.000 | 0.000 | 0.030 | 0.030 | 0.182 |
| B0 Random (mean ± std, 30 trials) | 0.011 ± 0.015 | 0.019 ± 0.020 | 0.042 ± 0.033 | 0.103 ± 0.064 | 0.227 ± 0.085 |

### Statistical tests (McNemar exact, K=50)

Bonferroni-corrected α = 0.0167. None of the four pair-wise
comparisons reaches significance.

| Comparison | Statistic | p-value | algo-only | baseline-only | both | neither |
|---|---:|---:|---:|---:|---:|---:|
| algorithm vs B1 TopDegree (min) | 0.0 | 0.5000 | 2 | 0 | 0 | 31 |
| algorithm vs TopDegree (sum, sup) | 2.0 | 1.0 | 2 | 3 | 0 | 28 |
| algorithm vs B2 TopBetweenness | 1.0 | 1.0 | 2 | 1 | 0 | 30 |
| algorithm vs B0 Random (seed=42) | 1.0 | 1.0 | 2 | 1 | 0 | 30 |

The disagreement counts (top-50 contains at most 0–3 leaks for any
method) are small enough that the test has essentially zero power
against +5pp differences. **At K=50, this single-network task is
too sparse to distinguish methods statistically with n=33 leaks.**

### Verdict (per preregistration §5.2 strict reading)

**INCONCLUSIVE.**

Walking the preregistration §5.2 ladder against the literal B1=min
preregistration baseline:

- **H1 success** requires algorithm beats ALL baselines by ≥+5pp at
  K=50 AND beats ≥1 baseline at p<0.0167 (Bonferroni). Algorithm
  delta vs best baseline (Random mean = 0.042) = +0.018 < +0.05,
  and no test reaches significance. **Not H1.**
- **H3 failure** fires if algorithm < Random or algorithm < TopDegree.
  Against literal preregistration baselines, algorithm > Random
  (0.061 > 0.042) AND algorithm > B1 TopDegree (0.061 > 0.000).
  **Not H3.**
- **H2 qualified success** requires tied-with-betweenness (within
  ~2pp) AND beats both Random and TopDegree. Algorithm-vs-betweenness
  gap = 0.061 − 0.030 = 3.1pp, just outside the 2pp tolerance. Beats
  both Random and B1 TopDegree. **Borderline, but per the
  pre-committed 2pp tolerance, not H2.**
- → **INCONCLUSIVE.**

### What this result means

- Against the **literal preregistration baseline panel**, the algorithm
  is **marginally above all baselines** but does not clear the
  preregistered falsifiability bars (+5pp threshold, statistical
  significance, or 2pp betweenness tolerance for qualified success).
- Against a **stronger TopDegree variant** (sum-of-degrees, supplementary
  Note 1), the algorithm **loses** (0.061 < 0.091). This sensitivity
  to baseline choice is itself informative: the algorithm's edge over
  random is small enough that simple variations in how a "TopDegree"
  baseline is defined can flip the qualitative comparison.
- The result does NOT support claiming `#25 Water Management` is a
  **decisive** win zone for the algorithm. It does NOT support
  claiming it is a clear failure zone either.
- For the [applicability.md](applicability.md) classification, this
  argues against retaining the unqualified "Plausible" label and in
  favor of demoting it to "Plausible but no decisive single-test
  support; sensitive to baseline definition."

### What this result does NOT mean

- It does NOT mean the algorithm fails at the BattLeDIM canonical
  task (SCADA-based real-time leak detection). That task uses
  time-series anomaly signals the algorithm is not designed to
  consume; it was excluded by preregistration §3.
- It does NOT generalize to "water networks in general" (n=1
  network).
- It does NOT invalidate the algorithm's specification compliance
  (the 629-test synthetic suite still passes).
- It does NOT establish whether parameter tuning would change the
  result (preregistration §5.1 forbade hyperparameter search).

### Implementation notes (disclosure)

**Note 1 (verifier-caught): TopDegree baseline definition deviated from
literal preregistration text in v1.** Preregistration §4 H1 specifies
B1 TopDegree as "両端ノードの次数の**小さい方**" (min of endpoint
degrees). The first version of `phase_b1_battledim/run.py` used
**sum** of endpoint degrees, which is a stronger baseline than the
literal preregistration. The v1 result with sum-TopDegree was
H3_ACCEPT_FAILURE; correcting B1 to the literal min-TopDegree per
preregistration flipped the verdict to INCONCLUSIVE. This disclosure
is the result of an independent verification audit that caught the
deviation. The current `topdegree_pipe_ranking()` accepts an
`aggregator` parameter and reports both `min` (primary B1) and `sum`
(supplementary) ranking results in `results.json`. **The literal
preregistration baseline (min) is the verdict-determining one; the
sum variant is reported for transparency but is not part of the
preregistered protocol.**

**Note 2 (verifier-caught): edge-weight normalization disclosure.**
Preregistration §2 commits "edge weight = pipe length". The
implementation at `phase_b1_battledim/run.py:154` normalizes weight to
`length / max_length` (clamped to ≥ 1e-6) for numerical-range hygiene
in the algorithm. **Rank order is preserved**: any monotonic
transformation of length yields the same ranking under the algorithm's
local-congestion logic. This deviation is hygienic and does not affect
the ranking, but is now disclosed.

**Note 3 (verifier-caught): pre-commit verdict-logic correction.**
The very first version of the verdict-classification function in
`run.py` would have labeled this result `H2_ACCEPT_QUALIFIED`. While
inspecting the H2 verdict for plausibility against the recall@K
table, a missing condition was found: H2 requires beating both
TopDegree AND Random, but the v0 H2 condition only checked
betweenness-tied AND beats-Random. The v0 code was corrected before
the first git commit. The current `main()` function evaluates H3 first
to prevent H2 from masking failure cases, and the H2 condition
explicitly checks both Random and TopDegree. **No git diff exists for
this fix** (the bug existed only in pre-commit working state); the
disclosure is honest documentation that v0 was wrong, v1 (current,
hash `ca926192...`) is correct per preregistration §5.2, and the
audit caught a similar but unrelated B1-definition issue.

### Limitations honestly disclosed

1. **Single-network result**: L-Town is one Cypriot water utility;
   no replication across networks was performed in this Phase B-1.
2. **Small leak count (n=33)**: statistical power is essentially zero
   for paired tests at K=50. The +5pp falsifiability bar in H1 is
   meaningful (random recall@50 ≈ 0.042 with std 0.033, so +5pp is
   ≈1.5σ over random), but McNemar's test on 33 paired outcomes
   cannot detect such a difference at α=0.0167.
3. **Framing**: leak ground truth records "where leaks happened
   during 2018–2019". Whether structural criticality should
   correlate with leak occurrence is a researcher hypothesis, not a
   physical necessity. Leaks depend on pipe age, pressure, soil
   conditions, manufacturing defects — not just structure.
4. **Default parameters**: per preregistration, no hyperparameter
   search was performed. Whether tuning would improve the result
   is unanswered.
5. **Score formulation**: `(rare_count, edge_survived,
   -initial_degree_sum)` was committed before the run. Alternative
   formulations are explicitly out of scope for this preregistration.
6. **Baseline-sensitivity**: the verdict differs under
   sum-TopDegree (H3 failure) vs min-TopDegree (literal preregistration
   = INCONCLUSIVE). This argues for treating any single baseline
   panel as fragile evidence on this dataset.

### Cross-reference with kdf-perovskite

Consistent with the broader pattern from
[`kdf-perovskite` F-061](sync_with_kdf_perovskite.md): the algorithm
does not show a decisive lift over classical degree-based baselines
on real graphs even when the regime (planar non-scale-free utility
network) was structurally classified as "Plausible". The new
information is the **strength** of the absence-of-lift on a
structurally favorable single network: marginal positive but no
preregistered success criterion satisfied.

### Independent verification

Verifier (fresh-context Claude agent, see commit message):
**PASS_WITH_NOTES**.

| # | Audit category | Verifier finding |
|---|---|---|
| 1 | Data integrity (HASHES.sha256 match) | clean |
| 2 | Code-vs-spec faithfulness | note 1 (TopDegree formula), note 2 (weight normalization) |
| 3 | Numerical reproducibility (seed=42 bit-identical) | clean |
| 4 | Verdict derivation per §5.2 | clean |
| 5 | Post-hoc reframing check | clean |
| 6 | Implementation transparency note | note 3 (git history claim corrected) |

All three notes addressed in this revision (B1 baseline corrected to
literal preregistration definition, weight normalization disclosed,
git history claim reworded). The verifier's substantive verdict
(PASS_WITH_NOTES, not FAIL) was based on the H3 result obtained with
sum-TopDegree; with the corrected min-TopDegree the verdict changes
to INCONCLUSIVE. The verifier's audit is what enabled this
correction.
