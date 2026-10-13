import json
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from backend.app.models.models import (
    Asset, ServicePort, NetworkRelationship, VulnerabilityFinding, Assessment
)

class JSONImporterError(Exception):
    pass

class JSONAssetImporter:
    """
    Imports normalized JSON topologies or asset inventories into the Digital Twin database.
    """

    @classmethod
    def import_payload(cls, db: Session, payload: Dict[str, Any], assessment_title: str = "JSON Asset Ingestion") -> Assessment:
        if not isinstance(payload, dict):
            raise JSONImporterError("Invalid payload: root must be a JSON object")

        assets_data = payload.get("assets", [])
        relationships_data = payload.get("relationships", [])

        if not isinstance(assets_data, list):
            raise JSONImporterError("Invalid payload: 'assets' must be a list")

        assessment = Assessment(
            title=assessment_title,
            description=payload.get("description", "Imported via JSON schema"),
            assessment_type="imported_json",
            target_scope=payload.get("scope", "Custom JSON Scope"),
            status="completed",
            total_assets_found=len(assets_data),
            total_vulns_found=0,
            overall_risk_score=0.0,
            execution_duration_seconds=0.5
        )
        db.add(assessment)
        db.flush()

        ip_to_asset_id = {}
        total_vulns = 0

        for a_data in assets_data:
            ip = a_data.get("ip_address")
            if not ip:
                continue

            # Check if asset already exists in DB
            existing_asset = db.query(Asset).filter(Asset.ip_address == ip).first()
            if existing_asset:
                asset = existing_asset
                asset.hostname = a_data.get("hostname", asset.hostname)
                asset.os_name = a_data.get("os_name", asset.os_name)
                asset.criticality = a_data.get("criticality", asset.criticality)
                asset.asset_type = a_data.get("asset_type", asset.asset_type)
            else:
                asset = Asset(
                    hostname=a_data.get("hostname"),
                    ip_address=ip,
                    mac_address=a_data.get("mac_address"),
                    os_name=a_data.get("os_name"),
                    os_version=a_data.get("os_version"),
                    asset_type=a_data.get("asset_type", "server"),
                    criticality=a_data.get("criticality", "MEDIUM"),
                    environment=a_data.get("environment", "internal"),
                    subnet=a_data.get("subnet"),
                    is_isolated=a_data.get("is_isolated", False),
                    is_perimeter=a_data.get("is_perimeter", False),
                    business_impact_score=float(a_data.get("business_impact_score", 50.0)),
                    notes=a_data.get("notes")
                )
                db.add(asset)
                db.flush()

            ip_to_asset_id[ip] = asset.id

            # Services
            service_map = {}
            for s_data in a_data.get("services", []):
                port = int(s_data.get("port", 0))
                proto = s_data.get("protocol", "tcp")
                existing_srv = db.query(ServicePort).filter(
                    ServicePort.asset_id == asset.id,
                    ServicePort.port == port,
                    ServicePort.protocol == proto
                ).first()
                if not existing_srv:
                    srv = ServicePort(
                        asset_id=asset.id,
                        port=port,
                        protocol=proto,
                        service_name=s_data.get("service_name"),
                        product=s_data.get("product"),
                        version=s_data.get("version"),
                        state=s_data.get("state", "open"),
                        is_exposed=s_data.get("is_exposed", True)
                    )
                    db.add(srv)
                    db.flush()
                    service_map[port] = srv.id
                else:
                    service_map[port] = existing_srv.id

            # Findings
            for f_data in a_data.get("findings", []):
                total_vulns += 1
                cve = f_data.get("cve_id", "UNKNOWN-CVE")
                port_ref = f_data.get("port")
                srv_id = service_map.get(port_ref) if port_ref else None

                finding = VulnerabilityFinding(
                    assessment_id=assessment.id,
                    asset_id=asset.id,
                    service_id=srv_id,
                    cve_id=cve,
                    title=f_data.get("title", f"Vulnerability {cve}"),
                    description=f_data.get("description"),
                    cvss_v3_score=float(f_data.get("cvss_v3_score", 5.0)),
                    cvss_v3_severity=f_data.get("cvss_v3_severity", "MEDIUM"),
                    cvss_vector=f_data.get("cvss_vector"),
                    reference_url=f_data.get("reference_url"),
                    source=f_data.get("source", "Imported JSON"),
                    match_type=f_data.get("match_type", "confirmed_signature"),
                    reachability_status=f_data.get("reachability_status", "subnet_reachable"),
                    raw_score=float(f_data.get("raw_score", 50.0)),
                    contextual_risk_score=float(f_data.get("contextual_risk_score", 50.0)),
                    remediation_advice=f_data.get("remediation_advice")
                )
                db.add(finding)

        # Relationships
        for r_data in relationships_data:
            src_ip = r_data.get("source_ip")
            tgt_ip = r_data.get("target_ip")
            src_id = ip_to_asset_id.get(src_ip)
            tgt_id = ip_to_asset_id.get(tgt_ip)
            if src_id and tgt_id:
                rel = NetworkRelationship(
                    source_asset_id=src_id,
                    target_asset_id=tgt_id,
                    relationship_type=r_data.get("relationship_type", "can_connect"),
                    protocol=r_data.get("protocol", "tcp"),
                    port=r_data.get("port"),
                    is_inferred=r_data.get("is_inferred", False),
                    confidence=r_data.get("confidence", "HIGH"),
                    weight=float(r_data.get("weight", 1.0)),
                    description=r_data.get("description")
                )
                db.add(rel)

        assessment.total_vulns_found = total_vulns
        db.commit()
        db.refresh(assessment)
        return assessment
