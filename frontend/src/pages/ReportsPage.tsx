import React, { useEffect, useState } from 'react';
import { FileText, Download, FileSpreadsheet, CheckCircle2, ShieldCheck, AlertCircle, Layers } from 'lucide-react';
import { Link } from 'react-router-dom';
import api from '../api/client';

export const ReportsPage: React.FC = () => {
  const [offerings, setOfferings] = useState<any[]>([]);
  const [selectedOfferingId, setSelectedOfferingId] = useState<number>(1);
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Load offerings
  useEffect(() => {
    api.get('/academic/offerings')
      .then((res) => {
        setOfferings(res.data);
        if (res.data.length > 0) {
          setSelectedOfferingId(res.data[0].id);
        }
      })
      .catch((err) => {
        console.error('Failed to load offerings', err);
        setErrorMsg('Failed to load course offerings.');
      });
  }, []);

  // Fetch latest attainment run for selected offering
  const fetchReportData = async (offeringId: number) => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await api.get(`/attainment/offerings/${offeringId}/latest`);
      setData(res.data);
    } catch (err: any) {
      console.error(err);
      setErrorMsg('Failed to fetch report data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedOfferingId) {
      fetchReportData(selectedOfferingId);
    }
  }, [selectedOfferingId]);

  const currentOffering = offerings.find((o) => o.id === selectedOfferingId);
  const coResults = data?.co_results || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Accreditation Reports & Dossiers</h1>
          <p className="text-sm text-slate-400 mt-0.5">
            NBA / NAAC criterion compliance reports, attainment matrices, and remedial continuous improvement files.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          {/* Offering Selector */}
          <div className="flex items-center gap-2 bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5">
            <span className="text-[11px] text-slate-400 font-medium">Offering:</span>
            <select
              value={selectedOfferingId}
              onChange={(e) => setSelectedOfferingId(Number(e.target.value))}
              className="bg-transparent text-xs text-white font-semibold focus:outline-none"
            >
              {offerings.map((o) => (
                <option key={o.id} value={o.id} className="bg-slate-900 text-white">
                  {o.course_code} - Sec {o.section} ({o.semester_name || 'Sem 5'})
                </option>
              ))}
            </select>
          </div>

          <a
            href={`/api/reports/offerings/${selectedOfferingId}/pdf`}
            target="_blank"
            rel="noopener noreferrer"
            className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold flex items-center gap-2 shadow-lg shadow-blue-500/20 transition-all"
          >
            <Download className="w-4 h-4" />
            <span>Download Official PDF</span>
          </a>

          <a
            href={`/api/reports/offerings/${selectedOfferingId}/excel`}
            target="_blank"
            rel="noopener noreferrer"
            className="px-4 py-2 rounded-lg bg-emerald-700 hover:bg-emerald-600 text-white text-xs font-semibold flex items-center gap-2 transition-all"
          >
            <FileSpreadsheet className="w-4 h-4" />
            <span>Download Excel Dataset</span>
          </a>
        </div>
      </div>

      {currentOffering && (
        <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <span className="font-bold text-white text-sm">{currentOffering.course_code}: {currentOffering.course_name}</span>
            <span className="px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 font-bold">
              Section {currentOffering.section} • {currentOffering.faculty_name}
            </span>
          </div>
          <span className="text-slate-400 font-mono">
            {data ? `Run #${data.id} • ${new Date(data.run_date).toLocaleDateString()}` : 'Awaiting Calculation'}
          </span>
        </div>
      )}

      {errorMsg && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 flex items-center gap-3 text-xs">
          <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Accreditation Dossier Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="glass-card p-5 rounded-xl border border-slate-800 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 text-blue-400 mb-2">
              <FileText className="w-5 h-5" />
              <span className="font-bold text-sm text-white">Course Attainment Report</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Official document featuring institutional metadata, course outcomes, direct/indirect aggregate scores, and NBA attainment levels.
            </p>
          </div>
          <a
            href={`/api/reports/offerings/${selectedOfferingId}/pdf`}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-4 text-xs font-semibold text-blue-400 hover:text-blue-300 flex items-center gap-1"
          >
            <span>Generate & Download</span>
            <Download className="w-3.5 h-3.5" />
          </a>
        </div>

        <div className="glass-card p-5 rounded-xl border border-slate-800 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 text-emerald-400 mb-2">
              <FileSpreadsheet className="w-5 h-5" />
              <span className="font-bold text-sm text-white">Full Analytics Excel Workbook</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Multi-tab spreadsheet with student marks, question-CO distributions, PO mapping contribution weights, and formulas.
            </p>
          </div>
          <a
            href={`/api/reports/offerings/${selectedOfferingId}/excel`}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-4 text-xs font-semibold text-emerald-400 hover:text-emerald-300 flex items-center gap-1"
          >
            <span>Download .XLSX</span>
            <Download className="w-3.5 h-3.5" />
          </a>
        </div>

        <div className="glass-card p-5 rounded-xl border border-slate-800 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 text-purple-400 mb-2">
              <ShieldCheck className="w-5 h-5" />
              <span className="font-bold text-sm text-white">CQI Remedial Dossier</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Audit log of identified attainment gaps, assigned faculty action plans, and verified post-reassessment improvement statistics.
            </p>
          </div>
          <span className="mt-4 text-xs font-semibold text-purple-400 flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Included in Official PDF</span>
          </span>
        </div>
      </div>

      {/* Live Preview Card */}
      {loading ? (
        <div className="p-8 text-center text-slate-400 text-sm">Loading report dataset...</div>
      ) : !data ? (
        <div className="p-12 text-center border border-dashed border-slate-800 rounded-2xl glass-card">
          <Layers className="w-8 h-8 text-slate-600 mx-auto mb-2" />
          <h2 className="text-base font-bold text-white">No Calculation Available For This Offering</h2>
          <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
            Please run the attainment calculation engine first to generate and download official NBA/NAAC dossiers.
          </p>
          <Link
            to="/attainment"
            className="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg inline-flex items-center gap-1.5"
          >
            <span>Go to Calculation Center</span>
          </Link>
        </div>
      ) : (
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 shadow-2xl">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 border-b border-slate-800 mb-4">
            <div>
              <h2 className="text-base font-bold text-white">Live Report Table Preview</h2>
              <div className="text-xs text-slate-400 mt-0.5">
                {currentOffering?.course_code}: {currentOffering?.course_name} • Academic Year {currentOffering?.academic_year_name || '2024-2025'}
              </div>
            </div>
            <div className="text-xs text-emerald-400 font-mono font-bold flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Status: Ready for Accreditation Audit</span>
            </div>
          </div>

          <div className="overflow-x-auto border border-slate-800 rounded-lg">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900 text-slate-400 font-semibold text-[10px] uppercase border-b border-slate-800">
                <tr>
                  <th className="py-2.5 px-3">CO Code</th>
                  <th className="py-2.5 px-3">Bloom's Taxonomy</th>
                  <th className="py-2.5 px-3">Target</th>
                  <th className="py-2.5 px-3">Direct Attainment</th>
                  <th className="py-2.5 px-3">Indirect Attainment</th>
                  <th className="py-2.5 px-3">Overall Attainment</th>
                  <th className="py-2.5 px-3">Gap (points)</th>
                  <th className="py-2.5 px-3">Attainment Level</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 text-slate-300">
                {coResults.map((co: any) => (
                  <tr key={co.id} className="hover:bg-slate-800/30">
                    <td className="py-2.5 px-3 font-bold text-white">{co.co_code}</td>
                    <td className="py-2.5 px-3">{co.blooms_level}</td>
                    <td className="py-2.5 px-3">{co.target_attainment}%</td>
                    <td className="py-2.5 px-3">{co.direct_attainment}%</td>
                    <td className="py-2.5 px-3">{co.indirect_attainment !== null ? `${co.indirect_attainment}%` : 'N/A'}</td>
                    <td className="py-2.5 px-3 font-bold text-white">{co.overall_attainment}%</td>
                    <td className="py-2.5 px-3 font-mono">
                      {co.gap_percentage_points > 0 ? (
                        <span className="text-rose-400">+{co.gap_percentage_points} pts</span>
                      ) : (
                        <span className="text-emerald-400">{co.gap_percentage_points} pts</span>
                      )}
                    </td>
                    <td className="py-2.5 px-3">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-500/20 text-blue-300">
                        Level {co.attainment_level}
                      </span>
                    </td>
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
