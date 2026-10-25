import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  GraduationCap,
  ArrowLeft,
  BookOpen,
  Award,
  AlertCircle,
  CheckCircle2,
  Calendar,
  Mail,
  User,
  TrendingUp,
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
} from 'recharts';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';

export const StudentDetailPage: React.FC = () => {
  const { id } = useParams<{ id?: string }>();
  const { user, isStudent } = useAuth();
  const navigate = useNavigate();

  // If student role and no id passed, use student's own ID
  const targetStudentId = id || (isStudent ? user?.student_id : null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    if (!targetStudentId) {
      setError('No student identifier specified.');
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    api
      .get(`/academic/students/${targetStudentId}/performance`)
      .then((res) => {
        setData(res.data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.response?.data?.detail || 'Failed to load student performance data.');
        setLoading(false);
      });
  }, [targetStudentId]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-3">
        <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
        <p className="text-slate-400 text-sm">Loading student academic record...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="space-y-6">
        <button
          onClick={() => navigate(-1)}
          className="inline-flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-white"
        >
          <ArrowLeft className="w-4 h-4" /> Back
        </button>
        <div className="glass-panel p-8 rounded-xl border border-rose-500/30 text-center space-y-3">
          <AlertCircle className="w-12 h-12 text-rose-400 mx-auto" />
          <h2 className="text-lg font-bold text-white">Access Denied or Record Not Found</h2>
          <p className="text-sm text-slate-400 max-w-md mx-auto">{error}</p>
          <button
            onClick={() => navigate('/dashboard')}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white text-xs rounded-lg font-semibold"
          >
            Return to Dashboard
          </button>
        </div>
      </div>
    );
  }

  const { student, courses_performance } = data;

  return (
    <div className="space-y-6">
      {/* Back button */}
      <div>
        <button
          onClick={() => navigate(-1)}
          className="inline-flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Directory
        </button>
      </div>

      {/* Student Profile Card */}
      <div className="glass-panel p-6 rounded-xl border border-slate-800 bg-gradient-to-r from-blue-950/20 via-slate-900/40 to-indigo-950/20 shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white text-2xl font-bold shadow-lg shadow-blue-500/30">
              {student.full_name?.charAt(0).toUpperCase()}
            </div>
            <div>
              <div className="flex items-center gap-3">
                <h1 className="text-2xl font-bold text-white tracking-tight">{student.full_name}</h1>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-blue-500/20 text-blue-400 border border-blue-500/30">
                  {student.usn}
                </span>
              </div>
              <div className="flex flex-wrap items-center gap-4 mt-2 text-xs text-slate-400">
                <span className="flex items-center gap-1.5">
                  <Mail className="w-3.5 h-3.5 text-slate-500" />
                  {student.email || 'No email registered'}
                </span>
                <span className="flex items-center gap-1.5">
                  <Calendar className="w-3.5 h-3.5 text-slate-500" />
                  Cohort: {student.batch_year}
                </span>
                <span className="flex items-center gap-1.5">
                  <Award className="w-3.5 h-3.5 text-slate-500" />
                  Current Semester: {student.current_semester}
                </span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="text-right">
              <div className="text-[10px] uppercase font-semibold text-slate-400 tracking-wider">
                Enrollments
              </div>
              <div className="text-2xl font-extrabold text-white">{courses_performance?.length || 0} Courses</div>
            </div>
          </div>
        </div>
      </div>

      {/* Course Performance Breakdown */}
      <div className="space-y-6">
        {courses_performance.map((cp: any, index: number) => {
          // Prepare chart data for this course
          const chartData = cp.marks_breakdown.map((m: any) => ({
            name: `${m.assessment_name.replace('Internal Assessment ', 'IA-')} ${m.question_number}`,
            Obtained: m.is_absent ? 0 : m.marks_obtained,
            Max: m.max_marks,
            pct: m.max_marks > 0 ? Math.round(((m.marks_obtained || 0) / m.max_marks) * 100) : 0,
          }));

          const isAtRisk = cp.overall_score_percentage < 60;

          return (
            <div
              key={cp.offering_id || index}
              className="glass-panel p-6 rounded-xl border border-slate-800 space-y-6 shadow-xl"
            >
              {/* Header */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20">
                    <BookOpen className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-lg font-bold text-white">{cp.course_code}: {cp.course_name}</span>
                      <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                        Sec {cp.section}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 mt-0.5">
                      Direct assessment questions and score breakdown
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <div
                    className={`px-3 py-1.5 rounded-lg border text-xs font-bold flex items-center gap-2 ${
                      isAtRisk
                        ? 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                        : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                    }`}
                  >
                    {isAtRisk ? <AlertCircle className="w-4 h-4" /> : <CheckCircle2 className="w-4 h-4" />}
                    <span>Overall: {cp.overall_score_percentage}%</span>
                    <span className="text-[10px] font-medium opacity-80">
                      ({isAtRisk ? 'Needs Intervention' : 'Target Achieved'})
                    </span>
                  </div>
                </div>
              </div>

              {/* Chart */}
              {chartData.length > 0 && (
                <div className="space-y-2">
                  <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                    Question-Level Marks vs Max Marks
                  </h3>
                  <div className="h-56 w-full pt-2">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                        <XAxis dataKey="name" stroke="#64748b" tick={{ fontSize: 10 }} interval={0} angle={-25} textAnchor="end" />
                        <YAxis stroke="#64748b" tick={{ fontSize: 10 }} />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: '#0f172a',
                            borderColor: '#334155',
                            borderRadius: '0.5rem',
                            fontSize: '11px',
                          }}
                        />
                        <Bar dataKey="Max" fill="#334155" radius={[4, 4, 0, 0]} name="Max Marks" />
                        <Bar dataKey="Obtained" fill="#3b82f6" radius={[4, 4, 0, 0]} name="Marks Obtained" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}

              {/* Table of Marks */}
              <div className="overflow-x-auto rounded-lg border border-slate-800">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-900/90 text-slate-400 font-semibold text-[10px] uppercase border-b border-slate-800">
                    <tr>
                      <th className="py-2.5 px-4">Assessment</th>
                      <th className="py-2.5 px-4">Question</th>
                      <th className="py-2.5 px-4 text-right">Max Marks</th>
                      <th className="py-2.5 px-4 text-right">Marks Scored</th>
                      <th className="py-2.5 px-4 text-right">Performance %</th>
                      <th className="py-2.5 px-4 text-center">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 text-slate-300">
                    {cp.marks_breakdown.map((m: any, idx: number) => {
                      const scorePct =
                        m.max_marks > 0 && !m.is_absent && m.marks_obtained !== null
                          ? Math.round((m.marks_obtained / m.max_marks) * 100)
                          : 0;

                      return (
                        <tr key={idx} className="hover:bg-slate-800/20">
                          <td className="py-2 px-4 font-medium text-white">{m.assessment_name}</td>
                          <td className="py-2 px-4 font-mono text-slate-300">{m.question_number}</td>
                          <td className="py-2 px-4 text-right font-mono text-slate-400">{m.max_marks}</td>
                          <td className="py-2 px-4 text-right font-mono font-bold text-white">
                            {m.is_absent ? (
                              <span className="text-rose-400">ABS</span>
                            ) : m.marks_obtained !== null ? (
                              m.marks_obtained
                            ) : (
                              '--'
                            )}
                          </td>
                          <td className="py-2 px-4 text-right font-mono">
                            {m.is_absent ? (
                              <span className="text-rose-400">0%</span>
                            ) : (
                              <span
                                className={
                                  scorePct >= 70
                                    ? 'text-emerald-400 font-bold'
                                    : scorePct >= 50
                                    ? 'text-amber-400'
                                    : 'text-rose-400 font-bold'
                                }
                              >
                                {scorePct}%
                              </span>
                            )}
                          </td>
                          <td className="py-2 px-4 text-center">
                            {m.is_absent ? (
                              <span className="px-2 py-0.5 rounded text-[10px] bg-rose-500/20 text-rose-400 font-semibold">
                                Absent
                              </span>
                            ) : scorePct >= 60 ? (
                              <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-500/20 text-emerald-400 font-semibold">
                                Satisfied
                              </span>
                            ) : (
                              <span className="px-2 py-0.5 rounded text-[10px] bg-rose-500/20 text-rose-400 font-semibold">
                                Deficient
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
          );
        })}
      </div>
    </div>
  );
};
export default StudentDetailPage;
