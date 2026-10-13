import React, { useEffect, useState } from 'react';
import {
  FileText, Download, ShieldCheck, FileSpreadsheet, CheckCircle2,
  Calendar, UserCheck, Lock, ExternalLink
} from 'lucide-react';
import { getPdfExportUrl, getCsvExportUrl, getDashboardMetrics } from '../services/api';
import { DashboardMetrics } from '../types';

export const ReportsPage: React.FC = () => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);

  useEffect(() => {
    getDashboardMetrics().then(setMetrics).catch(console.error);
  }, []);

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-bold text-white tracking-wide">
            ASSESSMENT AUDIT REPORTS & COMPLIANCE EXPORTS
          </h1>
          <p className="text-xs text-slate-400">
            Export comprehensive security assessment findings, topology exposure analysis, and prioritized remediation worklists
          </p>
        </div>
      </div>

      {/* Export Cards Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* PDF Assessment Report */}
        <div className="bg-soc-card border border-soc-border rounded-xl p-6 shadow-sm flex flex-col justify-between space-y-5">
          <div className="space-y-3">
            <div className="w-10 h-10 rounded-lg bg-cyan-500/10 text-cyan-400 flex items-center justify-center">
              <FileText className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">
                Comprehensive PDF Security Audit Report
              </h2>
              <p className="text-xs text-slate-400 leading-relaxed mt-1">
                Generates a formal, publication-ready cybersecurity assessment report compiling Executive Summary, Asset Inventory, Context-Aware Risk Scores, Topological Attack Trajectories, and Algorithmic Remediation Roadmaps.
              </p>
            </div>
            <ul className="text-xs text-slate-300 space-y-1.5 pt-2">
              <li className="flex items-center space-x-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" />
                <span>Executive Summary & Risk KPI Statistics</span>
              </li>
              <li className="flex items-center space-x-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" />
                <span>Multi-Hop Traversal Narrative & MITRE ATT&CK Mapping</span>
              </li>
              <li className="flex items-center space-x-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" />
                <span>Formal Academic Synopsis & Methodology Documentation</span>
              </li>
            </ul>
          </div>

          <a
            href={getPdfExportUrl()}
            target="_blank"
            rel="noopener noreferrer"
            className="w-full flex items-center justify-center space-x-2 py-3 bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs rounded-lg shadow-sm transition active:scale-95"
          >
            <Download className="w-4 h-4" />
            <span>Download Official PDF Assessment Report</span>
          </a>
        </div>

        {/* CSV Vulnerability Export */}
        <div className="bg-soc-card border border-soc-border rounded-xl p-6 shadow-sm flex flex-col justify-between space-y-5">
          <div className="space-y-3">
            <div className="w-10 h-10 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
              <FileSpreadsheet className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">
                Vulnerability Findings CSV Export
              </h2>
              <p className="text-xs text-slate-400 leading-relaxed mt-1">
                Export raw vulnerability records and topology metrics in standardized CSV format for spreadsheet analysis, compliance logging, or SIEM integration.
              </p>
            </div>
            <ul className="text-xs text-slate-300 space-y-1.5 pt-2">
              <li className="flex items-center space-x-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                <span>CVE ID, CVSS v3.1 Base Score, and Context Risk (0-100)</span>
              </li>
              <li className="flex items-center space-x-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                <span>Affected Asset IP, Hostname, Subnet, and Environment</span>
              </li>
              <li className="flex items-center space-x-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                <span>Topological Reachability & Remediation Instructions</span>
              </li>
            </ul>
          </div>

          <a
            href={getCsvExportUrl()}
            className="w-full flex items-center justify-center space-x-2 py-3 bg-slate-800 hover:bg-slate-700 text-emerald-400 font-bold text-xs rounded-lg border border-slate-700 shadow-sm transition active:scale-95"
          >
            <Download className="w-4 h-4" />
            <span>Export Findings CSV</span>
          </a>
        </div>
      </div>

      {/* Methodology & Academic Provenance Card */}
      <div className="bg-soc-card border border-soc-border rounded-xl p-6 shadow-sm space-y-4">
        <h3 className="text-xs font-bold text-white uppercase tracking-wider">
          Academic Project Provenance & Technical Methodology
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs text-slate-300">
          <div className="bg-slate-900/60 p-4 rounded-lg border border-slate-800 space-y-1">
            <span className="text-cyan-400 font-semibold block">Formula Specification</span>
            <p className="text-[11px] text-slate-400 leading-relaxed font-mono">
              Risk(p) = &Sigma; [CVSS(k) &times; Access(k)] &times; Impact(Asset_target)
            </p>
            <p className="text-[11px] text-slate-500">
              Evaluates overall blast radius rather than isolated host severity ratings.
            </p>
          </div>

          <div className="bg-slate-900/60 p-4 rounded-lg border border-slate-800 space-y-1">
            <span className="text-cyan-400 font-semibold block">Adversary Emulation</span>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Mapped against MITRE ATT&CK Matrix: T1190 (Initial Access), T1021 / T1210 (Lateral Movement), T1068 (Privilege Escalation), T1565 (Impact).
            </p>
          </div>

          <div className="bg-slate-900/60 p-4 rounded-lg border border-slate-800 space-y-1">
            <span className="text-cyan-400 font-semibold block">Audit & Governance</span>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Standard: <strong>NIST SP 800-115 / MITRE ATT&CK</strong>
              <br />Classification: Internal Security Assessment
              <br />Environment: Software-Defined Digital Twin
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
