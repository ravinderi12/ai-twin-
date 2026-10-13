import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Crosshair, Play, ShieldAlert, ArrowRight, CheckCircle2, AlertTriangle,
  History, Info, RefreshCw, Zap, Server
} from 'lucide-react';
import { CytoscapeGraph } from '../components/CytoscapeGraph';
import { SeverityBadge } from '../components/Badge';
import {
  getAssets, simulateAttackPath, getSimulationHistory, getCytoscapeGraph
} from '../services/api';
import { Asset, SimulatedPathResponse } from '../types';

export const AttackSimulation: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [assets, setAssets] = useState<Asset[]>([]);
  const [startAssetId, setStartAssetId] = useState<number | ''>('');
  const [targetAssetId, setTargetAssetId] = useState<number | ''>('');
  const [algorithm, setAlgorithm] = useState<'Dijkstra' | 'BFS'>('Dijkstra');
  const [simulating, setSimulating] = useState(false);
  const [result, setResult] = useState<SimulatedPathResponse | null>(null);
  const [graphData, setGraphData] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);

  useEffect(() => {
    const init = async () => {
      try {
        const [assetsData, graph, hist] = await Promise.all([
          getAssets(),
          getCytoscapeGraph(),
          getSimulationHistory()
        ]);
        setAssets(assetsData);
        setGraphData(graph);
        setHistory(hist);

        // Pre-select start and target
        const urlStart = searchParams.get('startId');
        if (urlStart) {
          setStartAssetId(parseInt(urlStart));
        } else {
          const perimeter = assetsData.find((a) => a.is_perimeter);
          if (perimeter) setStartAssetId(perimeter.id);
          else if (assetsData.length > 0) setStartAssetId(assetsData[0].id);
        }

        const critical = assetsData.find((a) => a.criticality === 'CRITICAL');
        if (critical) setTargetAssetId(critical.id);
        else if (assetsData.length > 1) setTargetAssetId(assetsData[assetsData.length - 1].id);
      } catch (err) {
        console.error("Failed to initialize simulator", err);
      }
    };
    init();
  }, [searchParams]);

  const handleRunSimulation = async () => {
    if (!startAssetId || !targetAssetId) return;
    try {
      setSimulating(true);
      const simResult = await simulateAttackPath({
        start_asset_id: Number(startAssetId),
        target_asset_id: Number(targetAssetId),
        algorithm
      });
      setResult(simResult);

      // Re-fetch graph with attack path nodes highlighted
      if (simResult.path_found) {
        const nodeIds = simResult.nodes.map((n) => n.id).join(',');
        const updatedGraph = await getCytoscapeGraph({ attack_path_nodes: nodeIds });
        setGraphData(updatedGraph);
      }

      const hist = await getSimulationHistory();
      setHistory(hist);
    } catch (err) {
      console.error("Simulation failed", err);
    } finally {
      setSimulating(false);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-lg font-bold text-white tracking-wide">
              OFFLINE ATTACK PATH SIMULATION
            </h1>
            <span className="text-xs px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 font-mono font-medium border border-amber-500/30">
              SAFE MATHEMATICAL MODEL
            </span>
          </div>
          <p className="text-xs text-slate-400">
            Traverses the digital twin topology via Dijkstra and BFS graph algorithms to evaluate multi-hop lateral compromise vectors
          </p>
        </div>
      </div>

      {/* Simulation Setup Control Panel */}
      <div className="bg-soc-card border border-soc-border rounded-xl p-5 shadow-sm space-y-4">
        <div className="flex items-center space-x-2 text-xs font-semibold text-slate-300 uppercase tracking-wider">
          <Crosshair className="w-4 h-4 text-cyan-400" />
          <span>Simulation Parameters</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Start Asset Dropdown */}
          <div className="space-y-1.5">
            <label className="text-xs text-slate-400 font-medium">Simulated Ingress Node (Source):</label>
            <select
              value={startAssetId}
              onChange={(e) => setStartAssetId(e.target.value ? Number(e.target.value) : '')}
              className="w-full bg-slate-900 border border-slate-700 text-white text-xs rounded-lg px-3 py-2.5 focus:border-cyan-500 outline-none"
            >
              <option value="">Select Ingress Asset</option>
              {assets.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.hostname || a.ip_address} ({a.ip_address}) {a.is_perimeter ? '[PERIMETER]' : ''}
                </option>
              ))}
            </select>
          </div>

          {/* Target Asset Dropdown */}
          <div className="space-y-1.5">
            <label className="text-xs text-slate-400 font-medium">Crown Jewel Target (Destination):</label>
            <select
              value={targetAssetId}
              onChange={(e) => setTargetAssetId(e.target.value ? Number(e.target.value) : '')}
              className="w-full bg-slate-900 border border-slate-700 text-white text-xs rounded-lg px-3 py-2.5 focus:border-cyan-500 outline-none"
            >
              <option value="">Select Target Crown Jewel</option>
              {assets.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.hostname || a.ip_address} ({a.ip_address}) [{a.criticality}]
                </option>
              ))}
            </select>
          </div>

          {/* Algorithm Toggle */}
          <div className="space-y-1.5">
            <label className="text-xs text-slate-400 font-medium">Pathfinding Algorithm:</label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setAlgorithm('Dijkstra')}
                className={`py-2 px-3 text-xs font-semibold rounded-lg border transition ${
                  algorithm === 'Dijkstra'
                    ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/50'
                    : 'bg-slate-900 text-slate-400 border-slate-700 hover:text-white'
                }`}
              >
                Dijkstra (Weighted)
              </button>
              <button
                type="button"
                onClick={() => setAlgorithm('BFS')}
                className={`py-2 px-3 text-xs font-semibold rounded-lg border transition ${
                  algorithm === 'BFS'
                    ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/50'
                    : 'bg-slate-900 text-slate-400 border-slate-700 hover:text-white'
                }`}
              >
                BFS (Shortest Hops)
              </button>
            </div>
          </div>
        </div>

        {/* Action Button & Safety Disclaimer */}
        <div className="flex flex-col sm:flex-row items-center justify-between pt-2 border-t border-slate-800 gap-3">
          <p className="text-[11px] text-slate-500 flex items-center space-x-1.5">
            <Info className="w-3.5 h-3.5 text-cyan-400" />
            <span>Safety Rule: Operates strictly within the mathematical graph. Zero packets or exploit payloads are sent.</span>
          </p>

          <button
            onClick={handleRunSimulation}
            disabled={simulating || !startAssetId || !targetAssetId}
            className="w-full sm:w-auto px-5 py-2.5 bg-cyan-600 hover:bg-cyan-500 active:scale-95 disabled:opacity-50 text-white text-xs font-bold rounded-lg shadow-sm flex items-center justify-center space-x-2 transition"
          >
            <Play className={`w-3.5 h-3.5 fill-current ${simulating ? 'animate-spin' : ''}`} />
            <span>{simulating ? 'Simulating Graph Traversal...' : 'Run Simulation'}</span>
          </button>
        </div>
      </div>

      {/* Simulation Result Area */}
      {result && (
        <div className="space-y-6">
          {/* Summary Metric Ribbon */}
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
            <div className="p-4 rounded-xl bg-soc-card border border-soc-border">
              <span className="text-xs text-slate-400 block">Path Status</span>
              <span className={`text-xl font-bold ${result.path_found ? 'text-red-400' : 'text-emerald-400'}`}>
                {result.path_found ? 'EXPOSURE PATH FOUND' : 'NO PATH REACHABLE'}
              </span>
            </div>
            <div className="p-4 rounded-xl bg-soc-card border border-soc-border">
              <span className="text-xs text-slate-400 block">Hop Distance</span>
              <span className="text-xl font-bold text-white font-mono">{result.hop_count} Lateral Hops</span>
            </div>
            <div className="p-4 rounded-xl bg-soc-card border border-soc-border">
              <span className="text-xs text-slate-400 block">Total Traversal Friction</span>
              <span className="text-xl font-bold text-white font-mono">{result.total_path_cost} pts</span>
            </div>
            <div className="p-4 rounded-xl bg-soc-card border border-soc-border">
              <span className="text-xs text-slate-400 block">Cumulative Path Risk</span>
              <span className="text-xl font-bold text-red-400 font-mono">{result.total_path_risk}/100</span>
            </div>
          </div>

          {/* Choke Point Callout */}
          {result.bottleneck_asset && (
            <div className="p-4 bg-pink-950/40 border border-pink-500/40 rounded-xl flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <AlertTriangle className="w-5 h-5 text-pink-400" />
                <div>
                  <h4 className="text-xs font-bold text-pink-300 uppercase">Topological Choke Point on Active Path</h4>
                  <p className="text-xs text-white font-semibold">
                    {result.bottleneck_asset.label} ({result.bottleneck_asset.ip_address})
                  </p>
                  <p className="text-[11px] text-slate-400">
                    Applying a security patch or firewall rule on this single asset eliminates the entire path trajectory.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Visual Path Display & Cytoscape Canvas */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Visual Cytoscape Canvas */}
            <div className="lg:col-span-2 bg-soc-card border border-soc-border rounded-xl p-4 h-96">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-xs font-semibold text-slate-300">Topology Path Highlight</h3>
                <span className="text-[11px] text-red-400 font-mono font-medium">Dashed Red Line = Potential Breach Route</span>
              </div>
              <div className="w-full h-[calc(100%-1.75rem)]">
                <CytoscapeGraph graphData={graphData} />
              </div>
            </div>

            {/* Path Narrative Explanation */}
            <div className="bg-soc-card border border-soc-border rounded-xl p-5 flex flex-col justify-between space-y-3">
              <div>
                <h3 className="text-xs font-bold text-white uppercase tracking-wider mb-2">Simulated Adversary Narrative</h3>
                <p className="text-xs text-slate-300 leading-relaxed">{result.explanation}</p>
              </div>
              <div className="pt-3 border-t border-slate-800 text-[11px] text-slate-400 space-y-1">
                <div className="font-semibold text-slate-300">MITRE ATT&CK Mapping:</div>
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {result.mitre_tactics.map((t, idx) => (
                    <span key={idx} className="px-2 py-0.5 rounded bg-slate-900 border border-slate-700 font-mono text-[10px] text-cyan-300">
                      {t.id}: {t.name} ({t.tactic})
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Step-by-Step Traversal Breakdown Table */}
          <div className="bg-soc-card border border-soc-border rounded-xl p-5 shadow-sm space-y-3">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider">
              Step-by-Step Lateral Movement Trajectory ({result.steps.length} Steps)
            </h3>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400">
                    <th className="pb-2 font-medium">Hop</th>
                    <th className="pb-2 font-medium">Source Asset</th>
                    <th className="pb-2 font-medium">Target Asset</th>
                    <th className="pb-2 font-medium">Port / Channel</th>
                    <th className="pb-2 font-medium">MITRE Technique</th>
                    <th className="pb-2 font-medium">Adversary Rationale</th>
                    <th className="pb-2 font-medium text-right">Hop Friction</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {result.steps.map((st) => (
                    <tr key={st.step_number} className="hover:bg-slate-800/30 transition">
                      <td className="py-3 font-mono font-bold text-cyan-400">#{st.step_number}</td>
                      <td className="py-3 font-medium text-white">{st.from_asset_label}</td>
                      <td className="py-3 font-medium text-red-300">{st.to_asset_label}</td>
                      <td className="py-3 font-mono text-slate-300">{st.port_used || 'any'} / {st.relationship_type}</td>
                      <td className="py-3">
                        <span className="font-mono text-amber-300 font-semibold">{st.mitre_technique_id}</span>
                        <span className="text-[10px] text-slate-400 block">{st.mitre_technique_name}</span>
                      </td>
                      <td className="py-3 text-slate-300 max-w-xs">{st.rationale}</td>
                      <td className="py-3 text-right font-mono text-slate-400">{st.hop_cost}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Historical Simulations Table */}
      {history.length > 0 && (
        <div className="bg-soc-card border border-soc-border rounded-xl p-5 shadow-sm space-y-3">
          <div className="flex items-center space-x-2 text-xs font-semibold text-slate-300 uppercase tracking-wider">
            <History className="w-4 h-4 text-cyan-400" />
            <span>Simulation History & Past Executions</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400">
                  <th className="pb-2 font-medium">Execution</th>
                  <th className="pb-2 font-medium">Algorithm</th>
                  <th className="pb-2 font-medium">Hops</th>
                  <th className="pb-2 font-medium">Path Risk</th>
                  <th className="pb-2 font-medium">Start Node</th>
                  <th className="pb-2 font-medium">Target Node</th>
                  <th className="pb-2 font-medium text-right">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {history.slice(0, 5).map((h) => (
                  <tr key={h.id} className="hover:bg-slate-800/30 transition">
                    <td className="py-2.5 font-medium text-white">{h.name}</td>
                    <td className="py-2.5 font-mono text-cyan-400">{h.algorithm_used}</td>
                    <td className="py-2.5 font-mono text-slate-300">{h.hop_count}</td>
                    <td className="py-2.5 font-mono font-semibold text-red-400">{h.total_path_risk}/100</td>
                    <td className="py-2.5 text-slate-400">{h.start_asset}</td>
                    <td className="py-2.5 text-slate-400">{h.target_asset}</td>
                    <td className="py-2.5 text-right font-mono text-slate-500">{h.created_at}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
