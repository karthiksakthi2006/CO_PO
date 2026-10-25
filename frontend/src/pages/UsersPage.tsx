import React, { useEffect, useState } from 'react';
import { Users, Shield, Plus, CheckCircle2 } from 'lucide-react';
import api from '../api/client';

export const UsersPage: React.FC = () => {
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/users').then((res) => {
      setUsers(res.data);
      setLoading(false);
    });
  }, []);

  return (
    <div className="space-y-6">
      <div className="pb-2 border-b border-slate-800">
        <h1 className="text-2xl font-bold tracking-tight text-white">User & Role Administration</h1>
        <p className="text-sm text-slate-400 mt-0.5">
          Role-based access control (RBAC), department boundaries, and active status.
        </p>
      </div>

      <div className="glass-panel rounded-xl border border-slate-800 overflow-hidden shadow-2xl">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-900/80 text-slate-400 font-semibold text-[10px] uppercase border-b border-slate-800">
            <tr>
              <th className="py-3 px-4">Full Name</th>
              <th className="py-3 px-4">Institutional Email</th>
              <th className="py-3 px-4">System Role</th>
              <th className="py-3 px-4">Account Status</th>
              <th className="py-3 px-4">Created Date</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-300">
            {users.map((u) => (
              <tr key={u.id} className="hover:bg-slate-800/30">
                <td className="py-3 px-4 font-bold text-white">{u.full_name}</td>
                <td className="py-3 px-4 text-slate-400">{u.email}</td>
                <td className="py-3 px-4">
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-blue-500/10 text-blue-400 border border-blue-500/20">
                    {u.role}
                  </span>
                </td>
                <td className="py-3 px-4">
                  <span className="inline-flex items-center gap-1 text-emerald-400 font-medium">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Active</span>
                  </span>
                </td>
                <td className="py-3 px-4 text-slate-500 font-mono">{new Date(u.created_at).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
