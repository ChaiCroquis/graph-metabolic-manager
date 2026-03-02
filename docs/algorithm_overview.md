# Algorithm Overview

## Architecture

Graph Metabolic Manager consists of four cooperating components:

```
                    MetaControl
                   (feedback loop)
                        |
                   adjusts alpha
                        |
                        v
Input Graph --> MetabolicControl --> Pruned Graph
                        |
                  RarityProtection
                  (protects rare nodes)
                        |
                ConsistencyDiscovery
                (finds hidden relationships)
                        |
                        v
                  Managed Graph
```

---

## Component 1: Metabolic Control

**Purpose**: Automatically remove low-value edges while preserving important connections.

**Key insight**: Edges in crowded regions are less individually valuable than edges in sparse regions. A densely connected node losing one edge barely notices; an isolated node losing its only edge is destroyed.

### Formula

```
Decay rate:    lambda(C) = beta * (1 + gamma * C^alpha)
Weight update: w_new = w * exp(-lambda * dt)
Congestion:    C = deg(u) + deg(v)
```

### Parameters

| Parameter | Default | Meaning |
|-----------|---------|---------|
| alpha     | 2.0     | How sensitive to congestion (higher = more aggressive in crowded areas) |
| beta      | 0.05    | Base decay rate (minimum speed of decay) |
| gamma     | 0.5     | How much congestion amplifies decay |
| threshold | 0.1     | Weight below which an edge is removed |

### Why it works

- **Local only**: Each edge needs only deg(u) and deg(v) — no graph traversal
- **Adaptive**: Dense regions self-clean; sparse regions self-preserve
- **Continuous**: Smooth exponential decay, no abrupt deletions

---

## Component 2: Rarity Protection

**Purpose**: Prevent valuable but isolated nodes from being killed by metabolic control.

**Key insight**: Low connectivity does NOT mean low value. A node with one connection might be a rare gemstone (valuable niche product, important legacy document) or actual garbage. You can't tell by degree alone.

### Two-Phase Review

```
Phase 1 (Twait1 = 50 steps): "Maybe you'll find friends"
  - Node is unconditionally protected
  - If new connections appear -> node is saved
  - If not -> move to Phase 2

Phase 2 (Twait2 = 50 steps): "Last chance"
  - Node is observed
  - If connections appear -> node is saved
  - If still isolated (degree 0) -> safely removed
```

### Why two phases?

- Phase 1 catches nodes that are just "slow starters"
- Phase 2 gives a final opportunity
- After both phases with zero connections, removal is justified

---

## Component 3: Consistency Discovery

**Purpose**: Find non-obvious relationships between nodes based on structural similarity.

**Key insight**: If two nodes' neighborhoods have similar structural patterns (measured by Laplacian eigenvalue spectra), they may be related even if not directly connected.

### Process

1. Extract k-hop subgraph around each node
2. Compute Laplacian matrix L = D - A
3. Extract eigenvalue spectrum as "structural fingerprint"
4. Compare fingerprints using composite score:
   ```
   S = (7 * S_sys + 2 * S_rel + 1 * S_attr) / 10
   ```

### Sandwich Threshold

Accept only if: `theta_L (0.70) <= S <= theta_U (0.80)`

- **Below theta_L**: Structures are too different — no real relationship
- **Above theta_U**: Structures are trivially similar (same node comparing to itself). This is the "upside-down reversal" — extremely high scores are rejected.

### Why it works

The Laplacian eigenvalue spectrum captures fundamental structural properties (number of connected components, clustering coefficient, diameter approximation) in a compact vector, enabling meaningful comparison.

---

## Component 4: Meta Control

**Purpose**: Automatically tune metabolic control parameters to maintain graph health.

**Key insight**: A fixed alpha may be too aggressive or too gentle depending on the graph's current state. Meta control provides a feedback loop.

### Health Index

```
H = 1 - |kAvg - kOpt| / kOpt
```

- H = 1.0: Average degree is exactly at the target
- H = 0.0: Average degree is completely off target

### Update Rule

```
delta = eta * delta_k^4

If H < target: alpha += delta  (more aggressive pruning)
If H >= target: alpha -= delta * 0.5  (ease off)
```

The 4th-power rule means:
- Small deviations -> tiny corrections (stability)
- Large deviations -> rapid corrections (responsiveness)

---

## Hierarchy: Edge / Core / Rare Layers

Nodes are classified into three layers with different processing frequencies:

| Layer | dt | Meaning |
|-------|----|---------|
| Edge  | 5  | Peripheral nodes, processed least frequently |
| Core  | 3  | Central nodes, medium frequency |
| Rare  | 1  | Protected rare nodes, processed most frequently |

The 5:3:1 ratio ensures rare nodes get the most attention without wasting compute on stable peripheral nodes.
