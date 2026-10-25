import React, { useEffect, useState } from 'react';
import { Users, Search, CheckCircle2 } from 'lucide-react';
import api from '../api/client';

export const StudentDirectoryPage: React.FC = () => {
  const [students, setStudents] = useState<any[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/academic/students').then((res) => {
      setStudents(res.data);
      setLoading(false);
    });
  }, []);

  const filtered = students.filter(
    (s) =>
      s.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      s.usn.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Student Academic Directory</h1>
          <p className="text-sm text-slate-400 mt-0.5">
            Enrolled student records, batch cohorts, and outcome performance eligibility.
          </p>
        </div>

        {/* Search */}
        <div className="relative w-full sm:w-64">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search USN or Name..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
        </div>
      </div>

      {/* Students Table */}
      <div className="glass-panel rounded-xl border border-slate-800 overflow-hidden shadow-2xl">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-900/80 text-slate-400 font-semibold text-[10px] uppercase border-b border-slate-800">
            <tr>
              <th className="py-3 px-4">USN / Roll No</th>
              <th className="py-3 px-4">Student Full Name</th>
              <th className="py-3 px-4">Email Address</th>
              <th className="py-3 px-4">Batch</th>
              <th className="py-3 px-4">Semester</th>
              <th className="py-3 px-4">Enrollment Status</th>
              <th className="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-300">
            {filtered.map((s) => (
              <tr key={s.id} className="hover:bg-slate-800/30">
                <td className="py-2.5 px-4 font-mono font-bold text-white">{s.usn}</td>
                <td className="py-2.5 px-4 font-medium text-slate-200">{s.full_name}</td>
                <td className="py-2.5 px-4 text-slate-400">{s.email || '--'}</td>
                <td className="py-2.5 px-4">{s.batch_year}</td>
                <td className="py-2.5 px-4">Semester {s.current_semester}</td>
                <td className="py-2.5 px-4">
                  <span className="inline-flex items-center gap-1 text-emerald-400 text-[11px] font-medium">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Active</span>
                  </span>
                </td>
                <td className="py-2.5 px-4 text-right">
                  <a
                    href={`/students/${s.id}`}
                    className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 border border-blue-500/30 text-[11px] font-semibold transition-colors"
                  >
                    <span>View Performance</span>
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
