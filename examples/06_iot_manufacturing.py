#!/usr/bin/env python3
"""
IoT / Manufacturing Sensor Network Example
============================================

Simulates a factory sensor network where equipment, sensors,
and alert events are connected in a graph.

Scenario:
- 15 pieces of equipment with sensor readings and alert histories
- 6 rare anomaly patterns (early warning signs of equipment failure
  that have only appeared once or twice - must be preserved)
- 8 obsolete sensor readings (from decommissioned equipment)
- Consistency discovery identifies equipment that shares failure
  patterns, enabling predictive maintenance

The manager should:
1. Maintain equipment-sensor-alert relationships
2. Protect rare anomaly patterns (they predict future failures)
3. Clean up obsolete sensor data
4. Discover equipment with similar failure profiles
"""

import logging
import random

from graph_metabolic_manager import (
    ConsistencyDiscovery,
    Graph,
    GraphMetabolicManager,
)

logging.basicConfig(level=logging.INFO, format="%(message)s")


def build_factory_network(seed: int = 42) -> tuple:
    """Build a simulated factory IoT sensor network."""
    random.seed(seed)
    g = Graph()

    # Equipment organized by production line
    lines = {
        "Line_A": ["Press_A1", "Conveyor_A1", "Robot_A1", "Welder_A1", "Inspector_A1"],
        "Line_B": ["Press_B1", "Conveyor_B1", "Robot_B1", "Welder_B1", "Inspector_B1"],
        "Line_C": ["Press_C1", "Conveyor_C1", "Robot_C1", "Welder_C1", "Inspector_C1"],
    }

    equipment = []
    line_nodes = {}
    for line, equip_names in lines.items():
        line_nodes[line] = []
        for name in equip_names:
            nid = g.add_node(name, node_type="normal", entity="equipment", line=line)
            equipment.append(nid)
            line_nodes[line].append(nid)

    # Sensors attached to equipment
    sensors = []
    sensor_types = ["Temperature", "Vibration", "Pressure", "Current", "Noise"]
    for equip_id in equipment:
        equip_label = g.nodes[equip_id].label
        n_sensors = random.randint(2, 4)
        for stype in random.sample(sensor_types, n_sensors):
            nid = g.add_node(
                f"{equip_label}_{stype}",
                node_type="normal",
                entity="sensor",
            )
            g.add_edge(equip_id, nid, weight=random.uniform(0.7, 1.0))
            sensors.append(nid)

    # Equipment-to-equipment relationships (same line = strong, cross-line = weak)
    for _line, nodes in line_nodes.items():
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                if random.random() < 0.6:
                    g.add_edge(nodes[i], nodes[j], weight=random.uniform(0.4, 0.8))

    # Cross-line relationships (similar equipment types)
    all_lines = list(line_nodes.values())
    for i in range(len(all_lines)):
        for j in range(i + 1, len(all_lines)):
            for k in range(min(len(all_lines[i]), len(all_lines[j]))):
                if random.random() < 0.3:
                    g.add_edge(all_lines[i][k], all_lines[j][k],
                               weight=random.uniform(0.2, 0.5))

    # Known alert patterns
    alerts = []
    alert_names = [
        "Overheat_Pattern", "Vibration_Spike", "Pressure_Drop",
        "Current_Surge", "Bearing_Wear", "Motor_Degradation",
    ]
    for name in alert_names:
        nid = g.add_node(name, node_type="normal", entity="alert_pattern")
        # Connect to relevant equipment
        for _ in range(random.randint(3, 6)):
            equip = random.choice(equipment)
            g.add_edge(nid, equip, weight=random.uniform(0.3, 0.7))
        alerts.append(nid)

    # Rare anomaly patterns (early warning of NEW failure modes)
    # These have appeared only once or twice - critical to preserve!
    rare_anomalies = []
    rare_names = [
        "Micro_Crack_Signal", "Harmonic_Resonance",
        "Thermal_Runaway_Precursor", "Seal_Degradation_Early",
        "Lubricant_Contamination", "Electrical_Arc_Trace",
    ]
    for name in rare_names:
        nid = g.add_node(name, node_type="truth", entity="rare_anomaly")
        # Only 1 weak connection (seen once on one machine)
        equip = random.choice(equipment)
        g.add_edge(nid, equip, weight=random.uniform(0.05, 0.12))
        rare_anomalies.append(nid)

    # Obsolete sensor data (from decommissioned equipment)
    obsolete = []
    obsolete_names = [
        "Decom_Sensor_1", "Decom_Sensor_2", "Decom_Sensor_3",
        "Old_Line_D_Temp", "Old_Line_D_Vib", "Old_Line_D_Press",
        "Retired_Robot_Log", "Legacy_PLC_Data",
    ]
    for name in obsolete_names:
        nid = g.add_node(name, node_type="garbage", entity="obsolete")
        # No connections (equipment decommissioned)
        obsolete.append(nid)

    return g, equipment, sensors, alerts, rare_anomalies, obsolete


def main():
    print("=" * 60)
    print("  Example 6: IoT / Manufacturing Sensor Network")
    print("=" * 60)

    g, equipment, sensors, alerts, rare_anomalies, obsolete = build_factory_network()

    print("\nInitial factory network:")
    print(f"  Equipment:        {len(equipment)} (3 production lines)")
    print(f"  Sensors:          {len(sensors)} (attached to equipment)")
    print(f"  Alert patterns:   {len(alerts)} (known failure modes)")
    print(f"  Rare anomalies:   {len(rare_anomalies)} (early failure warnings)")
    print(f"  Obsolete data:    {len(obsolete)} (decommissioned equipment)")
    print(f"  Total: {g.node_count()} nodes, {g.edge_count()} edges")
    print(f"  Average degree: {g.avg_degree():.2f}")

    # ----------------------------------------------------------
    # Part 1: Network maintenance with protection
    # ----------------------------------------------------------
    print("\n--- Part 1: Sensor Network Maintenance (150 steps) ---")

    mgr = GraphMetabolicManager(
        g,
        seed=42,
        enable_rarity=True,
        enable_consistency=False,
        k_opt=5.0,
        alpha=1.5,
        beta=0.02,
        prune_threshold=0.05,
    )

    mgr.run(steps=150, verbose=True)

    rare_survived = sum(1 for nid in rare_anomalies if g.has_node(nid))
    obsolete_survived = sum(1 for nid in obsolete if g.has_node(nid))
    equip_survived = sum(1 for nid in equipment if g.has_node(nid))
    sensor_survived = sum(1 for nid in sensors if g.has_node(nid))

    print("\n  Results:")
    print(f"  Equipment:      {equip_survived}/{len(equipment)} remaining")
    print(f"  Sensors:        {sensor_survived}/{len(sensors)} remaining")
    print(f"  Rare anomalies: {rare_survived}/{len(rare_anomalies)} PROTECTED")
    print(f"  Obsolete data:  {len(obsolete) - obsolete_survived}/{len(obsolete)} cleaned")

    # ----------------------------------------------------------
    # Part 2: Predictive maintenance discovery
    # ----------------------------------------------------------
    print("\n--- Part 2: Predictive Maintenance Discovery ---")
    print("  (Finding equipment with similar anomaly profiles)")

    g2, equip2, _, _, rare2, _ = build_factory_network(seed=99)
    cd = ConsistencyDiscovery(theta_l=0.55, theta_u=0.85, k_hop=2)
    discoveries = cd.discover(g2, rare_node_ids=rare2, candidate_ids=equip2)

    if discoveries:
        print(f"\n  Found {len(discoveries)} predictive connections:")
        seen = set()
        count = 0
        for rare_id, equip_id, score in discoveries:
            if count >= 6:
                break
            r_label = g2.nodes[rare_id].label
            e_label = g2.nodes[equip_id].label
            key = (r_label, e_label)
            if key not in seen:
                seen.add(key)
                print(f"    {r_label} -> may also affect {e_label} (score: {score:.3f})")
                count += 1

        print("\n  These suggest which equipment might experience")
        print("  similar anomalies, enabling proactive maintenance.")
    else:
        print("\n  No cross-equipment anomaly patterns detected.")

    # ----------------------------------------------------------
    # Evaluation
    # ----------------------------------------------------------
    print("\n--- Evaluation ---")
    if rare_survived > 0:
        print(f"  [OK] Rare anomaly signals preserved ({rare_survived}/{len(rare_anomalies)})")
        print("       Early failure warnings are available for analysis")
    else:
        print("  [!!] Rare anomaly signals lost!")
        print("       Future equipment failures may go undetected")

    if obsolete_survived < len(obsolete):
        print(f"  [OK] Obsolete data cleaned ({len(obsolete) - obsolete_survived}/{len(obsolete)})")
        print("       Storage freed from decommissioned equipment data")

    print("\n  In manufacturing, catching a failure precursor early")
    print("  can prevent hours of unplanned downtime (cost: $10K-$100K+/hour).")

    print("\nDone!")


if __name__ == "__main__":
    main()
