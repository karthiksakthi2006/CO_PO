import React, { useEffect, useState } from 'react';
import { Calendar, CheckCircle2 } from 'lucide-react';
import api from '../api/client';

export const CalendarPage: React.FC = () => {
  const [years, setYears] = useState<any[]>([]);
  const [semesters, setSemesters] = useState<any[]>([]);

  useEffect(() => {
    Promise.all([api.get('/academic/academic-years'), api.get('/academic/semesters')]).then(
      ([yearsRes, semRes]) => {
        setYears(yearsRes.data);
        setSemesters(semRes.data);
      }
    );
  }, []);

  return (
    <div className="space-y-6">
      <div className="pb-2 border-b border-slate-800">
        <h1 className="text-2xl font-bold tracking-tight text-white">Academic Calendar & Semesters</h1>
        <p className="text-sm text-slate-400 mt-0.5">
          Active academic years, semester terms, and examination schedules.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="glass-panel p-5 rounded-xl border border-slate-800">
          <h2 className="text-sm font-bold text-white mb-3">Academic Years</h2>
          <div className="space-y-2">
            {years.map((y) => (
              <div key={y.id} className="p-3 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-between text-xs">
                <span className="font-bold text-white">{y.name}</span>
                {y.is_current && (
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    Current Year
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="glass-panel p-5 rounded-xl border border-slate-800">
          <h2 className="text-sm font-bold text-white mb-3">Semesters / Terms</h2>
          <div className="space-y-2">
            {semesters.map((s) => (
              <div key={s.id} className="p-3 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-between text-xs">
                <span className="font-semibold text-white">{s.name}</span>
                <span className="text-slate-400 font-mono">Sem {s.semester_number}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
