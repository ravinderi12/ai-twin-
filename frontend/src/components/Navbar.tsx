import React, { useState } from 'react';
import { Shield, Activity, RefreshCw, FileText, CheckCircle2, AlertCircle } from 'lucide-react';
import { loadDemoTopology, getPdfExportUrl } from '../services/api';

interface NavbarProps {
  onDataRefresh?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onDataRefresh }) => {
  const [reloading, setReloading] = useState(false);
  const [notification, setNotification] = useState<string | null>(null);

  const handleReloadDemo = async () => {
    try {
      setReloading(true);
      await loadDemoTopology();
      setNotification("Sample enterprise topology reloaded!");
      setTimeout(() => setNotification(null), 3500);
      if (onDataRefresh) onDataRefresh();
    } catch (err) {
      setNotification("Failed to reload demo data");
      setTimeout(() => setNotification(null), 3500);
    } finally {
      setReloading(false);
    }
  };

  return (
    <header className="h-16 bg-soc-card border-b border-soc-border px-6 flex items-center justify-between sticky top-0 z-40">
      {/* Brand & Title */}
      <div className="flex items-center space-x-3">
        <div className="w-10 h-10 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-soc-accent shadow-sm">
          <Shield className="w-6 h-6 text-soc-cyan animate-pulse" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="font-bold text-base tracking-wide text-white">
              CYBER DIGITAL TWIN
            </h1>
            <span className="text-xs px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-400 font-mono font-medium border border-cyan-500/30">
              v1.0 SOC
            </span>
          </div>
          <p className="text-xs text-slate-400">
            Intelligent Risk Analysis & Multi-Hop Attack Path Simulator
          </p>
        </div>
      </div>

      {/* Center Notification */}
      {notification && (
        <div className="bg-cyan-950/80 border border-cyan-500/50 text-cyan-300 text-xs px-3 py-1.5 rounded-md flex items-center space-x-2 animate-fade-in shadow-md">
          <CheckCircle2 className="w-4 h-4 text-cyan-400" />
          <span>{notification}</span>
        </div>
      )}

      {/* Right Controls */}
      <div className="flex items-center space-x-4">

        {/* Telemetry Status */}
        <div className="flex items-center space-x-2 px-3 py-1.5 rounded-md bg-slate-800/60 border border-slate-700/60 text-xs">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span>
          <span className="text-slate-300 font-medium">SOC Engine Active</span>
        </div>

        {/* Load / Reset Demo Data Button */}
        <button
          onClick={handleReloadDemo}
          disabled={reloading}
          className="flex items-center space-x-2 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 active:scale-95 text-slate-200 text-xs font-medium rounded-md border border-slate-700 transition"
          title="Reloads the simulated multi-tier enterprise network"
        >
          <RefreshCw className={`w-3.5 h-3.5 text-cyan-400 ${reloading ? 'animate-spin' : ''}`} />
          <span>{reloading ? 'Loading...' : 'Load Enterprise Demo'}</span>
        </button>

        {/* PDF Report Quick Export */}
        <a
          href={getPdfExportUrl()}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center space-x-2 px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 active:scale-95 text-white text-xs font-medium rounded-md shadow-sm transition"
        >
          <FileText className="w-3.5 h-3.5" />
          <span>Export PDF Report</span>
        </a>
      </div>
    </header>
  );
};
