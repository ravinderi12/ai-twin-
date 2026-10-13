from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.integrations.nvd_client import NVDClient

router = APIRouter()

@router.get("/lookup/{cve_id}")
def lookup_cve(cve_id: str, db: Session = Depends(get_db)):
    result = NVDClient.get_cve_details(cve_id, db)
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"CVE '{cve_id}' not found in local cache or NVD repository. Please verify the identifier format (e.g. CVE-2021-44228)."
        )
    return result

@router.get("/search")
def search_cves(q: str = Query(..., min_length=2), db: Session = Depends(get_db)):
    results = NVDClient.search_cves(q, db)
    return {
        "query": q,
        "count": len(results),
        "results": results
    }
