import React, { useEffect, useState } from 'react';
import {
  Server, Plus, Search, Filter, Trash2, Eye, RefreshCw, X, Shield, Globe
} from 'lucide-react';
import { SeverityBadge } from '../components/Badge';
import { getAssets, createAsset, deleteAsset, getAssetDetail } from '../services/api';
import { Asset } from '../types';

export const AssetInventory: React.FC = () => {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filterCriticality, setFilterCriticality] = useState('');
  const [filterEnv, setFilterEnv] = useState('');
  const [selectedAsset, setSelectedAsset] = useState<Asset | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);

  // Form State for new asset
  const [newHostname, setNewHostname] = useState('');
  const [newIp, setNewIp] = useState('');
  const [newType, setNewType] = useState('server');
  const [newCriticality, setNewCriticality] = useState('MEDIUM');
  const [newEnvironment, setNewEnvironment] = useState('internal');
  const [newSubnet, setNewSubnet] = useState('192.168.1.0/24');
  const [newPerimeter, setNewPerimeter] = useState(false);
  const [newImpact, setNewImpact] = useState(50);
  const [formError, setFormError] = useState<string | null>(null);

  const fetchAssetsList = async () => {
    try {
      setLoading(true);
      const data = await getAssets({
        query: search || undefined,
        criticality: filterCriticality || undefined,
        environment: filterEnv || undefined
      });
      setAssets(data);
    } catch (err) {
      console.error("Failed to load assets", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAssetsList();
  }, [search, filterCriticality, filterEnv]);

  const handleDelete = async (id: number) => {
    if (!window.confirm("Are you sure you want to remove this asset from the digital twin model?")) return;
    try {
      await deleteAsset(id);
      fetchAssetsList();
      if (selectedAsset?.id === id) setSelectedAsset(null);
    } catch (err) {
      alert("Failed to delete asset");
    }
  };

  const handleSelectAsset = async (id: number) => {
    try {
      const full = await getAssetDetail(id);
      setSelectedAsset(full);
    } catch (err) {
      console.error("Failed to fetch asset detail", err);
    }
  };

  const handleCreateAsset = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    try {
      await createAsset({
        hostname: newHostname || undefined,
        ip_address: newIp,
        asset_type: newType as any,
        criticality: newCriticality as any,
        environment: newEnvironment as any,
        subnet: newSubnet || undefined,
        is_perimeter: newPerimeter,
        business_impact_score: Number(newImpact)
      });
      setShowAddModal(false);
      // Reset form
      setNewHostname('');
      setNewIp('');
      fetchAssetsList();
    } catch (err: any) {
      setFormError(err.response?.data?.detail || "Failed to create asset. Check if IP address is duplicate.");
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-bold text-white tracking-wide">
            ENTERPRISE ASSET INVENTORY
          </h1>
          <p className="text-xs text-slate-400">
            Discovered nodes, exposed services, and vulnerability annotations across network subnets
          </p>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center space-x-2 px-3.5 py-2 bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold rounded-lg shadow-sm transition active:scale-95"
        >
          <Plus className="w-4 h-4" />
          <span>Add Asset</span>
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-soc-card border border-soc-border rounded-xl p-4 flex flex-wrap items-center justify-between gap-3 shadow-sm">
        <div className="relative flex-1 min-w-[240px]">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search hostname, IP address, OS..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 text-white text-xs rounded-lg pl-9 pr-3 py-2 focus:border-cyan-500 outline-none"
          />
        </div>

        <div className="flex items-center space-x-3">
          <select
            value={filterCriticality}
            onChange={(e) => setFilterCriticality(e.target.value)}
            className="bg-slate-900 border border-slate-700 text-slate-300 text-xs rounded-lg px-3 py-2 outline-none focus:border-cyan-500"
          >
            <option value="">All Criticalities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>

          <select
            value={filterEnv}
            onChange={(e) => setFilterEnv(e.target.value)}
            className="bg-slate-900 border border-slate-700 text-slate-300 text-xs rounded-lg px-3 py-2 outline-none focus:border-cyan-500"
          >
            <option value="">All Environments</option>
            <option value="dmz">DMZ</option>
            <option value="internal">Internal</option>
            <option value="external">External</option>
            <option value="management">Management</option>
          </select>
        </div>
      </div>

      {/* Main Asset Table */}
      <div className="bg-soc-card border border-soc-border rounded-xl p-5 shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400">
                <th className="pb-3 font-medium">Hostname / IP</th>
                <th className="pb-3 font-medium">Asset Type</th>
                <th className="pb-3 font-medium">Criticality</th>
                <th className="pb-3 font-medium">Environment</th>
                <th className="pb-3 font-medium">Subnet</th>
                <th className="pb-3 font-medium">Services</th>
                <th className="pb-3 font-medium text-right">Risk Score</th>
                <th className="pb-3 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {assets.map((a) => (
                <tr key={a.id} className="hover:bg-slate-800/30 transition">
                  <td className="py-3">
                    <span className="font-semibold text-white block">{a.hostname || 'N/A'}</span>
                    <span className="text-slate-400 font-mono text-[11px]">{a.ip_address}</span>
                  </td>
                  <td className="py-3 capitalize text-slate-300">{a.asset_type}</td>
                  <td className="py-3">
                    <SeverityBadge severity={a.criticality} size="sm" />
                  </td>
                  <td className="py-3 uppercase font-mono text-[11px] text-slate-400">
                    <span className={`px-2 py-0.5 rounded ${a.environment === 'dmz' ? 'bg-amber-500/10 text-amber-400' : 'bg-slate-800 text-slate-300'}`}>
                      {a.environment}
                    </span>
                  </td>
                  <td className="py-3 font-mono text-slate-400">{a.subnet || 'Unknown'}</td>
                  <td className="py-3 font-mono text-slate-300">{a.services_count} port(s)</td>
                  <td className="py-3 text-right font-mono font-semibold text-red-400">
                    {a.calculated_risk ? `${a.calculated_risk}/100` : '0/100'}
                  </td>
                  <td className="py-3 text-right">
                    <div className="flex items-center justify-end space-x-2">
                      <button
                        onClick={() => handleSelectAsset(a.id)}
                        className="p-1 hover:bg-slate-800 text-cyan-400 rounded"
                        title="View Asset Details"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(a.id)}
                        className="p-1 hover:bg-slate-800 text-red-400 rounded"
                        title="Delete Asset"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Asset Details Slide-Over Drawer */}
      {selectedAsset && (
        <div className="fixed inset-y-0 right-0 w-96 bg-soc-card border-l border-soc-border shadow-2xl p-6 overflow-y-auto z-50 space-y-5 animate-slide-left">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <h2 className="text-sm font-bold text-white">{selectedAsset.hostname}</h2>
              <p className="text-xs text-slate-400 font-mono">{selectedAsset.ip_address}</p>
            </div>
            <button
              onClick={() => setSelectedAsset(null)}
              className="p-1 hover:bg-slate-800 text-slate-400 hover:text-white rounded"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          <div className="space-y-4 text-xs">
            <div className="grid grid-cols-2 gap-2">
              <div className="bg-slate-900 p-2.5 rounded border border-slate-800">
                <span className="text-slate-500 block text-[10px]">CRITICALITY</span>
                <SeverityBadge severity={selectedAsset.criticality} size="sm" />
              </div>
              <div className="bg-slate-900 p-2.5 rounded border border-slate-800">
                <span className="text-slate-500 block text-[10px]">ENVIRONMENT</span>
                <span className="text-white font-mono uppercase">{selectedAsset.environment}</span>
              </div>
            </div>

            <div>
              <h3 className="font-semibold text-slate-300 uppercase tracking-wider mb-2">
                Open Services ({selectedAsset.services?.length || 0})
              </h3>
              <div className="space-y-1.5">
                {selectedAsset.services?.map((s) => (
                  <div key={s.id} className="p-2 bg-slate-900 rounded border border-slate-800 flex justify-between">
                    <span className="font-mono text-cyan-400">{s.port}/{s.protocol}</span>
                    <span className="text-slate-300">{s.product} {s.version}</span>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h3 className="font-semibold text-slate-300 uppercase tracking-wider mb-2">
                Vulnerabilities ({selectedAsset.findings?.length || 0})
              </h3>
              <div className="space-y-2">
                {selectedAsset.findings?.map((f) => (
                  <div key={f.id} className="p-2.5 bg-slate-900 rounded border border-slate-800 space-y-1">
                    <div className="flex justify-between">
                      <span className="font-mono text-red-400 font-bold">{f.cve_id}</span>
                      <SeverityBadge severity={f.cvss_v3_severity} size="sm" />
                    </div>
                    <p className="text-slate-300 text-[11px]">{f.title}</p>
                    <p className="text-[10px] text-cyan-400 font-mono">Context Risk: {f.contextual_risk_score}/100</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Add Asset Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-soc-card border border-soc-border rounded-xl p-6 w-full max-w-md shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-sm font-bold text-white">Add New Network Asset</h3>
              <button onClick={() => setShowAddModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-4 h-4" />
              </button>
            </div>

            {formError && (
              <div className="p-2.5 rounded bg-red-950/60 border border-red-500/40 text-red-300 text-xs">
                {formError}
              </div>
            )}

            <form onSubmit={handleCreateAsset} className="space-y-3 text-xs">
              <div>
                <label className="text-slate-400 block mb-1">Hostname:</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. app-srv-02.internal.corp"
                  value={newHostname}
                  onChange={(e) => setNewHostname(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 text-white rounded px-3 py-2 outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label className="text-slate-400 block mb-1">IPv4 Address:</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. 192.168.2.25"
                  value={newIp}
                  onChange={(e) => setNewIp(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 text-white rounded px-3 py-2 outline-none focus:border-cyan-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-slate-400 block mb-1">Asset Type:</label>
                  <select
                    value={newType}
                    onChange={(e) => setNewType(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 text-white rounded px-2.5 py-2 outline-none focus:border-cyan-500"
                  >
                    <option value="server">Server</option>
                    <option value="workstation">Workstation</option>
                    <option value="gateway">Gateway</option>
                    <option value="database">Database</option>
                    <option value="firewall">Firewall</option>
                  </select>
                </div>

                <div>
                  <label className="text-slate-400 block mb-1">Criticality:</label>
                  <select
                    value={newCriticality}
                    onChange={(e) => setNewCriticality(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 text-white rounded px-2.5 py-2 outline-none focus:border-cyan-500"
                  >
                    <option value="CRITICAL">Critical</option>
                    <option value="HIGH">High</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="LOW">Low</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-slate-400 block mb-1">Environment:</label>
                  <select
                    value={newEnvironment}
                    onChange={(e) => setNewEnvironment(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 text-white rounded px-2.5 py-2 outline-none focus:border-cyan-500"
                  >
                    <option value="internal">Internal</option>
                    <option value="dmz">DMZ</option>
                    <option value="external">External</option>
                    <option value="management">Management</option>
                  </select>
                </div>

                <div>
                  <label className="text-slate-400 block mb-1">Subnet:</label>
                  <input
                    type="text"
                    placeholder="192.168.2.0/24"
                    value={newSubnet}
                    onChange={(e) => setNewSubnet(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 text-white rounded px-3 py-2 outline-none focus:border-cyan-500"
                  />
                </div>
              </div>

              <div className="flex items-center space-x-2 pt-1">
                <input
                  type="checkbox"
                  id="perim"
                  checked={newPerimeter}
                  onChange={(e) => setNewPerimeter(e.target.checked)}
                  className="rounded border-slate-700 bg-slate-900 text-cyan-500"
                />
                <label htmlFor="perim" className="text-slate-300 cursor-pointer">
                  Directly exposed perimeter asset
                </label>
              </div>

              <div className="flex justify-end space-x-2 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-xs"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white font-semibold rounded text-xs"
                >
                  Create Asset
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
