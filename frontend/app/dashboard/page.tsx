"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  getReconciliationSummary,
  getReconciliationResults,
  getAnomalySummary,
  ReconciliationSummary,
  ReconciliationItem,
  AnomalySummary,
} from "@/lib/api";
import { MetricCard } from "@/components/MetricCard";
import { StatusBadge } from "@/components/StatusBadge";
import {
  FileSpreadsheet,
  AlertTriangle,
  CheckCircle2,
  Cpu,
  Layers,
  ArrowUpRight,
  RefreshCw,
  Database,
  ArrowRight,
} from "lucide-react";
import { clsx } from "clsx";

export default function DashboardPage() {
  const [recSummary, setRecSummary] = useState<ReconciliationSummary | null>(null);
  const [anomSummary, setAnomSummary] = useState<AnomalySummary | null>(null);
  const [topExceptions, setTopExceptions] = useState<ReconciliationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadDashboardData() {
    setLoading(true);
    setError(null);
    try {
      const [sumData, anomData, items] = await Promise.all([
        getReconciliationSummary(),
        getAnomalySummary().catch(() => null),
        getReconciliationResults({ has_discrepancy: true, limit: 6 }).catch(() => []),
      ]);

      setRecSummary(sumData);
      setAnomSummary(anomData);
      setTopExceptions(items);
    } catch (err: any) {
      setError(err.message || "Failed to load dashboard metrics");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDashboardData();
  }, []);

  const totalRecords = recSummary?.total_records || 0;
  const matchedCount = recSummary?.matched_count || 0;
  const exceptionCount = recSummary?.exception_count || 0;
  const matchRate = recSummary?.match_rate_percentage || 0;

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8 w-full">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 pb-6 border-b border-slate-200 dark:border-slate-800">
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            Financial Operations
          </span>
          <h1 className="text-2xl font-extrabold tracking-tight text-slate-900 dark:text-slate-50 sm:text-3xl">
            Reconciliation Overview
          </h1>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={loadDashboardData}
            disabled={loading}
            className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-200 dark:hover:bg-slate-800 transition-colors shadow-xs"
          >
            <RefreshCw className={clsx("h-3.5 w-3.5", loading && "animate-spin")} />
            <span>Refresh</span>
          </button>

          <Link
            href="/reconciliation"
            className="inline-flex items-center gap-1.5 rounded-lg bg-indigo-600 px-3.5 py-2 text-xs font-semibold text-white shadow-sm hover:bg-indigo-500 transition-colors"
          >
            <Database className="h-3.5 w-3.5" />
            <span>Load Demo Data</span>
          </Link>
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div className="mt-6 rounded-xl border border-rose-200 bg-rose-50 p-4 text-xs text-rose-800 dark:border-rose-900/60 dark:bg-rose-950/40 dark:text-rose-200">
          <div className="flex items-center justify-between">
            <span>Unable to load live backend data: {error}</span>
            <button
              onClick={loadDashboardData}
              className="font-semibold underline hover:text-rose-900"
            >
              Retry
            </button>
          </div>
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && totalRecords === 0 && (
        <div className="mt-8 rounded-2xl border border-dashed border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900/40 p-12 text-center">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-50 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-400 mb-4">
            <Database className="h-6 w-6" />
          </div>
          <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">
            No Reconciliation Records Found
          </h3>
          <p className="mt-2 text-xs text-slate-500 max-w-sm mx-auto">
            Load the 1,000-cluster synthetic benchmark dataset to inspect live multi-pass reconciliation, anomaly scoring, and Groq AI investigations.
          </p>
          <div className="mt-6">
            <Link
              href="/reconciliation"
              className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-5 py-2.5 text-xs font-semibold text-white shadow-md hover:bg-indigo-500 transition-all"
            >
              <span>Go to Demo Center</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>
        </div>
      )}

      {/* Main Content */}
      {totalRecords > 0 && (
        <div className="mt-6 space-y-6">
          {/* Top KPI Metric Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <MetricCard
              title="Records Processed"
              value={totalRecords.toLocaleString()}
              subtext="100% Deterministic Coverage"
              icon={FileSpreadsheet}
              variant="default"
            />
            <MetricCard
              title="Match Rate"
              value={`${matchRate.toFixed(1)}%`}
              subtext={`${matchedCount.toLocaleString()} balanced records`}
              icon={CheckCircle2}
              variant={matchRate >= 90 ? "success" : "warning"}
            />
            <MetricCard
              title="Exceptions & Discrepancies"
              value={`₹${parseFloat(recSummary?.total_discrepancy_amount || "0").toLocaleString("en-IN", { minimumFractionDigits: 2 })}`}
              subtext={`${exceptionCount} transactions with variances`}
              icon={AlertTriangle}
              variant={exceptionCount > 0 ? "danger" : "success"}
            />
            <MetricCard
              title="ML Anomalies Flagged"
              value={(anomSummary?.anomalies_detected || 0).toLocaleString()}
              subtext={`Avg score: ${anomSummary?.avg_normalized_score || 0}/100`}
              icon={Cpu}
              variant="info"
            />
          </div>

          {/* Secondary Row: Status Distribution & Anomaly Distribution */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Reconciliation Health Breakdown */}
            <div className="lg:col-span-2 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 p-5 shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100">
                    Reconciliation Status Breakdown
                  </h3>
                  <p className="text-xs text-slate-500">Distribution of observable settlement states</p>
                </div>
                <span className="text-xs font-mono font-semibold text-slate-700 dark:text-slate-300">
                  {totalRecords} Total Records
                </span>
              </div>

              {/* Progress visual bar */}
              <div className="h-3 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800 flex">
                <div
                  style={{ width: `${(matchedCount / totalRecords) * 100}%` }}
                  className="bg-emerald-500"
                  title={`Matched: ${matchedCount}`}
                />
                <div
                  style={{ width: `${((recSummary?.missing_bank_count || 0) / totalRecords) * 100}%` }}
                  className="bg-amber-500"
                  title={`Missing Bank: ${recSummary?.missing_bank_count}`}
                />
                <div
                  style={{ width: `${((recSummary?.missing_settlement_count || 0) / totalRecords) * 100}%` }}
                  className="bg-rose-500"
                  title={`Missing Settlement: ${recSummary?.missing_settlement_count}`}
                />
                <div
                  style={{ width: `${((recSummary?.duplicate_count || 0) / totalRecords) * 100}%` }}
                  className="bg-purple-500"
                  title={`Duplicate: ${recSummary?.duplicate_count}`}
                />
                <div
                  style={{ width: `${((recSummary?.review_count || 0) / totalRecords) * 100}%` }}
                  className="bg-sky-500"
                  title={`Review: ${recSummary?.review_count}`}
                />
              </div>

              {/* Legend grid */}
              <div className="mt-5 grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
                <div className="flex items-center gap-2">
                  <div className="h-2.5 w-2.5 rounded-full bg-emerald-500" />
                  <span className="text-slate-600 dark:text-slate-400">Matched:</span>
                  <span className="font-semibold">{matchedCount}</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="h-2.5 w-2.5 rounded-full bg-rose-500" />
                  <span className="text-slate-600 dark:text-slate-400">Missing Settlement:</span>
                  <span className="font-semibold">{recSummary?.missing_settlement_count || 0}</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="h-2.5 w-2.5 rounded-full bg-amber-500" />
                  <span className="text-slate-600 dark:text-slate-400">Missing Bank Credit:</span>
                  <span className="font-semibold">{recSummary?.missing_bank_count || 0}</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="h-2.5 w-2.5 rounded-full bg-purple-500" />
                  <span className="text-slate-600 dark:text-slate-400">Duplicate:</span>
                  <span className="font-semibold">{recSummary?.duplicate_count || 0}</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="h-2.5 w-2.5 rounded-full bg-sky-500" />
                  <span className="text-slate-600 dark:text-slate-400">Review Required:</span>
                  <span className="font-semibold">{recSummary?.review_count || 0}</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="h-2.5 w-2.5 rounded-full bg-slate-400" />
                  <span className="text-slate-600 dark:text-slate-400">SLA Delays:</span>
                  <span className="font-semibold">{recSummary?.operational_warnings_count || 0}</span>
                </div>
              </div>
            </div>

            {/* ML Anomaly Severity Distribution */}
            <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 p-5 shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100">
                    ML Anomaly Risk Profile
                  </h3>
                  <p className="text-xs text-slate-500">Isolation Forest (14 Features)</p>
                </div>
                <span className="text-[10px] font-mono rounded bg-slate-100 px-1.5 py-0.5 dark:bg-slate-800 text-slate-500">
                  {anomSummary?.model_version || "v1.0"}
                </span>
              </div>

              <div className="space-y-3 mt-4 text-xs">
                <div>
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-rose-600 dark:text-rose-400 font-semibold">High Anomaly (70–100)</span>
                    <span className="font-mono font-bold">{anomSummary?.severity_breakdown?.HIGH || 0}</span>
                  </div>
                  <div className="h-2 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                    <div
                      style={{ width: `${((anomSummary?.severity_breakdown?.HIGH || 0) / totalRecords) * 100}%` }}
                      className="h-full bg-rose-500 rounded-full"
                    />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-amber-600 dark:text-amber-400 font-semibold">Medium Anomaly (40–69)</span>
                    <span className="font-mono font-bold">{anomSummary?.severity_breakdown?.MEDIUM || 0}</span>
                  </div>
                  <div className="h-2 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                    <div
                      style={{ width: `${((anomSummary?.severity_breakdown?.MEDIUM || 0) / totalRecords) * 100}%` }}
                      className="h-full bg-amber-500 rounded-full"
                    />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-slate-600 dark:text-slate-400 font-semibold">Low Inlier (0–39)</span>
                    <span className="font-mono font-bold">{anomSummary?.severity_breakdown?.LOW || 0}</span>
                  </div>
                  <div className="h-2 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                    <div
                      style={{ width: `${((anomSummary?.severity_breakdown?.LOW || 0) / totalRecords) * 100}%` }}
                      className="h-full bg-emerald-500 rounded-full"
                    />
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 text-[11px] text-slate-500">
                Unsupervised anomaly scoring highlights population outliers without knowing synthetic ground truth.
              </div>
            </div>
          </div>

          {/* High-Priority Exceptions Queue */}
          <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 shadow-sm overflow-hidden">
            <div className="flex items-center justify-between p-5 border-b border-slate-200 dark:border-slate-800">
              <div>
                <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100">
                  High-Priority Discrepancy Queue
                </h3>
                <p className="text-xs text-slate-500">Click any transaction to launch AI evidence investigation</p>
              </div>

              <Link
                href="/investigations"
                className="inline-flex items-center gap-1 text-xs font-semibold text-indigo-600 hover:text-indigo-500 dark:text-indigo-400"
              >
                <span>View All Investigations</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </Link>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 dark:bg-slate-800/60 text-slate-500 border-b border-slate-200 dark:border-slate-800 font-semibold">
                  <tr>
                    <th className="py-3 px-4">Transaction / Payment</th>
                    <th className="py-3 px-4">Expected Net</th>
                    <th className="py-3 px-4">Actual Bank Credit</th>
                    <th className="py-3 px-4">Discrepancy</th>
                    <th className="py-3 px-4">Classification</th>
                    <th className="py-3 px-4">Status</th>
                    <th className="py-3 px-4 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800/80">
                  {topExceptions.map((item) => {
                    const disc = parseFloat(item.discrepancy_amount || "0");
                    return (
                      <tr
                        key={item.id}
                        className="hover:bg-slate-50/80 dark:hover:bg-slate-800/40 transition-colors"
                      >
                        <td className="py-3.5 px-4 font-mono font-medium text-slate-900 dark:text-slate-100">
                          <div>{item.payment_reference || item.payment_id}</div>
                          <div className="text-[10px] text-slate-400 font-sans">{item.id}</div>
                        </td>
                        <td className="py-3.5 px-4 font-mono">
                          ₹{parseFloat(item.expected_settlement_amount || "0").toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                        </td>
                        <td className="py-3.5 px-4 font-mono">
                          {item.actual_bank_amount ? (
                            `₹${parseFloat(item.actual_bank_amount).toLocaleString("en-IN", { minimumFractionDigits: 2 })}`
                          ) : (
                            <span className="text-rose-500 font-sans italic">Missing Credit</span>
                          )}
                        </td>
                        <td className="py-3.5 px-4 font-mono font-bold text-rose-600 dark:text-rose-400">
                          ₹{Math.abs(disc).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                        </td>
                        <td className="py-3.5 px-4">
                          <span className="rounded bg-slate-100 dark:bg-slate-800 px-2 py-0.5 text-[11px] font-mono text-slate-700 dark:text-slate-300">
                            {item.classification}
                          </span>
                        </td>
                        <td className="py-3.5 px-4">
                          <StatusBadge status={item.status} type="reconciliation" />
                        </td>
                        <td className="py-3.5 px-4 text-right">
                          <Link
                            href={`/investigations/${item.id}`}
                            className="inline-flex items-center gap-1 rounded bg-indigo-50 px-2.5 py-1 text-xs font-semibold text-indigo-700 hover:bg-indigo-100 dark:bg-indigo-950/60 dark:text-indigo-300 transition-colors"
                          >
                            <span>Investigate</span>
                            <ArrowUpRight className="h-3 w-3" />
                          </Link>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
