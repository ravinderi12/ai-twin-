import json
from typing import Dict, Any, List, Optional
import networkx as nx
from sqlalchemy.orm import Session
from backend.app.digital_twin.graph_builder import DigitalTwinGraph
from backend.app.risk_engine.context_risk import ContextualRiskEngine
from backend.app.simulation.attack_simulator import AttackSimulationEngine
from backend.app.models.models import VulnerabilityFinding, NetworkRelationship, Asset, RemediationScenario

class RemediationSimulator:
    """
    Performs what-if scenario simulations on cloned digital twin models.
    Enables analysts to test patches or firewall blocks and measure risk/path impact
    without modifying live systems.
    """

    @classmethod
    def simulate_what_if(
        cls,
        db: Session,
        patch_finding_ids: List[int],
        block_relationship_ids: List[int],
        isolate_asset_ids: List[int],
        start_asset_id: Optional[int] = None,
        target_asset_id: Optional[int] = None,
        assessment_id: Optional[int] = None,
        scenario_name: str = "Proposed Mitigation Scenario"
    ) -> Dict[str, Any]:
        # 1. Build baseline digital twin
        baseline_twin = DigitalTwinGraph.build_from_db(db, assessment_id=assessment_id)
        baseline_graph = baseline_twin.graph

        # Auto-pick start and target if not provided
        # Start: perimeter node or gateway; Target: critical asset (e.g. database or AD)
        if not start_asset_id or not target_asset_id:
            perimeter_nodes = [n for n, d in baseline_graph.nodes(data=True) if d.get("is_perimeter")]
            target_nodes = [n for n, d in baseline_graph.nodes(data=True) if d.get("criticality") == "CRITICAL"]

            start_id = int(perimeter_nodes[0]) if perimeter_nodes else (int(list(baseline_graph.nodes)[0]) if baseline_graph.nodes else 1)
            target_id = int(target_nodes[0]) if target_nodes else (int(list(baseline_graph.nodes)[-1]) if baseline_graph.nodes else 1)
        else:
            start_id = start_asset_id
            target_id = target_asset_id

        # Run baseline simulation
        baseline_sim = AttackSimulationEngine.simulate_path(
            db=db,
            start_asset_id=start_id,
            target_asset_id=target_id,
            algorithm="Dijkstra",
            assessment_id=assessment_id
        )

        baseline_risk = baseline_sim.get("total_path_risk", 75.0) if baseline_sim["path_found"] else 0.0
        baseline_path_count = 1 if baseline_sim["path_found"] else 0

        # 2. Clone graph for simulation
        simulated_graph = baseline_graph.copy()

        # Apply simulated patches: remove patched vulnerabilities from node data
        patched_cves = []
        if patch_finding_ids:
            findings_to_patch = db.query(VulnerabilityFinding).filter(VulnerabilityFinding.id.in_(patch_finding_ids)).all()
            for f in findings_to_patch:
                patched_cves.append(f"{f.cve_id} on {f.asset.hostname or f.asset.ip_address}")
                node_str = str(f.asset_id)
                if simulated_graph.has_node(node_str):
                    # Filter out this vulnerability from node
                    node_data = simulated_graph.nodes[node_str]
                    remaining_vulns = [v for v in node_data.get("vulnerabilities", []) if v.get("id") != f.id]
                    node_data["vulnerabilities"] = remaining_vulns
                    new_max_cvss = max([v.get("cvss_v3_score", 0.0) for v in remaining_vulns], default=0.0)
                    node_data["max_cvss"] = new_max_cvss
                    node_data["max_context_risk"] = max([v.get("contextual_risk_score", 0.0) for v in remaining_vulns], default=0.0)

                    # Also increase traversal weight of inbound edges to this node (patching increases attacker friction)
                    for in_u, in_v, in_edge in simulated_graph.in_edges(node_str, data=True):
                        in_edge["weight"] = max(2.5, in_edge.get("weight", 1.0) * 2.5)

        # Apply simulated relationship blocks (firewall ACL simulation)
        if block_relationship_ids:
            rels_to_block = db.query(NetworkRelationship).filter(NetworkRelationship.id.in_(block_relationship_ids)).all()
            for r in rels_to_block:
                src_s = str(r.source_asset_id)
                tgt_s = str(r.target_asset_id)
                if simulated_graph.has_edge(src_s, tgt_s):
                    simulated_graph.remove_edge(src_s, tgt_s)

        # Apply simulated asset isolations
        if isolate_asset_ids:
            for a_id in isolate_asset_ids:
                a_str = str(a_id)
                if simulated_graph.has_node(a_str):
                    # Remove all edges for isolated node
                    edges_to_remove = list(simulated_graph.in_edges(a_str)) + list(simulated_graph.out_edges(a_str))
                    for eu, ev in edges_to_remove:
                        if simulated_graph.has_edge(eu, ev):
                            simulated_graph.remove_edge(eu, ev)

        # 3. Recalculate path on simulated twin
        start_str = str(start_id)
        target_str = str(target_id)
        simulated_path_found = False
        simulated_path_nodes = []
        simulated_risk = 0.0
        after_steps = []

        try:
            if simulated_graph.has_node(start_str) and simulated_graph.has_node(target_str):
                simulated_path_nodes = nx.shortest_path(simulated_graph, source=start_str, target=target_str, weight="weight")
                simulated_path_found = True
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            simulated_path_found = False

        if simulated_path_found:
            target_data = simulated_graph.nodes[target_str]
            simulated_risk, _ = ContextualRiskEngine.calculate_path_risk(
                simulated_path_nodes,
                dict(simulated_graph.nodes(data=True)),
                target_data.get("business_impact", 80.0)
            )
            for i in range(len(simulated_path_nodes) - 1):
                u = simulated_path_nodes[i]
                v = simulated_path_nodes[i+1]
                after_steps.append({
                    "step": i + 1,
                    "from": simulated_graph.nodes[u].get("label"),
                    "to": simulated_graph.nodes[v].get("label")
                })
        else:
            simulated_risk = 0.0

        # Calculate reduction metrics
        if baseline_risk > 0:
            risk_reduction_pct = round(((baseline_risk - simulated_risk) / baseline_risk) * 100.0, 1)
        else:
            risk_reduction_pct = 0.0

        eliminated_paths = 1 if (baseline_sim["path_found"] and not simulated_path_found) else 0
        choke_point_broken = baseline_sim["path_found"] and not simulated_path_found

        choke_info = baseline_sim.get("bottleneck_asset")
        choke_label = choke_info["label"] if choke_info else None

        if choke_point_broken:
            summary = (
                f"Mitigation successfully BROKE the active attack path from "
                f"'{baseline_graph.nodes[start_str].get('label')}' to '{baseline_graph.nodes[target_str].get('label')}'. "
                f"Overall simulated path risk reduced by {risk_reduction_pct}% (from {baseline_risk} to {simulated_risk})."
            )
        else:
            summary = (
                f"Simulated mitigation reduced contextual exposure by {risk_reduction_pct}% "
                f"(baseline risk: {baseline_risk} -> post-mitigation: {simulated_risk}). "
                f"An alternative path remains available through remaining routes."
            )

        # Save scenario record
        scenario = RemediationScenario(
            assessment_id=assessment_id,
            name=scenario_name,
            description=summary,
            baseline_risk_score=baseline_risk,
            simulated_risk_score=simulated_risk,
            risk_reduction_percentage=risk_reduction_pct,
            eliminated_paths_count=eliminated_paths,
            remaining_paths_count=1 if simulated_path_found else 0,
            patches_applied_json=json.dumps(patched_cves),
            scenario_details_json=json.dumps({
                "patch_finding_ids": patch_finding_ids,
                "block_relationship_ids": block_relationship_ids,
                "isolate_asset_ids": isolate_asset_ids,
                "start_asset_id": start_id,
                "target_asset_id": target_id
            })
        )
        db.add(scenario)
        db.commit()

        return {
            "scenario_name": scenario_name,
            "baseline_risk_score": baseline_risk,
            "simulated_risk_score": simulated_risk,
            "risk_reduction_percentage": risk_reduction_pct,
            "baseline_path_count": baseline_path_count,
            "simulated_path_count": 1 if simulated_path_found else 0,
            "eliminated_paths_count": eliminated_paths,
            "remediated_findings_count": len(patch_finding_ids),
            "choke_point_broken": choke_point_broken,
            "choke_point_label": choke_label,
            "before_path_steps": baseline_sim.get("steps", []),
            "after_path_steps": after_steps,
            "comparison_summary": summary
        }
