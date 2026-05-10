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

Findings under review are clearly labeled **PRE-VERIFICATION DRAFT**
until step 2 completes.

---

## F-001 (PRE-VERIFICATION DRAFT) BattLeDIM L-Town leak-pipe ranking — H3 honest failure

**Status**: PRE-VERIFICATION DRAFT — independent verification not yet
performed. **DO NOT cite externally** until verification completes.

**Date drafted**: 2026-05-10
**Preregistration**: [docs/phase_b1_battledim_preregistration.md](phase_b1_battledim_preregistration.md)
**Implementation**: [phase_b1_battledim/run.py](../phase_b1_battledim/run.py) (sha256 `c6c9d506...`)
**Raw results**: [phase_b1_battledim/results/results.json](../phase_b1_battledim/results/results.json) (sha256 `11d902f0...`)
**Data hashes**: [data/battledim/HASHES.sha256](../data/battledim/HASHES.sha256)

### Summary

The graph-metabolic-manager algorithm, run with default parameters
(seed=42, 100 steps) and the preregistered structural-rareness
score, was applied to the BattLeDIM L-Town water distribution network
(785 nodes, 905 pipes) with the 33-pipe leak ground truth from 2018+
2019. The algorithm's pipe ranking achieved **recall@50 = 0.061** vs
**TopDegree baseline recall@50 = 0.091**. Per the preregistration's
strict §5.2 criteria, this is **H3_ACCEPT_FAILURE**.

### Key numbers

| Method | recall@10 | recall@25 | **recall@50 (primary)** | recall@100 | recall@200 |
|---|---:|---:|---:|---:|---:|
| **algorithm** | 0.000 | 0.000 | **0.061** | 0.121 | 0.242 |
| TopDegree | 0.000 | 0.030 | **0.091** | 0.091 | 0.182 |
| TopBetweenness | 0.000 | 0.000 | **0.030** | 0.030 | 0.182 |
| Random (mean ± std, 30 trials) | 0.011 ± 0.015 | 0.019 ± 0.020 | **0.042 ± 0.033** | 0.103 ± 0.064 | 0.227 ± 0.085 |

### Statistical tests (McNemar exact, K=50)

All paired tests yielded **p = 1.0** (no significant difference).
Bonferroni-corrected α = 0.0167.

| Comparison | Statistic | p-value | algo-only | baseline-only | both | neither |
|---|---:|---:|---:|---:|---:|---:|
| algorithm vs TopDegree | 2.0 | 1.0 | 2 | 3 | 0 | 28 |
| algorithm vs TopBetweenness | 1.0 | 1.0 | 2 | 1 | 0 | 30 |
| algorithm vs Random (seed=42) | 1.0 | 1.0 | 2 | 1 | 0 | 30 |

The disagreement counts (top-50 contains at most 2–3 leaks for any
method) are small enough that the test has essentially zero power
against +5pp differences. This is itself a finding: **at K=50 the
problem is too sparse to distinguish methods statistically with
n=33 leaks**.

### Verdict (per preregistration §5.2 strict reading)

**H3_ACCEPT_FAILURE**

- algorithm recall@50 (0.061) **< TopDegree recall@50 (0.091)**
- delta vs best baseline = **−0.030**
- No baseline significantly beaten under Bonferroni
- Per preregistration: "Algorithm が Random / TopDegree いずれかに敗北
  → **H3 採択 = failure**"

The algorithm fails to identify leak pipes in this single static
ranking task at the preregistered primary metric. A simple
"top-degree-sum" heuristic outperforms it.

### Implementation transparency note

The author's first run of `run.py` had a verdict-classification bug
that would have classified this result as `H2_ACCEPT_QUALIFIED`. The
preregistration's explicit §5.2 criteria forced an audit when the
H2 result felt incongruent with the recall@K table, revealing that
the H2 condition in the code was missing the "beats TopDegree"
requirement that the preregistration text mandates. The bug was
fixed and the script re-ran deterministically (seed=42 produces
bit-identical recall numbers); only the verdict label changed
**from a too-lenient H2 to the correct H3**.

This is a structural validation of the preregistration discipline:
**it caught an error that would have led to an over-positive public
claim.** The diff in the verdict logic is in `run.py` git history.

### What this result means

- The 28-industry classification in [applicability.md](applicability.md)
  currently lists `#25 Water Management` as "**Plausible** (path-critical
  pattern)". This finding does NOT yet update that classification,
  because:
  1. Independent verification has not been performed.
  2. A single-network result (L-Town only) cannot generalize to "water
     networks fail" — kdf-perovskite F-061 etc. discipline requires
     multi-instance evidence.
  3. The framing is static criticality ranking, NOT real-time SCADA-
     based leak detection. The latter is the canonical BattLeDIM
     task and is outside this algorithm's design.

- Once independently verified, applicability.md #25 should be
  reclassified to reflect this single negative result honestly. The
  appropriate label is something between "Plausible" and "Unlikely
  to apply" — with the leak-pipe-ranking framing, the algorithm did
  not beat TopDegree on the only real test attempted.

### What this result does NOT mean

- It does NOT mean the algorithm fails at the BattLeDIM canonical
  task (SCADA-based leak detection). That task uses time-series
  anomaly signals the algorithm is not designed to consume.
- It does NOT generalize to "water networks in general" (n=1).
- It does NOT mean the algorithm fails at all path-critical /
  non-scale-free regimes — kdf-perovskite F-061 establishes the
  algorithm wins on synthetic SBM/random graphs in the same regime.
  L-Town's structural properties may differ from those benchmarks
  in ways that matter (planar, geographic constraints, age-driven
  leak distribution).
- It does NOT invalidate the algorithm's specification compliance
  (the 629-test synthetic suite still passes).

### Limitations honestly disclosed

1. **Single-network result**: L-Town is one Cypriot water utility;
   no replication across networks was performed in this Phase B-1.
2. **Small leak count (n=33)**: statistical power is essentially zero
   for paired tests at K=50.
3. **Framing**: The leak ground truth is "where leaks happened during
   2018–2019". Whether structural criticality should correlate with
   leak occurrence is a researcher hypothesis, not a physical
   necessity. Leaks depend on pipe age, pressure, soil conditions,
   manufacturing defects — not just structure. The preregistration
   acknowledged this.
4. **Default parameters**: per preregistration, no hyperparameter
   search was performed. Whether tuning would improve the result is
   unanswered (and would require a separate preregistration to test
   honestly).
5. **Score formulation**: The `(rare_count, edge_survived,
   -initial_degree_sum)` tuple was committed BEFORE running, but it
   is one of several plausible formulations. Alternative formulations
   are explicitly out of scope for this preregistration.
6. **Verdict-logic bug**: see "Implementation transparency note"
   above. Fixed before final result was recorded.

### Cross-reference with kdf-perovskite

This finding is consistent with the broader pattern from
[`kdf-perovskite` F-061](sync_with_kdf_perovskite.md) (algorithm
ties or loses to TopDegree on certain real graph regimes). It is
NOT redundant with that finding because L-Town is a planar utility
network, not the scale-free graphs that F-061 falsified. **The new
information is**: even on a non-scale-free planar graph that we
classified as "Plausible", the algorithm did not beat the simplest
degree-based baseline on this specific framing.

### Independent verification — required next step

Per preregistration §5.4, this finding cannot be "verified" until
a fresh Claude session reviews:

1. Data hashes match `data/battledim/HASHES.sha256`
2. `phase_b1_battledim/run.py` faithfully implements the
   preregistered protocol (Graph conversion, score formulation,
   baselines, recall@K, McNemar test)
3. The recorded numbers in `results.json` are bit-reproducible from
   running the script (seed=42)
4. The verdict (H3_ACCEPT_FAILURE) is correctly derived from those
   numbers per preregistration §5.2 — and no post-hoc K-shopping or
   alternative score formulation was introduced
5. The `applicability.md` update plan above is consistent with the
   preregistration commitment

Verifier verdict: **PASS** / **PASS_WITH_NOTES** / **FAIL** —
to be entered when independent verification runs.
