import pytest
from backend.app.database.session import SessionLocal
from backend.app.sample_data.enterprise_topology import load_sample_topology
from backend.app.services.report_generator import ReportGeneratorService

def test_csv_report_generation():
    db = SessionLocal()
    try:
        load_sample_topology(db, force_reload=True)
        csv_str = ReportGeneratorService.generate_csv_report(db)
        assert "Finding ID,CVE ID,Severity" in csv_str
        assert "CVE-2021-44228" in csv_str
        assert "CVE-2021-41773" in csv_str
    finally:
        db.close()

def test_pdf_report_generation():
    db = SessionLocal()
    try:
        load_sample_topology(db, force_reload=True)
        pdf_bytes = ReportGeneratorService.generate_pdf_report(db)
        assert len(pdf_bytes) > 1000
        # Valid PDF header %PDF-
        assert pdf_bytes.startswith(b"%PDF-")
    finally:
        db.close()
