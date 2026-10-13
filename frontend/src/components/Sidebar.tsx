import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Server,
  Network,
  Crosshair,
  ShieldAlert,
  Wrench,
  Scan,
  Database,
  FileCheck
} from 'lucide-react';

const NAV_ITEMS = [
  { path: '/', label: 'Overview Dashboard', icon: LayoutDashboard },
  { path: '/topology', label: 'Digital Twin Map', icon: Network },
  { path: '/simulation', label: 'Attack Path Simulator', icon: Crosshair },
  { path: '/remediation', label: 'Remediation Planner', icon: Wrench },
  { path: '/assets', label: 'Asset Inventory', icon: Server },
  { path: '/vulnerabilities', label: 'Vulnerability Center', icon: ShieldAlert },
  { path: '/assessments', label: 'Assessments & Scans', icon: Scan },
  { path: '/cve-intel', label: 'CVE Intelligence', icon: Database },
  { path: '/reports', label: 'Compliance Reports', icon: FileCheck },
];

export const Sidebar: React.FC = () => {
  return (
    <aside className="w-64 bg-soc-card border-r border-soc-border flex flex-col justify-between h-[calc(100vh-4rem)] sticky top-16 select-none">
      <div className="p-4 space-y-6">
        <div>
          <div className="px-3 text-[11px] font-semibold text-slate-400 tracking-wider uppercase mb-2">
            Operations & Analytics
          </div>
          <nav className="space-y-1">
            {NAV_ITEMS.slice(0, 4).map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) =>
                    `flex items-center space-x-3 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                      isActive
                        ? 'bg-cyan-500/15 text-cyan-400 border border-cyan-500/30'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                    }`
                  }
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </NavLink>
              );
            })}
          </nav>
        </div>

        <div>
          <div className="px-3 text-[11px] font-semibold text-slate-400 tracking-wider uppercase mb-2">
            Security Intelligence
          </div>
          <nav className="space-y-1">
            {NAV_ITEMS.slice(4).map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) =>
                    `flex items-center space-x-3 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                      isActive
                        ? 'bg-cyan-500/15 text-cyan-400 border border-cyan-500/30'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                    }`
                  }
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </NavLink>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Footer Info Box */}
      <div className="p-4 m-3 rounded-lg bg-slate-900/80 border border-slate-800 text-[11px] text-slate-400 space-y-1.5">
        <div className="flex items-center justify-between text-slate-300 font-semibold">
          <span>Digital Twin Mode</span>
          <span className="text-cyan-400 font-mono">STANDALONE</span>
        </div>
        <p className="leading-relaxed text-slate-500 text-[10px]">
          Simulations run completely offline in the software-defined replica with zero risk of live service disruption.
        </p>
      </div>
    </aside>
  );
};
