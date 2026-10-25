import React, { useEffect, useState } from 'react';
import { CheckCircle2, AlertTriangle, TrendingUp, Plus, ShieldCheck, History, X, AlertCircle, Layers } from 'lucide-react';
import { useSearchParams } from 'react-router-dom';
import api from '../api/client';

export const InterventionsPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [offerings, setOfferings] = useState<any[]>([]);
  const [selectedOfferingId, setSelectedOfferingId] = useState<number>(1);
  const [interventions, setInterventions] = useState<any[]>([]);
  const [cos, setCos] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // New Intervention Modal
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newCoId, setNewCoId] = useState<number>(1);
  const [newGap, setNewGap] = useState(12.5);
  const [newSeverity, setNewSeverity] = useState('HIGH');
  const [newRootCause, setNewRootCause] = useState('');
  const [newActionPlan, setNewActionPlan] = useState('');
  const [newPedagogicalTool, setNewPedagogicalTool] = useState('Guided Problem-Solving Tutorials');
  const [newPreAttainment, setNewPreAttainment] = useState(55.0);

  // Reassessment Modal
  const [selectedIntId, setSelectedIntId] = useState<number | null>(null);
  const [reassName, setReassName] = useState('');
  const [totalStudents, setTotalStudents] = useState(25);
  const [passedStudents, setPassedStudents] = useState(20);
  const [avgScore, setAvgScore] = useState(18.0);
  const [reassAttainment, setReassAttainment] = useState(80.0);
  const [notes, setNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

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

  // Fetch interventions and COs for selected offering
  const fetchInterventions = async (offeringId: number) => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await api.get(`/interventions/offerings/${offeringId}`);
      setInterventions(res.data);

      const matched = offerings.find((o) => o.id === offeringId);
      if (matched?.course_id) {
        const cosRes = await api.get(`/academic/courses/${matched.course_id}/cos`);
        setCos(cosRes.data);
        if (cosRes.data.length > 0) setNewCoId(cosRes.data[0].id);
      }
    } catch (err: any) {
      console.error(err);
      setErrorMsg('Failed to load interventions.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedOfferingId) {
      fetchInterventions(selectedOfferingId);
    }
  }, [selectedOfferingId, offerings]);

  const handleOfferingChange = (id: number) => {
    setSelectedOfferingId(id);
    setSearchParams({ offeringId: String(id) });
  };

  const handleCreateIntervention = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setErrorMsg(null);
    try {
      await api.post('/interventions', {
        course_offering_id: selectedOfferingId,
        course_outcome_id: Number(newCoId),
        gap_percentage_points: Number(newGap),
        severity: newSeverity,
        root_cause_analysis: newRootCause.trim(),
        action_plan: newActionPlan.trim(),
        pedagogical_tool: newPedagogicalTool.trim(),
        pre_intervention_attainment: Number(newPreAttainment),
      });
      setShowCreateModal(false);
      setNewRootCause('');
      setNewActionPlan('');
      fetchInterventions(selectedOfferingId);
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || 'Failed to create intervention');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRecordReassessment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedIntId) return;
    setIsSubmitting(true);
    setErrorMsg(null);
    try {
      await api.post(`/interventions/${selectedIntId}/reassessments`, {
        intervention_id: selectedIntId,
        assessment_name: reassName.trim(),
        total_students: Number(totalStudents),
        students_passed: Number(passedStudents),
        average_score: Number(avgScore),
        reassessment_attainment: Number(reassAttainment),
        notes: notes.trim(),
      });
      setSelectedIntId(null);
      setReassName('');
      setNotes('');
      fetchInterventions(selectedOfferingId);
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || 'Failed to record reassessment');
    } finally {
      setIsSubmitting(false);
    }
  };

  const currentOffering = offerings.find((o) => o.id === selectedOfferingId);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Continuous Quality Improvement (CQI)</h1>
          <p className="text-sm text-slate-400 mt-0.5">
            Remedial teaching tracking, reassessment verification, and measurable attainment improvement.
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

          <button
            onClick={() => setShowCreateModal(true)}
            className="px-3.5 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold flex items-center gap-2 shadow-lg shadow-blue-500/20 transition-all"
          >
            <Plus className="w-4 h-4" />
            <span>Create Remedial Plan</span>
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
          <span className="text-slate-400">{interventions.length} Interventions Tracked</span>
        </div>
      )}

      {errorMsg && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 flex items-center gap-3 text-xs">
          <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Interventions List */}
      {loading ? (
        <div className="p-8 text-center text-slate-400 text-sm">Loading CQI intervention records...</div>
      ) : interventions.length === 0 ? (
        <div className="p-12 text-center border border-dashed border-slate-800 rounded-2xl glass-card">
          <ShieldCheck className="w-8 h-8 text-slate-600 mx-auto mb-2" />
          <h2 className="text-base font-bold text-white">No Remedial Plans Recorded</h2>
          <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
            Create an intervention plan manually or adopt targeted pedagogical recommendations from the Recommendations Center.
          </p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg inline-flex items-center gap-1.5"
          >
            <Plus className="w-4 h-4" />
            <span>Create First Remedial Plan</span>
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {interventions.map((item) => {
            const isCompleted = item.status === 'COMPLETED';
            const hasPost = item.post_intervention_attainment !== null;
            const improvement = item.improvement_percentage_points;

            return (
              <div key={item.id} className="glass-panel p-6 rounded-2xl border border-slate-800 shadow-xl">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800 mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-xl bg-blue-500/10 text-blue-400 font-bold flex items-center justify-center">
                      {item.co_code}
                    </div>
                    <div>
                      <h2 className="text-base font-bold text-white">
                        Remedial Action for {item.co_code} ({item.gap_percentage_points} pts gap)
                      </h2>
                      <div className="text-xs text-slate-400 mt-0.5">
                        Assigned Faculty: <strong className="text-slate-200">{item.assigned_faculty_name}</strong> • Tool:{' '}
                        <strong className="text-purple-300">{item.pedagogical_tool}</strong>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <span
                      className={`text-[10px] px-2.5 py-1 rounded-full font-bold uppercase ${
                        isCompleted
                          ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                          : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                      }`}
                    >
                      {item.status}
                    </span>
                    {item.effectiveness_rating !== 'PENDING_REASSESSMENT' && (
                      <span className="text-[10px] px-2.5 py-1 rounded-full font-bold bg-blue-500/20 text-blue-300 border border-blue-500/30 uppercase">
                        {item.effectiveness_rating}
                      </span>
                    )}
                  </div>
                </div>

                {/* Attainment Progression Card */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 p-4 rounded-xl bg-slate-900/60 border border-slate-800 mb-4 text-xs">
                  <div>
                    <span className="text-slate-400 block text-[11px]">Pre-Intervention Attainment</span>
                    <span className="text-lg font-bold text-rose-400">{item.pre_intervention_attainment}%</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[11px]">Post-Intervention Attainment</span>
                    <span className="text-lg font-bold text-white">
                      {hasPost ? `${item.post_intervention_attainment}%` : 'Pending Reassessment'}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[11px]">Measured Improvement</span>
                    <span className="text-lg font-bold text-emerald-400">
                      {improvement !== null ? `+${improvement} percentage points` : '--'}
                    </span>
                  </div>
                </div>

                {/* Action Plan Details */}
                <div className="text-xs space-y-2 text-slate-300 mb-4">
                  <div>
                    <strong className="text-slate-400 block mb-0.5">Root Cause Analysis:</strong>
                    {item.root_cause_analysis}
                  </div>
                  <div>
                    <strong className="text-slate-400 block mb-0.5">Remedial Action Plan Executed:</strong>
                    {item.action_plan}
                  </div>
                </div>

                {/* Reassessments List */}
                {item.reassessments?.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-slate-800">
                    <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                      <History className="w-3.5 h-3.5 text-blue-400" />
                      <span>Reassessment Records</span>
                    </div>
                    <div className="space-y-1.5 text-xs">
                      {item.reassessments.map((r: any) => (
                        <div key={r.id} className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-between">
                          <div>
                            <span className="font-semibold text-white">{r.assessment_name}</span>
                            <span className="text-slate-400 ml-2">({r.students_passed} / {r.total_students} students passed)</span>
                          </div>
                          <div className="flex items-center gap-3">
                            <span className="font-bold text-emerald-400">{r.reassessment_attainment}% Attainment</span>
                            <span className="text-slate-500 font-mono text-[10px]">{new Date(r.conduct_date).toLocaleDateString()}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Action Button */}
                <div className="mt-4 pt-3 border-t border-slate-800 flex justify-end">
                  <button
                    onClick={() => {
                      setSelectedIntId(item.id);
                      setReassName(`Reassessment Test for ${item.co_code}`);
                    }}
                    className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center gap-1.5 border border-slate-700 transition-colors"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    <span>Record Reassessment Exam</span>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Create Intervention Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-panel p-6 rounded-2xl max-w-lg w-full border border-slate-700 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-blue-400" />
                <span>Create Remedial Intervention Plan</span>
              </h3>
              <button
                onClick={() => setShowCreateModal(false)}
                className="text-slate-400 hover:text-white p-1 rounded-lg"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleCreateIntervention} className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Target Outcome</label>
                  <select
                    value={newCoId}
                    onChange={(e) => setNewCoId(Number(e.target.value))}
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
                  >
                    {cos.map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.code} ({c.blooms_level})
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Severity</label>
                  <select
                    value={newSeverity}
                    onChange={(e) => setNewSeverity(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
                  >
                    <option value="MODERATE">Moderate Gap (&lt;10 pts)</option>
                    <option value="HIGH">High Gap (10-20 pts)</option>
                    <option value="CRITICAL">Critical Gap (&gt;=20 pts)</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Measured Gap (pts)</label>
                  <input
                    type="number"
                    step="0.1"
                    required
                    value={newGap}
                    onChange={(e) => setNewGap(Number(e.target.value))}
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Pre-Attainment (%)</label>
                  <input
                    type="number"
                    step="0.1"
                    required
                    value={newPreAttainment}
                    onChange={(e) => setNewPreAttainment(Number(e.target.value))}
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Pedagogical Tool / Method</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Simulation Lab & Guided Problem-Solving Recitation"
                  value={newPedagogicalTool}
                  onChange={(e) => setNewPedagogicalTool(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Root Cause Analysis</label>
                <textarea
                  rows={2}
                  required
                  placeholder="e.g. Students struggled with multi-table JOIN optimization and subquery indexing..."
                  value={newRootCause}
                  onChange={(e) => setNewRootCause(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500 resize-none"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Remedial Action Plan</label>
                <textarea
                  rows={2}
                  required
                  placeholder="e.g. Conduct 3 tutorial recitation sessions with hands-on practice problems..."
                  value={newActionPlan}
                  onChange={(e) => setNewActionPlan(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500 resize-none"
                />
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-3.5 py-2 bg-slate-800 text-slate-300 rounded-lg font-medium hover:bg-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-500 transition-all disabled:opacity-50"
                >
                  {isSubmitting ? 'Saving...' : 'Create Plan'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Record Reassessment Modal */}
      {selectedIntId && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-panel p-6 rounded-2xl max-w-md w-full border border-slate-700 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
              <h3 className="text-base font-bold text-white">Record Post-Remedial Exam Results</h3>
              <button
                onClick={() => setSelectedIntId(null)}
                className="text-slate-400 hover:text-white p-1 rounded-lg"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleRecordReassessment} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Assessment Name</label>
                <input
                  type="text"
                  required
                  value={reassName}
                  onChange={(e) => setReassName(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Total Students</label>
                  <input
                    type="number"
                    min="1"
                    required
                    value={totalStudents}
                    onChange={(e) => setTotalStudents(Number(e.target.value))}
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Students Passed</label>
                  <input
                    type="number"
                    min="0"
                    required
                    value={passedStudents}
                    onChange={(e) => setPassedStudents(Number(e.target.value))}
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Average Score</label>
                  <input
                    type="number"
                    step="0.1"
                    required
                    value={avgScore}
                    onChange={(e) => setAvgScore(Number(e.target.value))}
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Reassessment Attainment (%)</label>
                  <input
                    type="number"
                    step="0.1"
                    required
                    value={reassAttainment}
                    onChange={(e) => setReassAttainment(Number(e.target.value))}
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Observation Notes</label>
                <textarea
                  rows={2}
                  placeholder="e.g. 20 out of 25 students achieved target threshold after tutorial sessions..."
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500 resize-none"
                />
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setSelectedIntId(null)}
                  className="px-3.5 py-2 bg-slate-800 text-slate-300 rounded-lg font-medium hover:bg-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-2 bg-emerald-600 text-white rounded-lg font-semibold hover:bg-emerald-500 transition-all disabled:opacity-50"
                >
                  {isSubmitting ? 'Recording...' : 'Commit Reassessment'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
