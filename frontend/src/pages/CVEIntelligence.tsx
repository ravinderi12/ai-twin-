import React, { useState } from 'react';
import {
  Database, Search, ExternalLink, ShieldAlert, CheckCircle2, Clock, Info, RefreshCw
} from 'lucide-react';
import { SeverityBadge } from '../components/Badge';
import { lookupCVE, searchCVEs } from '../services/api';

export const CVEIntelligence: React.FC = () => {
  const [query, setQuery] = useState('CVE-2021-44228');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any[]>([]);
  const [searched, setSearched] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    try {
      setLoading(true);
      setErrorMsg(null);
      setSearched(true);

      if (query.trim().toUpperCase().startsWith('CVE-')) {
        try {
          const detail = await lookupCVE(query.trim().toUpperCase());
          setResults([detail]);
        } catch (lookupErr: any) {
          const searchData = await searchCVEs(query.trim());
          setResults(searchData.results || []);
        }
      } else {
        const searchData = await searchCVEs(query.trim());
        setResults(searchData.results || []);
      }
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || "Unable to retrieve vulnerability intelligence.");
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-lg font-bold text-white tracking-wide">
              CVE INTELLIGENCE & NVD FEED SYNCHRONIZER
            </h1>
            <span className="text-xs px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-400 font-mono font-medium border border-cyan-500/30">
              NIST NVD 2.0 / CACHE
            </span>
          </div>
          <p className="text-xs text-slate-400">
            Real-time querying and automated caching of official National Vulnerability Database records
          </p>
        </div>
      </div>

      {/* Search Input Box */}
      <div className="bg-soc-card border border-soc-border rounded-xl p-5 shadow-sm space-y-4">
        <form onSubmit={handleSearch} className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search by CVE ID (e.g. CVE-2021-44228) or product keyword (e.g. Apache, Log4j)..."
              className="w-full bg-slate-900 border border-slate-700 text-white text-xs rounded-lg pl-10 pr-4 py-2.5 outline-none focus:border-cyan-500 font-mono"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="px-5 py-2.5 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white text-xs font-bold rounded-lg shadow-sm transition flex items-center justify-center space-x-2"
          >
            <Search className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>{loading ? 'Searching NVD / Cache...' : 'Query CVE Intelligence'}</span>
          </button>
        </form>

        {/* Quick Suggestion Pills */}
        <div className="flex flex-wrap items-center gap-2 text-[11px] text-slate-400">
          <span>Popular Test Queries:</span>
          {['CVE-2021-44228', 'CVE-2021-41773', 'CVE-2020-1472', 'CVE-2017-0144', 'CVE-2020-14812'].map((cve) => (
            <button
              key={cve}
              type="button"
              onClick={() => { setQuery(cve); }}
              className="px-2 py-0.5 rounded bg-slate-900 hover:bg-slate-800 text-cyan-400 font-mono border border-slate-800 transition"
            >
              {cve}
            </button>
          ))}
        </div>
      </div>

      {/* Results Section */}
      {errorMsg && (
        <div className="p-4 rounded-xl bg-red-950/60 border border-red-500/40 text-red-300 text-xs">
          {errorMsg}
        </div>
      )}

      {searched && results.length === 0 && !loading && !errorMsg && (
        <div className="p-8 text-center bg-soc-card border border-soc-border rounded-xl">
          <p className="text-xs text-slate-400">No CVE records matching "{query}" found in local cache or NVD repository.</p>
        </div>
      )}

      {results.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
            Vulnerability Records Returned ({results.length})
          </h2>

          <div className="grid grid-cols-1 gap-4">
            {results.map((rec, idx) => (
              <div key={idx} className="bg-soc-card border border-soc-border rounded-xl p-5 shadow-sm space-y-3">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
                  <div className="flex items-center space-x-3">
                    <span className="text-base font-bold text-red-400 font-mono">
                      {rec.cve_id}
                    </span>
                    <SeverityBadge severity={rec.cvss_v3_severity} />
                  </div>
                  <div className="flex items-center space-x-2 text-[11px] text-slate-400">
                    <span className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 font-mono text-cyan-400">
                      Source: {rec.source}
                    </span>
                    {rec.cached_at && (
                      <span className="flex items-center space-x-1 font-mono text-slate-500">
                        <Clock className="w-3 h-3" />
                        <span>Cached</span>
                      </span>
                    )}
                  </div>
                </div>

                <div className="space-y-1">
                  <h3 className="text-sm font-semibold text-white">{rec.title}</h3>
                  <p className="text-xs text-slate-300 leading-relaxed">{rec.description}</p>
                </div>

                {/* CVSS Metrics Row */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 p-3 bg-slate-900/80 rounded-lg border border-slate-800 text-xs">
                  <div>
                    <span className="text-slate-500 block text-[10px]">CVSS V3 BASE SCORE</span>
                    <span className="text-base font-bold font-mono text-red-400">{rec.cvss_v3_score} / 10.0</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-[10px]">SEVERITY RATING</span>
                    <span className="font-semibold text-slate-200">{rec.cvss_v3_severity}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-[10px]">CVSS VECTOR STRING</span>
                    <span className="font-mono text-[10px] text-slate-400 break-all">{rec.cvss_vector || 'N/A'}</span>
                  </div>
                </div>

                {/* Official References */}
                {rec.reference_urls && rec.reference_urls.length > 0 && (
                  <div className="space-y-1 pt-1">
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                      Authoritative References:
                    </span>
                    <div className="flex flex-wrap gap-2 text-xs">
                      {rec.reference_urls.slice(0, 3).map((url: string, uIdx: number) => (
                        <a
                          key={uIdx}
                          href={url}
                          target="_blank"
                          rel="noreferrer"
                          className="flex items-center space-x-1 text-cyan-400 hover:underline max-w-sm truncate"
                        >
                          <span className="truncate">{url}</span>
                          <ExternalLink className="w-3 h-3 flex-shrink-0" />
                        </a>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
