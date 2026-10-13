import json
from typing import Dict, Any, List, Optional
import networkx as nx
from sqlalchemy.orm import Session
from backend.app.digital_twin.graph_builder import DigitalTwinGraph
from backend.app.risk_engine.context_risk import ContextualRiskEngine
from backend.app.models.models import Asset, SimulatedAttackPath

MITRE_TECHNIQUE_MAPPING = {
    80: {"id": "T1190", "name": "Exploit Public-Facing Application", "tactic": "Initial Access"},
    443: {"id": "T1190", "name": "Exploit Public-Facing Application", "tactic": "Initial Access"},
    8080: {"id": "T1210", "name": "Exploitation of Remote Services", "tactic": "Lateral Movement"},
    22: {"id": "T1021.004", "name": "Remote Services: SSH", "tactic": "Lateral Movement"},
    445: {"id": "T1021.002", "name": "Remote Services: SMB/Windows Admin Shares", "tactic": "Lateral Movement"},
    3389: {"id": "T1021.001", "name": "Remote Services: Remote Desktop Protocol", "tactic": "Lateral Movement"},
    3306: {"id": "T1565", "name": "Data Manipulation / SQL Access", "tactic": "Impact"},
    5432: {"id": "T1565", "name": "Data Manipulation / PostgreSQL Access", "tactic": "Impact"},
    88: {"id": "T1558", "name": "Steal or Forge Kerberos Tickets", "tactic": "Credential Access"},
    389: {"id": "T1068", "name": "Exploitation for Privilege Escalation: LDAP/AD", "tactic": "Privilege Escalation"}
}

DEFAULT_MITRE = {"id": "T1210", "name": "Exploitation of Remote Services", "tactic": "Lateral Movement"}

class AttackSimulationEngine:
    """
    Simulates multi-hop attack paths exclusively within the mathematical Digital Twin.
    No live exploits are ever executed.
    """

    @classmethod
    def simulate_path(
        cls,
        db: Session,
        start_asset_id: int,
        target_asset_id: int,
        algorithm: str = "Dijkstra",
        assessment_id: Optional[int] = None
    ) -> Dict[str, Any]:
        twin = DigitalTwinGraph.build_from_db(db, assessment_id=assessment_id)
        graph = twin.graph

        start_str = str(start_asset_id)
        target_str = str(target_asset_id)

        if not graph.has_node(start_str) or not graph.has_node(target_str):
            return {
                "path_found": False,
                "algorithm_used": algorithm,
                "hop_count": 0,
                "total_path_cost": 0.0,
                "total_path_risk": 0.0,
                "nodes": [],
                "steps": [],
                "mitre_tactics": [],
                "explanation": "One or both selected assets do not exist in the digital twin topology."
            }

        if start_str == target_str:
            return {
                "path_found": False,
                "algorithm_used": algorithm,
                "hop_count": 0,
                "total_path_cost": 0.0,
                "total_path_risk": 0.0,
                "nodes": [],
                "steps": [],
                "mitre_tactics": [],
                "explanation": "Start node and target asset are identical."
            }

        # Pathfinding
        try:
            if algorithm.lower() == "bfs":
                path_nodes = nx.shortest_path(graph, source=start_str, target=target_str)
            else:  # Dijkstra
                path_nodes = nx.shortest_path(graph, source=start_str, target=target_str, weight="weight")
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return {
                "path_found": False,
                "algorithm_used": algorithm,
                "hop_count": 0,
                "total_path_cost": 0.0,
                "total_path_risk": 0.0,
                "nodes": [],
                "steps": [],
                "mitre_tactics": [],
                "explanation": f"No feasible network attack path exists from {start_str} to {target_str}. Target is isolated or blocked by access controls."
            }

        # Build detailed step explanation
        steps = []
        mitre_tactics_collected = []
        total_cost = 0.0
        cumulative_risk = 0.0

        for i in range(len(path_nodes) - 1):
            u = path_nodes[i]
            v = path_nodes[i+1]
            edge_data = graph.get_edge_data(u, v, default={})
            target_node_data = graph.nodes[v]
            src_node_data = graph.nodes[u]

            weight = edge_data.get("weight", 1.0)
            port = edge_data.get("port")
            rel_type = edge_data.get("relationship_type", "can_connect")
            total_cost += weight

            # Select MITRE technique
            mitre_info = MITRE_TECHNIQUE_MAPPING.get(port, DEFAULT_MITRE)
            if i == 0 and src_node_data.get("is_perimeter"):
                mitre_info = MITRE_TECHNIQUE_MAPPING.get(80, {"id": "T1190", "name": "Exploit Public-Facing Application", "tactic": "Initial Access"})
            mitre_tactics_collected.append(mitre_info)

            # Collect exploited vulnerabilities on target
            target_vulns = target_node_data.get("vulnerabilities", [])
            step_risk = target_node_data.get("max_context_risk", 20.0)
            cumulative_risk += step_risk

            rationale = (
                f"Adversary pivots from '{src_node_data.get('label')}' ({src_node_data.get('ip_address')}) "
                f"to '{target_node_data.get('label')}' ({target_node_data.get('ip_address')}) via {rel_type} "
                f"on port {port or 'dynamic'}. Exploits target service vulnerabilities to establish persistence or execute remote commands."
            )
            uncertainty = "Assumes network access rule permits inbound connection without endpoint detection blocking payload execution."

            steps.append({
                "step_number": i + 1,
                "from_asset_id": src_node_data.get("asset_id"),
                "from_asset_label": src_node_data.get("label"),
                "to_asset_id": target_node_data.get("asset_id"),
                "to_asset_label": target_node_data.get("label"),
                "relationship_type": rel_type,
                "port_used": port,
                "vulnerabilities_exploited": target_vulns,
                "hop_cost": round(weight, 2),
                "cumulative_risk": round(cumulative_risk, 1),
                "mitre_technique_id": mitre_info["id"],
                "mitre_technique_name": mitre_info["name"],
                "mitre_tactic": mitre_info["tactic"],
                "rationale": rationale,
                "uncertainty_notes": uncertainty
            })

        # Calculate path risk
        target_node = graph.nodes[target_str]
        final_path_risk, risk_explanation = ContextualRiskEngine.calculate_path_risk(
            path_nodes,
            dict(graph.nodes(data=True)),
            target_node.get("business_impact", 80.0)
        )

        # Choke point analysis
        choke_points = twin.get_choke_points()
        path_bottleneck = None
        for cp in choke_points:
            if str(cp["asset_id"]) in path_nodes[1:-1]:  # Intermediary node
                path_bottleneck = cp
                break

        node_dicts = [
            {
                "id": n,
                "label": graph.nodes[n].get("label"),
                "ip": graph.nodes[n].get("ip_address"),
                "asset_type": graph.nodes[n].get("asset_type"),
                "is_perimeter": graph.nodes[n].get("is_perimeter"),
                "risk_score": graph.nodes[n].get("max_context_risk", 0.0)
            } for n in path_nodes
        ]

        # Record simulation path in database
        sim_record = SimulatedAttackPath(
            assessment_id=assessment_id,
            name=f"Path: {graph.nodes[start_str].get('label')} -> {graph.nodes[target_str].get('label')}",
            start_asset_id=int(start_asset_id),
            target_asset_id=int(target_asset_id),
            algorithm_used=algorithm,
            total_path_cost=round(total_cost, 2),
            hop_count=len(path_nodes) - 1,
            total_path_risk=final_path_risk,
            path_nodes_json=json.dumps(path_nodes),
            path_steps_json=json.dumps(steps),
            mitre_tactics_json=json.dumps(mitre_tactics_collected),
            bottleneck_asset_id=path_bottleneck["asset_id"] if path_bottleneck else None
        )
        db.add(sim_record)
        db.commit()

        return {
            "path_found": True,
            "algorithm_used": algorithm,
            "hop_count": len(path_nodes) - 1,
            "total_path_cost": round(total_cost, 2),
            "total_path_risk": final_path_risk,
            "nodes": node_dicts,
            "steps": steps,
            "mitre_tactics": mitre_tactics_collected,
            "bottleneck_asset": path_bottleneck,
            "explanation": f"Successfully identified {len(path_nodes)-1}-hop simulated lateral movement path using {algorithm}. {risk_explanation}"
        }
