import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Server, ShieldAlert, Crosshair, AlertTriangle, ShieldCheck,
  TrendingDown, ArrowUpRight, Zap, RefreshCw, Network
} from 'lucide-react';
import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid
} from 'recharts';
import { StatCard } from '../components/StatCard';
import { SeverityBadge, StatusBadge } from '../components/Badge';
import { getDashboardMetrics, loadDemoTopology } from '../services/api';
import { DashboardMetrics } from '../types';

export const OverviewDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchMetrics = async () => {
    try {
      setLoading(true);
      const data = await getDashboardMetrics();
      setMetrics(data);
    } catch (err) {
      console.error("Failed to load metrics", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center min-h-[500px]">
        <div className="flex flex-col items-center space-y-3">
          <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin" />
          <p className="text-sm text-slate-400 font-mono">Synthesizing Digital Twin Telemetry...</p>
        </div>
      </div>
    );
  }

  const m = metrics || {
    total_assets: 0,
    total_services: 0,
    total_vulnerabilities: 0,
    critical_findings: 0,
    high_findings: 0,
    medium_findings: 0,
    low_findings: 0,
    simulated_attack_paths_count: 0,
    critical_assets_at_risk_count: 0,
    overall_network_risk_score: 0,
    choke_points: [],
    highest_risk_assets: [],
    top_remediation_actions: [],
    risk_history: []
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Top Banner / Choke Point Highlight */}
      {m.choke_points && m.choke_points.length > 0 && (
        <div className="bg-gradient-to-r from-red-950/40 via-amber-950/30 to-slate-900 border border-red-500/30 rounded-xl p-4 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-sm">
          <div className="flex items-start space-x-3">
            <div className="p-2 rounded-lg bg-red-500/20 text-red-400 mt-0.5">
              <AlertTriangle className="w-5 h-5 animate-bounce" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xs font-bold text-red-400 uppercase tracking-wider">
                  Topological Choke Point Identified
                </span>
                <span className="text-[10px] bg-red-500/20 text-red-300 px-1.5 py-0.5 rounded font-mono">
                  CRITICAL BOTTLENECK
                </span>
              </div>
              <p className="text-sm font-semibold text-white mt-0.5">
                {m.choke_points[0].label} ({m.choke_points[0].ip_address}) connects multiple lateral paths
              </p>
              <p className="text-xs text-slate-400 mt-0.5">
                Betweenness centrality: {m.choke_points[0].betweenness_score}. Remediating vulnerabilities on this node neutralizes multi-hop paths to internal databases.
              </p>
            </div>
          </div>
          <Link
            to="/remediation"
            className="flex items-center space-x-2 px-3 py-2 bg-red-600 hover:bg-red-500 text-white text-xs font-semibold rounded-lg shadow-sm transition whitespace-nowrap active:scale-95"
          >
            <span>Simulate Fix on Choke Point</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      )}

      {/* KPI Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Discovered Assets"
          value={m.total_assets}
          subtitle={`${m.total_services} active exposed services`}
          icon={Server}
          variant="blue"
        />
        <StatCard
          title="Total Vulnerabilities"
          value={m.total_vulnerabilities}
          subtitle={`${m.critical_findings} Critical, ${m.high_findings} High`}
          icon={ShieldAlert}
          variant="red"
        />
        <StatCard
          title="Simulated Attack Paths"
          value={m.simulated_attack_paths_count}
          subtitle={`${m.critical_assets_at_risk_count} critical assets reachable`}
          icon={Crosshair}
          variant="amber"
        />
        <StatCard
          title="Context-Aware Risk Index"
          value={`${m.overall_network_risk_score}/100`}
          subtitle="Augmented by topological reachability"
          icon={ShieldCheck}
          variant={m.overall_network_risk_score >= 70 ? 'red' : 'cyan'}
        />
      </div>

      {/* Charts & Analytics Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Risk Trend Chart */}
        <div className="lg:col-span-2 bg-soc-card border border-soc-border rounded-xl p-5 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-semibold text-white">Contextual Risk Exposure Over Time</h2>
              <p className="text-xs text-slate-400">Calculated after topology-aware remediation iterations</p>
            </div>
            <span className="flex items-center space-x-1 text-xs text-emerald-400 font-mono bg-emerald-500/10 px-2 py-1 rounded border border-emerald-500/20">
              <TrendingDown className="w-3.5 h-3.5" />
              <span>Down -18.5%</span>
            </span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={m.risk_history}>
                <defs>
                  <linearGradient id="riskGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#06b6d4" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="timestamp" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} domain={[0, 100]} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
                <Area
                  type="monotone"
                  dataKey="risk_score"
                  name="Context Risk"
                  stroke="#06b6d4"
                  strokeWidth={2.5}
                  fillOpacity={1}
                  fill="url(#riskGradient)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Severity Distribution & Quick Actions */}
        <div className="bg-soc-card border border-soc-border rounded-xl p-5 shadow-sm flex flex-col justify-between space-y-4">
          <div>
            <h2 className="text-sm font-semibold text-white">Vulnerability Severity Distribution</h2>
            <p className="text-xs text-slate-400 mb-4">Breakdown across active enterprise inventory</p>

            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-red-400 font-medium">Critical (CVSS 9.0+)</span>
                  <span className="text-white font-mono">{m.critical_findings}</span>
                </div>
                <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-red-500 rounded-full"
                    style={{ width: `${m.total_vulnerabilities ? (m.critical_findings / m.total_vulnerabilities) * 100 : 0}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-amber-400 font-medium">High (CVSS 7.0-8.9)</span>
                  <span className="text-white font-mono">{m.high_findings}</span>
                </div>
                <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-amber-500 rounded-full"
                    style={{ width: `${m.total_vulnerabilities ? (m.high_findings / m.total_vulnerabilities) * 100 : 0}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-yellow-400 font-medium">Medium (CVSS 4.0-6.9)</span>
                  <span className="text-white font-mono">{m.medium_findings}</span>
                </div>
                <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-yellow-500 rounded-full"
                    style={{ width: `${m.total_vulnerabilities ? (m.medium_findings / m.total_vulnerabilities) * 100 : 0}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-blue-400 font-medium">Low (CVSS 0.1-3.9)</span>
                  <span className="text-white font-mono">{m.low_findings}</span>
                </div>
                <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-500 rounded-full"
                    style={{ width: `${m.total_vulnerabilities ? (m.low_findings / m.total_vulnerabilities) * 100 : 0}%` }}
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="pt-4 border-t border-slate-800 flex flex-col space-y-2">
            <Link
              to="/topology"
              className="flex items-center justify-center space-x-2 w-full py-2 bg-cyan-600/20 hover:bg-cyan-600/30 text-cyan-400 border border-cyan-500/30 rounded-lg text-xs font-semibold transition"
            >
              <Network className="w-4 h-4" />
              <span>Launch Interactive Digital Twin Map</span>
            </Link>
            <Link
              to="/simulation"
              className="flex items-center justify-center space-x-2 w-full py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-semibold transition"
            >
              <Crosshair className="w-4 h-4" />
              <span>Execute Attack Path Simulation</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Tables Row: Highest-Risk Assets & Top Remediations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Highest Risk Assets */}
        <div className="bg-soc-card border border-soc-border rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-semibold text-white">Highest-Risk Network Assets</h2>
              <p className="text-xs text-slate-400">Ranked by calculated operational exposure</p>
            </div>
            <Link to="/assets" className="text-xs text-cyan-400 hover:underline flex items-center space-x-1">
              <span>View All</span>
              <ArrowUpRight className="w-3 h-3" />
            </Link>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400">
                  <th className="pb-2 font-medium">Asset</th>
                  <th className="pb-2 font-medium">IP Address</th>
                  <th className="pb-2 font-medium">Criticality</th>
                  <th className="pb-2 font-medium text-right">Risk Score</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {m.highest_risk_assets.map((asset) => (
                  <tr key={asset.id} className="hover:bg-slate-800/30 transition">
                    <td className="py-2.5 font-medium text-white flex items-center space-x-2">
                      <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
                      <span className="truncate max-w-[140px]">{asset.hostname}</span>
                    </td>
                    <td className="py-2.5 text-slate-400 font-mono">{asset.ip_address}</td>
                    <td className="py-2.5">
                      <SeverityBadge severity={asset.criticality} size="sm" />
                    </td>
                    <td className="py-2.5 text-right font-mono font-semibold text-red-400">
                      {asset.risk_score}/100
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Top Recommended Remediation Roadmap */}
        <div className="bg-soc-card border border-soc-border rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-semibold text-white">Prioritized Remediation Roadmap</h2>
              <p className="text-xs text-slate-400">Targeting topological bottlenecks to maximize benefit</p>
            </div>
            <Link to="/remediation" className="text-xs text-cyan-400 hover:underline flex items-center space-x-1">
              <span>Worklist</span>
              <ArrowUpRight className="w-3 h-3" />
            </Link>
          </div>

          <div className="space-y-3">
            {m.top_remediation_actions.map((act) => (
              <div
                key={act.id}
                className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition flex items-center justify-between gap-3"
              >
                <div className="min-w-0">
                  <div className="flex items-center space-x-2 mb-1">
                    <SeverityBadge severity={act.priority} size="sm" />
                    <span className="text-xs font-semibold text-white truncate">{act.title}</span>
                  </div>
                  <p className="text-[11px] text-slate-400">
                    Reduces path exposure by <span className="text-emerald-400 font-semibold font-mono">+{act.risk_reduction} pts</span> • Affects {act.affected_paths} paths
                  </p>
                </div>
                <StatusBadge status={act.status} />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
