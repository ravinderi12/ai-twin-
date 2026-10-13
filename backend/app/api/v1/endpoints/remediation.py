from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.models import RemediationRecommendation, RemediationScenario, Asset
from backend.app.schemas.schemas import (
    RemediationRecommendationResponse, RemediationStatusUpdate,
    SimulateRemediationRequest, RemediationScenarioResponse
)
from backend.app.simulation.remediation_engine import RemediationSimulator

router = APIRouter()

@router.get("/worklist", response_model=List[RemediationRecommendationResponse])
def get_remediation_worklist(db: Session = Depends(get_db)):
    remediations = db.query(RemediationRecommendation).order_by(
        RemediationRecommendation.risk_reduction_estimate.desc()
    ).all()

    results = []
    for r in remediations:
        asset = db.query(Asset).filter(Asset.id == r.asset_id).first()
        results.append(RemediationRecommendationResponse(
            id=r.id,
            assessment_id=r.assessment_id,
            finding_id=r.finding_id,
            asset_id=r.asset_id,
            asset_hostname=asset.hostname if asset else None,
            asset_ip=asset.ip_address if asset else None,
            title=r.title,
            action_description=r.action_description,
            priority=r.priority,
            status=r.status,
            risk_before=r.risk_before,
            risk_after=r.risk_after,
            risk_reduction_estimate=r.risk_reduction_estimate,
            affected_attack_paths_count=r.affected_attack_paths_count,
            expected_security_benefit=r.expected_security_benefit,
            notes=r.notes,
            created_at=r.created_at
        ))
    return results

@router.put("/{remediation_id}/status", response_model=RemediationRecommendationResponse)
def update_remediation_status(
    remediation_id: int,
    payload: RemediationStatusUpdate,
    db: Session = Depends(get_db)
):
    rem = db.query(RemediationRecommendation).filter(RemediationRecommendation.id == remediation_id).first()
    if not rem:
        raise HTTPException(status_code=404, detail="Remediation recommendation not found.")

    rem.status = payload.status.upper()
    if payload.notes:
        rem.notes = payload.notes
    db.commit()
    db.refresh(rem)

    asset = db.query(Asset).filter(Asset.id == rem.asset_id).first()
    return RemediationRecommendationResponse(
        id=rem.id,
        assessment_id=rem.assessment_id,
        finding_id=rem.finding_id,
        asset_id=rem.asset_id,
        asset_hostname=asset.hostname if asset else None,
        asset_ip=asset.ip_address if asset else None,
        title=rem.title,
        action_description=rem.action_description,
        priority=rem.priority,
        status=rem.status,
        risk_before=rem.risk_before,
        risk_after=rem.risk_after,
        risk_reduction_estimate=rem.risk_reduction_estimate,
        affected_attack_paths_count=rem.affected_attack_paths_count,
        expected_security_benefit=rem.expected_security_benefit,
        notes=rem.notes,
        created_at=rem.created_at
    )

@router.post("/simulate-what-if", response_model=RemediationScenarioResponse)
def simulate_remediation_scenario(
    payload: SimulateRemediationRequest,
    db: Session = Depends(get_db)
):
    result = RemediationSimulator.simulate_what_if(
        db=db,
        patch_finding_ids=payload.patch_finding_ids,
        block_relationship_ids=payload.block_relationship_ids,
        isolate_asset_ids=payload.isolate_asset_ids,
        start_asset_id=payload.start_asset_id,
        target_asset_id=payload.target_asset_id
    )
    return result

@router.get("/scenarios")
def list_remediation_scenarios(limit: int = 10, db: Session = Depends(get_db)):
    scenarios = db.query(RemediationScenario).order_by(RemediationScenario.created_at.desc()).limit(limit).all()
    results = []
    for s in scenarios:
        results.append({
            "id": s.id,
            "name": s.name,
            "description": s.description,
            "baseline_risk": s.baseline_risk_score,
            "simulated_risk": s.simulated_risk_score,
            "risk_reduction_pct": s.risk_reduction_percentage,
            "eliminated_paths": s.eliminated_paths_count,
            "remaining_paths": s.remaining_paths_count,
            "created_at": s.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    return results
