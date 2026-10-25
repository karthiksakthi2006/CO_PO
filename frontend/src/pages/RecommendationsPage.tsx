import React, { useEffect, useState } from 'react';
import { Lightbulb, CheckCircle2, ArrowRight, BookOpen, Clock, BrainCircuit, ShieldCheck, AlertCircle } from 'lucide-react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import api from '../api/client';

export const RecommendationsPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [offerings, setOfferings] = useState<any[]>([]);
  const [selectedOfferingId, setSelectedOfferingId] = useState<number>(1);
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [isCreating, setIsCreating] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const navigate = useNavigate();

  // Load offerings
  useEffect(() => {
    api.get('/academic/offerings')
      .then((res) => {
        setOfferings(res.data);
        const queryOffId = searchParams.get('offeringId');
        if (queryOffId) {
          setSelectedOfferingId(Number(queryOffId));
        } else if (res.data.length > 0) {
          setSelectedOfferingId(res.data[0].id);
        }
      })
      .catch((err) => {
        console.error('Failed to load offerings', err);
        setErrorMsg('Failed to load course offerings.');
      });
  }, [searchParams]);

  // Fetch recommendations for selected offering
  const fetchRecs = async (offeringId: number) => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await api.get(`/recommendations/offerings/${offeringId}`);
      setData(res.data);
    } catch (err: any) {
      console.error(err);
      setErrorMsg('Failed to generate recommendations for offering.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedOfferingId) {
      fetchRecs(selectedOfferingId);
    }
  }, [selectedOfferingId]);

  const handleOfferingChange = (id: number) => {
    setSelectedOfferingId(id);
    setSearchParams({ offeringId: String(id) });
  };

  const handleCreateIntervention = async (rec: any) => {
    setIsCreating(rec.id);
    setErrorMsg(null);
    try {
      await api.post('/interventions', {
        course_offering_id: selectedOfferingId,
        course_outcome_id: rec.course_outcome_id || 1,
        gap_percentage_points: rec.gap_percentage_points,
        severity: rec.severity,
        root_cause_analysis: rec.evidence,
        action_plan: `${rec.suggested_teaching_action} Practice: ${rec.suggested_practice_activity}`,
        pedagogical_tool: rec.suggested_teaching_action.split(',')[0],
        pre_intervention_attainment: rec.actual_attainment || 50.0,
      });
      alert('Remedial Intervention Plan successfully adopted and assigned!');
      navigate(`/interventions?offeringId=${selectedOfferingId}`);
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || 'Failed to create intervention');
    } finally {
      setIsCreating(null);
    }
  };

  const currentOffering = offerings.find((o) => o.id === selectedOfferingId);
  const recs = data?.recommendations || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Pedagogical Recommendations Center</h1>
          <p className="text-sm text-slate-400 mt-0.5">
            Bloom's Taxonomy Cognitive Domain Mapping & Deterministic CQI Remediation Strategies.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          {/* Offering Selector */}
          <div className="flex items-center gap-2 bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5">
            <span className="text-[11px] text-slate-400 font-medium">Offering:</span>
            <select
              value={selectedOfferingId}
              onChange={(e) => handleOfferingChange(Number(e.target.value))}
              className="bg-transparent text-xs text-white font-semibold focus:outline-none"
            >
              {offerings.map((o) => (
                <option key={o.id} value={o.id} className="bg-slate-900 text-white">
                  {o.course_code} - Sec {o.section} ({o.semester_name || 'Sem 5'})
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs">
            <ShieldCheck className="w-4 h-4" />
            <span>{data?.engine_type || "Bloom's Cognitive Engine"}</span>
          </div>
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
          <span className="text-slate-400">{recs.length} Actionable Recommendations</span>
        </div>
      )}

      {errorMsg && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 flex items-center gap-3 text-xs">
          <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Advisory Note */}
      {data?.advisory_note && (
        <div className="glass-panel p-4 rounded-xl border border-slate-800 text-xs text-slate-400 flex items-center justify-between">
          <span>{data.advisory_note}</span>
          <span className="text-[11px] text-slate-500 font-mono">100% Offline Cognitive Logic</span>
        </div>
      )}

      {/* Recommendations Cards */}
      {loading ? (
        <div className="p-8 text-center text-slate-400 text-sm">Generating pedagogical recommendations...</div>
      ) : recs.length === 0 ? (
        <div className="p-12 text-center border border-dashed border-slate-800 rounded-2xl glass-card">
          <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
          <h2 className="text-base font-bold text-white">No Learning Gaps Found</h2>
          <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
            {data?.message || 'All Course Outcomes are meeting or exceeding benchmarks. No remedial teaching is required.'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-5">
          {recs.map((rec: any, idx: number) => {
            const isUrgent = rec.priority === 'URGENT';
            return (
              <div
                key={idx}
                className={`p-6 rounded-2xl border transition-all ${
                  isUrgent
                    ? 'bg-rose-500/5 border-rose-500/30'
                    : 'glass-panel border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-800 mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-xl bg-blue-500/10 text-blue-400 flex items-center justify-center font-bold">
                      {rec.co_code}
                    </div>
                    <div>
                      <h2 className="text-base font-bold text-white">{rec.course_name} — {rec.co_code}</h2>
                      <div className="text-xs text-slate-400 flex items-center gap-2 mt-0.5">
                        <span>Bloom's Level: <strong className="text-purple-300">{rec.blooms_level}</strong></span>
                        <span>•</span>
                        <span>Gap: <strong className="text-rose-400">{rec.gap_percentage_points} percentage points</strong></span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <span
                      className={`text-[10px] px-2.5 py-1 rounded-full font-bold uppercase tracking-wider ${
                        isUrgent
                          ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                          : 'bg-blue-500/20 text-blue-300 border border-blue-500/30'
                      }`}
                    >
                      Priority: {rec.priority}
                    </span>
                    <span className="text-xs text-slate-500 flex items-center gap-1 font-mono">
                      <Clock className="w-3.5 h-3.5" />
                      <span>Target: {rec.target_completion_date}</span>
                    </span>
                  </div>
                </div>

                {/* Three-Column Remediation Strategy */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs mb-5">
                  <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-blue-400 block mb-1">
                      1. Recommended Teaching Action
                    </span>
                    <p className="text-slate-300 leading-relaxed">{rec.suggested_teaching_action}</p>
                  </div>

                  <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-purple-400 block mb-1">
                      2. Student Practice Activity
                    </span>
                    <p className="text-slate-300 leading-relaxed">{rec.suggested_practice_activity}</p>
                  </div>

                  <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-400 block mb-1">
                      3. Follow-up Assessment Tool
                    </span>
                    <p className="text-slate-300 leading-relaxed">{rec.follow_up_assessment}</p>
                  </div>
                </div>

                {/* Action conversion */}
                <div className="flex items-center justify-between pt-3 border-t border-slate-800 text-xs">
                  <span className="text-slate-400 font-medium">{rec.evidence}</span>
                  <button
                    onClick={() => handleCreateIntervention(rec)}
                    disabled={isCreating === rec.id}
                    className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold flex items-center gap-2 shadow-lg shadow-blue-500/20 transition-all disabled:opacity-50"
                  >
                    <CheckCircle2 className="w-4 h-4" />
                    <span>{isCreating === rec.id ? 'Creating...' : 'Adopt as CQI Intervention'}</span>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
