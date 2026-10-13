import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.simulation.attack_simulator import AttackSimulationEngine
from backend.app.models.models import SimulatedAttackPath, Asset
from backend.app.schemas.schemas import SimulatePathRequest, SimulatedPathResponse

router = APIRouter()

@router.post("/simulate", response_model=SimulatedPathResponse)
def simulate_attack_path(payload: SimulatePathRequest, db: Session = Depends(get_db)):
    start_asset = db.query(Asset).filter(Asset.id == payload.start_asset_id).first()
    target_asset = db.query(Asset).filter(Asset.id == payload.target_asset_id).first()

    if not start_asset or not target_asset:
        raise HTTPException(status_code=400, detail="Start or target asset does not exist.")

    result = AttackSimulationEngine.simulate_path(
        db=db,
        start_asset_id=payload.start_asset_id,
        target_asset_id=payload.target_asset_id,
        algorithm=payload.algorithm,
        assessment_id=payload.assessment_id
    )

    return result

@router.get("/history")
def list_simulation_history(limit: int = 20, db: Session = Depends(get_db)):
    records = db.query(SimulatedAttackPath).order_by(SimulatedAttackPath.created_at.desc()).limit(limit).all()
    results = []
    for r in records:
        start_a = db.query(Asset).filter(Asset.id == r.start_asset_id).first()
        target_a = db.query(Asset).filter(Asset.id == r.target_asset_id).first()
        results.append({
            "id": r.id,
            "name": r.name,
            "algorithm_used": r.algorithm_used,
            "hop_count": r.hop_count,
            "total_path_cost": r.total_path_cost,
            "total_path_risk": r.total_path_risk,
            "start_asset": start_a.hostname or start_a.ip_address if start_a else "N/A",
            "target_asset": target_a.hostname or target_a.ip_address if target_a else "N/A",
            "path_nodes": json.loads(r.path_nodes_json),
            "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    return results
