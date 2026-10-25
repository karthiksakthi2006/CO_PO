import React, { useEffect, useState } from 'react';
import {
  ShieldCheck,
  History,
  FileSpreadsheet,
  CheckCircle2,
  Filter,
  RefreshCw,
} from 'lucide-react';
import api from '../api/client';

export const AuditLogPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'logs' | 'jobs'>('logs');
  const [logs, setLogs] = useState<any[]>([]);
  const [jobs, setJobs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionFilter, setActionFilter] = useState('');

  const fetchData = async () => {
    setLoading(true);
    try {
      const [logsRes, jobsRes] = await Promise.all([
        api.get('/audit/logs?limit=100'),
        api.get('/audit/jobs?limit=50'),
      ]);
      setLogs(logsRes.data);
      setJobs(jobsRes.data);
    } catch (err) {
      console.error('Failed to fetch audit data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const filteredLogs = logs.filter((l) =>
    actionFilter ? l.action.toLowerCase().includes(actionFilter.toLowerCase()) : true
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2.5">
            <ShieldCheck className="w-6 h-6 text-blue-400" />
            <span>System Audit & Operational Logs</span>
          </h1>
          <p className="text-sm text-slate-400 mt-0.5">
            Cryptographic and relational event tracing for OBE calculations, user actions, and file imports.
          </p>
        </div>

        <button
          onClick={fetchData}
          disabled={loading}
          className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-white transition-colors self-start sm:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Records</span>
        </button>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-3 border-b border-slate-800 pb-px">
        <button
          onClick={() => setActiveTab('logs')}
          className={`flex items-center gap-2 px-4 py-2.5 text-xs font-semibold border-b-2 transition-colors ${
            activeTab === 'logs'
              ? 'border-blue-500 text-blue-400 bg-blue-500/5'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <History className="w-4 h-4" />
          <span>Audit Trail ({logs.length})</span>
        </button>
        <button
          onClick={() => setActiveTab('jobs')}
          className={`flex items-center gap-2 px-4 py-2.5 text-xs font-semibold border-b-2 transition-colors ${
            activeTab === 'jobs'
              ? 'border-blue-500 text-blue-400 bg-blue-500/5'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <FileSpreadsheet className="w-4 h-4" />
          <span>Import Jobs ({jobs.length})</span>
        </button>
      </div>

      {/* Tab 1: Audit Logs */}
      {activeTab === 'logs' && (
        <div className="space-y-4">
          {/* Filter */}
          <div className="flex items-center gap-3 max-w-sm">
            <Filter className="w-4 h-4 text-slate-500" />
            <input
              type="text"
              placeholder="Filter by action (e.g., CALCULATE_ATTAINMENT, LOGIN)..."
              value={actionFilter}
              onChange={(e) => setActionFilter(e.target.value)}
              className="w-full px-3 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
            />
          </div>

          <div className="glass-panel rounded-xl border border-slate-800 overflow-hidden shadow-2xl">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900/90 text-slate-400 font-semibold text-[10px] uppercase border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4">Timestamp</th>
                  <th className="py-3 px-4">Action</th>
                  <th className="py-3 px-4">User</th>
                  <th className="py-3 px-4">Entity</th>
                  <th className="py-3 px-4">IP Address</th>
                  <th className="py-3 px-4">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300 font-mono text-[11px]">
                {filteredLogs.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="py-8 text-center text-slate-500">
                      No audit events matching criteria.
                    </td>
                  </tr>
                ) : (
                  filteredLogs.map((l) => (
                    <tr key={l.id} className="hover:bg-slate-800/30">
                      <td className="py-2.5 px-4 text-slate-400 whitespace-nowrap">
                        {new Date(l.created_at).toLocaleString()}
                      </td>
                      <td className="py-2.5 px-4 font-bold text-white">
                        <span className="px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 text-[10px]">
                          {l.action}
                        </span>
                      </td>
                      <td className="py-2.5 px-4 text-slate-300">{l.user_email}</td>
                      <td className="py-2.5 px-4 text-slate-400">
                        {l.entity_type ? `${l.entity_type} #${l.entity_id || ''}` : '--'}
                      </td>
                      <td className="py-2.5 px-4 text-slate-500">{l.ip_address || '127.0.0.1'}</td>
                      <td className="py-2.5 px-4 text-slate-400 max-w-xs truncate font-sans text-xs">
                        {l.details ? JSON.stringify(l.details) : '--'}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 2: Import Jobs */}
      {activeTab === 'jobs' && (
        <div className="glass-panel rounded-xl border border-slate-800 overflow-hidden shadow-2xl">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/90 text-slate-400 font-semibold text-[10px] uppercase border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Job ID</th>
                <th className="py-3 px-4">Filename</th>
                <th className="py-3 px-4">Type</th>
                <th className="py-3 px-4">Triggered By</th>
                <th className="py-3 px-4 text-right">Total Rows</th>
                <th className="py-3 px-4 text-right">Imported</th>
                <th className="py-3 px-4 text-right">Failed</th>
                <th className="py-3 px-4 text-center">Status</th>
                <th className="py-3 px-4">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {jobs.length === 0 ? (
                <tr>
                  <td colSpan={9} className="py-8 text-center text-slate-500">
                    No import jobs recorded yet.
                  </td>
                </tr>
              ) : (
                jobs.map((j) => (
                  <tr key={j.id} className="hover:bg-slate-800/30">
                    <td className="py-2.5 px-4 font-mono font-bold text-white">#{j.id}</td>
                    <td className="py-2.5 px-4 font-medium text-slate-200">{j.file_name}</td>
                    <td className="py-2.5 px-4">
                      <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-300">
                        {j.import_type}
                      </span>
                    </td>
                    <td className="py-2.5 px-4 text-slate-400">{j.user_email}</td>
                    <td className="py-2.5 px-4 text-right font-mono text-slate-300">{j.total_rows}</td>
                    <td className="py-2.5 px-4 text-right font-mono text-emerald-400 font-semibold">
                      {j.imported_rows}
                    </td>
                    <td className="py-2.5 px-4 text-right font-mono text-rose-400 font-semibold">
                      {j.failed_rows}
                    </td>
                    <td className="py-2.5 px-4 text-center">
                      <span
                        className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold ${
                          j.status === 'COMPLETED'
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                        }`}
                      >
                        <CheckCircle2 className="w-3 h-3" />
                        <span>{j.status}</span>
                      </span>
                    </td>
                    <td className="py-2.5 px-4 text-slate-400 font-mono text-[11px]">
                      {new Date(j.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
export default AuditLogPage;
