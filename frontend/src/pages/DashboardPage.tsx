import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  BookOpen,
  Users,
  CheckCircle2,
  AlertTriangle,
  TrendingUp,
  FileSpreadsheet,
  FileText,
  Calculator,
  ArrowUpRight,
  ShieldAlert,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import api from '../api/client';

export const DashboardPage: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const res = await api.get('/dashboard/metrics');
        setData(res.data);
      } catch (err) {
        console.error('Failed to load dashboard metrics', err);
      } finally {
        setLoading(false);
      }
    };
    fetchMetrics();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[500px]">
        <div className="text-center">
          <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <div className="text-sm text-slate-400">Loading academic metrics...</div>
        </div>
      </div>
    );
  }

  const kpis = data?.kpis || {};
  const barData = data?.charts?.co_attainment_bars || [];
  const severityData = data?.charts?.severity_distribution || [];

  return (
    <div className="space-y-6">
      {/* Top Banner & Quick Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Course Outcome Attainment Dashboard</h1>
          <p className="text-sm text-slate-400 mt-0.5">
            Real-time Outcome-Based Education (OBE) metrics computed directly from assessment databases.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <Link
            to="/attainment"
            className="px-3.5 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold flex items-center gap-2 shadow-lg shadow-blue-500/20 transition-all"
          >
            <Calculator className="w-3.5 h-3.5" />
            <span>Run Attainment</span>
          </Link>

          <Link
            to="/marks/import"
            className="px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center gap-2 border border-slate-700 transition-all"
          >
            <FileSpreadsheet className="w-3.5 h-3.5" />
            <span>Import Marks</span>
          </Link>

          <a
            href="/api/reports/offerings/1/pdf"
            target="_blank"
            rel="noopener noreferrer"
            className="px-3.5 py-2 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 text-xs font-semibold flex items-center gap-2 transition-all"
          >
            <FileText className="w-3.5 h-3.5" />
            <span>Export Report</span>
          </a>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* Card 1: Attainment Rate */}
        <div className="glass-card p-4 rounded-xl border border-slate-800">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Attainment Rate</span>
            <div className="p-1.5 rounded-lg bg-blue-500/10 text-blue-400">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-white mt-2">{kpis.overall_attainment_rate || 0}%</div>
          <div className="text-[11px] text-slate-400 mt-1 flex items-center gap-1">
            <span className="text-emerald-400 font-semibold">{kpis.cos_meeting_target || 0} COs</span> meeting target
          </div>
        </div>

        {/* Card 2: Evaluated COs */}
        <div className="glass-card p-4 rounded-xl border border-slate-800">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">COs Evaluated</span>
            <div className="p-1.5 rounded-lg bg-purple-500/10 text-purple-400">
              <BookOpen className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-white mt-2">{kpis.cos_evaluated || 0}</div>
          <div className="text-[11px] text-slate-400 mt-1">
            Across {kpis.total_active_courses || 0} active courses
          </div>
        </div>

        {/* Card 3: Below Target & Gaps */}
        <div className="glass-card p-4 rounded-xl border border-slate-800">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Gaps Detected</span>
            <div className="p-1.5 rounded-lg bg-rose-500/10 text-rose-400">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-rose-400 mt-2">{kpis.cos_below_target || 0}</div>
          <div className="text-[11px] text-slate-400 mt-1 flex items-center gap-1">
            <span className="text-amber-400 font-semibold">{kpis.open_interventions || 0}</span> open interventions
          </div>
        </div>

        {/* Card 4: CQI Improvement */}
        <div className="glass-card p-4 rounded-xl border border-slate-800">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">CQI Improvement</span>
            <div className="p-1.5 rounded-lg bg-emerald-500/10 text-emerald-400">
              <CheckCircle2 className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-emerald-400 mt-2">+{kpis.average_improvement_pts || 0} pts</div>
          <div className="text-[11px] text-slate-400 mt-1">Verified post-reassessment</div>
        </div>
      </div>

      {/* Main Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chart 1: CO Attainment vs Target */}
        <div className="lg:col-span-2 glass-panel p-5 rounded-xl border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-semibold text-white">Course Outcome Attainment vs Target (%)</h2>
              <p className="text-xs text-slate-400 mt-0.5">Calculated using approved Method A (Threshold Method)</p>
            </div>
            <div className="flex items-center gap-3 text-xs">
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-sm bg-blue-500 inline-block" />
                <span className="text-slate-400">Actual Attainment</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-sm bg-indigo-400 inline-block" />
                <span className="text-slate-400">Target (70%)</span>
              </div>
            </div>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barData} margin={{ top: 10, right: 10, left: -20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                <XAxis dataKey="name" stroke="#64748b" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={11} domain={[0, 100]} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                  formatter={(val: any) => [`${val}%`, '']}
                />
                <ReferenceLine y={70} stroke="#6366f1" strokeDasharray="4 4" label={{ value: 'Target 70%', fill: '#818cf8', fontSize: 10, position: 'right' }} />
                <Bar dataKey="actual" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 2: Gap Severity Donut Chart */}
        <div className="glass-panel p-5 rounded-xl border border-slate-800 flex flex-col justify-between">
          <div>
            <h2 className="text-sm font-semibold text-white">Gap Severity Distribution</h2>
            <p className="text-xs text-slate-400 mt-0.5">Categorized by percentage points below target</p>
          </div>

          <div className="h-52 w-full my-auto">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={severityData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={75}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {severityData.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="grid grid-cols-2 gap-2 text-xs pt-3 border-t border-slate-800/80">
            {severityData.map((s: any, idx: number) => (
              <div key={idx} className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: s.color }} />
                <span className="text-slate-400 truncate">{s.name}:</span>
                <span className="text-white font-semibold ml-auto">{s.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Evaluated Course Outcomes Breakdown Table */}
      <div className="glass-panel rounded-xl border border-slate-800 overflow-hidden">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <div>
            <h2 className="text-sm font-semibold text-white">Outcome Attainment Breakdown & Status</h2>
            <p className="text-xs text-slate-400">Directly synchronized with stored calculation runs</p>
          </div>
          <Link
            to="/gaps"
            className="text-xs text-blue-400 hover:text-blue-300 font-medium flex items-center gap-1"
          >
            <span>Explore Gap Diagnostics</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/60 text-slate-400 uppercase font-semibold text-[10px] tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Outcome</th>
                <th className="py-3 px-4">Bloom's Level</th>
                <th className="py-3 px-4">Target (%)</th>
                <th className="py-3 px-4">Actual Attainment (%)</th>
                <th className="py-3 px-4">Gap (points)</th>
                <th className="py-3 px-4">Attainment Level</th>
                <th className="py-3 px-4">Severity Status</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {barData.map((co: any, idx: number) => {
                const isMeeting = co.gap <= 0;
                return (
                  <tr key={idx} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3 px-4 font-semibold text-white">{co.name}</td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-slate-800 text-slate-300 border border-slate-700">
                        {co.blooms}
                      </span>
                    </td>
                    <td className="py-3 px-4">{co.target}%</td>
                    <td className="py-3 px-4 font-bold text-white">{co.actual}%</td>
                    <td className="py-3 px-4 font-mono">
                      {co.gap > 0 ? (
                        <span className="text-rose-400">+{co.gap} pts</span>
                      ) : (
                        <span className="text-emerald-400">{co.gap} pts</span>
                      )}
                    </td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-500/10 text-blue-400 border border-blue-500/20">
                        Level {co.level}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      {isMeeting ? (
                        <span className="inline-flex items-center gap-1 text-emerald-400 font-medium">
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          <span>On Target</span>
                        </span>
                      ) : co.severity === 'CRITICAL' ? (
                        <span className="inline-flex items-center gap-1 text-rose-400 font-medium">
                          <ShieldAlert className="w-3.5 h-3.5" />
                          <span>Critical Gap</span>
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-amber-400 font-medium">
                          <AlertTriangle className="w-3.5 h-3.5" />
                          <span>Moderate Gap</span>
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <Link
                        to="/recommendations"
                        className="text-xs text-blue-400 hover:text-blue-300 underline"
                      >
                        Remedy Plan
                      </Link>
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
