from typing import Dict, Any
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.ingestion.nmap_parser import NmapXMLParser, NmapParserError
from backend.app.ingestion.json_importer import JSONAssetImporter, JSONImporterError
from backend.app.models.models import Assessment, Asset, ServicePort, VulnerabilityFinding
from backend.app.schemas.schemas import AssessmentResponse

router = APIRouter()

@router.post("/upload-nmap-xml", response_model=AssessmentResponse)
async def upload_nmap_xml(
    file: UploadFile = File(...),
    title: str = Form("Imported Nmap XML Audit"),
    description: str = Form("Network scan results ingested via Nmap XML upload"),
    db: Session = Depends(get_db)
):
    try:
        content_bytes = await file.read()
        content_str = content_bytes.decode("utf-8", errors="replace")

        hosts = NmapXMLParser.parse_xml(content_str)
        if not hosts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="XML parsed successfully but contains no active or reachable hosts."
            )

        assessment = Assessment(
            title=title,
            description=description,
            assessment_type="imported_xml",
            target_scope=f"{len(hosts)} targets from {file.filename}",
            status="completed",
            total_assets_found=len(hosts),
            execution_duration_seconds=1.2
        )
        db.add(assessment)
        db.flush()

        total_vulns = 0
        for h in hosts:
            # Check existing asset
            existing_asset = db.query(Asset).filter(Asset.ip_address == h["ip_address"]).first()
            if existing_asset:
                asset = existing_asset
                asset.hostname = h["hostname"] or asset.hostname
                asset.os_name = h["os_name"] or asset.os_name
            else:
                asset = Asset(
                    hostname=h["hostname"],
                    ip_address=h["ip_address"],
                    mac_address=h.get("mac_address"),
                    os_name=h.get("os_name"),
                    os_version=h.get("os_version"),
                    asset_type=h.get("asset_type", "server"),
                    criticality="MEDIUM",
                    environment="internal",
                    business_impact_score=50.0
                )
                db.add(asset)
                db.flush()

            for s in h.get("services", []):
                srv = ServicePort(
                    asset_id=asset.id,
                    port=s["port"],
                    protocol=s["protocol"],
                    service_name=s.get("service_name"),
                    product=s.get("product"),
                    version=s.get("version"),
                    banner=s.get("banner"),
                    state=s.get("state", "open")
                )
                db.add(srv)
                db.flush()

                # Add any script detected CVEs
                for sf in s.get("script_findings", []):
                    total_vulns += 1
                    finding = VulnerabilityFinding(
                        assessment_id=assessment.id,
                        asset_id=asset.id,
                        service_id=srv.id,
                        cve_id=sf["cve_id"],
                        title=f"Detected Vulnerability {sf['cve_id']}",
                        description=sf["output_snippet"],
                        cvss_v3_score=7.5,
                        cvss_v3_severity="HIGH",
                        source="Nmap NSE Script",
                        match_type="confirmed_signature",
                        raw_score=75.0,
                        contextual_risk_score=70.0
                    )
                    db.add(finding)

        assessment.total_vulns_found = total_vulns
        db.commit()
        db.refresh(assessment)
        return assessment

    except NmapParserError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ingestion error: {str(e)}")

@router.post("/import-json", response_model=AssessmentResponse)
def import_json_payload(
    payload: Dict[str, Any],
    title: str = "Imported JSON Topology",
    db: Session = Depends(get_db)
):
    try:
        assessment = JSONAssetImporter.import_payload(db, payload, assessment_title=title)
        return assessment
    except JSONImporterError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"JSON ingestion error: {str(e)}")
