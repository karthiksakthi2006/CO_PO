import React, { useState } from 'react';
import { User, ShieldCheck, KeyRound, Building, CheckCircle2, AlertCircle, Mail, Award } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import api from '../api/client';

export const ProfileSettingsPage: React.FC = () => {
  const { user } = useAuth();
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    setSuccessMsg(null);
    setErrorMsg(null);

    if (newPassword !== confirmPassword) {
      setErrorMsg('New password and confirmation do not match.');
      return;
    }
    if (newPassword.length < 8) {
      setErrorMsg('New password must be at least 8 characters long.');
      return;
    }

    setLoading(true);
    try {
      await api.post('/auth/change-password', {
        current_password: currentPassword,
        new_password: newPassword,
      });
      setSuccessMsg('Password updated successfully! Your account is protected.');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || 'Failed to update password.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl space-y-6">
      {/* Header */}
      <div className="pb-2 border-b border-slate-800">
        <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2.5">
          <User className="w-6 h-6 text-blue-400" />
          <span>User Profile & Security Settings</span>
        </h1>
        <p className="text-sm text-slate-400 mt-0.5">
          Manage your credentials, role privileges, and institutional affiliation.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Profile Card */}
        <div className="glass-panel p-6 rounded-xl border border-slate-800 space-y-5 shadow-xl">
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-blue-400" />
            <span>Account Details</span>
          </h2>

          <div className="flex items-center space-x-4 pb-4 border-b border-slate-800">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white text-xl font-bold shadow-lg shadow-blue-500/20">
              {user?.full_name?.charAt(0).toUpperCase()}
            </div>
            <div>
              <div className="text-base font-bold text-white">{user?.full_name}</div>
              <div className="text-xs text-blue-400 font-semibold">{user?.role}</div>
            </div>
          </div>

          <div className="space-y-3 text-xs">
            <div>
              <label className="text-slate-500 block mb-0.5">Email Address</label>
              <div className="p-2.5 bg-slate-900 border border-slate-800 rounded-lg text-slate-200 flex items-center gap-2">
                <Mail className="w-4 h-4 text-slate-500" />
                <span>{user?.email}</span>
              </div>
            </div>

            <div>
              <label className="text-slate-500 block mb-0.5">System Access Role</label>
              <div className="p-2.5 bg-slate-900 border border-slate-800 rounded-lg text-slate-200 flex items-center justify-between">
                <span>{user?.role}</span>
                <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold">
                  Active
                </span>
              </div>
            </div>

            <div>
              <label className="text-slate-500 block mb-0.5">Assigned Institution & Dept</label>
              <div className="p-2.5 bg-slate-900 border border-slate-800 rounded-lg text-slate-200 flex items-center gap-2">
                <Building className="w-4 h-4 text-slate-500" />
                <span>Apex Institute of Technology • CSE Dept</span>
              </div>
            </div>
          </div>
        </div>

        {/* Change Password Card */}
        <div className="glass-panel p-6 rounded-xl border border-slate-800 space-y-5 shadow-xl">
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
            <KeyRound className="w-4 h-4 text-blue-400" />
            <span>Update Password</span>
          </h2>

          {successMsg && (
            <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-lg text-emerald-400 text-xs flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <span>{successMsg}</span>
            </div>
          )}

          {errorMsg && (
            <div className="p-3 bg-rose-500/10 border border-rose-500/20 rounded-lg text-rose-400 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          <form onSubmit={handlePasswordChange} className="space-y-4 text-xs">
            <div>
              <label className="text-slate-400 block mb-1">Current Password</label>
              <input
                type="password"
                required
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
              />
            </div>

            <div>
              <label className="text-slate-400 block mb-1">New Password (min 8 chars)</label>
              <input
                type="password"
                required
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
              />
            </div>

            <div>
              <label className="text-slate-400 block mb-1">Confirm New Password</label>
              <input
                type="password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 px-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold rounded-lg shadow-lg shadow-blue-500/20 transition-all text-xs"
            >
              {loading ? 'Updating Credentials...' : 'Save New Password'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
export default ProfileSettingsPage;
