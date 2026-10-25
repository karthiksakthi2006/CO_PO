import React, { useEffect, useState } from 'react';
import { Calculator, Play, CheckCircle2, ShieldAlert, AlertTriangle, History } from 'lucide-react';
import api from '../api/client';

export const AttainmentCalculationPage: React.FC = () => {
  const [offerings, setOfferings] = useState<any[]>([]);
  const [selectedOfferingId, setSelectedOfferingId] = useState<number>(1);
  const [config, setConfig] = useState<any>({
    direct_method: 'THRESHOLD',
    threshold_percentage: 60.0,
    target_percentage: 70.0,
    level1_threshold: 60.0,
    level2_threshold: 70.0,
    level3_threshold: 80.0,
    enable_indirect: 1,
    direct_weight: 80.0,
    indirect_weight: 20.0,
    missing_mark_policy: 'EXCLUDE',
  });
  const [latestRun, setLatestRun] = useState<any>(null);
  const [isCalculating, setIsCalculating] = useState(false);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Load offerings
  useEffect(() => {
    api.get('/academic/offerings')
      .then((res) => {
        setOfferings(res.data);
        if (res.data.length > 0) {
          setSelectedOfferingId(res.data[0].id);
        }
      })
      .catch((err) => {
        console.error('Failed to load offerings', err);
        setErrorMsg('Failed to load course offerings.');
      });
  }, []);

  const fetchData = async (offeringId: number) => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const [configRes, runRes] = await Promise.all([
        api.get(`/attainment/config/${offeringId}`),
        api.get(`/attainment/offerings/${offeringId}/latest`),
      ]);
      if (configRes.data) setConfig(configRes.data);
      setLatestRun(runRes.data || null);
    } catch (err: any) {
      console.error(err);
      setErrorMsg('Failed to load calculation configuration or results.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedOfferingId) {
      fetchData(selectedOfferingId);
    }
  }, [selectedOfferingId]);

  const handleRunCalculation = async () => {
    setIsCalculating(true);
    setErrorMsg(null);
    try {
      // 1. Save config first
      await api.post(`/attainment/config/${selectedOfferingId}`, config);
      // 2. Trigger calculation run
      const res = await api.post('/attainment/run', {
        course_offering_id: selectedOfferingId,
        summary_notes: `Manual calculation via dashboard (${config.direct_method})`,
      });
      setLatestRun(res.data);
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || 'Calculation run failed.');
    } finally {
      setIsCalculating(false);
    }
  };

  const currentOffering = offerings.find((o) => o.id === selectedOfferingId);
  const coResults = latestRun?.co_results || [];
  const poResults = latestRun?.po_results || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Attainment Calculation Center</h1>
          <p className="text-sm text-slate-400 mt-0.5">
            Execute OBE direct and indirect outcome aggregation using verified mathematical algorithms.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          {/* Offering Selector */}
          <div className="flex items-center gap-2 bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5">
            <span className="text-[11px] text-slate-400 font-medium">Offering:</span>
            <select
              value={selectedOfferingId}
              onChange={(e) => setSelectedOfferingId(Number(e.target.value))}
              className="bg-transparent text-xs text-white font-semibold focus:outline-none"
            >
              {offerings.map((o) => (
                <option key={o.id} value={o.id} className="bg-slate-900 text-white">
                  {o.course_code} - Sec {o.section} ({o.semester_name || 'Sem 5'})
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={handleRunCalculation}
            disabled={isCalculating || loading}
            className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold flex items-center gap-2 shadow-lg shadow-blue-500/20 transition-all disabled:opacity-50"
          >
            <Play className={`w-4 h-4 ${isCalculating ? 'animate-spin' : ''}`} />
            <span>{isCalculating ? 'Computing Attainment...' : 'Run Attainment Engine'}</span>
          </button>
        </div>
      </div>

      {currentOffering && (
        <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <span className="font-bold text-white text-sm">{currentOffering.course_code}: {currentOffering.course_name}</span>
            <span className="px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 font-bold">
              Section {currentOffering.section} • {currentOffering.faculty_name}
            </span>
          </div>
          <span className="text-slate-400">
            {latestRun ? `Last Run: ${new Date(latestRun.run_date).toLocaleString()}` : 'No Runs Executed'}
          </span>
        </div>
      )}

      {errorMsg && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 flex items-center gap-3 text-xs">
          <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Configuration Controls Bar */}
      <div className="glass-panel p-5 rounded-2xl border border-slate-800">
        <h2 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-2">
          <Calculator className="w-4 h-4 text-blue-400" />
          <span>Calculation Parameters & Institutional Thresholds</span>
        </h2>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 text-xs">
          <div>
            <label className="block text-slate-400 mb-1">Direct Method</label>
            <select
              value={config.direct_method}
              onChange={(e) => setConfig({ ...config, direct_method: e.target.value })}
              className="w-full px-2.5 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-white text-xs focus:outline-none focus:border-blue-500"
            >
              <option value="THRESHOLD">Method A (Threshold)</option>
              <option value="NORMALIZED_SCORE">Method B (Normalized)</option>
            </select>
          </div>

          <div>
            <label className="block text-slate-400 mb-1">Student Cutoff (%)</label>
            <input
              type="number"
              value={config.threshold_percentage}
              onChange={(e) => setConfig({ ...config, threshold_percentage: Number(e.target.value) })}
              className="w-full px-2.5 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-white text-xs focus:outline-none focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-slate-400 mb-1">Target Attainment (%)</label>
            <input
              type="number"
              value={config.target_percentage}
              onChange={(e) => setConfig({ ...config, target_percentage: Number(e.target.value) })}
              className="w-full px-2.5 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-white text-xs focus:outline-none focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-slate-400 mb-1">Direct Weight (%)</label>
            <input
              type="number"
              value={config.direct_weight}
              onChange={(e) => setConfig({ ...config, direct_weight: Number(e.target.value) })}
              className="w-full px-2.5 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-white text-xs focus:outline-none focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-slate-400 mb-1">Indirect Weight (%)</label>
            <input
              type="number"
              value={config.indirect_weight}
              onChange={(e) => setConfig({ ...config, indirect_weight: Number(e.target.value) })}
              className="w-full px-2.5 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-white text-xs focus:outline-none focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-slate-400 mb-1">Absence Policy</label>
            <select
              value={config.missing_mark_policy}
              onChange={(e) => setConfig({ ...config, missing_mark_policy: e.target.value })}
              className="w-full px-2.5 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-white text-xs focus:outline-none focus:border-blue-500"
            >
              <option value="EXCLUDE">Exclude from Pool</option>
              <option value="ZERO">Score as 0 Marks</option>
            </select>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="p-8 text-center text-slate-400 text-sm">Loading calculation records...</div>
      ) : !latestRun ? (
        <div className="p-12 text-center border border-dashed border-slate-800 rounded-2xl glass-card">
          <History className="w-8 h-8 text-slate-600 mx-auto mb-2" />
          <h2 className="text-base font-bold text-white">No Attainment Calculations Executed Yet</h2>
          <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
            Assessment marks are loaded. Click the "Run Attainment Engine" button above to execute pure mathematical calculation.
          </p>
        </div>
      ) : (
        /* Results Section */
        <div className="space-y-6">
          {/* Table 1: Course Outcomes (CO) Results */}
          <div className="glass-panel rounded-xl border border-slate-800 overflow-hidden shadow-2xl">
            <div className="p-4 border-b border-slate-800 flex items-center justify-between">
              <div>
                <h2 className="text-sm font-bold text-white">Course Outcome (CO) Attainment Matrix</h2>
                <p className="text-xs text-slate-400">
                  Computed via {latestRun.method_used} algorithm with direct & indirect weight combination
                </p>
              </div>
              <span className="text-xs font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-1 rounded-full font-bold">
                Run #{latestRun.id} Verified
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-900/80 text-slate-400 uppercase text-[10px] font-semibold border-b border-slate-800">
                  <tr>
                    <th className="py-3 px-4">CO Code</th>
                    <th className="py-3 px-4">Target (%)</th>
                    <th className="py-3 px-4">Direct (%)</th>
                    <th className="py-3 px-4">Indirect (%)</th>
                    <th className="py-3 px-4">Overall Score</th>
                    <th className="py-3 px-4">Level (0-3)</th>
                    <th className="py-3 px-4">Gap (pts)</th>
                    <th className="py-3 px-4">Status & Severity</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-slate-300">
                  {coResults.map((cr: any) => {
                    const isTargetMet = cr.gap_percentage_points <= 0;
                    return (
                      <tr key={cr.id} className="hover:bg-slate-800/30">
                        <td className="py-3 px-4 font-mono font-bold text-white">{cr.co_code}</td>
                        <td className="py-3 px-4 text-slate-400">{cr.target_attainment}%</td>
                        <td className="py-3 px-4 font-medium">{cr.direct_attainment}%</td>
                        <td className="py-3 px-4 text-slate-400">{cr.indirect_attainment}%</td>
                        <td className="py-3 px-4 font-bold text-white text-sm">{cr.overall_attainment}%</td>
                        <td className="py-3 px-4">
                          <span className="px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 font-bold">
                            Level {cr.attainment_level}
                          </span>
                        </td>
                        <td className="py-3 px-4 font-mono font-semibold">
                          {isTargetMet ? (
                            <span className="text-emerald-400">{cr.gap_percentage_points} pts</span>
                          ) : (
                            <span className="text-rose-400">+{cr.gap_percentage_points} pts</span>
                          )}
                        </td>
                        <td className="py-3 px-4">
                          {isTargetMet ? (
                            <span className="inline-flex items-center gap-1 text-emerald-400 font-medium">
                              <CheckCircle2 className="w-3.5 h-3.5" />
                              <span>On Target</span>
                            </span>
                          ) : cr.severity === 'CRITICAL' ? (
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
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Table 2: Program Outcomes (PO/PSO) Results */}
          {poResults.length > 0 && (
            <div className="glass-panel rounded-xl border border-slate-800 overflow-hidden shadow-2xl">
              <div className="p-4 border-b border-slate-800">
                <h2 className="text-sm font-bold text-white">Program Outcome (PO & PSO) Attainment Mapping</h2>
                <p className="text-xs text-slate-400">Aggregated via weighted mapping matrix contribution</p>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-900/80 text-slate-400 uppercase text-[10px] font-semibold border-b border-slate-800">
                    <tr>
                      <th className="py-3 px-4">Outcome Code</th>
                      <th className="py-3 px-4">Calculated Attainment (%)</th>
                      <th className="py-3 px-4">Average Mapping Strength (1-3)</th>
                      <th className="py-3 px-4">Contributing COs Count</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 text-slate-300">
                    {poResults.map((po: any) => (
                      <tr key={po.id} className="hover:bg-slate-800/30">
                        <td className="py-3 px-4 font-bold text-white">{po.outcome_code}</td>
                        <td className="py-3 px-4 font-bold text-blue-400 text-sm">{po.calculated_attainment}%</td>
                        <td className="py-3 px-4">{po.average_strength} / 3.0</td>
                        <td className="py-3 px-4">{po.mapped_co_count} COs</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
