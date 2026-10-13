from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.digital_twin.graph_builder import DigitalTwinGraph
from backend.app.models.models import NetworkRelationship, Asset
from backend.app.schemas.schemas import (
    NetworkRelationshipCreate, NetworkRelationshipResponse, CytoscapeGraphResponse
)

router = APIRouter()

@router.get("/cytoscape")
def get_cytoscape_graph(
    attack_path_nodes: Optional[str] = Query(None, description="Comma-separated node IDs to highlight as attack path"),
    assessment_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    twin = DigitalTwinGraph.build_from_db(db, assessment_id=assessment_id)
    path_nodes_list = [n.strip() for n in attack_path_nodes.split(",")] if attack_path_nodes else None
    return twin.export_for_cytoscape(attack_path_nodes=path_nodes_list)

@router.get("/relationships", response_model=List[NetworkRelationshipResponse])
def list_relationships(db: Session = Depends(get_db)):
    rels = db.query(NetworkRelationship).all()
    results = []
    for r in rels:
        src = db.query(Asset).filter(Asset.id == r.source_asset_id).first()
        tgt = db.query(Asset).filter(Asset.id == r.target_asset_id).first()
        results.append(NetworkRelationshipResponse(
            id=r.id,
            source_asset_id=r.source_asset_id,
            target_asset_id=r.target_asset_id,
            relationship_type=r.relationship_type,
            protocol=r.protocol,
            port=r.port,
            is_inferred=r.is_inferred,
            confidence=r.confidence,
            weight=r.weight,
            description=r.description,
            created_at=r.created_at,
            source_hostname=src.hostname if src else None,
            source_ip=src.ip_address if src else None,
            target_hostname=tgt.hostname if tgt else None,
            target_ip=tgt.ip_address if tgt else None
        ))
    return results

@router.post("/relationships", response_model=NetworkRelationshipResponse, status_code=status.HTTP_201_CREATED)
def create_relationship(payload: NetworkRelationshipCreate, db: Session = Depends(get_db)):
    src = db.query(Asset).filter(Asset.id == payload.source_asset_id).first()
    tgt = db.query(Asset).filter(Asset.id == payload.target_asset_id).first()
    if not src or not tgt:
        raise HTTPException(status_code=400, detail="Source or target asset ID does not exist.")

    rel = NetworkRelationship(**payload.model_dump())
    db.add(rel)
    db.commit()
    db.refresh(rel)

    return NetworkRelationshipResponse(
        id=rel.id,
        source_asset_id=rel.source_asset_id,
        target_asset_id=rel.target_asset_id,
        relationship_type=rel.relationship_type,
        protocol=rel.protocol,
        port=rel.port,
        is_inferred=rel.is_inferred,
        confidence=rel.confidence,
        weight=rel.weight,
        description=rel.description,
        created_at=rel.created_at,
        source_hostname=src.hostname,
        source_ip=src.ip_address,
        target_hostname=tgt.hostname,
        target_ip=tgt.ip_address
    )

@router.delete("/relationships/{relationship_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_relationship(relationship_id: int, db: Session = Depends(get_db)):
    rel = db.query(NetworkRelationship).filter(NetworkRelationship.id == relationship_id).first()
    if not rel:
        raise HTTPException(status_code=404, detail="Network relationship not found.")
    db.delete(rel)
    db.commit()
    return None
