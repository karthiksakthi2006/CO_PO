import React, { useEffect, useState } from 'react';
import { AlertTriangle, ShieldAlert, BookOpen, Users, ArrowRight, Layers, AlertCircle } from 'lucide-react';
import { Link } from 'react-router-dom';
import api from '../api/client';

export const GapAnalysisPage: React.FC = () => {
  const [offerings, setOfferings] = useState<any[]>([]);
  const [selectedOfferingId, setSelectedOfferingId] = useState<number>(1);
  const [data, setData] = useState<any>(null);
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

  // Fetch gap analysis for selected offering
  const fetchGaps = async (offeringId: number) => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await api.get(`/gaps/offerings/${offeringId}/analysis`);
      setData(res.data);
    } catch (err: any) {
      console.error(err);
      setErrorMsg('Failed to load gap analysis diagnostics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedOfferingId) {
      fetchGaps(selectedOfferingId);
    }
  }, [selectedOfferingId]);

  const currentOffering = offerings.find((o) => o.id === selectedOfferingId);
  const coGaps = data?.co_gaps || [];
  const weakQuestions = data?.weak_questions || [];
  const disparities = data?.component_disparities || [];
  const atRiskStudents = data?.at_risk_students || [];
  const summary = data?.summary || {};

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Gap Analysis & Academic Diagnostics</h1>
          <p className="text-sm text-slate-400 mt-0.5">
            Transparent detection of learning deficits, cognitive hurdles, assessment disparities, and at-risk cohorts.
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

          <Link
            to={`/recommendations?offeringId=${selectedOfferingId}`}
            className="px-3.5 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold flex items-center gap-2 shadow-lg shadow-blue-500/20 transition-all"
          >
            <span>View Remedial Recommendations</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
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
            {summary.underperforming_cos_count || 0} Underperforming COs Detected
          </span>
        </div>
      )}

      {errorMsg && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 flex items-center gap-3 text-xs">
          <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Overview Stat Badges */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="glass-card p-4 rounded-xl border border-slate-800">
          <div className="text-xs text-slate-400">Underperforming COs</div>
          <div className="text-2xl font-bold text-rose-400 mt-1">{summary.underperforming_cos_count || 0}</div>
          <div className="text-[11px] text-slate-500 mt-0.5">Below institutional benchmark</div>
        </div>

        <div className="glass-card p-4 rounded-xl border border-slate-800">
          <div className="text-xs text-slate-400">Weak Exam Questions</div>
          <div className="text-2xl font-bold text-amber-400 mt-1">{summary.weak_questions_count || 0}</div>
          <div className="text-[11px] text-slate-500 mt-0.5">&lt; 50% student success rate</div>
        </div>

        <div className="glass-card p-4 rounded-xl border border-slate-800">
          <div className="text-xs text-slate-400">Component Disparities</div>
          <div className="text-2xl font-bold text-purple-400 mt-1">{summary.component_disparities_count || 0}</div>
          <div className="text-[11px] text-slate-500 mt-0.5">&gt; 15 pts CIE vs SEE gap</div>
        </div>

        <div className="glass-card p-4 rounded-xl border border-slate-800">
          <div className="text-xs text-slate-400">At-Risk Students</div>
          <div className="text-2xl font-bold text-blue-400 mt-1">{summary.at_risk_students_count || 0}</div>
          <div className="text-[11px] text-slate-500 mt-0.5">Failing 2+ course outcomes</div>
        </div>
      </div>

      {loading ? (
        <div className="p-8 text-center text-slate-400 text-sm">Analyzing academic gap diagnostics...</div>
      ) : coGaps.length === 0 && weakQuestions.length === 0 ? (
        <div className="p-12 text-center border border-dashed border-slate-800 rounded-2xl glass-card">
          <Layers className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
          <h2 className="text-base font-bold text-white">No Critical Gaps Detected</h2>
          <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
            All Course Outcomes for this offering are meeting or exceeding attainment targets.
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Section 1: Underperforming Course Outcomes */}
          {coGaps.length > 0 && (
            <div className="glass-panel p-5 rounded-xl border border-slate-800">
              <h2 className="text-sm font-bold text-white mb-1 flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-rose-400" />
                <span>Underperforming Course Outcomes (Target Deficit)</span>
              </h2>
              <p className="text-xs text-slate-400 mb-4">
                Identifies Course Outcomes that did not meet institutional target percentages.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {coGaps.map((g: any, idx: number) => (
                  <div key={idx} className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-mono font-bold text-white text-sm">{g.co_code}</span>
                        <span
                          className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase ${
                            g.severity === 'CRITICAL'
                              ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                              : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                          }`}
                        >
                          {g.severity} GAP
                        </span>
                      </div>
                      <p className="text-xs text-slate-300 leading-relaxed mb-3">
                        {g.educational_impact || g.description || g.evidence}
                      </p>
                    </div>

                    <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
                      <div>
                        <span className="text-slate-500 block text-[10px]">Actual vs Target</span>
                        <span className="font-bold text-white">
                          <span className="text-rose-400">{g.actual_attainment}%</span> / {g.target_attainment}%
                        </span>
                      </div>
                      <div className="text-right">
                        <span className="text-slate-500 block text-[10px]">Gap</span>
                        <span className="font-bold text-rose-400 font-mono">+{g.gap_percentage_points} pts</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Section 2: High Failure Rate Questions */}
          {weakQuestions.length > 0 && (
            <div className="glass-panel p-5 rounded-xl border border-slate-800">
              <h2 className="text-sm font-bold text-white mb-1 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                <span>High-Failure-Rate Exam Questions (&lt; 50% Success Rate)</span>
              </h2>
              <p className="text-xs text-slate-400 mb-4">
                Questions where fewer than 50% of eligible students achieved the benchmark threshold score.
              </p>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-900 text-slate-400 text-[10px] uppercase font-semibold border-b border-slate-800">
                    <tr>
                      <th className="py-3 px-4">Question & Assessment Component</th>
                      <th className="py-3 px-4">Mapped Outcome</th>
                      <th className="py-3 px-4">Student Success Rate</th>
                      <th className="py-3 px-4">Rule & Evidence</th>
                      <th className="py-3 px-4">Remedial Recommendation</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 text-slate-300">
                    {weakQuestions.map((q: any, idx: number) => (
                      <tr key={idx} className="hover:bg-slate-800/30">
                        <td className="py-3 px-4 font-semibold text-white">{q.question_number}</td>
                        <td className="py-3 px-4">
                          <span className="px-2 py-0.5 rounded text-[10px] bg-blue-500/10 text-blue-400 border border-blue-500/20 font-bold font-mono">
                            {q.mapped_co || 'CO3'}
                          </span>
                        </td>
                        <td className="py-3 px-4 font-bold text-rose-400 text-sm">
                          {q.attainment_percentage !== undefined ? `${q.attainment_percentage}%` : '0%'}
                        </td>
                        <td className="py-3 px-4 text-slate-400 max-w-xs">{q.evidence}</td>
                        <td className="py-3 px-4 text-slate-300 text-xs">{q.recommended_action}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Section 3: Assessment Component Disparities */}
          {disparities.length > 0 && (
            <div className="glass-panel p-5 rounded-xl border border-slate-800">
              <h2 className="text-sm font-bold text-white mb-1 flex items-center gap-2">
                <BookOpen className="w-4 h-4 text-purple-400" />
                <span>Assessment Component Disparities (CIE vs SEE)</span>
              </h2>
              <p className="text-xs text-slate-400 mb-4">
                Identifies evaluation disparities where continuous internal marks diverge significantly from terminal exams.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {disparities.map((d: any, idx: number) => (
                  <div key={idx} className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-xs">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-bold text-white">{d.title}</span>
                      <span className="font-mono font-bold text-purple-400">{d.difference} pts gap</span>
                    </div>
                    <div className="flex justify-between text-slate-400 py-1 border-b border-slate-800">
                      <span>CIE Attainment:</span>
                      <strong className="text-white">{d.cie_attainment}%</strong>
                    </div>
                    <div className="flex justify-between text-slate-400 py-1 border-b border-slate-800">
                      <span>SEE Attainment:</span>
                      <strong className="text-white">{d.see_attainment}%</strong>
                    </div>
                    <p className="mt-2.5 text-slate-400 leading-relaxed italic">{d.evidence}</p>
                    <p className="mt-1 text-blue-400 text-[11px]">{d.recommended_action}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Section 4: At-Risk Students Identified */}
          {atRiskStudents.length > 0 && (
            <div className="glass-panel p-5 rounded-xl border border-slate-800">
              <h2 className="text-sm font-bold text-white mb-1 flex items-center gap-2">
                <Users className="w-4 h-4 text-blue-400" />
                <span>At-Risk Students Identified for Academic Remediation</span>
              </h2>
              <p className="text-xs text-slate-400 mb-4">
                Students scoring below passing benchmarks across two or more Course Outcomes.
              </p>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-900 text-slate-400 text-[10px] uppercase font-semibold border-b border-slate-800">
                    <tr>
                      <th className="py-3 px-4">USN / Roll No</th>
                      <th className="py-3 px-4">Student Name</th>
                      <th className="py-3 px-4">Average Score</th>
                      <th className="py-3 px-4">Struggling Outcomes</th>
                      <th className="py-3 px-4">Rule & Evidence</th>
                      <th className="py-3 px-4">Support Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 text-slate-300">
                    {atRiskStudents.map((s: any, idx: number) => (
                      <tr key={idx} className="hover:bg-slate-800/30">
                        <td className="py-3 px-4 font-mono font-bold text-white">{s.usn}</td>
                        <td className="py-3 px-4 font-medium text-slate-200">{s.full_name}</td>
                        <td className="py-3 px-4 font-bold text-amber-400">{s.average_score_pct}%</td>
                        <td className="py-3 px-4">
                          <div className="flex gap-1 flex-wrap">
                            {(s.failed_cos || []).map((c: string, cIdx: number) => (
                              <span key={cIdx} className="px-1.5 py-0.5 rounded text-[10px] bg-rose-500/20 text-rose-300 border border-rose-500/30 font-bold">
                                {c}
                              </span>
                            ))}
                          </div>
                        </td>
                        <td className="py-3 px-4 text-slate-400 max-w-xs">{s.evidence}</td>
                        <td className="py-3 px-4 text-blue-400">{s.recommended_action}</td>
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
