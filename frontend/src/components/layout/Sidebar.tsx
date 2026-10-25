import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  GraduationCap,
  Network,
  BookOpen,
  FileSpreadsheet,
  Calculator,
  AlertTriangle,
  Lightbulb,
  CheckCircle2,
  FileText,
  Users,
  Settings,
  HelpCircle,
  TrendingUp,
  Building2,
  Calendar,
  Award,
  ShieldCheck,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

interface NavItemProps {
  to: string;
  icon: React.ElementType;
  label: string;
  badge?: string;
}

const NavItem: React.FC<NavItemProps> = ({ to, icon: Icon, label, badge }) => (
  <NavLink
    to={to}
    className={({ isActive }) =>
      `flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm font-medium transition-colors ${
        isActive
          ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30'
          : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
      }`
    }
  >
    <div className="flex items-center space-x-3">
      <Icon className="w-4 h-4 shrink-0" />
      <span>{label}</span>
    </div>
    {badge && (
      <span className="text-[10px] px-1.5 py-0.5 rounded font-bold uppercase bg-blue-500/20 text-blue-300 border border-blue-500/30">
        {badge}
      </span>
    )}
  </NavLink>
);

export const Sidebar: React.FC<{ isOpen: boolean; onClose: () => void }> = ({ isOpen, onClose }) => {
  const { isSuperAdmin, isFaculty, isStudent } = useAuth();

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 w-64 bg-[#0a0f1d] border-r border-slate-800/80 flex flex-col transition-transform duration-300 lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand Header */}
        <div className="h-16 flex items-center px-5 border-b border-slate-800/80">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
              <GraduationCap className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="font-bold text-sm tracking-wide text-white flex items-center gap-1.5">
                CO-ATTAIN <span className="text-xs px-1 rounded bg-blue-500/20 text-blue-400 font-mono">PRO</span>
              </div>
              <div className="text-[10px] text-slate-400 tracking-wider">OBE ACCREDITATION AI</div>
            </div>
          </div>
        </div>

        {/* Navigation Links */}
        <div className="flex-1 overflow-y-auto px-3.5 py-4 space-y-6">
          {/* Analytics Overview */}
          <div>
            <div className="px-3 text-[11px] font-semibold tracking-wider uppercase text-slate-500 mb-2">
              Analytics & Trends
            </div>
            <div className="space-y-1">
              <NavItem to="/dashboard" icon={LayoutDashboard} label="Live Dashboard" />
              <NavItem to="/semester-trends" icon={TrendingUp} label="Semester Trends" />
            </div>
          </div>

          {/* Outcomes & Curriculum */}
          <div>
            <div className="px-3 text-[11px] font-semibold tracking-wider uppercase text-slate-500 mb-2">
              Curriculum & Outcomes
            </div>
            <div className="space-y-1">
              <NavItem to="/outcomes/cos" icon={BookOpen} label="Course Outcomes (CO)" />
              <NavItem to="/outcomes/mapping" icon={Network} label="CO-PO Mapping Matrix" badge="OBE" />
              <NavItem to="/courses" icon={BookOpen} label="Courses & Offerings" />
            </div>
          </div>

          {/* Assessments & Import */}
          <div>
            <div className="px-3 text-[11px] font-semibold tracking-wider uppercase text-slate-500 mb-2">
              Assessments & Marks
            </div>
            <div className="space-y-1">
              <NavItem to="/assessments" icon={FileSpreadsheet} label="Examinations & Tests" />
              <NavItem to="/marks/import" icon={FileSpreadsheet} label="Spreadsheet Import" badge="CSV/XLS" />
            </div>
          </div>

          {/* Attainment Analytics */}
          <div>
            <div className="px-3 text-[11px] font-semibold tracking-wider uppercase text-slate-500 mb-2">
              Attainment Engine
            </div>
            <div className="space-y-1">
              <NavItem to="/attainment" icon={Calculator} label="Calculation Center" badge="Run" />
              <NavItem to="/gaps" icon={AlertTriangle} label="Gap Analysis Explorer" />
              <NavItem to="/recommendations" icon={Lightbulb} label="AI Recommendations" />
              <NavItem to="/interventions" icon={CheckCircle2} label="Continuous Quality (CQI)" />
            </div>
          </div>

          {/* Reports & Exports */}
          <div>
            <div className="px-3 text-[11px] font-semibold tracking-wider uppercase text-slate-500 mb-2">
              Accreditation
            </div>
            <div className="space-y-1">
              <NavItem to="/reports" icon={FileText} label="NBA/NAAC Reports" badge="PDF" />
              <NavItem to="/methodology" icon={HelpCircle} label="OBE Methodology" />
            </div>
          </div>

          {/* Student Access */}
          {isStudent && (
            <div>
              <div className="px-3 text-[11px] font-semibold tracking-wider uppercase text-slate-500 mb-2">
                Student Portal
              </div>
              <div className="space-y-1">
                <NavItem to="/my-performance" icon={Award} label="My Academic Record" badge="Scores" />
              </div>
            </div>
          )}

          {/* Administration */}
          {(isSuperAdmin || isFaculty) && (
            <div>
              <div className="px-3 text-[11px] font-semibold tracking-wider uppercase text-slate-500 mb-2">
                Administration
              </div>
              <div className="space-y-1">
                <NavItem to="/students" icon={Users} label="Student Directory" />
                {isSuperAdmin && (
                  <>
                    <NavItem to="/institutions" icon={Building2} label="Institutions & Depts" />
                    <NavItem to="/calendar" icon={Calendar} label="Academic Calendar" />
                    <NavItem to="/users" icon={Settings} label="User Roles & Access" />
                    <NavItem to="/audit" icon={ShieldCheck} label="System Audit Logs" badge="Trace" />
                  </>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Footer info */}
        <div className="p-3.5 border-t border-slate-800/80 bg-[#070b14]/50">
          <div className="text-[11px] text-slate-400">UN SDG 4 Aligned</div>
          <div className="text-[10px] text-slate-500">Quality Education • v1.0.0</div>
        </div>
      </aside>
    </>
  );
};
