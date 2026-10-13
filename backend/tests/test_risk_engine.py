import pytest
from backend.app.risk_engine.context_risk import ContextualRiskEngine

def test_contextual_risk_comparison_reachable_vs_isolated():
    """
    Validates that a vulnerability on an internet-facing critical asset
    receives a substantially higher contextual risk score than the exact same
    vulnerability on an isolated, low-impact asset.
    """
    identical_cvss = 7.5

    # Asset A: Exposed perimeter asset with critical impact
    risk_exposed, factors_a, exp_a = ContextualRiskEngine.calculate_finding_risk(
        cvss_score=identical_cvss,
        is_perimeter=True,
        reachability_status="internet_reachable",
        asset_impact_score=95.0,
        asset_criticality="CRITICAL",
        match_type="confirmed_signature"
    )

    # Asset B: Isolated internal asset with low impact
    risk_isolated, factors_b, exp_b = ContextualRiskEngine.calculate_finding_risk(
        cvss_score=identical_cvss,
        is_perimeter=False,
        reachability_status="isolated",
        asset_impact_score=20.0,
        asset_criticality="LOW",
        match_type="version_heuristic"
    )

    assert risk_exposed > risk_isolated
    assert (risk_exposed - risk_isolated) > 25.0  # Significant context delta
    assert 0.0 <= risk_exposed <= 100.0
    assert 0.0 <= risk_isolated <= 100.0
    assert "internet_reachable" in exp_a
    assert "isolated" in exp_b

def test_risk_score_boundary_conditions():
    # Maximum extreme values
    max_risk, _, _ = ContextualRiskEngine.calculate_finding_risk(
        cvss_score=10.0,
        is_perimeter=True,
        reachability_status="internet_reachable",
        asset_impact_score=100.0,
        asset_criticality="CRITICAL",
        match_type="confirmed_signature"
    )
    assert max_risk <= 100.0

    # Minimum extreme values
    min_risk, _, _ = ContextualRiskEngine.calculate_finding_risk(
        cvss_score=0.0,
        is_perimeter=False,
        reachability_status="isolated",
        asset_impact_score=0.0,
        asset_criticality="LOW"
    )
    assert min_risk == 0.0
