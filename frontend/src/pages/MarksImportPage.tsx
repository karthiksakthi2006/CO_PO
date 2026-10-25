import React, { useEffect, useState } from 'react';
import { FileSpreadsheet, Upload, Download, CheckCircle2, AlertTriangle, FileCheck, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import api from '../api/client';

export const MarksImportPage: React.FC = () => {
  const [offerings, setOfferings] = useState<any[]>([]);
  const [selectedOfferingId, setSelectedOfferingId] = useState<number>(1);
  const [assessments, setAssessments] = useState<any[]>([]);
  const [selectedAssId, setSelectedAssId] = useState<number>(1);
  const [file, setFile] = useState<File | null>(null);

  const [previewData, setPreviewData] = useState<any>(null);
  const [validationResult, setValidationResult] = useState<any>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [commitSuccess, setCommitSuccess] = useState<any>(null);
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

  // Fetch assessments for the selected offering
  useEffect(() => {
    if (selectedOfferingId) {
      api.get(`/assessments/offerings/${selectedOfferingId}`)
        .then((res) => {
          setAssessments(res.data);
          if (res.data.length > 0) {
            setSelectedAssId(res.data[0].id);
          } else {
            setSelectedAssId(0);
          }
        })
        .catch((err) => {
          console.error(err);
          setErrorMsg('Failed to load assessments for offering.');
        });
    }
  }, [selectedOfferingId]);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      setPreviewData(null);
      setValidationResult(null);
      setCommitSuccess(null);
      setErrorMsg(null);

      // Auto preview
      const formData = new FormData();
      formData.append('file', selectedFile);
      try {
        const res = await api.post('/assessments/import/preview', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        setPreviewData(res.data);
      } catch (err: any) {
        setErrorMsg('Failed to parse file. Ensure it is a valid CSV or XLSX.');
      }
    }
  };

  const handleValidate = async () => {
    if (!file || !selectedAssId) return;
    setIsProcessing(true);
    setErrorMsg(null);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('assessment_id', String(selectedAssId));
      const res = await api.post('/assessments/import/validate-marks', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setValidationResult(res.data);
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || 'Validation failed.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleCommit = async () => {
    if (!file || !selectedAssId) return;
    setIsProcessing(true);
    setErrorMsg(null);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('assessment_id', String(selectedAssId));
      const res = await api.post('/assessments/import/commit-marks', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setCommitSuccess(res.data);
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || 'Commit failed.');
    } finally {
      setIsProcessing(false);
    }
  };

  const currentOffering = offerings.find((o) => o.id === selectedOfferingId);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Assessment Marks Import Center</h1>
          <p className="text-sm text-slate-400 mt-0.5">
            Validated CSV and Excel upload for student assessment marks with row-level validation.
          </p>
        </div>

        {/* Offering Selector */}
        <div className="flex items-center gap-2 bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 self-start sm:self-auto">
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
      </div>

      {currentOffering && (
        <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <span className="font-bold text-white text-sm">{currentOffering.course_code}: {currentOffering.course_name}</span>
            <span className="px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 font-bold">
              Section {currentOffering.section} • {currentOffering.faculty_name}
            </span>
          </div>
          <span className="text-slate-400">{assessments.length} Components Available</span>
        </div>
      )}

      {commitSuccess && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
            <div>
              <div className="text-sm font-bold text-white">Import Committed Successfully!</div>
              <div className="text-xs text-emerald-400 mt-0.5">
                {commitSuccess.imported_count} student marks recorded into database transactionally.
              </div>
            </div>
          </div>
          <Link
            to="/attainment"
            className="px-3.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold flex items-center gap-1.5 transition-all"
          >
            <span>Proceed to Attainment Calculation</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      )}

      {errorMsg && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 flex items-center gap-3 text-xs">
          <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Import Steps & Controls */}
        <div className="space-y-4">
          {/* Step 1: Select Assessment */}
          <div className="glass-panel p-5 rounded-xl border border-slate-800">
            <span className="text-[10px] font-bold uppercase tracking-wider text-blue-400 mb-1 block">Step 1</span>
            <h2 className="text-sm font-bold text-white mb-2">Target Assessment</h2>
            {assessments.length === 0 ? (
              <div className="text-xs text-slate-400 py-2">
                No assessments found for this offering.{' '}
                <Link to="/assessments" className="text-blue-400 hover:underline">
                  Create an assessment first.
                </Link>
              </div>
            ) : (
              <>
                <select
                  value={selectedAssId}
                  onChange={(e) => setSelectedAssId(Number(e.target.value))}
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm text-white focus:outline-none focus:border-blue-500"
                >
                  {assessments.map((a) => (
                    <option key={a.id} value={a.id}>
                      {a.name} ({a.assessment_type})
                    </option>
                  ))}
                </select>

                <div className="mt-3 pt-3 border-t border-slate-800">
                  <a
                    href={`/api/assessments/templates/assessment-marks/${selectedAssId}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="w-full py-2 px-3 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium flex items-center justify-center gap-2 border border-slate-700 transition-colors"
                  >
                    <Download className="w-3.5 h-3.5 text-blue-400" />
                    <span>Download Sample Template</span>
                  </a>
                </div>
              </>
            )}
          </div>

          {/* Step 2: Upload File */}
          <div className="glass-panel p-5 rounded-xl border border-slate-800">
            <span className="text-[10px] font-bold uppercase tracking-wider text-blue-400 mb-1 block">Step 2</span>
            <h2 className="text-sm font-bold text-white mb-2">Upload Spreadsheet</h2>

            <label className="border-2 border-dashed border-slate-700 hover:border-blue-500 rounded-xl p-6 flex flex-col items-center justify-center text-center cursor-pointer transition-colors bg-slate-900/40">
              <Upload className="w-7 h-7 text-blue-400 mb-2" />
              <span className="text-xs font-medium text-slate-200">
                {file ? file.name : 'Choose CSV or Excel file'}
              </span>
              <span className="text-[10px] text-slate-500 mt-1">Accepts .csv, .xlsx formats up to 15MB</span>
              <input
                type="file"
                accept=".csv,.xlsx,.xls"
                onChange={handleFileChange}
                className="hidden"
              />
            </label>

            {file && (
              <div className="mt-4 flex gap-2">
                <button
                  onClick={handleValidate}
                  disabled={isProcessing || !selectedAssId}
                  className="flex-1 py-2 px-3 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition-all disabled:opacity-50"
                >
                  <FileCheck className="w-3.5 h-3.5" />
                  <span>{isProcessing ? 'Validating...' : 'Validate Marks'}</span>
                </button>
              </div>
            )}
          </div>

          {/* Step 3: Commit if Validated */}
          {validationResult && (
            <div className="glass-panel p-5 rounded-xl border border-slate-800">
              <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-400 mb-1 block">Step 3</span>
              <h2 className="text-sm font-bold text-white mb-2">Commit to Database</h2>

              <div className="space-y-2 mb-4 text-xs">
                <div className="flex justify-between py-1 border-b border-slate-800">
                  <span className="text-slate-400">Total Rows:</span>
                  <span className="font-semibold text-white">{validationResult.total_rows}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-800">
                  <span className="text-emerald-400">Valid Marks:</span>
                  <span className="font-semibold text-emerald-400">{validationResult.valid_records_count}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-800">
                  <span className="text-rose-400">Errors:</span>
                  <span className="font-semibold text-rose-400">{validationResult.error_records_count}</span>
                </div>
              </div>

              {validationResult.can_commit ? (
                <button
                  onClick={handleCommit}
                  disabled={isProcessing}
                  className="w-full py-2.5 px-4 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-lg text-xs flex items-center justify-center gap-2 shadow-lg shadow-emerald-500/20 transition-all disabled:opacity-50"
                >
                  <CheckCircle2 className="w-4 h-4" />
                  <span>{isProcessing ? 'Saving to Database...' : 'Commit Marks to Database'}</span>
                </button>
              ) : (
                <div className="p-3 bg-rose-500/10 border border-rose-500/20 rounded-lg text-rose-300 text-[11px] leading-relaxed">
                  Validation errors detected. Fix the highlighted rows in your spreadsheet before committing.
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right Column: Spreadsheet Preview & Errors */}
        <div className="lg:col-span-2 space-y-4">
          <div className="glass-panel p-5 rounded-xl border border-slate-800 min-h-[400px]">
            <h2 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
              <FileSpreadsheet className="w-4 h-4 text-blue-400" />
              <span>Spreadsheet Preview & Diagnostics</span>
            </h2>

            {/* Preview Table */}
            {previewData && (
              <div className="space-y-3">
                <div className="text-xs text-slate-400 flex items-center justify-between">
                  <span>Showing first {previewData.preview_rows.length} rows of {previewData.total_rows} total</span>
                  <span className="text-emerald-400 font-medium">Columns: {previewData.columns.join(', ')}</span>
                </div>

                <div className="overflow-x-auto border border-slate-800 rounded-lg">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-slate-900 text-slate-400 text-[10px] uppercase font-semibold">
                      <tr>
                        {previewData.columns.map((col: string, idx: number) => (
                          <th key={idx} className="py-2 px-3 border-b border-slate-800 whitespace-nowrap">{col}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800 text-slate-300">
                      {previewData.preview_rows.map((row: any, rIdx: number) => (
                        <tr key={rIdx} className="hover:bg-slate-800/30">
                          {previewData.columns.map((col: string, cIdx: number) => (
                            <td key={cIdx} className="py-2 px-3 whitespace-nowrap">{String(row[col])}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Error breakdown if any */}
            {validationResult?.errors?.length > 0 && (
              <div className="border border-rose-500/30 rounded-xl p-4 bg-rose-500/5 mt-4">
                <h3 className="text-xs font-bold text-rose-400 flex items-center gap-1.5 mb-2">
                  <AlertTriangle className="w-4 h-4" />
                  <span>Validation Issues Identified ({validationResult.errors.length})</span>
                </h3>
                <div className="max-h-48 overflow-y-auto space-y-1.5 text-xs text-slate-300 pr-2">
                  {validationResult.errors.map((err: any, idx: number) => (
                    <div key={idx} className="p-2 rounded bg-slate-900 border border-slate-800 flex items-center justify-between">
                      <span className="font-mono text-slate-400">Row {err.row} ({err.usn || 'No USN'}):</span>
                      <span className="text-rose-300 font-medium">{err.message}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {!previewData && (
              <div className="p-12 text-center text-slate-500 text-xs flex flex-col items-center justify-center">
                <FileSpreadsheet className="w-10 h-10 text-slate-600 mb-2" />
                <span>Upload a spreadsheet to preview columns and validate student scores.</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
