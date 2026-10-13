import pytest
from backend.app.database.session import SessionLocal
from backend.app.sample_data.enterprise_topology import load_sample_topology
from backend.app.simulation.remediation_engine import RemediationSimulator
from backend.app.models.models import VulnerabilityFinding, Asset

def test_remediation_what_if_scenario():
    db = SessionLocal()
    try:
        load_sample_topology(db, force_reload=True)

        gw = db.query(Asset).filter(Asset.ip_address == "198.51.100.1").first()
        db_srv = db.query(Asset).filter(Asset.ip_address == "192.168.3.50").first()

        # Find the Log4j finding on the App Server (the critical choke point!)
        log4j_finding = db.query(VulnerabilityFinding).filter(VulnerabilityFinding.cve_id == "CVE-2021-44228").first()
        assert log4j_finding is not None

        # Simulate patching Log4j
        result = RemediationSimulator.simulate_what_if(
            db=db,
            patch_finding_ids=[log4j_finding.id],
            block_relationship_ids=[],
            isolate_asset_ids=[],
            start_asset_id=gw.id,
            target_asset_id=db_srv.id,
            scenario_name="Test Patch Log4Shell on App Server"
        )

        assert "baseline_risk_score" in result
        assert "simulated_risk_score" in result
        assert result["baseline_risk_score"] > 0.0
        assert result["remediated_findings_count"] == 1
        assert "comparison_summary" in result
        # Verify database record saved
        assert result["risk_reduction_percentage"] >= 0.0
    finally:
        db.close()
