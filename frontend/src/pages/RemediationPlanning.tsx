import React, { useEffect, useState } from 'react';
import {
  Wrench, ShieldCheck, Play, ArrowRight, CheckCircle2, AlertTriangle,
  RefreshCw, TrendingDown, Layers, Filter
} from 'lucide-react';
import { SeverityBadge, StatusBadge } from '../components/Badge';
import {
  getRemediationWorklist, updateRemediationStatus, simulateWhatIfScenario,
  getRemediationScenarios, getAssets
} from '../services/api';
import { RemediationRecommendation, RemediationScenarioResponse, Asset } from '../types';

export const RemediationPlanning: React.FC = () => {
  const [worklist, setWorklist] = useState<RemediationRecommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedFindingIds, setSelectedFindingIds] = useState<number[]>([]);
  const [simulating, setSimulating] = useState(false);
  const [scenarioResult, setScenarioResult] = useState<RemediationScenarioResponse | null>(null);
  const [scenarios, setScenarios] = useState<any[]>([]);
  const [updatingId, setUpdatingId] = useState<number | null>(null);

  const fetchWorklist = async () => {
    try {
      setLoading(true);
      const [w, sc] = await Promise.all([
        getRemediationWorklist(),
        getRemediationScenarios()
      ]);
      setWorklist(w);
      setScenarios(sc);

      // Auto-select the top recommendation for what-if demonstration
      if (w.length > 0 && w[0].finding_id) {
        setSelectedFindingIds([w[0].finding_id]);
      }
    } catch (err) {
      console.error("Failed to load remediation worklist", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWorklist();
  }, []);

  const handleStatusChange = async (id: number, newStatus: string) => {
    try {
      setUpdatingId(id);
      await updateRemediationStatus(id, newStatus);
      const updated = await getRemediationWorklist();
      setWorklist(updated);
    } catch (err) {
      console.error("Failed to update status", err);
    } finally {
      setUpdatingId(null);
    }
  };

  const handleToggleSelectFinding = (findingId: number) => {
    setSelectedFindingIds((prev) =>
      prev.includes(findingId) ? prev.filter((id) => id !== findingId) : [...prev, findingId]
    );
  };

  const handleRunWhatIfSimulation = async () => {
    if (selectedFindingIds.length === 0) return;
    try {
      setSimulating(true);
      const res = await simulateWhatIfScenario({
        patch_finding_ids: selectedFindingIds,
        block_relationship_ids: [],
        isolate_asset_ids: []
      });
      setScenarioResult(res);
      const sc = await getRemediationScenarios();
      setScenarios(sc);
    } catch (err) {
      console.error("What-if simulation error", err);
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
              REMEDIATION PRIORITIZATION & WHAT-IF SIMULATION
            </h1>
            <span className="text-xs px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-mono font-medium border border-emerald-500/30">
              OPTIMIZED ROADMAP
            </span>
          </div>
          <p className="text-xs text-slate-400">
            Algorithmic patch ranking targeting network choke points to maximize risk reduction across simulated attack paths
          </p>
        </div>

        <button
          onClick={fetchWorklist}
          className="flex items-center space-x-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded-lg border border-slate-700 transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 text-cyan-400 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Worklist</span>
        </button>
      </div>

      {/* Interactive What-If Simulation Sandbox Card */}
      <div className="bg-gradient-to-r from-slate-900 via-soc-card to-slate-900 border border-cyan-500/30 rounded-xl p-5 shadow-lg space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="p-1.5 bg-cyan-500/10 text-cyan-400 rounded-lg">
              <Play className="w-4 h-4 fill-current" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-white">Interactive "What-If" Patch Simulation Sandbox</h2>
              <p className="text-xs text-slate-400">
                Select patches below and evaluate their impact on a virtual clone of the digital twin with zero production downtime.
              </p>
            </div>
          </div>

          <button
            onClick={handleRunWhatIfSimulation}
            disabled={simulating || selectedFindingIds.length === 0}
            className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 active:scale-95 disabled:opacity-50 text-white text-xs font-bold rounded-lg shadow-sm flex items-center space-x-2 transition"
          >
            <Play className={`w-3.5 h-3.5 fill-current ${simulating ? 'animate-spin' : ''}`} />
            <span>{simulating ? 'Calculating Delta...' : `Simulate (${selectedFindingIds.length}) Proposed Fixes`}</span>
          </button>
        </div>

        {/* What-If Comparative Results Callout */}
        {scenarioResult && (
          <div className="bg-slate-950/80 border border-cyan-500/40 rounded-xl p-4 space-y-3 animate-fade-in">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
              <div>
                <span className="text-[10px] text-cyan-400 font-mono uppercase font-bold tracking-wider">
                  SCENARIO OUTCOME
                </span>
                <h3 className="text-sm font-bold text-white">
                  {scenarioResult.comparison_summary}
                </h3>
              </div>
              <div className="flex items-center space-x-3 text-right">
                <div>
                  <span className="text-[10px] text-slate-400 block">RISK REDUCTION</span>
                  <span className="text-lg font-bold font-mono text-emerald-400">
                    -{scenarioResult.risk_reduction_percentage}%
                  </span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 block">PATHS SEVERED</span>
                  <span className="text-lg font-bold font-mono text-cyan-400">
                    {scenarioResult.eliminated_paths_count}
                  </span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800">
                <span className="text-slate-400 font-semibold block mb-1">Baseline State (Before Fix):</span>
                <p className="text-slate-300 font-mono">
                  Path Risk: <strong className="text-red-400">{scenarioResult.baseline_risk_score}</strong> | Active Routes: <strong className="text-white">{scenarioResult.baseline_path_count}</strong>
                </p>
                <p className="text-[11px] text-slate-500 mt-1">Multi-hop route remains unhindered through external DMZ.</p>
              </div>

              <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800">
                <span className="text-slate-400 font-semibold block mb-1">Simulated State (After Virtual Patch):</span>
                <p className="text-slate-300 font-mono">
                  Path Risk: <strong className="text-emerald-400">{scenarioResult.simulated_risk_score}</strong> | Remaining Routes: <strong className="text-white">{scenarioResult.simulated_path_count}</strong>
                </p>
                <p className="text-[11px] text-emerald-400/80 mt-1">
                  {scenarioResult.choke_point_broken ? "Critical lateral movement choke point successfully neutralized!" : "Alternative lateral routes constrained."}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Remediation Worklist Table */}
      <div className="bg-soc-card border border-soc-border rounded-xl p-5 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2 text-xs font-semibold text-slate-300 uppercase tracking-wider">
            <Wrench className="w-4 h-4 text-cyan-400" />
            <span>Ranked Remediation Actions ({worklist.length})</span>
          </div>
          <span className="text-xs text-slate-400">
            Check boxes to include in the what-if simulation sandbox
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400">
                <th className="pb-2 w-8">Sim</th>
                <th className="pb-2 font-medium">Priority</th>
                <th className="pb-2 font-medium">Remediation Action</th>
                <th className="pb-2 font-medium">Target Host</th>
                <th className="pb-2 font-medium">Risk Reduction</th>
                <th className="pb-2 font-medium">Paths Affected</th>
                <th className="pb-2 font-medium text-center">Lifecycle Status</th>
                <th className="pb-2 font-medium text-right">Update Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {worklist.map((item) => {
                const isSelected = item.finding_id ? selectedFindingIds.includes(item.finding_id) : false;
                return (
                  <tr key={item.id} className={`hover:bg-slate-800/30 transition ${isSelected ? 'bg-cyan-950/20' : ''}`}>
                    <td className="py-3">
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => item.finding_id && handleToggleSelectFinding(item.finding_id)}
                        className="rounded border-slate-700 bg-slate-900 text-cyan-500 focus:ring-0 cursor-pointer"
                      />
                    </td>
                    <td className="py-3">
                      <SeverityBadge severity={item.priority} size="sm" />
                    </td>
                    <td className="py-3 max-w-sm">
                      <span className="font-semibold text-white block truncate">{item.title}</span>
                      <span className="text-[11px] text-slate-400 line-clamp-1">{item.action_description}</span>
                    </td>
                    <td className="py-3">
                      <span className="text-slate-200 block font-medium">{item.asset_hostname || 'N/A'}</span>
                      <span className="text-slate-500 font-mono text-[10px]">{item.asset_ip}</span>
                    </td>
                    <td className="py-3 font-mono font-semibold text-emerald-400">
                      +{item.risk_reduction_estimate.toFixed(1)} pts
                    </td>
                    <td className="py-3 font-mono text-slate-300">
                      {item.affected_attack_paths_count} path(s)
                    </td>
                    <td className="py-3 text-center">
                      <StatusBadge status={item.status} />
                    </td>
                    <td className="py-3 text-right">
                      <select
                        value={item.status}
                        onChange={(e) => handleStatusChange(item.id, e.target.value)}
                        disabled={updatingId === item.id}
                        className="bg-slate-900 border border-slate-700 text-slate-300 text-[11px] rounded px-2 py-1 focus:ring-1 focus:ring-cyan-500 outline-none"
                      >
                        <option value="PLANNED">Planned</option>
                        <option value="IN_PROGRESS">In Progress</option>
                        <option value="RESOLVED">Resolved</option>
                      </select>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
