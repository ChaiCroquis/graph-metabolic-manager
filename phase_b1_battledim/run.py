"""
Phase B-1 — BattLeDIM L-Town real-data validation.

Purpose
-------
Test the preregistered hypothesis (docs/phase_b1_battledim_preregistration.md
H1) that the graph-metabolic-manager algorithm's structural-rareness pipe
ranking achieves higher recall@K than Random / TopDegree / TopBetweenness
baselines on the BattLeDIM L-Town water distribution network leak labels.

Score commitment (committed BEFORE running, addresses preregistration §3 gap)
---------------------------------------------------------------------------
For each pipe (u, v) in the original network, define the algorithm score
lexicographically (descending) as:

    (rare_count, edge_survived, -initial_degree_sum)

where:
    rare_count        = number of endpoints u, v with phase != "normal" after
                        running GraphMetabolicManager (default params, seed=42,
                        100 steps), in {0, 1, 2}.
    edge_survived     = 1 if the edge still exists after the run, else 0.
    initial_degree_sum= deg(u) + deg(v) in the ORIGINAL graph (before run).

The score is computed once per pipe; ties are broken arbitrarily by Python's
stable sort over the deterministic input order.

This score formulation is fixed BEFORE the run. It MUST NOT be changed after
seeing the result.

This script is a one-shot evaluator. It does NOT re-run with different
parameters, does NOT search hyperparameters, and does NOT shop for a
better K.
"""

from __future__ import annotations

import json
import logging
import random
import sys
from pathlib import Path

import networkx as nx
import numpy as np
import wntr
from statsmodels.stats.contingency_tables import mcnemar

# Ensure local package is importable when running this script directly.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from graph_metabolic_manager import Graph, GraphMetabolicManager  # noqa: E402

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# Pre-committed evaluation parameters (do NOT change after run)
# ------------------------------------------------------------------
SEED = 42
ALGORITHM_STEPS = 100
K_VALUES = [10, 25, 50, 100, 200]
PRIMARY_K = 50
RANDOM_TRIALS = 30
ALPHA_LEVEL = 0.05
NUM_BASELINES = 3  # Random, TopDegree, TopBetweenness
BONFERRONI_ALPHA = ALPHA_LEVEL / NUM_BASELINES  # 0.0167

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data" / "battledim"
RESULTS_DIR = Path(__file__).resolve().parent / "results"


# ------------------------------------------------------------------
# Data loading
# ------------------------------------------------------------------
def load_battledim_data() -> tuple[
    list[str], list[tuple[str, str, str, float]], set[str]
]:
    """Load L-Town network and leak ground truth.

    Returns:
        junctions: list of junction node IDs (strings).
        pipes: list of (pipe_id, u_id, v_id, length) tuples.
        leak_pipe_ids: set of pipe IDs that experienced a leak in 2018+2019.
    """
    inp_path = DATA_DIR / "L-TOWN.inp"
    wn = wntr.network.WaterNetworkModel(str(inp_path))

    # Node list (junctions, tanks, reservoirs all become graph nodes for
    # connectivity purposes; the algorithm operates on the unified node set).
    junctions = list(wn.node_name_list)

    # Pipe list with original endpoint IDs and length (length = edge weight
    # per preregistration §2 commitment).
    pipes: list[tuple[str, str, str, float]] = []
    for pipe_name, pipe in wn.pipes():
        pipes.append((pipe_name, pipe.start_node_name, pipe.end_node_name, float(pipe.length)))

    # Leak ground truth: union of pipe IDs that appear as columns in
    # 2018_Leakages.csv and 2019_Leakages.csv (each column is a leaked pipe).
    leak_pipe_ids: set[str] = set()
    for csv_name in ("2018_Leakages.csv", "2019_Leakages.csv"):
        with open(DATA_DIR / csv_name, encoding="utf-8") as f:
            header = f.readline().strip()
        cols = header.split(";")
        # First column is "Timestamp", remaining are pipe IDs.
        leak_pipe_ids.update(cols[1:])

    # Sanity check: leak pipe IDs should all exist in the network.
    pipe_id_set = {p[0] for p in pipes}
    missing = leak_pipe_ids - pipe_id_set
    if missing:
        raise ValueError(f"Leak pipe IDs not in network: {sorted(missing)}")

    return junctions, pipes, leak_pipe_ids


# ------------------------------------------------------------------
# Graph construction
# ------------------------------------------------------------------
def build_graph(
    junctions: list[str], pipes: list[tuple[str, str, str, float]]
) -> tuple[Graph, dict[str, int], list[tuple[str, int, int]]]:
    """Build a graph_metabolic_manager.Graph from BattLeDIM topology.

    Edge weight = pipe length (commitment per preregistration §2).
    To keep weights in a numerically reasonable range for the algorithm
    (which expects weights typically in [0, 1] or O(1)), normalize by max.

    Returns:
        graph: the constructed Graph.
        name_to_id: mapping from BattLeDIM node name to internal int ID.
        edge_index: list of (pipe_id, u_int, v_int) for downstream lookup.
    """
    g = Graph()
    name_to_id: dict[str, int] = {}
    for name in junctions:
        nid = g.add_node(name, node_type="normal")
        name_to_id[name] = nid

    # Some pipes connect to nodes not in the junction list (tanks/reservoirs
    # would appear above; here all WN nodes are included). Defensive check.
    max_length = max(p[3] for p in pipes) if pipes else 1.0
    edge_index: list[tuple[str, int, int]] = []
    for pipe_id, u_name, v_name, length in pipes:
        if u_name not in name_to_id:
            name_to_id[u_name] = g.add_node(u_name, node_type="normal")
        if v_name not in name_to_id:
            name_to_id[v_name] = g.add_node(v_name, node_type="normal")
        u_int = name_to_id[u_name]
        v_int = name_to_id[v_name]
        # Normalized weight in (0, 1]. Higher length => higher weight (slower
        # decay because longer pipes are "heavier" in the network).
        weight = length / max_length if max_length > 0 else 1.0
        # Avoid degenerate zero-weight edges.
        weight = max(weight, 1e-6)
        # If multiple pipes connect the same two junctions (rare but possible),
        # use the maximum weight.
        if g.has_edge(u_int, v_int):
            existing = g.get_weight(u_int, v_int)
            g.set_weight(u_int, v_int, max(existing, weight))
        else:
            g.add_edge(u_int, v_int, weight=weight)
        edge_index.append((pipe_id, u_int, v_int))

    return g, name_to_id, edge_index


# ------------------------------------------------------------------
# Algorithm score
# ------------------------------------------------------------------
def algorithm_pipe_scores(
    junctions: list[str],
    pipes: list[tuple[str, str, str, float]],
    edge_index: list[tuple[str, int, int]],
) -> list[tuple[str, tuple[int, int, int]]]:
    """Run GraphMetabolicManager and extract per-pipe scores.

    Returns:
        list of (pipe_id, (rare_count, edge_survived, -degree_sum)) ordered
        by descending score lex.
    """
    # Build a fresh graph (manager mutates it in place).
    g, _name_to_id, _ = build_graph(junctions, pipes)

    # Snapshot the original degree of each node BEFORE the run.
    initial_degree: dict[int, int] = {nid: g.degree(nid) for nid in list(g.nodes)}

    # Configure manager with default parameters per preregistration §5.1.
    # Note: GraphMetabolicManager picks alpha/beta/gamma defaults from
    # the metabolic module unless overridden. We pass only seed and steps
    # explicitly, leaving algorithm parameters at their defaults.
    mgr = GraphMetabolicManager(g, seed=SEED)
    mgr.run(steps=ALGORITHM_STEPS)

    # Score each ORIGINAL pipe (some endpoints / edges may have been pruned).
    scores: list[tuple[str, tuple[int, int, int]]] = []
    for pipe_id, u_int, v_int in edge_index:
        u_alive = g.has_node(u_int)
        v_alive = g.has_node(v_int)

        rare_count = 0
        if u_alive and g.nodes[u_int].phase != "normal":
            rare_count += 1
        if v_alive and g.nodes[v_int].phase != "normal":
            rare_count += 1

        edge_survived = (
            1 if (u_alive and v_alive and g.has_edge(u_int, v_int)) else 0
        )

        deg_sum = initial_degree.get(u_int, 0) + initial_degree.get(v_int, 0)
        scores.append((pipe_id, (rare_count, edge_survived, -deg_sum)))

    # Sort lex descending by score tuple.
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores


# ------------------------------------------------------------------
# Baselines
# ------------------------------------------------------------------
def random_pipe_ranking(
    edge_index: list[tuple[str, int, int]], rng_seed: int
) -> list[str]:
    """Random pipe ranking (one trial)."""
    pipe_ids = [p[0] for p in edge_index]
    rng = random.Random(rng_seed)
    rng.shuffle(pipe_ids)
    return pipe_ids


def topdegree_pipe_ranking(
    junctions: list[str],
    pipes: list[tuple[str, str, str, float]],
    edge_index: list[tuple[str, int, int]],
) -> list[str]:
    """Pipes sorted by descending sum of endpoint degrees in the original graph."""
    g, _name_to_id, _ = build_graph(junctions, pipes)
    initial_degree = {nid: g.degree(nid) for nid in list(g.nodes)}
    keyed = [
        (pipe_id, initial_degree.get(u, 0) + initial_degree.get(v, 0))
        for pipe_id, u, v in edge_index
    ]
    keyed.sort(key=lambda x: x[1], reverse=True)
    return [pipe_id for pipe_id, _ in keyed]


def topbetweenness_pipe_ranking(
    junctions: list[str],
    pipes: list[tuple[str, str, str, float]],
    edge_index: list[tuple[str, int, int]],
) -> list[str]:
    """Pipes sorted by descending NetworkX edge betweenness centrality."""
    nxg = nx.Graph()
    for pipe_id, u, v, _length in pipes:
        # NetworkX edge keyed by (u, v) string names.
        # If multi-pipe between same endpoints, keep max length as weight.
        if nxg.has_edge(u, v):
            continue
        nxg.add_edge(u, v, pipe_id=pipe_id)
    bc = nx.edge_betweenness_centrality(nxg, weight=None, seed=SEED)
    # Map back to pipe_ids; for multi-edge pipes, all pipes between same
    # endpoints share the same betweenness (acceptable approximation).
    pipe_score_pairs: list[tuple[str, float]] = []
    for pipe_id, u, v in edge_index:
        # Look up undirected edge betweenness (NetworkX handles direction).
        score = bc.get((u, v), bc.get((v, u), 0.0))
        pipe_score_pairs.append((pipe_id, score))
    pipe_score_pairs.sort(key=lambda x: x[1], reverse=True)
    return [pipe_id for pipe_id, _ in pipe_score_pairs]


# ------------------------------------------------------------------
# Metrics & tests
# ------------------------------------------------------------------
def recall_at_k(ranked_pipe_ids: list[str], leak_set: set[str], k: int) -> float:
    """Recall@K = (# leak pipes in top K) / (# leak pipes total)."""
    if not leak_set:
        return 0.0
    top_k = set(ranked_pipe_ids[:k])
    return len(top_k & leak_set) / len(leak_set)


def mcnemar_paired(
    algo_top_k: set[str],
    baseline_top_k: set[str],
    leak_set: set[str],
) -> tuple[float, float, dict[str, int]]:
    """McNemar's exact test on per-leak-pipe paired outcomes.

    For each leak pipe, observe whether algorithm and baseline each include
    it in top K. Build the 2x2 contingency table on disagreements and run
    McNemar's exact test.

    Returns:
        (statistic, p_value, table_dict) where table_dict has keys
        algo_only, baseline_only, both, neither.
    """
    algo_only = 0
    baseline_only = 0
    both = 0
    neither = 0
    for leak in leak_set:
        a = leak in algo_top_k
        b = leak in baseline_top_k
        if a and b:
            both += 1
        elif a and not b:
            algo_only += 1
        elif b and not a:
            baseline_only += 1
        else:
            neither += 1
    table = np.array([[both, algo_only], [baseline_only, neither]])
    # Use exact binomial test (recommended for small disagreement counts).
    res = mcnemar(table, exact=True)
    return (
        float(res.statistic),
        float(res.pvalue),
        {
            "both": both,
            "algo_only": algo_only,
            "baseline_only": baseline_only,
            "neither": neither,
        },
    )


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------
def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    RESULTS_DIR.mkdir(exist_ok=True)

    logger.info("Phase B-1 BattLeDIM L-Town evaluation")
    logger.info("Random seed: %d", SEED)
    logger.info("Algorithm steps: %d", ALGORITHM_STEPS)
    logger.info("K values: %s (primary K=%d)", K_VALUES, PRIMARY_K)
    logger.info("Random trials: %d", RANDOM_TRIALS)
    logger.info(
        "Statistical: McNemar exact, alpha=%.4f (Bonferroni for %d baselines)",
        BONFERRONI_ALPHA,
        NUM_BASELINES,
    )
    logger.info("")

    # 1. Load data
    junctions, pipes, leak_set = load_battledim_data()
    n_pipes = len(pipes)
    n_leaks = len(leak_set)
    logger.info("Network: %d nodes, %d pipes", len(junctions), n_pipes)
    logger.info("Leak ground truth: %d distinct pipes", n_leaks)
    logger.info("")

    # 2. Algorithm
    logger.info("Running graph-metabolic-manager algorithm...")
    edge_idx = _edge_index_int(junctions, pipes)
    algo_scored = algorithm_pipe_scores(junctions, pipes, edge_idx)
    algo_ranking = [pid for pid, _ in algo_scored]

    # 3. Baselines
    logger.info("Computing baselines...")
    topdeg_ranking = topdegree_pipe_ranking(junctions, pipes, edge_idx)
    topbc_ranking = topbetweenness_pipe_ranking(junctions, pipes, edge_idx)

    # Random panel: 30 trials, each with seed = SEED + trial_idx
    random_recalls: dict[int, list[float]] = {k: [] for k in K_VALUES}
    random_rankings: list[list[str]] = []
    for trial in range(RANDOM_TRIALS):
        ranking = random_pipe_ranking(edge_idx, rng_seed=SEED + trial)
        random_rankings.append(ranking)
        for k in K_VALUES:
            random_recalls[k].append(recall_at_k(ranking, leak_set, k))

    # 4. Compute recall@K for each method
    logger.info("Computing recall@K...")
    results: dict[str, object] = {
        "config": {
            "seed": SEED,
            "algorithm_steps": ALGORITHM_STEPS,
            "k_values": K_VALUES,
            "primary_k": PRIMARY_K,
            "random_trials": RANDOM_TRIALS,
            "bonferroni_alpha": BONFERRONI_ALPHA,
        },
        "network": {
            "n_nodes": len(junctions),
            "n_pipes": n_pipes,
            "n_leak_pipes": n_leaks,
        },
        "recall_at_k": {},
        "mcnemar": {},
        "score_definition": (
            "lex desc by (rare_count, edge_survived, -initial_degree_sum)"
        ),
    }

    recall_table: dict[str, dict[int, float]] = {
        "algorithm": {},
        "topdegree": {},
        "topbetweenness": {},
        "random_mean": {},
        "random_std": {},
    }
    for k in K_VALUES:
        recall_table["algorithm"][k] = recall_at_k(algo_ranking, leak_set, k)
        recall_table["topdegree"][k] = recall_at_k(topdeg_ranking, leak_set, k)
        recall_table["topbetweenness"][k] = recall_at_k(topbc_ranking, leak_set, k)
        recall_table["random_mean"][k] = float(np.mean(random_recalls[k]))
        recall_table["random_std"][k] = float(np.std(random_recalls[k], ddof=1))
    results["recall_at_k"] = recall_table

    logger.info("")
    logger.info("Recall@K results:")
    logger.info(
        "%-20s %s",
        "method",
        "  ".join(f"K={k:>3}" for k in K_VALUES),
    )
    for label, key in [
        ("algorithm", "algorithm"),
        ("topdegree", "topdegree"),
        ("topbetweenness", "topbetweenness"),
        ("random (mean±std)", None),
    ]:
        if key:
            row = "  ".join(f"{recall_table[key][k]:.3f}" for k in K_VALUES)
        else:
            row = "  ".join(
                f"{recall_table['random_mean'][k]:.3f}" for k in K_VALUES
            )
        logger.info("%-20s %s", label, row)

    # 5. McNemar tests at primary K
    logger.info("")
    logger.info("McNemar paired tests at K=%d (alpha=%.4f Bonferroni):", PRIMARY_K, BONFERRONI_ALPHA)
    algo_top_primary = set(algo_ranking[:PRIMARY_K])
    mcnemar_results: dict[str, dict[str, object]] = {}
    for label, ranking in [
        ("topdegree", topdeg_ranking),
        ("topbetweenness", topbc_ranking),
        ("random_seed42", random_rankings[0]),
    ]:
        baseline_top = set(ranking[:PRIMARY_K])
        stat, pval, table = mcnemar_paired(algo_top_primary, baseline_top, leak_set)
        mcnemar_results[label] = {
            "statistic": stat,
            "p_value": pval,
            "table": table,
            "significant_bonferroni": pval < BONFERRONI_ALPHA,
        }
        logger.info(
            "  algo vs %s: stat=%.4f p=%.4f sig=%s table=%s",
            label,
            stat,
            pval,
            pval < BONFERRONI_ALPHA,
            table,
        )
    results["mcnemar"] = mcnemar_results

    # 6. Verdict (auto-applied per preregistration §5.2 — strict reading)
    # H1 success:    algorithm beats ALL baselines by >=+5pp AND p<Bonferroni for >=1 baseline
    # H2 qualified:  algorithm tied (~within 2pp) with betweenness AND beats both random AND topdegree
    # H3 failure:    algorithm < random OR algorithm < topdegree (preregistration text:
    #                "Algorithm が Random / TopDegree いずれかに敗北")
    # else:          inconclusive
    primary_recall = recall_table["algorithm"][PRIMARY_K]
    primary_random = recall_table["random_mean"][PRIMARY_K]
    primary_topdeg = recall_table["topdegree"][PRIMARY_K]
    primary_topbc = recall_table["topbetweenness"][PRIMARY_K]
    baseline_max = max(primary_topdeg, primary_topbc, primary_random)
    delta = primary_recall - baseline_max
    any_significant = any(
        m["significant_bonferroni"] for m in mcnemar_results.values()
    )
    verdict: str
    # H3 check FIRST (it represents an explicit failure mode and must not be
    # masked by H2's looser definition).
    if primary_recall < primary_random or primary_recall < primary_topdeg:
        verdict = "H3_ACCEPT_FAILURE"  # honest failure per preregistration §5.2
    elif delta >= 0.05 and any_significant:
        verdict = "H1_ACCEPT"  # success
    elif (
        abs(primary_recall - primary_topbc) <= 0.02
        and primary_recall > primary_random
        and primary_recall > primary_topdeg
    ):
        verdict = "H2_ACCEPT_QUALIFIED"  # qualified success
    else:
        verdict = "INCONCLUSIVE"
    results["verdict"] = verdict
    results["verdict_basis"] = {
        "primary_recall_algorithm": primary_recall,
        "primary_recall_baseline_max": baseline_max,
        "delta": delta,
        "any_significant": any_significant,
    }

    logger.info("")
    logger.info("Verdict: %s", verdict)
    logger.info("  algorithm recall@%d = %.3f", PRIMARY_K, primary_recall)
    logger.info("  best baseline recall@%d = %.3f", PRIMARY_K, baseline_max)
    logger.info("  delta = %+.3f", delta)
    logger.info("  any baseline significantly beaten (Bonferroni) = %s", any_significant)

    # 7. Persist
    out_json = RESULTS_DIR / "results.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    logger.info("")
    logger.info("Wrote: %s", out_json)
    return 0


def _edge_index_int(
    junctions: list[str], pipes: list[tuple[str, str, str, float]]
) -> list[tuple[str, int, int]]:
    """Helper: build edge index of (pipe_id, u_int, v_int) consistently
    with build_graph()."""
    _g, _name_to_id, edge_index = build_graph(junctions, pipes)
    return edge_index


if __name__ == "__main__":
    raise SystemExit(main())
