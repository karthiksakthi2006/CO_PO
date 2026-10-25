import React, { useEffect, useState } from 'react';
import { Plus, ChevronRight, AlertCircle, HelpCircle, X, Layers } from 'lucide-react';
import api from '../api/client';

export const AssessmentsPage: React.FC = () => {
  const [offerings, setOfferings] = useState<any[]>([]);
  const [selectedOfferingId, setSelectedOfferingId] = useState<number>(1);
  const [assessments, setAssessments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedAss, setSelectedAss] = useState<any>(null);
  const [questions, setQuestions] = useState<any[]>([]);
  const [cos, setCos] = useState<any[]>([]);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Modals
  const [showAssModal, setShowAssModal] = useState(false);
  const [showQModal, setShowQModal] = useState(false);

  // New Assessment Form
  const [assName, setAssName] = useState('');
  const [assType, setAssType] = useState('CIE');
  const [assWeight, setAssWeight] = useState(25.0);
  const [assMaxMarks, setAssMaxMarks] = useState(30.0);

  // New Question Form
  const [qNumber, setQNumber] = useState('');
  const [qMaxMarks, setQMaxMarks] = useState(10.0);
  const [qDesc, setQDesc] = useState('');
  const [selectedCoIds, setSelectedCoIds] = useState<number[]>([]);

  // Load all offerings
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

  // Fetch assessments and COs for the selected offering
  const fetchOfferingData = async (offeringId: number) => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const assRes = await api.get(`/assessments/offerings/${offeringId}`);
      setAssessments(assRes.data);

      const matchedOff = offerings.find((o) => o.id === offeringId);
      if (matchedOff?.course_id) {
        const cosRes = await api.get(`/academic/courses/${matchedOff.course_id}/cos`);
        setCos(cosRes.data);
      } else {
        // Fallback: fetch course from offering details
        const cosRes = await api.get('/academic/courses/1/cos');
        setCos(cosRes.data);
      }

      if (assRes.data.length > 0) {
        setSelectedAss(assRes.data[0]);
        loadQuestions(assRes.data[0].id);
      } else {
        setSelectedAss(null);
        setQuestions([]);
      }
    } catch (err: any) {
      console.error(err);
      setErrorMsg('Failed to load assessments for selected offering.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedOfferingId) {
      fetchOfferingData(selectedOfferingId);
    }
  }, [selectedOfferingId, offerings]);

  const loadQuestions = async (assId: number) => {
    try {
      const res = await api.get(`/assessments/${assId}/questions`);
      setQuestions(res.data);
    } catch (err: any) {
      console.error(err);
    }
  };

  const handleSelectAssessment = (ass: any) => {
    setSelectedAss(ass);
    loadQuestions(ass.id);
  };

  const handleCreateAssessment = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    try {
      const res = await api.post(`/assessments/offerings/${selectedOfferingId}`, {
        course_offering_id: selectedOfferingId,
        name: assName.trim(),
        assessment_type: assType,
        weight_percentage: Number(assWeight),
        max_marks: Number(assMaxMarks),
      });
      setShowAssModal(false);
      setAssName('');
      await fetchOfferingData(selectedOfferingId);
      setSelectedAss(res.data);
      loadQuestions(res.data.id);
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || 'Failed to create assessment component');
    }
  };

  const handleCreateQuestion = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAss) return;
    setErrorMsg(null);
    try {
      await api.post(`/assessments/${selectedAss.id}/questions`, {
        assessment_id: selectedAss.id,
        question_number: qNumber.trim(),
        max_marks: Number(qMaxMarks),
        description: qDesc.trim(),
        course_outcome_ids: selectedCoIds,
      });
      setShowQModal(false);
      setQNumber('');
      setQDesc('');
      setSelectedCoIds([]);
      loadQuestions(selectedAss.id);
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || 'Failed to add question');
    }
  };

  const currentOffering = offerings.find((o) => o.id === selectedOfferingId);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Examinations & Assessment Components</h1>
          <p className="text-sm text-slate-400 mt-0.5">
            Configure CIE & SEE assessment structures, question blueprints, and Bloom's CO mapping weights.
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
            onClick={() => setShowAssModal(true)}
            className="px-3.5 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold flex items-center gap-2 shadow-lg shadow-blue-500/20 transition-all"
          >
            <Plus className="w-4 h-4" />
            <span>New Assessment Component</span>
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
          <span className="text-slate-400">{assessments.length} Components Configured</span>
        </div>
      )}

      {errorMsg && (
        <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
          <span>{errorMsg}</span>
        </div>
      )}

      {loading ? (
        <div className="p-8 text-center text-slate-400 text-sm">Loading assessment components...</div>
      ) : assessments.length === 0 ? (
        <div className="p-12 text-center border border-dashed border-slate-800 rounded-2xl glass-card">
          <Layers className="w-8 h-8 text-slate-600 mx-auto mb-2" />
          <h2 className="text-base font-bold text-white">No Assessments Created</h2>
          <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
            Create assessment components such as CIE Internal Tests, Assignment Quizzes, or Semester End Exams (SEE).
          </p>
          <button
            onClick={() => setShowAssModal(true)}
            className="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg inline-flex items-center gap-1.5"
          >
            <Plus className="w-4 h-4" />
            <span>Create First Assessment</span>
          </button>
        </div>
      ) : (
        /* Main Grid: Assessments list (Left) + Questions Blueprint (Right) */
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Assessment Components List */}
          <div className="space-y-3">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
              Components Configured ({assessments.length})
            </h2>
            {assessments.map((ass) => {
              const isSelected = selectedAss?.id === ass.id;
              return (
                <div
                  key={ass.id}
                  onClick={() => handleSelectAssessment(ass)}
                  className={`p-4 rounded-xl border cursor-pointer transition-all ${
                    isSelected
                      ? 'bg-blue-600/15 border-blue-500/50 shadow-lg shadow-blue-500/10'
                      : 'glass-card border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-sm font-bold text-white">{ass.name}</span>
                    <span
                      className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider ${
                        ass.assessment_type === 'CIE'
                          ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                          : 'bg-purple-500/20 text-purple-400 border border-purple-500/30'
                      }`}
                    >
                      {ass.assessment_type}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-xs text-slate-400 mt-2 pt-2 border-t border-slate-800/60">
                    <span>Weight: <strong className="text-slate-200">{ass.weight_percentage}%</strong></span>
                    <span>Max Marks: <strong className="text-slate-200">{ass.max_marks}</strong></span>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Right: Question Blueprint & CO Mappings */}
          <div className="lg:col-span-2 space-y-4">
            <div className="glass-panel p-5 rounded-xl border border-slate-800">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800 mb-4">
                <div>
                  <h2 className="text-base font-bold text-white flex items-center gap-2">
                    <span>{selectedAss ? selectedAss.name : 'Select an Assessment'}</span>
                    {selectedAss && (
                      <span className="text-xs text-slate-400 font-normal">
                        ({questions.length} questions • Max Marks: {selectedAss.max_marks})
                      </span>
                    )}
                  </h2>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Question-level marks distribution and Course Outcome (CO) alignment matrix.
                  </p>
                </div>

                {selectedAss && (
                  <button
                    onClick={() => setShowQModal(true)}
                    className="px-3 py-1.5 rounded-lg bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 border border-blue-500/30 text-xs font-semibold flex items-center gap-1.5 transition-colors self-start sm:self-auto"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    <span>Add Question</span>
                  </button>
                )}
              </div>

              {/* Questions Table */}
              {questions.length === 0 ? (
                <div className="p-8 text-center text-slate-500 text-xs border border-dashed border-slate-800 rounded-lg">
                  No questions blueprint configured for this assessment component. Click "Add Question" to begin.
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-slate-900/60 text-slate-400 font-semibold text-[11px] uppercase border-b border-slate-800">
                      <tr>
                        <th className="py-2.5 px-3">Q#</th>
                        <th className="py-2.5 px-3">Topic / Question Description</th>
                        <th className="py-2.5 px-3">Max Marks</th>
                        <th className="py-2.5 px-3">Mapped COs</th>
                        <th className="py-2.5 px-3">Bloom's Level</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60 text-slate-300">
                      {questions.map((q) => (
                        <tr key={q.id} className="hover:bg-slate-800/30">
                          <td className="py-3 px-3 font-mono font-bold text-white">{q.question_number}</td>
                          <td className="py-3 px-3 text-slate-300">{q.description || 'General examination question'}</td>
                          <td className="py-3 px-3 font-semibold text-slate-100">{q.max_marks}</td>
                          <td className="py-3 px-3">
                            <div className="flex flex-wrap gap-1">
                              {q.mapped_cos?.length > 0 ? (
                                q.mapped_cos.map((mc: any) => (
                                  <span
                                    key={mc.co_id}
                                    className="px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 text-[10px] font-bold"
                                  >
                                    {mc.co_code}
                                  </span>
                                ))
                              ) : (
                                <span className="text-slate-500 text-[11px] italic">Unmapped</span>
                              )}
                            </div>
                          </td>
                          <td className="py-3 px-3">
                            <span className="px-2 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/20 text-[10px] font-semibold">
                              {q.mapped_cos?.[0]?.blooms_level || 'Apply'}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Create Assessment Component Modal */}
      {showAssModal && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-panel p-6 rounded-2xl max-w-md w-full border border-slate-700 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
              <h3 className="text-base font-bold text-white">Create Assessment Component</h3>
              <button
                onClick={() => setShowAssModal(false)}
                className="text-slate-400 hover:text-white p-1 rounded-lg"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleCreateAssessment} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Assessment Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. CIE Midterm Test 1, Assignment Quiz"
                  value={assName}
                  onChange={(e) => setAssName(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Component Type</label>
                  <select
                    value={assType}
                    onChange={(e) => setAssType(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
                  >
                    <option value="CIE">CIE (Continuous Internal)</option>
                    <option value="SEE">SEE (Semester End Exam)</option>
                    <option value="ASSIGNMENT">Assignment / Quiz</option>
                    <option value="LAB">Practical / Lab Test</option>
                  </select>
                </div>
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Max Marks</label>
                  <input
                    type="number"
                    min="1"
                    max="200"
                    required
                    value={assMaxMarks}
                    onChange={(e) => setAssMaxMarks(Number(e.target.value))}
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Attainment Weight (%)</label>
                <input
                  type="number"
                  min="1"
                  max="100"
                  required
                  value={assWeight}
                  onChange={(e) => setAssWeight(Number(e.target.value))}
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
                />
                <span className="text-[10px] text-slate-500 mt-1 block">Relative weight towards final Course Outcome direct score.</span>
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowAssModal(false)}
                  className="px-3.5 py-2 bg-slate-800 text-slate-300 rounded-lg font-medium hover:bg-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-500 transition-all"
                >
                  Create Assessment
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add Question Modal */}
      {showQModal && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-panel p-6 rounded-2xl max-w-md w-full border border-slate-700 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
              <h3 className="text-base font-bold text-white">Add Question to {selectedAss?.name}</h3>
              <button
                onClick={() => setShowQModal(false)}
                className="text-slate-400 hover:text-white p-1 rounded-lg"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleCreateQuestion} className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Question Number</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Q1a, Q2"
                    value={qNumber}
                    onChange={(e) => setQNumber(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500 uppercase"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Max Marks</label>
                  <input
                    type="number"
                    min="1"
                    max="100"
                    required
                    value={qMaxMarks}
                    onChange={(e) => setQMaxMarks(Number(e.target.value))}
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Topic / Question Concept</label>
                <input
                  type="text"
                  placeholder="e.g. SQL Subqueries and View constraints"
                  value={qDesc}
                  onChange={(e) => setQDesc(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1.5">Map to Course Outcomes (COs)</label>
                <div className="space-y-1.5 max-h-36 overflow-y-auto p-2 bg-slate-900 rounded-lg border border-slate-800">
                  {cos.map((c) => (
                    <label key={c.id} className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer hover:text-white">
                      <input
                        type="checkbox"
                        checked={selectedCoIds.includes(c.id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedCoIds([...selectedCoIds, c.id]);
                          } else {
                            setSelectedCoIds(selectedCoIds.filter((id) => id !== c.id));
                          }
                        }}
                        className="rounded border-slate-700 text-blue-600 focus:ring-0"
                      />
                      <span className="font-semibold text-white">{c.code}</span>
                      <span className="text-[11px] text-slate-400 truncate">({c.blooms_level}) - {c.description}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowQModal(false)}
                  className="px-3.5 py-2 bg-slate-800 text-slate-300 rounded-lg font-medium hover:bg-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-500 transition-all"
                >
                  Add Question
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
