import React, { useEffect, useState } from 'react';
import {
  Scan, Upload, FileCode, Play, AlertCircle, CheckCircle2, History, RefreshCw, X, ShieldAlert
} from 'lucide-react';
import { StatusBadge } from '../components/Badge';
import {
  getAssessments, runLiveScan, uploadNmapXml, importJsonTopology, loadDemoTopology
} from '../services/api';
import { Assessment } from '../types';

export const AssessmentManagement: React.FC = () => {
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'xml' | 'json' | 'scan' | 'demo'>('xml');

  // Nmap XML Upload State
  const [xmlFile, setXmlFile] = useState<File | null>(null);
  const [xmlTitle, setXmlTitle] = useState('Nmap XML Ingestion');
  const [uploadingXml, setUploadingXml] = useState(false);

  // JSON Import State
  const [jsonText, setJsonText] = useState('');
  const [importingJson, setImportingJson] = useState(false);

  // Live Scan State
  const [scanTarget, setScanTarget] = useState('127.0.0.1');
  const [scanType, setScanType] = useState('quick');
  const [confirmAuth, setConfirmAuth] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [scanError, setScanError] = useState<string | null>(null);

  // Feedback Notification
  const [feedback, setFeedback] = useState<string | null>(null);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      const data = await getAssessments();
      setAssessments(data);
    } catch (err) {
      console.error("Failed to load assessments", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const showNotification = (msg: string) => {
    setFeedback(msg);
    setTimeout(() => setFeedback(null), 4000);
  };

  // 1. Handle Nmap XML Upload
  const handleUploadXml = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!xmlFile) return;
    try {
      setUploadingXml(true);
      const formData = new FormData();
      formData.append('file', xmlFile);
      formData.append('title', xmlTitle);
      await uploadNmapXml(formData);
      showNotification("Nmap XML ingested successfully!");
      setXmlFile(null);
      fetchHistory();
    } catch (err: any) {
      alert(err.response?.data?.detail || "Failed to parse Nmap XML");
    } finally {
      setUploadingXml(false);
    }
  };

  // 2. Handle JSON Import
  const handleImportJson = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setImportingJson(true);
      const parsed = JSON.parse(jsonText);
      await importJsonTopology(parsed);
      showNotification("JSON network topology ingested successfully!");
      setJsonText('');
      fetchHistory();
    } catch (err: any) {
      alert("Invalid JSON format or schema error: " + (err.response?.data?.detail || err.message));
    } finally {
      setImportingJson(false);
    }
  };

  // 3. Handle Live Scan
  const handleRunScan = async (e: React.FormEvent) => {
    e.preventDefault();
    setScanError(null);
    try {
      setScanning(true);
      await runLiveScan({
        target: scanTarget,
        scan_type: scanType,
        confirm_authorized: confirmAuth
      });
      showNotification("Authorized scan executed successfully!");
      fetchHistory();
    } catch (err: any) {
      setScanError(err.response?.data?.detail || "Scan execution error.");
    } finally {
      setScanning(false);
    }
  };

  // 4. Handle Demo Loader
  const handleLoadDemo = async () => {
    try {
      await loadDemoTopology();
      showNotification("Demonstration enterprise topology reloaded!");
      fetchHistory();
    } catch (err) {
      alert("Failed to load demo data");
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-bold text-white tracking-wide">
            ASSESSMENT MANAGEMENT & INGESTION
          </h1>
          <p className="text-xs text-slate-400">
            Import Nmap discovery sweeps, JSON network topologies, or execute authorized internal scans
          </p>
        </div>

        {feedback && (
          <div className="bg-cyan-950/90 border border-cyan-500/60 text-cyan-300 text-xs px-3 py-1.5 rounded-lg flex items-center space-x-2 animate-fade-in shadow-md">
            <CheckCircle2 className="w-4 h-4 text-cyan-400" />
            <span>{feedback}</span>
          </div>
        )}
      </div>

      {/* Ingestion Source Tabs Card */}
      <div className="bg-soc-card border border-soc-border rounded-xl p-6 shadow-sm space-y-5">
        <div className="flex border-b border-slate-800 space-x-4 text-xs font-semibold">
          <button
            onClick={() => setActiveTab('xml')}
            className={`pb-3 flex items-center space-x-2 border-b-2 transition ${
              activeTab === 'xml'
                ? 'border-cyan-500 text-cyan-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Upload className="w-4 h-4" />
            <span>Import Nmap XML</span>
          </button>

          <button
            onClick={() => setActiveTab('json')}
            className={`pb-3 flex items-center space-x-2 border-b-2 transition ${
              activeTab === 'json'
                ? 'border-cyan-500 text-cyan-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <FileCode className="w-4 h-4" />
            <span>Import JSON Schema</span>
          </button>

          <button
            onClick={() => setActiveTab('scan')}
            className={`pb-3 flex items-center space-x-2 border-b-2 transition ${
              activeTab === 'scan'
                ? 'border-cyan-500 text-cyan-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Scan className="w-4 h-4" />
            <span>Live Authorized Scan</span>
          </button>

          <button
            onClick={() => setActiveTab('demo')}
            className={`pb-3 flex items-center space-x-2 border-b-2 transition ${
              activeTab === 'demo'
                ? 'border-cyan-500 text-cyan-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <RefreshCw className="w-4 h-4" />
            <span>Enterprise Demo Topology</span>
          </button>
        </div>

        {/* Tab 1: Nmap XML */}
        {activeTab === 'xml' && (
          <form onSubmit={handleUploadXml} className="space-y-4 max-w-lg text-xs">
            <p className="text-slate-400">
              Upload an authorized Nmap XML scan output file (<code className="text-cyan-400">nmap -sV -oX scan.xml &lt;target&gt;</code>). The system securely extracts discovered hosts, ports, services, and script vulnerabilities.
            </p>
            <div>
              <label className="text-slate-300 block mb-1">Assessment Title:</label>
              <input
                type="text"
                required
                value={xmlTitle}
                onChange={(e) => setXmlTitle(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 text-white rounded px-3 py-2 outline-none focus:border-cyan-500"
              />
            </div>
            <div>
              <label className="text-slate-300 block mb-1">Select XML File:</label>
              <input
                type="file"
                required
                accept=".xml"
                onChange={(e) => setXmlFile(e.target.files ? e.target.files[0] : null)}
                className="w-full bg-slate-900 border border-slate-700 text-slate-300 rounded p-2 text-xs"
              />
            </div>
            <button
              type="submit"
              disabled={uploadingXml || !xmlFile}
              className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white font-semibold rounded text-xs transition"
            >
              {uploadingXml ? 'Parsing & Normalizing XML...' : 'Upload & Ingest XML'}
            </button>
          </form>
        )}

        {/* Tab 2: JSON Import */}
        {activeTab === 'json' && (
          <form onSubmit={handleImportJson} className="space-y-4 max-w-2xl text-xs">
            <p className="text-slate-400">
              Paste a structured JSON topology containing assets, services, and inter-host network relationships.
            </p>
            <div>
              <label className="text-slate-300 block mb-1">JSON Payload:</label>
              <textarea
                required
                rows={8}
                value={jsonText}
                onChange={(e) => setJsonText(e.target.value)}
                placeholder='{ "description": "Custom Lab", "assets": [...], "relationships": [...] }'
                className="w-full bg-slate-900 border border-slate-700 text-slate-200 font-mono text-[11px] rounded p-3 outline-none focus:border-cyan-500"
              />
            </div>
            <button
              type="submit"
              disabled={importingJson || !jsonText}
              className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white font-semibold rounded text-xs transition"
            >
              {importingJson ? 'Ingesting JSON Model...' : 'Ingest JSON Topology'}
            </button>
          </form>
        )}

        {/* Tab 3: Live Scan */}
        {activeTab === 'scan' && (
          <form onSubmit={handleRunScan} className="space-y-4 max-w-lg text-xs">
            {scanError && (
              <div className="p-3 rounded-lg bg-red-950/70 border border-red-500/50 text-red-300 space-y-1">
                <span className="font-bold block flex items-center space-x-1">
                  <ShieldAlert className="w-4 h-4" />
                  <span>Scanner Safeguard Triggered</span>
                </span>
                <p className="leading-relaxed">{scanError}</p>
              </div>
            )}

            <div className="p-3 rounded-lg bg-amber-950/30 border border-amber-500/30 text-amber-300 space-y-1">
              <span className="font-bold block">Safety Boundary & Policy Notice:</span>
              <p className="text-[11px] leading-relaxed text-slate-300">
                Live scans are strictly restricted to local loopback (127.0.0.1) and private RFC1918 subnets. Public Internet targets are rejected. Operator confirmation is required before subprocess launch.
              </p>
            </div>

            <div>
              <label className="text-slate-300 block mb-1">Target Address / CIDR:</label>
              <input
                type="text"
                required
                value={scanTarget}
                onChange={(e) => setScanTarget(e.target.value)}
                placeholder="127.0.0.1 or 192.168.1.0/24"
                className="w-full bg-slate-900 border border-slate-700 text-white rounded px-3 py-2 outline-none focus:border-cyan-500 font-mono"
              />
            </div>

            <div>
              <label className="text-slate-300 block mb-1">Scan Profile:</label>
              <select
                value={scanType}
                onChange={(e) => setScanType(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 text-white rounded px-2.5 py-2 outline-none focus:border-cyan-500"
              >
                <option value="quick">Quick Probe (Top 100 ports, fast)</option>
                <option value="standard">Standard Discovery (Service detection)</option>
                <option value="detailed">Comprehensive Audit (Service & version probe)</option>
              </select>
            </div>

            <div className="flex items-center space-x-2 pt-1">
              <input
                type="checkbox"
                id="confAuth"
                required
                checked={confirmAuth}
                onChange={(e) => setConfirmAuth(e.target.checked)}
                className="rounded border-slate-700 bg-slate-900 text-cyan-500"
              />
              <label htmlFor="confAuth" className="text-slate-300 cursor-pointer">
                I certify that I am explicitly authorized to assess this network scope.
              </label>
            </div>

            <button
              type="submit"
              disabled={scanning || !confirmAuth}
              className="px-4 py-2 bg-red-600 hover:bg-red-500 disabled:opacity-50 text-white font-semibold rounded text-xs transition flex items-center space-x-2"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>{scanning ? 'Executing Subprocess...' : 'Launch Authorized Discovery'}</span>
            </button>
          </form>
        )}

        {/* Tab 4: Demo */}
        {activeTab === 'demo' && (
          <div className="space-y-4 max-w-lg text-xs">
            <p className="text-slate-300 leading-relaxed">
              Instantly seed or reset the complete multi-tier enterprise digital twin topology (Edge Gateway, DMZ Web Server, Spring Boot API, Internal Workstations, MySQL Database, Active Directory Domain Controller).
            </p>
            <p className="text-slate-500">
              Ideal for offline evaluation and academic viva demonstrations when live networks or scanner tools are unavailable.
            </p>
            <button
              onClick={handleLoadDemo}
              className="px-4 py-2.5 bg-cyan-600 hover:bg-cyan-500 text-white font-bold rounded text-xs transition"
            >
              Load / Reset Fictional Enterprise Topology
            </button>
          </div>
        )}
      </div>

      {/* Assessment History Table */}
      <div className="bg-soc-card border border-soc-border rounded-xl p-5 shadow-sm space-y-4">
        <div className="flex items-center space-x-2 text-xs font-semibold text-slate-300 uppercase tracking-wider">
          <History className="w-4 h-4 text-cyan-400" />
          <span>Assessment Execution History ({assessments.length})</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400">
                <th className="pb-3 font-medium">Assessment Title</th>
                <th className="pb-3 font-medium">Source / Type</th>
                <th className="pb-3 font-medium">Target Scope</th>
                <th className="pb-3 font-medium">Assets Ingested</th>
                <th className="pb-3 font-medium">Vulns Identified</th>
                <th className="pb-3 font-medium">Duration</th>
                <th className="pb-3 font-medium text-center">Status</th>
                <th className="pb-3 font-medium text-right">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {assessments.map((a) => (
                <tr key={a.id} className="hover:bg-slate-800/30 transition">
                  <td className="py-3 font-semibold text-white">{a.title}</td>
                  <td className="py-3 uppercase font-mono text-[11px] text-cyan-400">{a.assessment_type}</td>
                  <td className="py-3 font-mono text-slate-400 max-w-xs truncate">{a.target_scope || 'N/A'}</td>
                  <td className="py-3 font-mono text-slate-200">{a.total_assets_found}</td>
                  <td className="py-3 font-mono text-red-400 font-bold">{a.total_vulns_found}</td>
                  <td className="py-3 font-mono text-slate-400">{a.execution_duration_seconds}s</td>
                  <td className="py-3 text-center">
                    <StatusBadge status={a.status} />
                  </td>
                  <td className="py-3 text-right font-mono text-slate-500">
                    {new Date(a.created_at).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
