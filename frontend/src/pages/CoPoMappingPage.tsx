import React, { useEffect, useState } from 'react';
import { Save, CheckCircle2, Info, AlertCircle, Layers } from 'lucide-react';
import { useSearchParams } from 'react-router-dom';
import api from '../api/client';

export const CoPoMappingPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [courses, setCourses] = useState<any[]>([]);
  const [selectedCourseId, setSelectedCourseId] = useState<number>(1);
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [matrixState, setMatrixState] = useState<Record<string, number>>({});
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Load courses
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
      .catch((err) => {
        console.error('Failed to load courses', err);
        setErrorMsg('Failed to load courses.');
      });
  }, [searchParams]);

  const fetchMatrix = async (courseId: number) => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await api.get(`/academic/courses/${courseId}/mappings`);
      setData(res.data);

      // Populate local matrix state
      const initialMap: Record<string, number> = {};
      const matrixObj = res.data.matrix || {};
      for (const [k, v] of Object.entries(matrixObj)) {
        initialMap[k] = (v as any).strength || 0;
      }
      setMatrixState(initialMap);
    } catch (err: any) {
      console.error(err);
      setErrorMsg('Failed to load CO-PO mapping matrix.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedCourseId) {
      fetchMatrix(selectedCourseId);
    }
  }, [selectedCourseId]);

  const handleCourseChange = (id: number) => {
    setSelectedCourseId(id);
    setSearchParams({ courseId: String(id) });
    setSaveSuccess(false);
  };

  const handleCellChange = (key: string, strength: number) => {
    setMatrixState((prev) => ({
      ...prev,
      [key]: strength,
    }));
    setSaveSuccess(false);
  };

  const handleBatchSave = async () => {
    setIsSaving(true);
    setErrorMsg(null);
    try {
      const mappingsPayload: any[] = [];
      const cos = data?.cos || [];
      const pos = data?.pos || [];
      const psos = data?.psos || [];

      for (const co of cos) {
        for (const po of pos) {
          const key = `CO_${co.id}_PO_${po.id}`;
          const strVal = matrixState[key] || 0;
          mappingsPayload.push({
            course_outcome_id: co.id,
            program_outcome_id: po.id,
            mapping_strength: strVal,
          });
        }
        for (const pso of psos) {
          const key = `CO_${co.id}_PSO_${pso.id}`;
          const strVal = matrixState[key] || 0;
          mappingsPayload.push({
            course_outcome_id: co.id,
            program_specific_outcome_id: pso.id,
            mapping_strength: strVal,
          });
        }
      }

      await api.post(`/academic/courses/${selectedCourseId}/mappings/batch`, { mappings: mappingsPayload });
      setSaveSuccess(true);
      fetchMatrix(selectedCourseId);
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || 'Failed to save mapping matrix');
    } finally {
      setIsSaving(false);
    }
  };

  const currentCourse = courses.find((c) => c.id === selectedCourseId);
  const cos = data?.cos || [];
  const pos = data?.pos || [];
  const psos = data?.psos || [];
  const stats = data?.stats || {};

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">CO-PO & CO-PSO Mapping Matrix</h1>
          <p className="text-sm text-slate-400 mt-0.5">
            Constructive alignment with NBA Washington Accord 12 Program Outcomes (PO1-PO12) & PSOs.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          {/* Course Selector */}
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
            onClick={handleBatchSave}
            disabled={isSaving || loading || cos.length === 0}
            className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold flex items-center gap-2 shadow-lg shadow-blue-500/20 transition-all disabled:opacity-50"
          >
            <Save className="w-4 h-4" />
            <span>{isSaving ? 'Saving Matrix...' : 'Save Matrix Changes'}</span>
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
          <span className="text-slate-400 font-mono">
            {stats.mapped_cells || 0} / {stats.total_cells || 0} Mapped Cells ({stats.coverage_percentage || 0}%)
          </span>
        </div>
      )}

      {saveSuccess && (
        <div className="p-3.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <span>Mapping matrix successfully updated and synchronized with accreditation calculations.</span>
        </div>
      )}

      {errorMsg && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 flex items-center gap-3 text-xs">
          <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Legend & Stats Banner */}
      <div className="glass-panel p-4 rounded-xl border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        {/* Mapping Levels Legend */}
        <div className="flex items-center gap-4 text-xs">
          <span className="font-semibold text-slate-300 flex items-center gap-1.5">
            <Info className="w-3.5 h-3.5 text-blue-400" />
            <span>Strength Scale:</span>
          </span>
          <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">0: None</span>
          <span className="px-2 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800 font-mono">1: Low</span>
          <span className="px-2 py-0.5 rounded bg-blue-900 text-blue-200 border border-blue-700 font-mono">2: Medium</span>
          <span className="px-2 py-0.5 rounded bg-indigo-700 text-white font-mono font-bold">3: High</span>
        </div>

        {/* Stats */}
        <div className="flex items-center gap-4 text-xs">
          <span className="text-slate-400">
            Total Mapped Cells: <strong className="text-white">{stats.mapped_cells || 0}</strong> / {stats.total_cells || 0}
          </span>
          <span className="px-2.5 py-0.5 rounded-full font-bold bg-blue-500/10 text-blue-400 border border-blue-500/20">
            {stats.coverage_percentage || 0}% Coverage
          </span>
        </div>
      </div>

      {loading ? (
        <div className="p-8 text-center text-slate-400 text-sm">Loading CO-PO matrix...</div>
      ) : cos.length === 0 ? (
        <div className="p-12 text-center border border-dashed border-slate-800 rounded-2xl glass-card">
          <Layers className="w-8 h-8 text-slate-600 mx-auto mb-2" />
          <h2 className="text-base font-bold text-white">No Outcomes Defined for {currentCourse?.code}</h2>
          <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
            Create Course Outcomes (COs) for this course first before defining the CO-PO correlation matrix.
          </p>
        </div>
      ) : (
        /* Interactive Matrix Table */
        <div className="glass-panel rounded-xl border border-slate-800 overflow-hidden shadow-2xl">
          <div className="overflow-x-auto">
            <table className="w-full text-center text-xs border-collapse">
              <thead>
                <tr className="bg-slate-900/80 text-slate-400 font-semibold text-[11px] border-b border-slate-800">
                  <th className="py-3 px-3 text-left sticky left-0 bg-slate-900 z-10 w-28">CO Code</th>
                  {pos.map((po: any) => (
                    <th key={po.id} className="py-3 px-2 min-w-12 border-l border-slate-800/80" title={po.title}>
                      {po.code}
                    </th>
                  ))}
                  {psos.map((pso: any) => (
                    <th key={pso.id} className="py-3 px-2 min-w-14 border-l border-slate-700 bg-indigo-950/20 text-indigo-300" title={pso.title}>
                      {pso.code}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {cos.map((co: any) => (
                  <tr key={co.id} className="hover:bg-slate-800/30">
                    <td className="py-2.5 px-3 text-left font-mono font-bold text-white sticky left-0 bg-slate-900/90 z-10 border-r border-slate-800">
                      <div>{co.code}</div>
                      <div className="text-[10px] text-slate-500 font-normal truncate max-w-28">{co.blooms_level}</div>
                    </td>

                    {/* PO Columns */}
                    {pos.map((po: any) => {
                      const cellKey = `CO_${co.id}_PO_${po.id}`;
                      const val = matrixState[cellKey] || 0;
                      return (
                        <td key={po.id} className="p-1 border-l border-slate-800/60">
                          <select
                            value={val}
                            onChange={(e) => handleCellChange(cellKey, Number(e.target.value))}
                            className={`w-11 py-1 text-center font-mono font-bold rounded border text-xs focus:outline-none transition-colors ${
                              val === 3
                                ? 'bg-indigo-600 text-white border-indigo-500'
                                : val === 2
                                ? 'bg-blue-900/80 text-blue-200 border-blue-700'
                                : val === 1
                                ? 'bg-blue-950 text-blue-300 border-blue-900'
                                : 'bg-slate-900/80 text-slate-600 border-slate-800'
                            }`}
                          >
                            <option value={0} className="bg-slate-900 text-slate-400">0</option>
                            <option value={1} className="bg-slate-900 text-blue-300">1</option>
                            <option value={2} className="bg-slate-900 text-blue-200">2</option>
                            <option value={3} className="bg-slate-900 text-white font-bold">3</option>
                          </select>
                        </td>
                      );
                    })}

                    {/* PSO Columns */}
                    {psos.map((pso: any) => {
                      const cellKey = `CO_${co.id}_PSO_${pso.id}`;
                      const val = matrixState[cellKey] || 0;
                      return (
                        <td key={pso.id} className="p-1 border-l border-slate-800/60 bg-indigo-950/10">
                          <select
                            value={val}
                            onChange={(e) => handleCellChange(cellKey, Number(e.target.value))}
                            className={`w-11 py-1 text-center font-mono font-bold rounded border text-xs focus:outline-none transition-colors ${
                              val === 3
                                ? 'bg-purple-600 text-white border-purple-500'
                                : val === 2
                                ? 'bg-purple-900/80 text-purple-200 border-purple-700'
                                : val === 1
                                ? 'bg-purple-950 text-purple-300 border-purple-900'
                                : 'bg-slate-900/80 text-slate-600 border-slate-800'
                            }`}
                          >
                            <option value={0} className="bg-slate-900 text-slate-400">0</option>
                            <option value={1} className="bg-slate-900 text-purple-300">1</option>
                            <option value={2} className="bg-slate-900 text-purple-200">2</option>
                            <option value={3} className="bg-slate-900 text-white font-bold">3</option>
                          </select>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
