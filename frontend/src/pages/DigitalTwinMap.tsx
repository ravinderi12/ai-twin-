import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Network, Server, Shield, Crosshair, X, ExternalLink, RefreshCw, Layers } from 'lucide-react';
import { CytoscapeGraph } from '../components/CytoscapeGraph';
import { SeverityBadge } from '../components/Badge';
import { getCytoscapeGraph, getAssetDetail } from '../services/api';
import { Asset } from '../types';

export const DigitalTwinMap: React.FC = () => {
  const [graphData, setGraphData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedNodeData, setSelectedNodeData] = useState<any>(null);
  const [assetDetail, setAssetDetail] = useState<Asset | null>(null);
  const [loadingDetail, setLoadingDetail] = useState<boolean>(false);
  const navigate = useNavigate();

  const loadGraph = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getCytoscapeGraph();
      setGraphData(data);
    } catch (err: any) {
      console.error("Failed to load graph data", err);
      const msg = err?.response?.data?.detail || err?.message || "Failed to connect to backend server on port 8000";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadGraph();
  }, []);

  // When a node is selected in Cytoscape, fetch complete asset details
  const handleNodeSelect = async (nodeData: any) => {
    setSelectedNodeData(nodeData);
    if (nodeData && nodeData.id) {
      try {
        setLoadingDetail(true);
        const detail = await getAssetDetail(parseInt(nodeData.id));
        setAssetDetail(detail);
      } catch (err) {
        console.error("Failed to fetch asset detail", err);
      } finally {
        setLoadingDetail(false);
      }
    } else {
      setAssetDetail(null);
    }
  };

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col p-6 space-y-4">
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-lg font-bold text-white tracking-wide">
              DIGITAL TWIN TOPOLOGY EXPLORER
            </h1>
            <span className="text-xs px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-400 font-mono font-medium border border-cyan-500/30">
              GRAPH ACTIVE
            </span>
          </div>
          <p className="text-xs text-slate-400">
            Interactive mathematical network graph modeling lateral movement pathways and access relationships
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="text-xs font-mono text-slate-400 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg flex items-center space-x-3">
            <span>Nodes: <strong className="text-white">{graphData?.total_nodes || 0}</strong></span>
            <span className="text-slate-600">|</span>
            <span>Edges: <strong className="text-white">{graphData?.total_edges || 0}</strong></span>
          </div>
          <button
            onClick={loadGraph}
            className="flex items-center space-x-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded-lg border border-slate-700 transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-cyan-400 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh Model</span>
          </button>
        </div>
      </div>

      {/* Main Graph Area with Slide-over Inspector */}
      <div className="flex-1 relative flex gap-4 min-h-0">
        {/* Cytoscape Canvas */}
        <div className="flex-1 h-full min-h-[450px]">
          {loading ? (
            <div className="w-full h-full bg-[#070b14] rounded-xl border border-soc-border flex items-center justify-center">
              <div className="flex flex-col items-center space-y-2">
                <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin" />
                <span className="text-xs text-slate-400 font-mono">Building Mathematical Adjacency Graph...</span>
              </div>
            </div>
          ) : error && !graphData ? (
            <div className="w-full h-full bg-[#070b14] rounded-xl border border-soc-border flex items-center justify-center p-6">
              <div className="flex flex-col items-center text-center space-y-3 max-w-md">
                <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-full text-red-400">
                  <Shield className="w-8 h-8" />
                </div>
                <h3 className="text-sm font-bold text-white">Digital Twin Graph Unavailable</h3>
                <p className="text-xs text-slate-400 font-mono">{error}</p>
                <button
                  onClick={loadGraph}
                  className="mt-2 px-4 py-2 bg-cyan-600 hover:bg-cyan-500 active:scale-95 text-white text-xs font-semibold rounded-lg flex items-center space-x-2 transition"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                  <span>Retry Connection</span>
                </button>
              </div>
            </div>
          ) : (
            <CytoscapeGraph
              graphData={graphData}
              onSelectNode={handleNodeSelect}
              selectedNodeId={selectedNodeData?.id}
            />
          )}
        </div>

        {/* Right Inspection Drawer */}
        {selectedNodeData && (
          <div className="w-96 bg-soc-card border border-soc-border rounded-xl p-5 overflow-y-auto flex flex-col justify-between shadow-2xl animate-fade-in z-20">
            <div className="space-y-5">
              {/* Drawer Header */}
              <div className="flex items-start justify-between border-b border-slate-800 pb-3">
                <div className="flex items-center space-x-2">
                  <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400">
                    <Server className="w-5 h-5" />
                  </div>
                  <div>
                    <h2 className="text-sm font-bold text-white truncate max-w-[200px]">
                      {selectedNodeData.label}
                    </h2>
                    <p className="text-xs text-slate-400 font-mono">{selectedNodeData.ip}</p>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedNodeData(null)}
                  className="p-1 hover:bg-slate-800 text-slate-400 hover:text-white rounded"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Status and Risk Metrics */}
              <div className="space-y-3">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-400">Contextual Exposure:</span>
                  <span className="font-mono font-bold text-red-400 text-sm">
                    {selectedNodeData.risk_score}/100
                  </span>
                </div>
                <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-red-500 rounded-full"
                    style={{ width: `${selectedNodeData.risk_score}%` }}
                  />
                </div>

                <div className="grid grid-cols-2 gap-2 text-xs pt-1">
                  <div className="bg-slate-900/60 p-2 rounded border border-slate-800">
                    <span className="text-slate-500 block text-[10px]">CRITICALITY</span>
                    <SeverityBadge severity={selectedNodeData.criticality} size="sm" />
                  </div>
                  <div className="bg-slate-900/60 p-2 rounded border border-slate-800">
                    <span className="text-slate-500 block text-[10px]">ENVIRONMENT</span>
                    <span className="text-white font-mono uppercase text-xs">{selectedNodeData.environment}</span>
                  </div>
                  <div className="bg-slate-900/60 p-2 rounded border border-slate-800">
                    <span className="text-slate-500 block text-[10px]">SUBNET</span>
                    <span className="text-slate-300 font-mono text-xs">{selectedNodeData.subnet}</span>
                  </div>
                  <div className="bg-slate-900/60 p-2 rounded border border-slate-800">
                    <span className="text-slate-500 block text-[10px]">PERIMETER</span>
                    <span className={`text-xs font-semibold ${selectedNodeData.is_perimeter ? 'text-amber-400' : 'text-slate-400'}`}>
                      {selectedNodeData.is_perimeter ? 'EXPOSED' : 'INTERNAL'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Open Services */}
              <div className="space-y-2">
                <h3 className="text-xs font-bold text-slate-300 tracking-wider uppercase">
                  Open Services & Ports ({assetDetail?.services?.length || 0})
                </h3>
                <div className="space-y-1.5 max-h-36 overflow-y-auto">
                  {assetDetail?.services && assetDetail.services.length > 0 ? (
                    assetDetail.services.map((s, idx) => (
                      <div key={idx} className="p-2 rounded bg-slate-900/70 border border-slate-800 text-xs flex justify-between items-center">
                        <span className="font-mono text-cyan-400 font-semibold">{s.port}/{s.protocol}</span>
                        <span className="text-slate-300">{s.product || s.service_name || 'unknown'} {s.version || ''}</span>
                      </div>
                    ))
                  ) : (
                    <p className="text-xs text-slate-500">No open ports recorded</p>
                  )}
                </div>
              </div>

              {/* Vulnerability Findings */}
              <div className="space-y-2">
                <h3 className="text-xs font-bold text-slate-300 tracking-wider uppercase">
                  Vulnerability Findings ({assetDetail?.findings?.length || 0})
                </h3>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {assetDetail?.findings && assetDetail.findings.length > 0 ? (
                    assetDetail.findings.map((f) => (
                      <div key={f.id} className="p-2.5 rounded bg-slate-900/80 border border-slate-800 space-y-1">
                        <div className="flex items-center justify-between">
                          <span className="font-mono font-bold text-xs text-red-400">{f.cve_id}</span>
                          <SeverityBadge severity={f.cvss_v3_severity} size="sm" />
                        </div>
                        <p className="text-[11px] text-slate-300 font-medium line-clamp-1">{f.title}</p>
                        <div className="flex items-center justify-between text-[10px] text-slate-400 pt-1">
                          <span>Raw CVSS: {f.cvss_v3_score}</span>
                          <span className="text-cyan-400 font-mono">Context Risk: {f.contextual_risk_score}</span>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-xs text-slate-500">No active vulnerability findings on this node</p>
                  )}
                </div>
              </div>
            </div>

            {/* Quick Simulation Link */}
            <div className="pt-4 border-t border-slate-800">
              <button
                onClick={() => navigate(`/simulation?startId=${selectedNodeData.id}`)}
                className="w-full flex items-center justify-center space-x-2 py-2.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-semibold shadow-sm transition active:scale-95"
              >
                <Crosshair className="w-4 h-4" />
                <span>Simulate Attack Path from This Node</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
