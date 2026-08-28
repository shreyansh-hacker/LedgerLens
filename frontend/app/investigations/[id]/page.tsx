"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  getReconciliationResultById,
  getInvestigationById,
  runInvestigation,
  submitHumanReview,
  getInvestigationAuditLogs,
  getAnomalyResults,
  ReconciliationItem,
  InvestigationItem,
  AuditLogItem,
  AnomalyItem,
} from "@/lib/api";
import { StatusBadge } from "@/components/StatusBadge";
import { MetricCard } from "@/components/MetricCard";
import { CalculationCard } from "@/components/CalculationCard";
import { EvidenceTimeline } from "@/components/EvidenceTimeline";
import { ConfidenceIndicator } from "@/components/ConfidenceIndicator";
import {
  ArrowLeft,
  Sparkles,
  RefreshCw,
  BrainCircuit,
  ShieldCheck,
  AlertTriangle,
  FileCheck,
  CheckCircle2,
  Clock,
  UserCheck,
  Tag,
  Cpu,
  History,
} from "lucide-react";
import { clsx } from "clsx";

export default function InvestigationDetailPage() {
  const params = useParams();
  const rawId = Array.isArray(params.id) ? params.id[0] : params.id;
  const recId = rawId ? rawId.replace("inv_", "rec_") : "";

  const [recItem, setRecItem] = useState<ReconciliationItem | null>(null);
  const [invItem, setInvItem] = useState<InvestigationItem | null>(null);
  const [anomItem, setAnomItem] = useState<AnomalyItem | null>(null);
  const [auditLogs, setAuditLogs] = useState<AuditLogItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [investigating, setInvestigating] = useState(false);
  const [reviewNote, setReviewNote] = useState("");
  const [submittingReview, setSubmittingReview] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadData() {
    if (!recId) return;
    setLoading(true);
    setError(null);
    try {
      // 1. Fetch Reconciliation Record
      const rec = await getReconciliationResultById(recId);
      setRecItem(rec);

      // 2. Fetch or trigger Investigation
      let inv: InvestigationItem | null = null;
      try {
        inv = await getInvestigationById(rec.id);
      } catch {
        // If not investigated yet, auto-investigate
        inv = await runInvestigation(rec.id, false);
      }
      setInvItem(inv);

      // 3. Fetch Anomaly Result
      try {
        const anomList = await getAnomalyResults({ limit: 100 });
        const matchedAnom = anomList.find((a) => a.reconciliation_id === rec.id);
        if (matchedAnom) setAnomItem(matchedAnom);
      } catch {}

      // 4. Fetch Audit Logs
      if (inv) {
        try {
          const logs = await getInvestigationAuditLogs(inv.id);
          setAuditLogs(logs);
        } catch {}
      }
    } catch (err: any) {
      setError(err.message || "Failed to load investigation details");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, [recId]);

  async function handleForceReinvestigate() {
    if (!recItem) return;
    setInvestigating(true);
    try {
      const inv = await runInvestigation(recItem.id, true);
      setInvItem(inv);
      const logs = await getInvestigationAuditLogs(inv.id);
      setAuditLogs(logs);
    } catch (err: any) {
      alert(`Investigation failed: ${err.message}`);
    } finally {
      setInvestigating(false);
    }
  }

  async function handleHumanAction(action: "RESOLVE" | "ESCALATE" | "ADD_NOTE") {
    if (!invItem) return;
    setSubmittingReview(true);
    try {
      const note = reviewNote.trim() || `Action: ${action} triggered by operator`;
      const updated = await submitHumanReview(invItem.id, action, note);
      setInvItem(updated);
      setReviewNote("");
      const logs = await getInvestigationAuditLogs(invItem.id);
      setAuditLogs(logs);
    } catch (err: any) {
      alert(`Failed to record review: ${err.message}`);
    } finally {
      setSubmittingReview(false);
    }
  }

  if (loading) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-20 text-center">
        <RefreshCw className="mx-auto h-8 w-8 animate-spin text-indigo-600 mb-3" />
        <p className="text-sm font-semibold text-slate-700 dark:text-slate-300">
          Loading investigation workspace & assembling evidence trail...
        </p>
      </div>
    );
  }

  if (error || !recItem) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-16 text-center">
        <AlertTriangle className="mx-auto h-10 w-10 text-rose-500 mb-3" />
        <h2 className="text-lg font-bold text-slate-800 dark:text-slate-200">
          Investigation Record Not Found
        </h2>
        <p className="text-xs text-slate-500 mt-2">{error || "No matching transaction record found in database."}</p>
        <div className="mt-6">
          <Link
            href="/investigations"
            className="inline-flex items-center gap-1.5 rounded-lg bg-indigo-600 px-4 py-2 text-xs font-semibold text-white shadow-sm hover:bg-indigo-500"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            <span>Back to Queue</span>
          </Link>
        </div>
      </div>
    );
  }

  const discrepancyNum = parseFloat(recItem.discrepancy_amount || "0");
  const hasDiscrepancy = Math.abs(discrepancyNum) > 0.001;
  const calcData = recItem.evidence_payload?.calculation || {};

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8 w-full space-y-6">
      {/* Top Breadcrumb & Actions Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-200 dark:border-slate-800">
        <div className="flex items-center gap-3">
          <Link
            href="/investigations"
            className="flex h-8 w-8 items-center justify-center rounded-lg border border-slate-200 hover:bg-slate-50 dark:border-slate-800 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300 transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold font-mono text-slate-900 dark:text-slate-100">
                {recItem.id.toUpperCase()}
              </h1>
              <span className="rounded bg-slate-100 dark:bg-slate-800 px-2 py-0.5 text-xs font-bold text-slate-700 dark:text-slate-300">
                {recItem.classification.replace(/_/g, " ")}
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-mono">
              Payment Reference: {recItem.payment_reference || recItem.payment_id}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={handleForceReinvestigate}
            disabled={investigating}
            className="inline-flex items-center gap-1.5 rounded-lg bg-indigo-600 px-3.5 py-2 text-xs font-semibold text-white shadow-sm hover:bg-indigo-500 disabled:opacity-50 transition-colors"
          >
            <Sparkles className={clsx("h-3.5 w-3.5", investigating && "animate-spin")} />
            <span>{investigating ? "Re-Investigating with Groq..." : "Re-Run AI Investigation"}</span>
          </button>
        </div>
      </div>

      {/* Top Banner KPI Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Payment Amount"
          value={`₹${parseFloat(calcData.payment_gross || recItem.expected_settlement_amount).toLocaleString("en-IN", { minimumFractionDigits: 2 })}`}
          subtext={`Captured: ${recItem.payment_reference || recItem.payment_id}`}
          variant="default"
        />
        <MetricCard
          title="Expected Net"
          value={`₹${parseFloat(recItem.expected_settlement_amount).toLocaleString("en-IN", { minimumFractionDigits: 2 })}`}
          subtext="After Fees & 18% GST"
          variant="default"
        />
        <MetricCard
          title="Actual Bank Credit"
          value={recItem.actual_bank_amount ? `₹${parseFloat(recItem.actual_bank_amount).toLocaleString("en-IN", { minimumFractionDigits: 2 })}` : "None (Missing)"}
          subtext={recItem.utr_number ? `UTR: ${recItem.utr_number}` : "Uncredited at Bank"}
          variant={recItem.actual_bank_amount ? "default" : "danger"}
        />
        <MetricCard
          title="Financial Discrepancy"
          value={hasDiscrepancy ? `₹${Math.abs(discrepancyNum).toLocaleString("en-IN", { minimumFractionDigits: 2 })}` : "₹0.00"}
          subtext={hasDiscrepancy ? "Variance Detected" : "Clean Match"}
          variant={hasDiscrepancy ? "danger" : "success"}
        />
      </div>

      {/* Main Grid: Left Column (AI + Confidence) | Right Column (Calculations + Timeline + Audit) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: AI Investigation Report & Confidence (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* AI Investigation Report Card */}
          {invItem && (
            <div className="rounded-2xl border border-indigo-200/90 dark:border-indigo-900/60 bg-white dark:bg-slate-900/80 p-6 shadow-sm space-y-5">
              {/* Header */}
              <div className="flex items-center justify-between pb-4 border-b border-slate-100 dark:border-slate-800">
                <div className="flex items-center gap-2.5">
                  <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-50 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-400">
                    <BrainCircuit className="h-5 w-5" />
                  </div>
                  <div>
                    <h2 className="text-base font-bold text-slate-900 dark:text-slate-100">
                      AI Investigation Report
                    </h2>
                    <p className="text-[11px] text-slate-500 font-mono">
                      Model: {invItem.model_name} • Latency: {invItem.latency_ms}ms • {invItem.cached ? "⚡ Cached (0ms)" : "Live Inference"}
                    </p>
                  </div>
                </div>

                <StatusBadge status={invItem.investigation_status} type="investigation" size="md" />
              </div>

              {/* Executive Summary */}
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">
                  Executive Summary
                </h4>
                <p className="text-sm font-semibold text-slate-800 dark:text-slate-200 leading-relaxed bg-slate-50 dark:bg-slate-800/40 p-3.5 rounded-xl border border-slate-200/60 dark:border-slate-800">
                  {invItem.summary}
                </p>
              </div>

              {/* Grounded Facts List */}
              {invItem.facts && invItem.facts.length > 0 && (
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
                    Verified Observable Facts (Strict Grounding)
                  </h4>
                  <div className="space-y-2">
                    {invItem.facts.map((fact: any, idx: number) => (
                      <div
                        key={idx}
                        className="flex items-start gap-2.5 p-3 rounded-lg bg-slate-50 dark:bg-slate-800/30 border border-slate-200/50 dark:border-slate-800 text-xs text-slate-700 dark:text-slate-300"
                      >
                        <CheckCircle2 className="h-4 w-4 text-emerald-500 mt-0.5 flex-shrink-0" />
                        <div className="flex-1">
                          <p>{fact.statement}</p>
                          {fact.evidence_ids && fact.evidence_ids.length > 0 && (
                            <div className="mt-1 flex flex-wrap gap-1">
                              {fact.evidence_ids.map((eid: string, i: number) => (
                                <span
                                  key={i}
                                  className="inline-flex items-center gap-1 rounded bg-indigo-50 dark:bg-indigo-950 px-1.5 py-0.2 text-[10px] font-mono text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800"
                                >
                                  <Tag className="h-2.5 w-2.5" />
                                  <span>{eid}</span>
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Step-by-Step Mathematical Explanation */}
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">
                  Root Cause Reasoning
                </h4>
                <div className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 whitespace-pre-wrap font-sans">
                  {invItem.explanation}
                </div>
              </div>

              {/* Missing Evidence Callout */}
              {invItem.missing_evidence && invItem.missing_evidence.length > 0 && (
                <div className="rounded-xl border border-rose-200 bg-rose-50/70 p-4 dark:border-rose-900/60 dark:bg-rose-950/20 text-xs text-rose-900 dark:text-rose-200 space-y-1.5">
                  <div className="flex items-center gap-2 font-bold">
                    <AlertTriangle className="h-4 w-4 text-rose-600 flex-shrink-0" />
                    <span>Unexplained Discrepancy — Missing Ledger Evidence</span>
                  </div>
                  <p className="text-[11px] text-rose-700 dark:text-rose-300">
                    The AI Investigator refused to speculate on unrecorded bank deductions. The following evidence is required for resolution:
                  </p>
                  <ul className="list-disc list-inside space-y-0.5 text-[11px] font-mono">
                    {invItem.missing_evidence.map((me: string, i: number) => (
                      <li key={i}>{me}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Recommended Action */}
              <div className="pt-2 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-semibold text-slate-500">Recommended Action:</span>
                  <span className="rounded-full bg-slate-900 text-white px-3 py-1 text-xs font-bold font-mono dark:bg-indigo-600">
                    {invItem.recommended_action}
                  </span>
                </div>
                <div className="text-[11px] text-slate-400">
                  Zero Hallucination Guardrails Active
                </div>
              </div>
            </div>
          )}

          {/* System Confidence Meter */}
          {invItem && (
            <ConfidenceIndicator
              score={invItem.system_confidence}
              tier={invItem.confidence_tier}
              showBreakdown={true}
            />
          )}

          {/* ML Anomaly Risk Card */}
          {anomItem && (
            <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/80 p-5 shadow-sm space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Cpu className="h-4 w-4 text-indigo-500" />
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300">
                    ML Anomaly Evaluation (Isolation Forest)
                  </h3>
                </div>
                <StatusBadge status={anomItem.severity} type="anomaly" />
              </div>

              <div className="flex items-baseline justify-between pt-1">
                <span className="text-xs text-slate-500">Normalized Anomaly Score:</span>
                <span className="text-lg font-mono font-bold text-slate-900 dark:text-slate-100">
                  {anomItem.normalized_score.toFixed(1)} / 100
                </span>
              </div>

              {anomItem.explanation_signals && anomItem.explanation_signals.length > 0 && (
                <div className="pt-2 border-t border-slate-100 dark:border-slate-800">
                  <span className="text-[11px] font-semibold text-slate-500">Observable Contributing Signals:</span>
                  <ul className="mt-1.5 space-y-1 text-xs text-slate-600 dark:text-slate-400">
                    {anomItem.explanation_signals.map((sig, i) => (
                      <li key={i} className="flex items-start gap-1.5">
                        <span className="text-indigo-500 font-bold">•</span>
                        <span>{sig}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right Column: Calculation Card + Evidence Timeline + Human Actions + Audit Log (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          {/* Side-by-Side Settlement Math Card */}
          <CalculationCard
            grossAmount={calcData.payment_gross || recItem.expected_settlement_amount}
            fees={[{ name: "Gateway MDR Fee", amount: calcData.total_fees || "0.00" }]}
            taxes={[{ name: "GST (18%)", amount: calcData.total_taxes || "0.00" }]}
            expectedSettlement={recItem.expected_settlement_amount}
            actualSettlement={recItem.actual_settlement_amount}
            actualBankAmount={recItem.actual_bank_amount}
            discrepancyAmount={recItem.discrepancy_amount}
          />

          {/* Interactive Evidence Timeline */}
          <EvidenceTimeline
            payment={{
              id: recItem.payment_id,
              reference: recItem.payment_reference,
              amount: calcData.payment_gross || recItem.expected_settlement_amount,
              gateway: "Razorpay",
              captured_at: recItem.reconciled_at,
            }}
            fees={calcData.total_fees ? [{ id: `fee_${recItem.payment_id.replace('pay_', '')}`, type: "gateway_fee", amount: calcData.total_fees }] : []}
            taxes={calcData.total_taxes ? [{ id: `tax_${recItem.payment_id.replace('pay_', '')}`, type: "GST_18", amount: calcData.total_taxes }] : []}
            settlement={
              recItem.settlement_id
                ? {
                    id: recItem.settlement_id,
                    reference: recItem.settlement_reference,
                    net_amount: recItem.actual_settlement_amount || recItem.expected_settlement_amount,
                    fee_amount: calcData.total_fees || "0.00",
                    tax_amount: calcData.total_taxes || "0.00",
                    settled_at: recItem.reconciled_at,
                  }
                : null
            }
            bank={
              recItem.bank_transaction_id
                ? {
                    id: recItem.bank_transaction_id,
                    reference: recItem.bank_reference,
                    utr_number: recItem.utr_number,
                    credit_amount: recItem.actual_bank_amount || "0.00",
                    transaction_date: recItem.reconciled_at,
                  }
                : null
            }
          />

          {/* Human Review Decision Panel */}
          {invItem && (
            <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/80 p-5 shadow-sm space-y-4">
              <div className="flex items-center gap-2">
                <UserCheck className="h-4 w-4 text-indigo-500" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300">
                  Human Operator Decision
                </h3>
              </div>

              {invItem.human_override && (
                <div className="p-3 rounded-lg bg-indigo-50/60 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-800 text-xs text-indigo-900 dark:text-indigo-200">
                  <span className="font-bold">Operator Note:</span> {invItem.reviewer_note}
                </div>
              )}

              <div>
                <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
                  Add Reviewer Justification / Note:
                </label>
                <textarea
                  rows={2}
                  value={reviewNote}
                  onChange={(e) => setReviewNote(e.target.value)}
                  placeholder="e.g. Verified with merchant support, gateway approved refund adjustment..."
                  className="w-full text-xs rounded-lg border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 p-2.5 focus:outline-none focus:border-indigo-500 dark:text-slate-100"
                />
              </div>

              <div className="grid grid-cols-2 gap-2 pt-1">
                <button
                  type="button"
                  onClick={() => handleHumanAction("RESOLVE")}
                  disabled={submittingReview}
                  className="rounded-lg bg-emerald-600 py-2 px-3 text-xs font-semibold text-white hover:bg-emerald-500 disabled:opacity-50 transition-colors shadow-xs"
                >
                  Mark Resolved
                </button>
                <button
                  type="button"
                  onClick={() => handleHumanAction("ESCALATE")}
                  disabled={submittingReview}
                  className="rounded-lg bg-rose-600 py-2 px-3 text-xs font-semibold text-white hover:bg-rose-500 disabled:opacity-50 transition-colors shadow-xs"
                >
                  Escalate to Treasury
                </button>
              </div>
            </div>
          )}

          {/* Immutable Chronological Audit Trail */}
          <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/80 p-5 shadow-sm space-y-3">
            <div className="flex items-center gap-2 pb-2 border-b border-slate-100 dark:border-slate-800">
              <History className="h-4 w-4 text-slate-500" />
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300">
                Immutable Audit Trail
              </h3>
            </div>

            <div className="space-y-3">
              {auditLogs.map((log) => (
                <div key={log.id} className="text-xs flex items-start gap-2.5">
                  <div className="h-2 w-2 rounded-full bg-indigo-500 mt-1.5 flex-shrink-0" />
                  <div className="flex-1">
                    <div className="flex justify-between items-center">
                      <span className="font-semibold text-slate-800 dark:text-slate-200 font-mono text-[11px]">
                        {log.action}
                      </span>
                      <span className="text-[10px] text-slate-400">
                        {new Date(log.created_at).toLocaleTimeString()}
                      </span>
                    </div>
                    <p className="text-slate-500 text-[11px] mt-0.5">{log.notes || `Actor: ${log.actor}`}</p>
                  </div>
                </div>
              ))}

              {auditLogs.length === 0 && (
                <div className="text-xs text-slate-400 italic py-1">
                  Reconciliation initialized and logged at database tier.
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
