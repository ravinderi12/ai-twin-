from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.models import (
    Asset, ServicePort, VulnerabilityFinding, SimulatedAttackPath,
    RemediationRecommendation, Assessment
)
from backend.app.digital_twin.graph_builder import DigitalTwinGraph
from backend.app.sample_data.enterprise_topology import load_sample_topology
from backend.app.schemas.schemas import DashboardMetricsResponse

router = APIRouter()

@router.get("/metrics", response_model=DashboardMetricsResponse)
def get_dashboard_metrics(db: Session = Depends(get_db)):
    assets = db.query(Asset).all()
    services_count = db.query(ServicePort).count()
    findings = db.query(VulnerabilityFinding).all()
    sim_paths = db.query(SimulatedAttackPath).all()
    remediations = db.query(RemediationRecommendation).order_by(RemediationRecommendation.risk_reduction_estimate.desc()).all()
    last_assessment = db.query(Assessment).order_by(Assessment.created_at.desc()).first()

    crit_vulns = sum(1 for f in findings if f.cvss_v3_severity == "CRITICAL")
    high_vulns = sum(1 for f in findings if f.cvss_v3_severity == "HIGH")
    med_vulns = sum(1 for f in findings if f.cvss_v3_severity == "MEDIUM")
    low_vulns = sum(1 for f in findings if f.cvss_v3_severity == "LOW")

    # Critical assets at risk (criticality CRITICAL or business_impact >= 80 with >= 1 finding)
    critical_assets_at_risk = 0
    for a in assets:
        if a.criticality in ("CRITICAL", "HIGH") or a.business_impact_score >= 80.0:
            if any(f.asset_id == a.id for f in findings):
                critical_assets_at_risk += 1

    # Network twin graph for choke points and overall risk
    twin = DigitalTwinGraph.build_from_db(db)
    choke_points = twin.get_choke_points()

    # Highest-risk assets
    asset_risks = []
    for a in assets:
        asset_findings = [f for f in findings if f.asset_id == a.id]
        max_context = max([f.contextual_risk_score for f in asset_findings], default=0.0)
        asset_risks.append({
            "id": a.id,
            "hostname": a.hostname or a.ip_address,
            "ip_address": a.ip_address,
            "asset_type": a.asset_type,
            "criticality": a.criticality,
            "risk_score": max_context,
            "vulnerabilities_count": len(asset_findings)
        })
    asset_risks.sort(key=lambda x: x["risk_score"], reverse=True)
    highest_risk_assets = asset_risks[:5]

    # Calculate overall network risk (weighted average of asset risks)
    if asset_risks:
        overall_risk = round(sum(a["risk_score"] for a in asset_risks) / len(asset_risks), 1)
    else:
        overall_risk = 0.0

    # Top remediation actions
    top_actions = []
    for r in remediations[:5]:
        top_actions.append({
            "id": r.id,
            "title": r.title,
            "priority": r.priority,
            "risk_reduction": round(r.risk_reduction_estimate, 1),
            "status": r.status,
            "affected_paths": r.affected_attack_paths_count
        })

    # Fictional / historical risk trend for visual SOC charting
    risk_history = [
        {"timestamp": "Day 1", "risk_score": min(100.0, overall_risk + 14.5), "vulns_count": len(findings) + 3},
        {"timestamp": "Day 2", "risk_score": min(100.0, overall_risk + 9.2), "vulns_count": len(findings) + 2},
        {"timestamp": "Day 3", "risk_score": min(100.0, overall_risk + 4.0), "vulns_count": len(findings) + 1},
        {"timestamp": "Current", "risk_score": overall_risk, "vulns_count": len(findings)}
    ]

    last_activity = None
    if last_assessment:
        last_activity = {
            "id": last_assessment.id,
            "title": last_assessment.title,
            "type": last_assessment.assessment_type,
            "status": last_assessment.status,
            "duration": last_assessment.execution_duration_seconds,
            "created_at": last_assessment.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }

    return {
        "total_assets": len(assets),
        "total_services": services_count,
        "total_vulnerabilities": len(findings),
        "critical_findings": crit_vulns,
        "high_findings": high_vulns,
        "medium_findings": med_vulns,
        "low_findings": low_vulns,
        "simulated_attack_paths_count": len(sim_paths),
        "critical_assets_at_risk_count": critical_assets_at_risk,
        "overall_network_risk_score": overall_risk,
        "choke_points": choke_points,
        "highest_risk_assets": highest_risk_assets,
        "top_remediation_actions": top_actions,
        "risk_history": risk_history,
        "last_assessment_activity": last_activity
    }

@router.post("/load-demo")
def seed_demo_data(db: Session = Depends(get_db)):
    """
    Seeds or resets the database with the demonstration enterprise network topology.
    """
    assessment = load_sample_topology(db, force_reload=True)
    return {
        "message": "Demonstration enterprise network topology loaded successfully",
        "assessment_id": assessment.id,
        "assets_count": assessment.total_assets_found,
        "findings_count": assessment.total_vulns_found
    }
