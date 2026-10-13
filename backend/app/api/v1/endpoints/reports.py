from typing import Optional
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.services.report_generator import ReportGeneratorService

router = APIRouter()

@router.get("/csv")
def download_csv_report(
    assessment_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    csv_data = ReportGeneratorService.generate_csv_report(db, assessment_id=assessment_id)
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=vulnerability_findings_assessment.csv"}
    )

@router.get("/pdf")
def download_pdf_report(
    assessment_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    pdf_bytes = ReportGeneratorService.generate_pdf_report(db, assessment_id=assessment_id)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=cybersecurity_digital_twin_report.pdf"}
    )
