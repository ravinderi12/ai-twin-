from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.models import Asset, ServicePort, VulnerabilityFinding, NetworkRelationship
from backend.app.schemas.schemas import (
    AssetCreate, AssetUpdate, AssetResponse, AssetDetailResponse,
    ServicePortCreate, ServicePortResponse
)

router = APIRouter()

@router.get("", response_model=List[AssetResponse])
def list_assets(
    query: Optional[str] = None,
    criticality: Optional[str] = None,
    environment: Optional[str] = None,
    asset_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    q = db.query(Asset)
    if query:
        term = f"%{query}%"
        q = q.filter((Asset.hostname.ilike(term)) | (Asset.ip_address.ilike(term)) | (Asset.os_name.ilike(term)))
    if criticality:
        q = q.filter(Asset.criticality == criticality.upper())
    if environment:
        q = q.filter(Asset.environment == environment.lower())
    if asset_type:
        q = q.filter(Asset.asset_type == asset_type.lower())

    assets = q.offset(skip).limit(limit).all()

    results = []
    for a in assets:
        findings = db.query(VulnerabilityFinding).filter(VulnerabilityFinding.asset_id == a.id).all()
        services_count = db.query(ServicePort).filter(ServicePort.asset_id == a.id).count()
        max_risk = max([f.contextual_risk_score for f in findings], default=0.0)

        results.append(AssetResponse(
            id=a.id,
            hostname=a.hostname,
            ip_address=a.ip_address,
            mac_address=a.mac_address,
            os_name=a.os_name,
            os_version=a.os_version,
            asset_type=a.asset_type,
            criticality=a.criticality,
            environment=a.environment,
            subnet=a.subnet,
            is_isolated=a.is_isolated,
            is_perimeter=a.is_perimeter,
            business_impact_score=a.business_impact_score,
            notes=a.notes,
            created_at=a.created_at,
            updated_at=a.updated_at,
            services_count=services_count,
            findings_count=len(findings),
            calculated_risk=max_risk
        ))

    return results

@router.post("", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
def create_asset(payload: AssetCreate, db: Session = Depends(get_db)):
    # Check duplicate IP
    existing = db.query(Asset).filter(Asset.ip_address == payload.ip_address).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"An asset with IP address '{payload.ip_address}' already exists (ID: {existing.id})."
        )

    asset = Asset(**payload.model_dump())
    db.add(asset)
    db.commit()
    db.refresh(asset)

    return AssetResponse(
        id=asset.id,
        hostname=asset.hostname,
        ip_address=asset.ip_address,
        mac_address=asset.mac_address,
        os_name=asset.os_name,
        os_version=asset.os_version,
        asset_type=asset.asset_type,
        criticality=asset.criticality,
        environment=asset.environment,
        subnet=asset.subnet,
        is_isolated=asset.is_isolated,
        is_perimeter=asset.is_perimeter,
        business_impact_score=asset.business_impact_score,
        notes=asset.notes,
        created_at=asset.created_at,
        updated_at=asset.updated_at,
        services_count=0,
        findings_count=0,
        calculated_risk=0.0
    )

@router.get("/{asset_id}", response_model=AssetDetailResponse)
def get_asset_detail(asset_id: int, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset with ID {asset_id} not found.")

    services = db.query(ServicePort).filter(ServicePort.asset_id == asset.id).all()
    findings = db.query(VulnerabilityFinding).filter(VulnerabilityFinding.asset_id == asset.id).all()
    max_risk = max([f.contextual_risk_score for f in findings], default=0.0)

    # Format findings with host metadata
    findings_resp = []
    for f in findings:
        srv_str = None
        if f.service:
            srv_str = f"{f.service.port}/{f.service.protocol} ({f.service.service_name or ''})"
        findings_resp.append({
            "id": f.id,
            "asset_id": f.asset_id,
            "assessment_id": f.assessment_id,
            "service_id": f.service_id,
            "cve_id": f.cve_id,
            "title": f.title,
            "description": f.description,
            "cvss_v3_score": f.cvss_v3_score,
            "cvss_v3_severity": f.cvss_v3_severity,
            "cvss_vector": f.cvss_vector,
            "reference_url": f.reference_url,
            "source": f.source,
            "match_type": f.match_type,
            "reachability_status": f.reachability_status,
            "raw_score": f.raw_score,
            "contextual_risk_score": f.contextual_risk_score,
            "risk_factors_json": f.risk_factors_json,
            "remediation_advice": f.remediation_advice,
            "created_at": f.created_at,
            "asset_hostname": asset.hostname,
            "asset_ip": asset.ip_address,
            "service_info": srv_str
        })

    return AssetDetailResponse(
        id=asset.id,
        hostname=asset.hostname,
        ip_address=asset.ip_address,
        mac_address=asset.mac_address,
        os_name=asset.os_name,
        os_version=asset.os_version,
        asset_type=asset.asset_type,
        criticality=asset.criticality,
        environment=asset.environment,
        subnet=asset.subnet,
        is_isolated=asset.is_isolated,
        is_perimeter=asset.is_perimeter,
        business_impact_score=asset.business_impact_score,
        notes=asset.notes,
        created_at=asset.created_at,
        updated_at=asset.updated_at,
        services_count=len(services),
        findings_count=len(findings),
        calculated_risk=max_risk,
        services=[ServicePortResponse.model_validate(s) for s in services],
        findings=findings_resp
    )

@router.put("/{asset_id}", response_model=AssetResponse)
def update_asset(asset_id: int, payload: AssetUpdate, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found.")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(asset, field, value)

    db.commit()
    db.refresh(asset)

    findings = db.query(VulnerabilityFinding).filter(VulnerabilityFinding.asset_id == asset.id).all()
    services_count = db.query(ServicePort).filter(ServicePort.asset_id == asset.id).count()
    max_risk = max([f.contextual_risk_score for f in findings], default=0.0)

    return AssetResponse(
        id=asset.id,
        hostname=asset.hostname,
        ip_address=asset.ip_address,
        mac_address=asset.mac_address,
        os_name=asset.os_name,
        os_version=asset.os_version,
        asset_type=asset.asset_type,
        criticality=asset.criticality,
        environment=asset.environment,
        subnet=asset.subnet,
        is_isolated=asset.is_isolated,
        is_perimeter=asset.is_perimeter,
        business_impact_score=asset.business_impact_score,
        notes=asset.notes,
        created_at=asset.created_at,
        updated_at=asset.updated_at,
        services_count=services_count,
        findings_count=len(findings),
        calculated_risk=max_risk
    )

@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(asset_id: int, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found.")
    db.delete(asset)
    db.commit()
    return None

@router.post("/{asset_id}/services", response_model=ServicePortResponse, status_code=status.HTTP_201_CREATED)
def add_service_port(asset_id: int, payload: ServicePortCreate, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found.")

    srv = ServicePort(
        asset_id=asset_id,
        port=payload.port,
        protocol=payload.protocol,
        service_name=payload.service_name,
        product=payload.product,
        version=payload.version,
        banner=payload.banner,
        state=payload.state,
        is_exposed=payload.is_exposed
    )
    db.add(srv)
    db.commit()
    db.refresh(srv)
    return srv

@router.delete("/{asset_id}/services/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service_port(asset_id: int, service_id: int, db: Session = Depends(get_db)):
    srv = db.query(ServicePort).filter(ServicePort.id == service_id, ServicePort.asset_id == asset_id).first()
    if not srv:
        raise HTTPException(status_code=404, detail="Service port not found.")
    db.delete(srv)
    db.commit()
    return None
