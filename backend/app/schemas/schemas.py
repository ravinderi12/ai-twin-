import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# --- User & Auth ---
class UserBase(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    role: str = "analyst"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    username: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str


# --- Service Ports ---
class ServicePortBase(BaseModel):
    port: int
    protocol: str = "tcp"
    service_name: Optional[str] = None
    product: Optional[str] = None
    version: Optional[str] = None
    banner: Optional[str] = None
    state: str = "open"
    is_exposed: bool = True

class ServicePortCreate(ServicePortBase):
    asset_id: int

class ServicePortResponse(ServicePortBase):
    id: int
    asset_id: int
    created_at: datetime.datetime

    class Config:
        from_attributes = True


# --- Network Relationships ---
class NetworkRelationshipBase(BaseModel):
    source_asset_id: int
    target_asset_id: int
    relationship_type: str = "can_connect"
    protocol: Optional[str] = "tcp"
    port: Optional[int] = None
    is_inferred: bool = False
    confidence: str = "HIGH"
    weight: float = 1.0
    description: Optional[str] = None

class NetworkRelationshipCreate(NetworkRelationshipBase):
    pass

class NetworkRelationshipResponse(NetworkRelationshipBase):
    id: int
    created_at: datetime.datetime
    source_hostname: Optional[str] = None
    source_ip: Optional[str] = None
    target_hostname: Optional[str] = None
    target_ip: Optional[str] = None

    class Config:
        from_attributes = True


# --- Vulnerabilities ---
class VulnerabilityFindingBase(BaseModel):
    cve_id: str
    title: str
    description: Optional[str] = None
    cvss_v3_score: float = 0.0
    cvss_v3_severity: str = "MEDIUM"
    cvss_vector: Optional[str] = None
    reference_url: Optional[str] = None
    source: str = "NVD"
    match_type: str = "version_heuristic"
    reachability_status: str = "subnet_reachable"
    raw_score: float = 0.0
    contextual_risk_score: float = 0.0
    risk_factors_json: Optional[str] = None
    remediation_advice: Optional[str] = None

class VulnerabilityFindingCreate(VulnerabilityFindingBase):
    asset_id: int
    assessment_id: Optional[int] = None
    service_id: Optional[int] = None

class VulnerabilityFindingResponse(VulnerabilityFindingBase):
    id: int
    asset_id: int
    assessment_id: Optional[int] = None
    service_id: Optional[int] = None
    asset_hostname: Optional[str] = None
    asset_ip: Optional[str] = None
    service_info: Optional[str] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True


# --- Assets ---
class AssetBase(BaseModel):
    hostname: Optional[str] = None
    ip_address: str
    mac_address: Optional[str] = None
    os_name: Optional[str] = None
    os_version: Optional[str] = None
    asset_type: str = "server"
    criticality: str = "MEDIUM"
    environment: str = "internal"
    subnet: Optional[str] = None
    is_isolated: bool = False
    is_perimeter: bool = False
    business_impact_score: float = 50.0
    notes: Optional[str] = None

class AssetCreate(AssetBase):
    pass

class AssetUpdate(BaseModel):
    hostname: Optional[str] = None
    os_name: Optional[str] = None
    os_version: Optional[str] = None
    asset_type: Optional[str] = None
    criticality: Optional[str] = None
    environment: Optional[str] = None
    subnet: Optional[str] = None
    is_isolated: Optional[bool] = None
    is_perimeter: Optional[bool] = None
    business_impact_score: Optional[float] = None
    notes: Optional[str] = None

class AssetResponse(AssetBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    services_count: int = 0
    findings_count: int = 0
    calculated_risk: float = 0.0

    class Config:
        from_attributes = True

class AssetDetailResponse(AssetResponse):
    services: List[ServicePortResponse] = []
    findings: List[VulnerabilityFindingResponse] = []


# --- Assessments ---
class AssessmentBase(BaseModel):
    title: str
    description: Optional[str] = None
    assessment_type: str = "simulated_demo"
    target_scope: Optional[str] = None

class AssessmentCreate(AssessmentBase):
    pass

class AssessmentResponse(AssessmentBase):
    id: int
    status: str
    total_assets_found: int
    total_vulns_found: int
    overall_risk_score: float
    execution_duration_seconds: float
    error_log: Optional[str] = None
    created_at: datetime.datetime
    completed_at: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True

class LiveScanRequest(BaseModel):
    target: str = Field(..., description="Authorized target IP or CIDR, e.g. 127.0.0.1 or 192.168.1.0/24")
    scan_type: str = Field("quick", description="quick, standard, or detailed")
    confirm_authorized: bool = Field(..., description="Must explicitly confirm operator authorization")


# --- Attack Path Simulation ---
class SimulatePathRequest(BaseModel):
    start_asset_id: int
    target_asset_id: int
    algorithm: str = "Dijkstra"  # BFS or Dijkstra
    assessment_id: Optional[int] = None

class PathStepDetail(BaseModel):
    step_number: int
    from_asset_id: int
    from_asset_label: str
    to_asset_id: int
    to_asset_label: str
    relationship_type: str
    port_used: Optional[int] = None
    vulnerabilities_exploited: List[Dict[str, Any]] = []
    hop_cost: float
    cumulative_risk: float
    mitre_technique_id: str
    mitre_technique_name: str
    mitre_tactic: str
    rationale: str
    uncertainty_notes: Optional[str] = None

class SimulatedPathResponse(BaseModel):
    path_found: bool
    algorithm_used: str
    hop_count: int
    total_path_cost: float
    total_path_risk: float
    nodes: List[Dict[str, Any]]
    steps: List[PathStepDetail]
    mitre_tactics: List[Dict[str, str]]
    bottleneck_asset: Optional[Dict[str, Any]] = None
    explanation: str


# --- Remediation & What-If ---
class RemediationRecommendationResponse(BaseModel):
    id: int
    assessment_id: Optional[int]
    finding_id: Optional[int]
    asset_id: int
    asset_hostname: Optional[str] = None
    asset_ip: Optional[str] = None
    title: str
    action_description: str
    priority: str
    status: str
    risk_before: float
    risk_after: float
    risk_reduction_estimate: float
    affected_attack_paths_count: int
    expected_security_benefit: Optional[str]
    notes: Optional[str]
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class RemediationStatusUpdate(BaseModel):
    status: str  # PLANNED, IN_PROGRESS, RESOLVED
    notes: Optional[str] = None

class SimulateRemediationRequest(BaseModel):
    patch_finding_ids: List[int] = []
    block_relationship_ids: List[int] = []
    isolate_asset_ids: List[int] = []
    start_asset_id: Optional[int] = None
    target_asset_id: Optional[int] = None

class RemediationScenarioResponse(BaseModel):
    scenario_name: str
    baseline_risk_score: float
    simulated_risk_score: float
    risk_reduction_percentage: float
    baseline_path_count: int
    simulated_path_count: int
    eliminated_paths_count: int
    remediated_findings_count: int
    choke_point_broken: bool
    choke_point_label: Optional[str] = None
    before_path_steps: List[Any] = []
    after_path_steps: List[Any] = []
    comparison_summary: str


# --- CVE Intelligence ---
class CVESearchQuery(BaseModel):
    query: str
    source: str = "auto"  # auto, cache, nvd


# --- Cytoscape Graph Data ---
class GraphNodeData(BaseModel):
    id: str
    label: str
    ip: str
    asset_type: str
    criticality: str
    environment: str
    subnet: Optional[str] = None
    risk_score: float
    is_perimeter: bool
    is_isolated: bool
    vulnerabilities_count: int
    services_count: int
    is_choke_point: bool = False

class GraphEdgeData(BaseModel):
    id: str
    source: str
    target: str
    label: str
    relationship_type: str
    port: Optional[int] = None
    weight: float
    confidence: str
    is_inferred: bool
    is_attack_path: bool = False

class CytoscapeGraphResponse(BaseModel):
    nodes: List[Dict[str, GraphNodeData]]
    edges: List[Dict[str, GraphEdgeData]]
    total_nodes: int
    total_edges: int
    topology_name: str


# --- Dashboard KPIs ---
class DashboardMetricsResponse(BaseModel):
    total_assets: int
    total_services: int
    total_vulnerabilities: int
    critical_findings: int
    high_findings: int
    medium_findings: int
    low_findings: int
    simulated_attack_paths_count: int
    critical_assets_at_risk_count: int
    overall_network_risk_score: float
    choke_points: List[Dict[str, Any]]
    highest_risk_assets: List[Dict[str, Any]]
    top_remediation_actions: List[Dict[str, Any]]
    risk_history: List[Dict[str, Any]]
    last_assessment_activity: Optional[Dict[str, Any]] = None
