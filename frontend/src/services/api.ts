import axios from 'axios';
import {
  Asset, Assessment, VulnerabilityFinding, NetworkRelationship,
  DashboardMetrics, SimulatedPathResponse, RemediationRecommendation,
  RemediationScenarioResponse
} from '../types';

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Dashboard
export const getDashboardMetrics = async (): Promise<DashboardMetrics> => {
  const res = await api.get('/dashboard/metrics');
  return res.data;
};

export const loadDemoTopology = async (): Promise<any> => {
  const res = await api.post('/dashboard/load-demo');
  return res.data;
};

// Assets
export const getAssets = async (params?: { query?: string; criticality?: string; environment?: string; asset_type?: string }): Promise<Asset[]> => {
  const res = await api.get('/assets', { params });
  return res.data;
};

export const getAssetDetail = async (id: number): Promise<Asset> => {
  const res = await api.get(`/assets/${id}`);
  return res.data;
};

export const createAsset = async (payload: Partial<Asset>): Promise<Asset> => {
  const res = await api.post('/assets', payload);
  return res.data;
};

export const updateAsset = async (id: number, payload: Partial<Asset>): Promise<Asset> => {
  const res = await api.put(`/assets/${id}`, payload);
  return res.data;
};

export const deleteAsset = async (id: number): Promise<void> => {
  await api.delete(`/assets/${id}`);
};

// Assessments
export const getAssessments = async (): Promise<Assessment[]> => {
  const res = await api.get('/assessments');
  return res.data;
};

export const runLiveScan = async (payload: { target: string; scan_type: string; confirm_authorized: boolean }): Promise<Assessment> => {
  const res = await api.post('/assessments/live-scan', payload);
  return res.data;
};

export const uploadNmapXml = async (formData: FormData): Promise<Assessment> => {
  const res = await api.post('/ingestion/upload-nmap-xml', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return res.data;
};

export const importJsonTopology = async (payload: any): Promise<Assessment> => {
  const res = await api.post('/ingestion/import-json', payload);
  return res.data;
};

// Network Map & Cytoscape
export const getCytoscapeGraph = async (params?: { attack_path_nodes?: string; assessment_id?: number }): Promise<any> => {
  const res = await api.get('/network-map/cytoscape', { params });
  return res.data;
};

export const getRelationships = async (): Promise<NetworkRelationship[]> => {
  const res = await api.get('/network-map/relationships');
  return res.data;
};

export const createRelationship = async (payload: Partial<NetworkRelationship>): Promise<NetworkRelationship> => {
  const res = await api.post('/network-map/relationships', payload);
  return res.data;
};

export const deleteRelationship = async (id: number): Promise<void> => {
  await api.delete(`/network-map/relationships/${id}`);
};

// Attack Path Simulation
export const simulateAttackPath = async (payload: {
  start_asset_id: number;
  target_asset_id: number;
  algorithm: string;
}): Promise<SimulatedPathResponse> => {
  const res = await api.post('/attack-paths/simulate', payload);
  return res.data;
};

export const getSimulationHistory = async (): Promise<any[]> => {
  const res = await api.get('/attack-paths/history');
  return res.data;
};

// Vulnerabilities
export const getVulnerabilities = async (params?: {
  query?: string;
  severity?: string;
  asset_id?: number;
  reachability?: string;
}): Promise<VulnerabilityFinding[]> => {
  const res = await api.get('/vulnerabilities', { params });
  return res.data;
};

export const getVulnerabilityDetail = async (id: number): Promise<VulnerabilityFinding> => {
  const res = await api.get(`/vulnerabilities/${id}`);
  return res.data;
};

// CVE Intel
export const lookupCVE = async (cveId: string): Promise<any> => {
  const res = await api.get(`/cve/lookup/${cveId}`);
  return res.data;
};

export const searchCVEs = async (query: string): Promise<any> => {
  const res = await api.get('/cve/search', { params: { q: query } });
  return res.data;
};

// Remediation
export const getRemediationWorklist = async (): Promise<RemediationRecommendation[]> => {
  const res = await api.get('/remediation/worklist');
  return res.data;
};

export const updateRemediationStatus = async (id: number, status: string, notes?: string): Promise<RemediationRecommendation> => {
  const res = await api.put(`/remediation/${id}/status`, { status, notes });
  return res.data;
};

export const simulateWhatIfScenario = async (payload: {
  patch_finding_ids: number[];
  block_relationship_ids: number[];
  isolate_asset_ids: number[];
  start_asset_id?: number;
  target_asset_id?: number;
}): Promise<RemediationScenarioResponse> => {
  const res = await api.post('/remediation/simulate-what-if', payload);
  return res.data;
};

export const getRemediationScenarios = async (): Promise<any[]> => {
  const res = await api.get('/remediation/scenarios');
  return res.data;
};

// Report Exports
export const getCsvExportUrl = () => '/api/v1/reports/csv';
export const getPdfExportUrl = () => '/api/v1/reports/pdf';

export default api;
