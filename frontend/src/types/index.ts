export interface ServicePort {
  id?: number;
  port: number;
  protocol: string;
  service_name?: string;
  product?: string;
  version?: string;
  state?: string;
  banner?: string;
  is_exposed?: boolean;
}

export interface VulnerabilityFinding {
  id: number;
  asset_id: number;
  assessment_id?: number;
  service_id?: number;
  cve_id: string;
  title: string;
  description?: string;
  cvss_v3_score: number;
  cvss_v3_severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'NONE';
  cvss_vector?: string;
  reference_url?: string;
  source: string;
  match_type: string;
  reachability_status: 'internet_reachable' | 'subnet_reachable' | 'isolated';
  raw_score: number;
  contextual_risk_score: number;
  risk_factors_json?: string;
  remediation_advice?: string;
  asset_hostname?: string;
  asset_ip?: string;
  service_info?: string;
  created_at: string;
}

export interface Asset {
  id: number;
  hostname?: string;
  ip_address: string;
  mac_address?: string;
  os_name?: string;
  os_version?: string;
  asset_type: 'server' | 'workstation' | 'gateway' | 'database' | 'firewall' | 'router';
  criticality: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  environment: 'dmz' | 'internal' | 'cloud' | 'management' | 'external';
  subnet?: string;
  is_isolated: boolean;
  is_perimeter: boolean;
  business_impact_score: number;
  notes?: string;
  created_at: string;
  updated_at: string;
  services_count: number;
  findings_count: number;
  calculated_risk: number;
  services?: ServicePort[];
  findings?: VulnerabilityFinding[];
}

export interface NetworkRelationship {
  id: number;
  source_asset_id: number;
  target_asset_id: number;
  relationship_type: string;
  protocol?: string;
  port?: number;
  is_inferred: boolean;
  confidence: string;
  weight: number;
  description?: string;
  created_at: string;
  source_hostname?: string;
  source_ip?: string;
  target_hostname?: string;
  target_ip?: string;
}

export interface Assessment {
  id: number;
  title: string;
  description?: string;
  assessment_type: string;
  target_scope?: string;
  status: string;
  total_assets_found: number;
  total_vulns_found: number;
  overall_risk_score: number;
  execution_duration_seconds: number;
  error_log?: string;
  created_at: string;
  completed_at?: string;
}

export interface PathStepDetail {
  step_number: number;
  from_asset_id: number;
  from_asset_label: string;
  to_asset_id: number;
  to_asset_label: string;
  relationship_type: string;
  port_used?: number;
  vulnerabilities_exploited: any[];
  hop_cost: number;
  cumulative_risk: number;
  mitre_technique_id: string;
  mitre_technique_name: string;
  mitre_tactic: string;
  rationale: string;
  uncertainty_notes?: string;
}

export interface SimulatedPathResponse {
  path_found: boolean;
  algorithm_used: string;
  hop_count: number;
  total_path_cost: number;
  total_path_risk: number;
  nodes: {
    id: string;
    label: string;
    ip: string;
    asset_type: string;
    is_perimeter: boolean;
    risk_score: number;
  }[];
  steps: PathStepDetail[];
  mitre_tactics: { id: string; name: string; tactic: string }[];
  bottleneck_asset?: {
    node_id: string;
    asset_id: number;
    label: string;
    ip_address: string;
    betweenness_score: number;
    description: string;
  };
  explanation: string;
}

export interface RemediationRecommendation {
  id: number;
  assessment_id?: number;
  finding_id?: number;
  asset_id: number;
  asset_hostname?: string;
  asset_ip?: string;
  title: string;
  action_description: string;
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  status: 'PLANNED' | 'IN_PROGRESS' | 'RESOLVED';
  risk_before: number;
  risk_after: number;
  risk_reduction_estimate: number;
  affected_attack_paths_count: number;
  expected_security_benefit?: string;
  notes?: string;
  created_at: string;
}

export interface RemediationScenarioResponse {
  scenario_name: string;
  baseline_risk_score: number;
  simulated_risk_score: number;
  risk_reduction_percentage: number;
  baseline_path_count: number;
  simulated_path_count: number;
  eliminated_paths_count: number;
  remediated_findings_count: number;
  choke_point_broken: boolean;
  choke_point_label?: string;
  before_path_steps: any[];
  after_path_steps: any[];
  comparison_summary: string;
}

export interface DashboardMetrics {
  total_assets: number;
  total_services: number;
  total_vulnerabilities: number;
  critical_findings: number;
  high_findings: number;
  medium_findings: number;
  low_findings: number;
  simulated_attack_paths_count: number;
  critical_assets_at_risk_count: number;
  overall_network_risk_score: number;
  choke_points: {
    node_id: string;
    asset_id: number;
    label: string;
    ip_address: string;
    betweenness_score: number;
    description: string;
  }[];
  highest_risk_assets: {
    id: number;
    hostname: string;
    ip_address: string;
    asset_type: string;
    criticality: string;
    risk_score: number;
    vulnerabilities_count: number;
  }[];
  top_remediation_actions: {
    id: number;
    title: string;
    priority: string;
    risk_reduction: number;
    status: string;
    affected_paths: number;
  }[];
  risk_history: {
    timestamp: string;
    risk_score: number;
    vulns_count: number;
  }[];
  last_assessment_activity?: {
    id: number;
    title: string;
    type: string;
    status: string;
    duration: number;
    created_at: string;
  };
}
