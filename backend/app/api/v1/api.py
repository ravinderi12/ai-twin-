from fastapi import APIRouter
from backend.app.api.v1.endpoints import (
    health, dashboard, assets, assessments, ingestion,
    vulnerabilities, cve_intel, network_map, attack_paths,
    remediation, reports, auth
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(assets.router, prefix="/assets", tags=["Assets"])
api_router.include_router(assessments.router, prefix="/assessments", tags=["Assessments"])
api_router.include_router(ingestion.router, prefix="/ingestion", tags=["Data Ingestion"])
api_router.include_router(vulnerabilities.router, prefix="/vulnerabilities", tags=["Vulnerabilities"])
api_router.include_router(cve_intel.router, prefix="/cve", tags=["CVE Intelligence"])
api_router.include_router(network_map.router, prefix="/network-map", tags=["Digital Twin Topology"])
api_router.include_router(attack_paths.router, prefix="/attack-paths", tags=["Attack Path Simulation"])
api_router.include_router(remediation.router, prefix="/remediation", tags=["Remediation & What-If"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports & Export"])
