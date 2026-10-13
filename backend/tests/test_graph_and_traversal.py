import pytest
from backend.app.database.session import SessionLocal
from backend.app.digital_twin.graph_builder import DigitalTwinGraph
from backend.app.simulation.attack_simulator import AttackSimulationEngine
from backend.app.sample_data.enterprise_topology import load_sample_topology
from backend.app.models.models import Asset

def test_graph_construction_and_traversal():
    db = SessionLocal()
    try:
        # Load sample enterprise topology
        load_sample_topology(db, force_reload=True)

        twin = DigitalTwinGraph.build_from_db(db)
        assert len(twin.graph.nodes) >= 6
        assert len(twin.graph.edges) >= 6

        # Identify Gateway (Start) and Database (Crown Jewel Target)
        gw = db.query(Asset).filter(Asset.ip_address == "198.51.100.1").first()
        db_srv = db.query(Asset).filter(Asset.ip_address == "192.168.3.50").first()
        ad_srv = db.query(Asset).filter(Asset.ip_address == "192.168.3.5").first()

        assert gw is not None
        assert db_srv is not None
        assert ad_srv is not None

        # Test Dijkstra Simulation from Gateway to Database
        dijkstra_res = AttackSimulationEngine.simulate_path(
            db=db,
            start_asset_id=gw.id,
            target_asset_id=db_srv.id,
            algorithm="Dijkstra"
        )

        assert dijkstra_res["path_found"] is True
        assert dijkstra_res["hop_count"] >= 2
        assert len(dijkstra_res["steps"]) >= 2
        assert dijkstra_res["total_path_risk"] > 0.0

        # Verify MITRE tactic assignment
        step1 = dijkstra_res["steps"][0]
        assert "mitre_technique_id" in step1
        assert step1["mitre_tactic"] in ("Initial Access", "Lateral Movement")

        # Test BFS Simulation
        bfs_res = AttackSimulationEngine.simulate_path(
            db=db,
            start_asset_id=gw.id,
            target_asset_id=ad_srv.id,
            algorithm="BFS"
        )
        assert bfs_res["path_found"] is True
        assert bfs_res["algorithm_used"] == "BFS"

        # Test Unreachable Node
        isolated = Asset(
            hostname="air-gapped-vault.internal",
            ip_address="192.168.99.1",
            asset_type="server",
            criticality="CRITICAL",
            is_isolated=True
        )
        db.add(isolated)
        db.commit()
        db.refresh(isolated)

        unreachable_res = AttackSimulationEngine.simulate_path(
            db=db,
            start_asset_id=gw.id,
            target_asset_id=isolated.id,
            algorithm="Dijkstra"
        )
        assert unreachable_res["path_found"] is False
        assert "No feasible" in unreachable_res["explanation"]

        # Clean up isolated node
        db.delete(isolated)
        db.commit()
    finally:
        db.close()
