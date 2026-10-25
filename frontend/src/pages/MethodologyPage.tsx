import React from 'react';
import { HelpCircle, CheckCircle2, ShieldCheck, Calculator, Target, BrainCircuit } from 'lucide-react';

export const MethodologyPage: React.FC = () => {
  return (
    <div className="space-y-6 max-w-4xl">
      <div className="pb-2 border-b border-slate-800">
        <h1 className="text-2xl font-bold tracking-tight text-white">OBE Attainment Methodology & Formula Reference</h1>
        <p className="text-sm text-slate-400 mt-0.5">
          Mathematical definitions, Bloom's cognitive taxonomy alignment, and continuous improvement formulas.
        </p>
      </div>

      {/* Philosophy Banner */}
      <div className="glass-panel p-5 rounded-xl border border-blue-500/30 bg-blue-500/5">
        <h2 className="text-sm font-bold text-white flex items-center gap-2 mb-1">
          <ShieldCheck className="w-4 h-4 text-blue-400" />
          <span>Outcome-Based Education (OBE) & UN SDG 4 Constructive Alignment</span>
        </h2>
        <p className="text-xs text-slate-300 leading-relaxed">
          OBE shifts education from traditional input-driven teaching to measurable student competencies.
          Every assessment question is mapped to a specific Course Outcome (CO) at an explicit Bloom's Taxonomy cognitive level,
          which in turn is mapped with documented strength to Program Outcomes (POs) and Program Specific Outcomes (PSOs).
        </p>
      </div>

      {/* Direct Calculation Methods */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Method A */}
        <div className="glass-panel p-5 rounded-xl border border-slate-800 space-y-3 text-xs">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800">
            <span className="font-bold text-sm text-white">Method A: Student Threshold Method</span>
            <span className="text-[10px] px-2 py-0.5 rounded font-bold uppercase bg-blue-500/10 text-blue-400 border border-blue-500/20">
              Primary Standard
            </span>
          </div>
          <p className="text-slate-300 leading-relaxed">
            Measures the proportion of eligible students who achieve at or above the designated benchmark percentage (e.g. 60%) of a question's maximum marks.
          </p>
          <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 font-mono text-[11px] text-blue-300 space-y-1">
            <div>eligible_students = valid students under policy</div>
            <div>meeting_threshold = students with score &gt;= threshold%</div>
            <div className="text-white font-bold pt-1">
              question_attainment = (meeting_threshold / eligible_students) × 100
            </div>
          </div>
        </div>

        {/* Method B */}
        <div className="glass-panel p-5 rounded-xl border border-slate-800 space-y-3 text-xs">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800">
            <span className="font-bold text-sm text-white">Method B: Normalized Score Method</span>
            <span className="text-[10px] px-2 py-0.5 rounded font-bold uppercase bg-purple-500/10 text-purple-400 border border-purple-500/20">
              Alternative Standard
            </span>
          </div>
          <p className="text-slate-300 leading-relaxed">
            Measures aggregate score yield by summing all marks scored by eligible students divided by the sum of maximum possible marks.
          </p>
          <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 font-mono text-[11px] text-purple-300 space-y-1">
            <div>total_obtained = sum(valid student marks)</div>
            <div>total_max = sum(corresponding max marks)</div>
            <div className="text-white font-bold pt-1">
              question_attainment = (total_obtained / total_max) × 100
            </div>
          </div>
        </div>
      </div>

      {/* Aggregation & CQI Formulas */}
      <div className="glass-panel p-5 rounded-xl border border-slate-800 space-y-4 text-xs">
        <h2 className="text-sm font-bold text-white">CO & PO Aggregation Formulas</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
            <strong className="text-slate-200 block mb-1">CO Direct Attainment from Questions:</strong>
            <div className="font-mono text-slate-400 text-[11px]">
              co_direct = sum(question_att_i × weight_i) / sum(weight_i)
            </div>
          </div>

          <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
            <strong className="text-slate-200 block mb-1">Direct & Indirect Combination:</strong>
            <div className="font-mono text-slate-400 text-[11px]">
              overall = (direct × direct_wt + indirect × indirect_wt) / total_wt
            </div>
          </div>

          <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
            <strong className="text-slate-200 block mb-1">Gap Detection (Percentage Points):</strong>
            <div className="font-mono text-slate-400 text-[11px]">
              gap_percentage_points = target_attainment - actual_attainment
            </div>
          </div>

          <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
            <strong className="text-slate-200 block mb-1">CQI Verified Improvement:</strong>
            <div className="font-mono text-slate-400 text-[11px]">
              improvement_points = post_reassessment_att - pre_attainment
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
