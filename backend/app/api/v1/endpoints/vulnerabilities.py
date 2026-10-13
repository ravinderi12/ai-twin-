from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.models import VulnerabilityFinding, Asset, ServicePort
from backend.app.schemas.schemas import (
    VulnerabilityFindingResponse, VulnerabilityFindingCreate
)
from backend.app.risk_engine.context_risk import ContextualRiskEngine

router = APIRouter()

@router.get("", response_model=List[VulnerabilityFindingResponse])
def list_vulnerabilities(
    query: Optional[str] = None,
    severity: Optional[str] = None,
    asset_id: Optional[int] = None,
    reachability: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    q = db.query(VulnerabilityFinding)
    if query:
        term = f"%{query}%"
        q = q.filter((VulnerabilityFinding.cve_id.ilike(term)) | (VulnerabilityFinding.title.ilike(term)))
    if severity:
        q = q.filter(VulnerabilityFinding.cvss_v3_severity == severity.upper())
    if asset_id:
        q = q.filter(VulnerabilityFinding.asset_id == asset_id)
    if reachability:
        q = q.filter(VulnerabilityFinding.reachability_status == reachability.lower())

    findings = q.order_by(VulnerabilityFinding.contextual_risk_score.desc()).offset(skip).limit(limit).all()

    results = []
    for f in findings:
        srv_str = None
        if f.service:
            srv_str = f"{f.service.port}/{f.service.protocol} ({f.service.service_name or ''})"

        results.append(VulnerabilityFindingResponse(
            id=f.id,
            asset_id=f.asset_id,
            assessment_id=f.assessment_id,
            service_id=f.service_id,
            cve_id=f.cve_id,
            title=f.title,
            description=f.description,
            cvss_v3_score=f.cvss_v3_score,
            cvss_v3_severity=f.cvss_v3_severity,
            cvss_vector=f.cvss_vector,
            reference_url=f.reference_url,
            source=f.source,
            match_type=f.match_type,
            reachability_status=f.reachability_status,
            raw_score=f.raw_score,
            contextual_risk_score=f.contextual_risk_score,
            risk_factors_json=f.risk_factors_json,
            remediation_advice=f.remediation_advice,
            created_at=f.created_at,
            asset_hostname=f.asset.hostname if f.asset else None,
            asset_ip=f.asset.ip_address if f.asset else None,
            service_info=srv_str
        ))

    return results

@router.get("/{finding_id}", response_model=VulnerabilityFindingResponse)
def get_vulnerability_detail(finding_id: int, db: Session = Depends(get_db)):
    f = db.query(VulnerabilityFinding).filter(VulnerabilityFinding.id == finding_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Vulnerability finding not found.")

    srv_str = None
    if f.service:
        srv_str = f"{f.service.port}/{f.service.protocol} ({f.service.service_name or ''})"

    return VulnerabilityFindingResponse(
        id=f.id,
        asset_id=f.asset_id,
        assessment_id=f.assessment_id,
        service_id=f.service_id,
        cve_id=f.cve_id,
        title=f.title,
        description=f.description,
        cvss_v3_score=f.cvss_v3_score,
        cvss_v3_severity=f.cvss_v3_severity,
        cvss_vector=f.cvss_vector,
        reference_url=f.reference_url,
        source=f.source,
        match_type=f.match_type,
        reachability_status=f.reachability_status,
        raw_score=f.raw_score,
        contextual_risk_score=f.contextual_risk_score,
        risk_factors_json=f.risk_factors_json,
        remediation_advice=f.remediation_advice,
        created_at=f.created_at,
        asset_hostname=f.asset.hostname if f.asset else None,
        asset_ip=f.asset.ip_address if f.asset else None,
        service_info=srv_str
    )

@router.post("", response_model=VulnerabilityFindingResponse, status_code=status.HTTP_201_CREATED)
def create_vulnerability(payload: VulnerabilityFindingCreate, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == payload.asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Target asset not found.")

    # Calculate contextual risk automatically
    score, factors, explanation = ContextualRiskEngine.calculate_finding_risk(
        cvss_score=payload.cvss_v3_score,
        is_perimeter=asset.is_perimeter,
        reachability_status=payload.reachability_status,
        asset_impact_score=asset.business_impact_score,
        asset_criticality=asset.criticality,
        match_type=payload.match_type
    )

    finding = VulnerabilityFinding(
        asset_id=payload.asset_id,
        assessment_id=payload.assessment_id,
        service_id=payload.service_id,
        cve_id=payload.cve_id,
        title=payload.title,
        description=payload.description,
        cvss_v3_score=payload.cvss_v3_score,
        cvss_v3_severity=payload.cvss_v3_severity,
        cvss_vector=payload.cvss_vector,
        reference_url=payload.reference_url,
        source=payload.source,
        match_type=payload.match_type,
        reachability_status=payload.reachability_status,
        raw_score=payload.cvss_v3_score * 10.0,
        contextual_risk_score=score,
        risk_factors_json=str(factors),
        remediation_advice=payload.remediation_advice
    )
    db.add(finding)
    db.commit()
    db.refresh(finding)

    return VulnerabilityFindingResponse(
        id=finding.id,
        asset_id=finding.asset_id,
        assessment_id=finding.assessment_id,
        service_id=finding.service_id,
        cve_id=finding.cve_id,
        title=finding.title,
        description=finding.description,
        cvss_v3_score=finding.cvss_v3_score,
        cvss_v3_severity=finding.cvss_v3_severity,
        cvss_vector=finding.cvss_vector,
        reference_url=finding.reference_url,
        source=finding.source,
        match_type=finding.match_type,
        reachability_status=finding.reachability_status,
        raw_score=finding.raw_score,
        contextual_risk_score=finding.contextual_risk_score,
        risk_factors_json=finding.risk_factors_json,
        remediation_advice=finding.remediation_advice,
        created_at=finding.created_at,
        asset_hostname=asset.hostname,
        asset_ip=asset.ip_address,
        service_info=None
    )
