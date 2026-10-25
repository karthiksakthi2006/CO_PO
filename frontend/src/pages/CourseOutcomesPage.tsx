import React, { useEffect, useState } from 'react';
import { Plus, CheckCircle2, Target, BrainCircuit, X, AlertCircle } from 'lucide-react';
import { useSearchParams } from 'react-router-dom';
import api from '../api/client';

export const CourseOutcomesPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [courses, setCourses] = useState<any[]>([]);
  const [selectedCourseId, setSelectedCourseId] = useState<number>(1);
  const [cos, setCos] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Form State
  const [newCode, setNewCode] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [newBlooms, setNewBlooms] = useState('Apply');
  const [newTarget, setNewTarget] = useState(70.0);

  // Initial load: fetch courses
  useEffect(() => {
    api.get('/academic/courses')
      .then((res) => {
        setCourses(res.data);
        const queryCourseId = searchParams.get('courseId');
        if (queryCourseId) {
          setSelectedCourseId(Number(queryCourseId));
        } else if (res.data.length > 0) {
          setSelectedCourseId(res.data[0].id);
        }
      })
      .catch((err) => console.error('Failed to load courses', err));
  }, [searchParams]);

  // Fetch COs when selected course changes
  const fetchCos = async (courseId: number) => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await api.get(`/academic/courses/${courseId}/cos`);
      setCos(res.data);
    } catch (err: any) {
      console.error(err);
      setErrorMsg('Failed to load course outcomes.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedCourseId) {
      fetchCos(selectedCourseId);
    }
  }, [selectedCourseId]);

  const handleCourseChange = (id: number) => {
    setSelectedCourseId(id);
    setSearchParams({ courseId: String(id) });
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setErrorMsg(null);
    try {
      await api.post(`/academic/courses/${selectedCourseId}/cos`, {
        course_id: selectedCourseId,
        code: newCode.trim(),
        description: newDesc.trim(),
        blooms_level: newBlooms,
        target_attainment_percentage: Number(newTarget),
      });
      setShowModal(false);
      setNewCode('');
      setNewDesc('');
      fetchCos(selectedCourseId);
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || 'Failed to create CO');
    } finally {
      setIsSubmitting(false);
    }
  };

  const currentCourse = courses.find((c) => c.id === selectedCourseId);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Course Outcomes (COs)</h1>
          <p className="text-sm text-slate-400 mt-0.5">
            Bloom's Taxonomy Cognitive Alignment, Target Benchmarks & NBA Criterion 3 Definitions.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          {/* Course Selector Dropdown */}
          <div className="flex items-center gap-2 bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5">
            <span className="text-[11px] text-slate-400 font-medium">Course:</span>
            <select
              value={selectedCourseId}
              onChange={(e) => handleCourseChange(Number(e.target.value))}
              className="bg-transparent text-xs text-white font-semibold focus:outline-none"
            >
              {courses.map((c) => (
                <option key={c.id} value={c.id} className="bg-slate-900 text-white">
                  {c.code} — {c.name}
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={() => setShowModal(true)}
            className="px-3.5 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold flex items-center gap-2 shadow-lg shadow-blue-500/20 transition-all"
          >
            <Plus className="w-4 h-4" />
            <span>Add Course Outcome</span>
          </button>
        </div>
      </div>

      {currentCourse && (
        <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <span className="font-bold text-white text-sm">{currentCourse.code}: {currentCourse.name}</span>
            <span className="px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 font-bold">
              {currentCourse.credits} Credits • Sem {currentCourse.semester_number}
            </span>
          </div>
          <span className="text-slate-400">{cos.length} Outcomes Defined</span>
        </div>
      )}

      {errorMsg && (
        <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* CO Cards Grid */}
      {loading ? (
        <div className="p-8 text-center text-slate-400 text-sm">Loading course outcomes...</div>
      ) : cos.length === 0 ? (
        <div className="p-12 text-center border border-dashed border-slate-800 rounded-2xl glass-card">
          <Target className="w-8 h-8 text-slate-600 mx-auto mb-2" />
          <h2 className="text-base font-bold text-white">No Course Outcomes Defined</h2>
          <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
            Define measurable outcome statements with Bloom's Taxonomy cognitive levels and attainment targets.
          </p>
          <button
            onClick={() => setShowModal(true)}
            className="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg inline-flex items-center gap-1.5"
          >
            <Plus className="w-4 h-4" />
            <span>Define First CO</span>
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {cos.map((co) => (
            <div key={co.id} className="glass-card p-5 rounded-xl border border-slate-800 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="text-base font-bold text-white tracking-wide">{co.code}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-xs px-2 py-0.5 rounded-full font-semibold bg-purple-500/10 text-purple-400 border border-purple-500/20 flex items-center gap-1">
                      <BrainCircuit className="w-3 h-3" />
                      <span>{co.blooms_level}</span>
                    </span>
                    <span className="text-xs px-2 py-0.5 rounded-full font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20 flex items-center gap-1">
                      <Target className="w-3 h-3" />
                      <span>{co.target_attainment_percentage}% Target</span>
                    </span>
                  </div>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">{co.description}</p>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
                <span className="flex items-center gap-1 text-emerald-400 font-medium">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>NBA Constructive Alignment Active</span>
                </span>
                <span className="font-mono text-slate-500">ID: {co.id}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add CO Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-panel p-6 rounded-2xl max-w-lg w-full border border-slate-700 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Target className="w-5 h-5 text-blue-400" />
                <span>Add Course Outcome ({currentCourse?.code})</span>
              </h3>
              <button
                onClick={() => setShowModal(false)}
                className="text-slate-400 hover:text-white p-1 rounded-lg"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleCreate} className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">CO Code</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. CO1, CO2"
                    value={newCode}
                    onChange={(e) => setNewCode(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 uppercase"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Bloom's Cognitive Level</label>
                  <select
                    value={newBlooms}
                    onChange={(e) => setNewBlooms(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
                  >
                    <option value="Remember">Remember (L1)</option>
                    <option value="Understand">Understand (L2)</option>
                    <option value="Apply">Apply (L3)</option>
                    <option value="Analyze">Analyze (L4)</option>
                    <option value="Evaluate">Evaluate (L5)</option>
                    <option value="Create">Create (L6)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Target Attainment Threshold (%)</label>
                <input
                  type="number"
                  step="0.1"
                  required
                  min={1}
                  max={100}
                  value={newTarget}
                  onChange={(e) => setNewTarget(Number(e.target.value))}
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
                />
                <span className="text-[10px] text-slate-500 mt-1 block">Institutional standard benchmark is typically 60% – 75%.</span>
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Outcome Description (Action-oriented)</label>
                <textarea
                  rows={3}
                  required
                  placeholder="e.g. Analyze normalization forms and construct BCNF schema decompositions..."
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 resize-none"
                />
              </div>

              <div className="flex items-center justify-end gap-2.5 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold transition-all disabled:opacity-50"
                >
                  {isSubmitting ? 'Creating...' : 'Save Outcome'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
