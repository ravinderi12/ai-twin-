from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.models import Assessment
from backend.app.schemas.schemas import AssessmentCreate, AssessmentResponse, LiveScanRequest
from backend.app.scanners.nmap_scanner import NmapScannerService, ScannerSafetyError

router = APIRouter()

@router.get("", response_model=List[AssessmentResponse])
def list_assessments(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    assessments = db.query(Assessment).order_by(Assessment.created_at.desc()).offset(skip).limit(limit).all()
    return assessments

@router.get("/{assessment_id}", response_model=AssessmentResponse)
def get_assessment(assessment_id: int, db: Session = Depends(get_db)):
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found.")
    return assessment

@router.post("", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
def create_assessment(payload: AssessmentCreate, db: Session = Depends(get_db)):
    assessment = Assessment(
        title=payload.title,
        description=payload.description,
        assessment_type=payload.assessment_type,
        target_scope=payload.target_scope,
        status="pending"
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment

@router.post("/live-scan", response_model=AssessmentResponse)
def trigger_live_scan(payload: LiveScanRequest, db: Session = Depends(get_db)):
    try:
        assessment = NmapScannerService.execute_authorized_scan(
            db=db,
            target=payload.target,
            scan_type=payload.scan_type,
            confirm_authorized=payload.confirm_authorized
        )
        return assessment
    except ScannerSafetyError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Scan execution error: {str(e)}")
