import React from 'react';

interface SeverityBadgeProps {
  severity: string;
  size?: 'sm' | 'md';
}

export const SeverityBadge: React.FC<SeverityBadgeProps> = ({ severity, size = 'md' }) => {
  const sev = (severity || 'NONE').toUpperCase();

  let colorClass = 'bg-slate-800 text-slate-300 border-slate-700';
  if (sev === 'CRITICAL') {
    colorClass = 'bg-red-500/15 text-red-400 border-red-500/40';
  } else if (sev === 'HIGH') {
    colorClass = 'bg-amber-500/15 text-amber-400 border-amber-500/40';
  } else if (sev === 'MEDIUM') {
    colorClass = 'bg-yellow-500/15 text-yellow-400 border-yellow-500/40';
  } else if (sev === 'LOW') {
    colorClass = 'bg-blue-500/15 text-blue-400 border-blue-500/40';
  }

  const padding = size === 'sm' ? 'px-1.5 py-0.5 text-[10px]' : 'px-2 py-0.5 text-xs';

  return (
    <span className={`inline-flex items-center font-semibold rounded border ${colorClass} ${padding}`}>
      {sev}
    </span>
  );
};

interface StatusBadgeProps {
  status: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  const st = (status || 'PLANNED').toUpperCase();

  let colorClass = 'bg-slate-800 text-slate-300 border-slate-700';
  if (st === 'RESOLVED' || st === 'COMPLETED') {
    colorClass = 'bg-emerald-500/15 text-emerald-400 border-emerald-500/40';
  } else if (st === 'IN_PROGRESS' || st === 'RUNNING') {
    colorClass = 'bg-cyan-500/15 text-cyan-400 border-cyan-500/40 animate-pulse';
  } else if (st === 'PLANNED' || st === 'PENDING') {
    colorClass = 'bg-slate-800 text-slate-300 border-slate-700';
  } else if (st === 'FAILED') {
    colorClass = 'bg-red-500/15 text-red-400 border-red-500/40';
  }

  return (
    <span className={`inline-flex items-center font-medium rounded border px-2 py-0.5 text-xs ${colorClass}`}>
      {st.replace('_', ' ')}
    </span>
  );
};
