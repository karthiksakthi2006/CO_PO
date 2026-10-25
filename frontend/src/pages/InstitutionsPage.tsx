import React, { useEffect, useState } from 'react';
import { Building2, Plus, CheckCircle2 } from 'lucide-react';
import api from '../api/client';

export const InstitutionsPage: React.FC = () => {
  const [institutions, setInstitutions] = useState<any[]>([]);
  const [departments, setDepartments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.get('/academic/institutions'), api.get('/academic/departments')]).then(
      ([instRes, deptRes]) => {
        setInstitutions(instRes.data);
        setDepartments(deptRes.data);
        setLoading(false);
      }
    );
  }, []);

  return (
    <div className="space-y-6">
      <div className="pb-2 border-b border-slate-800">
        <h1 className="text-2xl font-bold tracking-tight text-white">Institutions & Academic Departments</h1>
        <p className="text-sm text-slate-400 mt-0.5">
          Campus entities, organizational hierarchy, and department head assignments.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {institutions.map((inst) => (
          <div key={inst.id} className="glass-panel p-5 rounded-xl border border-slate-800">
            <div className="flex items-center justify-between mb-2">
              <span className="font-bold text-white text-base">{inst.name}</span>
              <span className="text-xs px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 font-bold">
                {inst.code}
              </span>
            </div>
            <p className="text-xs text-slate-400">{inst.address}</p>
            <div className="mt-3 text-xs text-slate-300">
              Contact: <strong className="text-white">{inst.contact_email}</strong>
            </div>
          </div>
        ))}

        {departments.map((dept) => (
          <div key={dept.id} className="glass-panel p-5 rounded-xl border border-slate-800">
            <div className="flex items-center justify-between mb-2">
              <span className="font-bold text-white text-base">{dept.name}</span>
              <span className="text-xs px-2 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/20 font-bold">
                Dept: {dept.code}
              </span>
            </div>
            <div className="text-xs text-slate-300 mt-2">
              Head of Department: <strong className="text-white">{dept.head_name}</strong>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
