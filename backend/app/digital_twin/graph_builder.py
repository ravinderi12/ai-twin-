import json
from typing import Dict, Any, List, Optional, Tuple
import networkx as nx
from sqlalchemy.orm import Session
from backend.app.models.models import Asset, NetworkRelationship, VulnerabilityFinding, ServicePort

class DigitalTwinGraph:
    """
    Constructs and manages the in-memory NetworkX mathematical graph model
    of the enterprise network infrastructure.
    """

    def __init__(self):
        self.graph = nx.DiGraph()

    @classmethod
    def build_from_db(cls, db: Session, assessment_id: Optional[int] = None) -> "DigitalTwinGraph":
        twin = cls()
        assets = db.query(Asset).all()
        relationships = db.query(NetworkRelationship).all()

        # Add Asset Nodes
        for asset in assets:
            # Query services
            services = db.query(ServicePort).filter(ServicePort.asset_id == asset.id).all()
            service_list = [
                {
                    "id": s.id,
                    "port": s.port,
                    "protocol": s.protocol,
                    "service_name": s.service_name,
                    "product": s.product,
                    "version": s.version,
                    "state": s.state
                } for s in services
            ]

            # Query findings
            findings_q = db.query(VulnerabilityFinding).filter(VulnerabilityFinding.asset_id == asset.id)
            if assessment_id:
                findings_q = findings_q.filter(VulnerabilityFinding.assessment_id == assessment_id)
            findings = findings_q.all()

            finding_list = [
                {
                    "id": f.id,
                    "cve_id": f.cve_id,
                    "title": f.title,
                    "cvss_v3_score": f.cvss_v3_score,
                    "cvss_v3_severity": f.cvss_v3_severity,
                    "contextual_risk_score": f.contextual_risk_score,
                    "remediation_advice": f.remediation_advice,
                    "service_id": f.service_id
                } for f in findings
            ]

            max_cvss = max([f.cvss_v3_score for f in findings], default=0.0)
            max_context_risk = max([f.contextual_risk_score for f in findings], default=0.0)

            twin.graph.add_node(
                str(asset.id),
                asset_id=asset.id,
                label=asset.hostname or asset.ip_address,
                ip_address=asset.ip_address,
                mac_address=asset.mac_address,
                os_name=asset.os_name,
                asset_type=asset.asset_type,
                criticality=asset.criticality,
                environment=asset.environment,
                subnet=asset.subnet,
                is_perimeter=asset.is_perimeter,
                is_isolated=asset.is_isolated,
                business_impact=asset.business_impact_score,
                services=service_list,
                vulnerabilities=finding_list,
                max_cvss=max_cvss,
                max_context_risk=max_context_risk
            )

        # Add Edges
        for rel in relationships:
            src_str = str(rel.source_asset_id)
            tgt_str = str(rel.target_asset_id)
            if twin.graph.has_node(src_str) and twin.graph.has_node(tgt_str):
                # Calculate edge traversal weight:
                # Base weight from rel. Higher vulnerability on target decreases traversal friction
                target_node_data = twin.graph.nodes[tgt_str]
                target_vulns = target_node_data.get("vulnerabilities", [])
                max_target_cvss = target_node_data.get("max_cvss", 0.0)

                # Friction model: edge weight is lower if target has high exploitable vulnerability
                friction = max(0.2, rel.weight * (1.0 - (max_target_cvss / 20.0)))

                twin.graph.add_edge(
                    src_str,
                    tgt_str,
                    rel_id=rel.id,
                    relationship_type=rel.relationship_type,
                    protocol=rel.protocol or "tcp",
                    port=rel.port,
                    confidence=rel.confidence,
                    is_inferred=rel.is_inferred,
                    weight=round(friction, 2),
                    base_weight=rel.weight,
                    description=rel.description
                )

        return twin

    def get_choke_points(self) -> List[Dict[str, Any]]:
        """
        Calculates network betweenness centrality to identify critical choke points
        and lateral movement bottlenecks.
        """
        if len(self.graph.nodes) < 2:
            return []

        try:
            betweenness = nx.betweenness_centrality(self.graph, weight="weight")
            sorted_nodes = sorted(betweenness.items(), key=lambda item: item[1], reverse=True)
            choke_points = []
            for node_id, score in sorted_nodes[:3]:
                if score > 0.0:
                    node_data = self.graph.nodes[node_id]
                    choke_points.append({
                        "node_id": node_id,
                        "asset_id": node_data.get("asset_id"),
                        "label": node_data.get("label"),
                        "ip_address": node_data.get("ip_address"),
                        "asset_type": node_data.get("asset_type"),
                        "betweenness_score": round(score, 4),
                        "description": f"Critical topological bottleneck connecting multiple network segments."
                    })
            return choke_points
        except Exception:
            return []

    def export_for_cytoscape(self, attack_path_nodes: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Serializes the graph for Cytoscape.js canvas rendering.
        """
        choke_points = {cp["node_id"] for cp in self.get_choke_points()}
        path_nodes_set = set(attack_path_nodes) if attack_path_nodes else set()

        elements_nodes = []
        for n, data in self.graph.nodes(data=True):
            elements_nodes.append({
                "data": {
                    "id": str(n),
                    "label": data.get("label", str(n)),
                    "ip": data.get("ip_address", ""),
                    "asset_type": data.get("asset_type", "server"),
                    "criticality": data.get("criticality", "MEDIUM"),
                    "environment": data.get("environment", "internal"),
                    "subnet": data.get("subnet") or "Unknown",
                    "risk_score": data.get("max_context_risk", 0.0),
                    "is_perimeter": data.get("is_perimeter", False),
                    "is_isolated": data.get("is_isolated", False),
                    "vulnerabilities_count": len(data.get("vulnerabilities", [])),
                    "services_count": len(data.get("services", [])),
                    "is_choke_point": str(n) in choke_points,
                    "is_in_attack_path": str(n) in path_nodes_set
                }
            })

        elements_edges = []
        for u, v, data in self.graph.edges(data=True):
            is_path_edge = False
            if attack_path_nodes:
                for i in range(len(attack_path_nodes) - 1):
                    if attack_path_nodes[i] == str(u) and attack_path_nodes[i+1] == str(v):
                        is_path_edge = True
                        break

            edge_label = f"{data.get('relationship_type')} ({data.get('port')})" if data.get('port') else data.get('relationship_type', '')
            elements_edges.append({
                "data": {
                    "id": f"e-{u}-{v}-{data.get('rel_id', '0')}",
                    "source": str(u),
                    "target": str(v),
                    "label": edge_label,
                    "relationship_type": data.get("relationship_type", "can_connect"),
                    "port": data.get("port"),
                    "weight": data.get("weight", 1.0),
                    "confidence": data.get("confidence", "HIGH"),
                    "is_inferred": data.get("is_inferred", False),
                    "is_attack_path": is_path_edge
                }
            })

        return {
            "nodes": elements_nodes,
            "edges": elements_edges,
            "total_nodes": len(elements_nodes),
            "total_edges": len(elements_edges),
            "topology_name": "Enterprise Digital Twin Model"
        }
