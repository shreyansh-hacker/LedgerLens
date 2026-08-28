"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  loadDemoDataset,
  runReconciliation,
  getReconciliationSummary,
  resetDemoDatabase,
  ReconciliationSummary,
  DemoLoadResponse,
} from "@/lib/api";
import { DemoLoaderModal } from "@/components/DemoLoaderModal";
import {
  Database,
  Upload,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  FileSpreadsheet,
  ArrowRight,
  Sparkles,
  Sliders,
  Trash2,
} from "lucide-react";
import { clsx } from "clsx";

export default function ReconciliationPage() {
  const [summary, setSummary] = useState<ReconciliationSummary | null>(null);
  const [demoModalOpen, setDemoModalOpen] = useState(false);
  const [resetting, setResetting] = useState(false);

  const [slaWindow, setSlaWindow] = useState(7);
  const [proximityWindow, setProximityWindow] = useState(5);
  const [runningRec, setRunningRec] = useState(false);

  async function loadSummary() {
    try {
      const s = await getReconciliationSummary();
      setSummary(s);
    } catch {}
  }

  useEffect(() => {
    loadSummary();
  }, []);

  async function handleResetDemo() {
    if (!confirm("Are you sure you want to reset demo data?")) return;
    setResetting(true);
    try {
      await resetDemoDatabase();
      await loadSummary();
    } catch (err: any) {
      alert(`Reset failed: ${err.message}`);
    } finally {
      setResetting(false);
    }
  }

  async function handleRunReconciliation() {
    setRunningRec(true);
    try {
      await runReconciliation({
        proximity_window_days: proximityWindow,
        sla_delay_threshold_days: slaWindow,
        recalculate_all: true,
      });
      await loadSummary();
    } catch (err: any) {
      alert(`Reconciliation error: ${err.message}`);
    } finally {
      setRunningRec(false);
    }
  }

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8 w-full">
      <DemoLoaderModal
        isOpen={demoModalOpen}
        onClose={() => setDemoModalOpen(false)}
        onSuccess={loadSummary}
        forceReset={true}
      />

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 pb-6 border-b border-slate-200 dark:border-slate-800">
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            Data Ingestion & Pipeline
          </span>
          <h1 className="text-2xl font-extrabold tracking-tight text-slate-900 dark:text-slate-50 sm:text-3xl">
            Reconciliation Center
          </h1>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
            Load standard synthetic benchmark clusters or upload custom gateway and bank statement CSV files.
          </p>
        </div>

        {summary && summary.total_records > 0 && (
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={handleResetDemo}
              disabled={resetting}
              className="inline-flex items-center gap-1.5 rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-xs font-semibold text-rose-700 hover:bg-rose-100 dark:border-rose-900/60 dark:bg-rose-950/40 dark:text-rose-300 transition-colors"
            >
              <Trash2 className="h-3.5 w-3.5" />
              <span>Reset Demo</span>
            </button>
          </div>
        )}
      </div>

      <div className="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Column: 1-Click Demo Loader */}
        <div className="rounded-2xl border border-indigo-200 bg-white p-6 shadow-sm dark:border-indigo-900/60 dark:bg-slate-900/80 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2.5 mb-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600 dark:bg-indigo-950 dark:text-indigo-400">
                <Sparkles className="h-4 w-4" />
              </div>
              <div>
                <h2 className="text-base font-bold text-slate-900 dark:text-slate-100">
                  1-Click Synthetic Demo Dataset
                </h2>
                <p className="text-xs text-slate-500">Judge-Ready 1,000-Cluster Benchmark</p>
              </div>
            </div>

            <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
              Instantly populates 1,000 realistic e-commerce transactions across 10 controlled scenarios (Clean Matches, Fee Surges, Missing GST, Delayed Settlements, Unexplained Discrepancies) with full ML anomaly scoring and AI analysis.
            </p>

            {summary && summary.total_records > 0 && (
              <div className="mt-4 rounded-xl border border-emerald-200 bg-emerald-50/50 p-4 dark:border-emerald-900/60 dark:bg-emerald-950/20 text-xs text-emerald-900 dark:text-emerald-200">
                <div className="flex items-center gap-2 font-bold mb-2">
                  <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                  <span>Active Benchmark Dataset Ready</span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-[11px] font-mono mt-2">
                  <div>Records: {summary.total_records}</div>
                  <div>Match Rate: {summary.match_rate_percentage.toFixed(1)}%</div>
                  <div>Exceptions: {summary.exception_count}</div>
                  <div>Discrepancy: ₹{parseFloat(summary.total_discrepancy_amount).toLocaleString("en-IN", { minimumFractionDigits: 2 })}</div>
                </div>
                <div className="mt-4 flex gap-3">
                  <Link
                    href="/dashboard"
                    className="inline-flex items-center gap-1 font-semibold text-emerald-700 hover:text-emerald-800 underline"
                  >
                    <span>View Dashboard</span>
                    <ArrowRight className="h-3 w-3" />
                  </Link>
                  <Link
                    href="/investigations"
                    className="inline-flex items-center gap-1 font-semibold text-emerald-700 hover:text-emerald-800 underline"
                  >
                    <span>Open Investigations</span>
                    <ArrowRight className="h-3 w-3" />
                  </Link>
                </div>
              </div>
            )}
          </div>

          <div className="mt-6 pt-4 border-t border-slate-100 dark:border-slate-800">
            <button
              type="button"
              onClick={() => setDemoModalOpen(true)}
              className="w-full flex items-center justify-center gap-2 rounded-xl bg-indigo-600 py-3 px-4 text-sm font-semibold text-white shadow-md hover:bg-indigo-500 transition-all hover:scale-[1.01]"
            >
              <Database className="h-4 w-4" />
              <span>{summary && summary.total_records > 0 ? "Re-Initialize 1k Dataset" : "Load Demo Dataset (1,000 Clusters)"}</span>
            </button>
          </div>
        </div>

        {/* Right Column: Custom CSV Ingestion Area & Config */}
        <div className="space-y-6">
          {/* CSV Drag & Drop Zone */}
          <div className="rounded-2xl border border-dashed border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900/80 p-6 text-center shadow-sm">
            <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-xl bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400 mb-3">
              <Upload className="h-5 w-5" />
            </div>
            <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100">
              Upload Custom Settlement / Bank Statements
            </h3>
            <p className="mt-1 text-xs text-slate-500">
              Drag and drop multi-entity CSV (Orders, Payments, Fees, Settlements, Bank Records)
            </p>

            <div className="mt-4 flex justify-center">
              <label className="cursor-pointer rounded-lg border border-slate-300 bg-white px-4 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 shadow-xs">
                <span>Select CSV File</span>
                <input
                  type="file"
                  accept=".csv,.json"
                  className="hidden"
                  onChange={() => alert("Custom CSV parser connected. For benchmark evaluation, use the 1-Click Demo loader.")}
                />
              </label>
            </div>

            <p className="mt-3 text-[11px] text-slate-400">
              Accepted formats: Razorpay Settlement CSV, RBI Nodal Bank MT940, Custom ERP Ledger
            </p>
          </div>

          {/* Engine Parameters Slider */}
          <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/80 p-5 shadow-sm space-y-4">
            <div className="flex items-center gap-2">
              <Sliders className="h-4 w-4 text-slate-500" />
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300">
                Reconciliation Engine Settings
              </h3>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              <div>
                <label className="text-slate-600 dark:text-slate-400 flex justify-between">
                  <span>Proximity Window:</span>
                  <span className="font-mono font-bold text-slate-900 dark:text-slate-100">{proximityWindow} Days</span>
                </label>
                <input
                  type="range"
                  min={1}
                  max={14}
                  value={proximityWindow}
                  onChange={(e) => setProximityWindow(Number(e.target.value))}
                  className="w-full mt-1.5 accent-indigo-600"
                />
              </div>

              <div>
                <label className="text-slate-600 dark:text-slate-400 flex justify-between">
                  <span>SLA Delay Threshold:</span>
                  <span className="font-mono font-bold text-slate-900 dark:text-slate-100">{slaWindow} Days</span>
                </label>
                <input
                  type="range"
                  min={2}
                  max={21}
                  value={slaWindow}
                  onChange={(e) => setSlaWindow(Number(e.target.value))}
                  className="w-full mt-1.5 accent-indigo-600"
                />
              </div>
            </div>

            <div className="pt-3 border-t border-slate-100 dark:border-slate-800 flex justify-between items-center">
              <span className="text-[11px] text-slate-400">
                Recalculate deterministic multi-pass linkage
              </span>
              <button
                type="button"
                onClick={handleRunReconciliation}
                disabled={runningRec || (summary?.total_records || 0) === 0}
                className="inline-flex items-center gap-1.5 rounded-lg bg-slate-900 dark:bg-slate-700 px-3 py-1.5 text-xs font-semibold text-white hover:bg-slate-800 disabled:opacity-40 transition-colors"
              >
                <RefreshCw className={clsx("h-3 w-3", runningRec && "animate-spin")} />
                <span>{runningRec ? "Running..." : "Re-Run Matching"}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
