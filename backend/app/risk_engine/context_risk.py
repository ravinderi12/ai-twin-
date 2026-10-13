import json
from typing import Dict, Any, Tuple

class ContextualRiskEngine:
    """
    Context-Aware Risk Analysis Engine.
    Implements topology-aware exposure scoring to replace isolated CVSS metrics:
    
    Formula:
      Contextual_Risk = Normalized_CVSS * Reachability_Weight * Asset_Impact_Weight * Confidence_Weight * 100
      
    Path Risk Formula (per academic synopsis):
      Risk(p) = Sum_{k in path} [CVSS_Score(k) * Accessibility_Weight(k)] * Impact(Asset_target) / 100
    """

    REACHABILITY_WEIGHTS = {
        "internet_reachable": 1.0,
        "subnet_reachable": 0.75,
        "isolated": 0.30
    }

    CONFIDENCE_WEIGHTS = {
        "confirmed_signature": 1.0,
        "simulated_intel": 0.90,
        "version_heuristic": 0.85,
        "manual_audit": 0.95
    }

    CRITICALITY_IMPACT = {
        "CRITICAL": 100.0,
        "HIGH": 80.0,
        "MEDIUM": 50.0,
        "LOW": 20.0
    }

    @classmethod
    def calculate_finding_risk(
        cls,
        cvss_score: float,
        is_perimeter: bool,
        reachability_status: str,
        asset_impact_score: float,
        asset_criticality: str,
        match_type: str = "version_heuristic"
    ) -> Tuple[float, Dict[str, Any], str]:
        """
        Calculates context-aware risk score for a single finding on an asset.
        Returns: (contextual_risk_score, factor_breakdown, explanation)
        """
        # Clamp inputs safely
        cvss = max(0.0, min(10.0, float(cvss_score)))
        impact = max(1.0, min(100.0, float(asset_impact_score or cls.CRITICALITY_IMPACT.get(asset_criticality, 50.0))))

        reach_weight = cls.REACHABILITY_WEIGHTS.get(reachability_status, 0.75)
        if is_perimeter and reachability_status != "isolated":
            reach_weight = max(reach_weight, 0.95)

        confidence_weight = cls.CONFIDENCE_WEIGHTS.get(match_type, 0.85)
        normalized_cvss = cvss / 10.0
        normalized_impact = 0.35 + 0.65 * (impact / 100.0)  # Baseline sensitivity floor

        # Compute contextual score
        raw_contextual = normalized_cvss * reach_weight * normalized_impact * confidence_weight * 100.0
        final_score = round(max(0.0, min(100.0, raw_contextual)), 1)
        raw_cvss_score = round(cvss * 10.0, 1)

        factors = {
            "cvss_base": cvss,
            "cvss_normalized": round(normalized_cvss, 3),
            "reachability_status": reachability_status,
            "reachability_weight": reach_weight,
            "is_perimeter": is_perimeter,
            "asset_impact_score": impact,
            "asset_impact_weight": round(normalized_impact, 3),
            "evidence_match_type": match_type,
            "evidence_confidence_weight": confidence_weight,
            "raw_cvss_100": raw_cvss_score,
            "contextual_risk_score": final_score
        }

        # Formulate human-readable explanation
        diff = final_score - raw_cvss_score
        if diff > 5:
            delta_note = f"elevated by +{round(diff, 1)} pts due to high network exposure and critical asset centrality."
        elif diff < -5:
            delta_note = f"downgraded by {round(diff, 1)} pts because the asset is segmented behind access controls or has moderate business impact."
        else:
            delta_note = "closely aligns with base CVSS due to balanced environmental exposure."

        explanation = (
            f"Vulnerability CVSS {cvss} has a raw score of {raw_cvss_score}/100. "
            f"Factoring in topological reachability ({reachability_status}, weight={reach_weight}) "
            f"and asset criticality impact ({impact}/100), the true operational risk is {final_score}/100 ({delta_note})."
        )

        return final_score, factors, explanation

    @classmethod
    def calculate_path_risk(
        cls,
        path_nodes: list,
        graph_data: dict,
        target_impact: float
    ) -> Tuple[float, str]:
        """
        Calculates cumulative attack path risk according to:
        Risk(p) = Sum_{k in path} [CVSS_Score(k) * Accessibility_Weight(k)] * (Target_Impact / 100)
        """
        if not path_nodes:
            return 0.0, "Empty path."

        cumulative_vuln_exposure = 0.0
        hops_count = max(1, len(path_nodes) - 1)

        for node_id in path_nodes:
            node = graph_data.get(str(node_id), {})
            vulns = node.get("vulnerabilities", [])
            is_perim = node.get("is_perimeter", False)
            access_weight = 1.0 if is_perim else 0.75

            # Sum max or weighted vulns
            if vulns:
                top_cvss = max([v.get("cvss_v3_score", 0.0) for v in vulns], default=0.0)
                cumulative_vuln_exposure += (top_cvss * access_weight)

        impact_factor = max(0.1, min(1.0, target_impact / 100.0))
        # Path risk accumulates with exposure and target value
        raw_path_risk = (cumulative_vuln_exposure / hops_count * 10.0) * impact_factor
        final_path_risk = round(max(5.0, min(100.0, raw_path_risk)), 1)

        explanation = (
            f"Simulated {hops_count}-hop attack path traverses assets with cumulative vulnerability exposure {round(cumulative_vuln_exposure, 1)}. "
            f"Multiplying by destination crown jewel impact ({target_impact}/100) yields an aggregate path risk score of {final_path_risk}/100."
        )

        return final_path_risk, explanation
