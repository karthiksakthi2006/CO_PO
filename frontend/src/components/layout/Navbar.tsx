import React from 'react';
import { Link } from 'react-router-dom';
import { Menu, Bell, User as UserIcon, LogOut, ShieldCheck } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

interface NavbarProps {
  onMenuToggle: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onMenuToggle }) => {
  const { user, logout } = useAuth();

  return (
    <header className="h-16 bg-[#0a0f1d]/90 backdrop-blur-md border-b border-slate-800/80 sticky top-0 z-30 flex items-center justify-between px-4 lg:px-8">
      {/* Left section: mobile hamburger & title */}
      <div className="flex items-center space-x-3">
        <button
          onClick={onMenuToggle}
          className="lg:hidden p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800"
          aria-label="Toggle navigation"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="hidden sm:flex items-center gap-2">
          <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">
            Fall 2024 (Sem 5)
          </span>
          <span className="text-slate-600 text-xs">•</span>
          <span className="text-xs text-slate-400 font-medium">CS501: Database Management Systems (Sec A)</span>
        </div>
      </div>

      {/* Right section: notifications & profile */}
      <div className="flex items-center space-x-3">
        {/* Academic status pill */}
        <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>OBE Calculation Engine: Active</span>
        </div>

        {/* User profile & logout */}
        <div className="flex items-center space-x-3 pl-2 border-l border-slate-800">
          <Link
            to="/profile"
            className="flex items-center space-x-2 text-right group hover:opacity-90 transition-opacity"
            title="View Profile & Security"
          >
            <div className="text-right hidden sm:block">
              <div className="text-xs font-medium text-slate-200 group-hover:text-blue-400 transition-colors">
                {user?.full_name || 'Academic User'}
              </div>
              <div className="text-[10px] text-blue-400 font-semibold">{user?.role || 'FACULTY'}</div>
            </div>

            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white text-xs font-bold ring-2 ring-transparent group-hover:ring-blue-500/50 transition-all">
              {user?.full_name ? user.full_name.charAt(0).toUpperCase() : 'U'}
            </div>
          </Link>

          <button
            onClick={logout}
            title="Sign Out"
            className="p-1.5 text-slate-400 hover:text-rose-400 rounded-lg hover:bg-rose-500/10 transition-colors"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
};
