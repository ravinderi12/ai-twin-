from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.core.config import settings
from backend.app.scanners.nmap_scanner import NmapScannerService

router = APIRouter()

@router.get("/health")
def get_health(db: Session = Depends(get_db)):
    db_status = "connected"
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": db_status,
        "nmap_cli_available": NmapScannerService.is_nmap_available(),
        "live_scanning_enabled": settings.ENABLE_LIVE_SCANNING,
        "allowed_scan_ranges": settings.ALLOWED_SCAN_RANGES
    }

@router.get("/readiness")
def get_readiness():
    return {"status": "ready"}
