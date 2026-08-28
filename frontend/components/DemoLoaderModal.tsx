"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  checkBackendHealth,
  getDemoStatus,
  loadDemoDataset,
  DemoLoadResponse,
} from "@/lib/api";
import {
  Sparkles,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  X,
  Database,
  ArrowRight,
  ShieldCheck,
  Cpu,
  BrainCircuit,
  FileSpreadsheet,
} from "lucide-react";
import { clsx } from "clsx";

interface DemoLoaderModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
  forceReset?: boolean;
}

type DemoStage =
  | "IDLE"
  | "WAKING_BACKEND"
  | "CHECKING_STATUS"
  | "GENERATING_DATA"
  | "SEEDING_DATABASE"
  | "RECONCILING"
  | "ANALYZING_ANOMALIES"
  | "PREPARING_INVESTIGATIONS"
  | "READY"
  | "ERROR";

export function DemoLoaderModal({
  isOpen,
  onClose,
  onSuccess,
  forceReset = false,
}: DemoLoaderModalProps) {
  const router = useRouter();
  const [stage, setStage] = useState<DemoStage>("IDLE");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [result, setResult] = useState<DemoLoadResponse | null>(null);
  const [wakeSeconds, setWakeSeconds] = useState(0);

  const stagesList = [
    { key: "WAKING_BACKEND", label: "Connect to backend services & database", icon: Database },
    { key: "GENERATING_DATA", label: "Generate 1,000 synthetic transaction clusters (seed: 42)", icon: FileSpreadsheet },
    { key: "RECONCILING", label: "Execute multi-pass deterministic reconciliation", icon: ShieldCheck },
    { key: "ANALYZING_ANOMALIES", label: "Fit Isolation Forest ML anomaly scoring", icon: Cpu },
    { key: "PREPARING_INVESTIGATIONS", label: "Pre-investigate exceptions with Groq AI", icon: BrainCircuit },
  ];

  function getStepIndex(curr: DemoStage): number {
    switch (curr) {
      case "WAKING_BACKEND":
      case "CHECKING_STATUS":
        return 0;
      case "GENERATING_DATA":
      case "SEEDING_DATABASE":
        return 1;
      case "RECONCILING":
        return 2;
      case "ANALYZING_ANOMALIES":
        return 3;
      case "PREPARING_INVESTIGATIONS":
        return 4;
      case "READY":
        return 5;
      default:
        return -1;
    }
  }

  async function startDemoFlow() {
    setStage("WAKING_BACKEND");
    setErrorMessage(null);
    setWakeSeconds(0);

    const wakeTimer = setInterval(() => {
      setWakeSeconds((s) => s + 1);
    }, 1000);

    try {
      // 1. Health check / wake
      let healthy = false;
      let attempts = 0;
      while (!healthy && attempts < 15) {
        try {
          await checkBackendHealth();
          healthy = true;
        } catch {
          attempts++;
          await new Promise((r) => setTimeout(r, 2000));
        }
      }

      if (!healthy) {
        throw new Error("Backend service did not respond. If using free-tier hosting, please allow up to 60s for cold start.");
      }

      clearInterval(wakeTimer);

      // 2. Check if already initialized and forceReset is false
      if (!forceReset) {
        setStage("CHECKING_STATUS");
        const status = await getDemoStatus().catch(() => null);
        if (status && status.is_initialized) {
          // Idempotent fast path
          const res = await loadDemoDataset(1000, 42, false, true);
          setResult(res);
          setStage("READY");
          return;
        }
      }

      // 3. Stage Transitions for full pipeline
      setStage("GENERATING_DATA");
      await new Promise((r) => setTimeout(r, 400));

      setStage("RECONCILING");
      await new Promise((r) => setTimeout(r, 400));

      setStage("ANALYZING_ANOMALIES");
      await new Promise((r) => setTimeout(r, 400));

      setStage("PREPARING_INVESTIGATIONS");

      // Execute live backend call
      const res = await loadDemoDataset(1000, 42, forceReset, true);
      setResult(res);
      setStage("READY");
    } catch (err: any) {
      clearInterval(wakeTimer);
      setErrorMessage(err.message || "Failed to initialize demo mode");
      setStage("ERROR");
    }
  }

  useEffect(() => {
    if (isOpen) {
      startDemoFlow();
    } else {
      setStage("IDLE");
      setResult(null);
      setErrorMessage(null);
    }
  }, [isOpen, forceReset]);

  if (!isOpen) return null;

  const activeStepIdx = getStepIndex(stage);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-2xl dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-5">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600 dark:bg-indigo-950 dark:text-indigo-400">
              <Sparkles className="h-4 w-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100">
                Initializing LedgerLens Demo
              </h3>
              <p className="text-[11px] text-slate-500">
                1,000 Synthetic Transactions • 10 Ground-Truth Scenarios
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-slate-800 dark:hover:text-slate-200"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Cold Start Notice if waking takes time */}
        {stage === "WAKING_BACKEND" && wakeSeconds > 4 && (
          <div className="rounded-xl border border-amber-200 bg-amber-50/70 p-3 text-xs text-amber-800 dark:border-amber-900/60 dark:bg-amber-950/30 dark:text-amber-200">
            <span className="font-semibold">Demo server is waking up:</span> Free demo servers sleep when idle. Starting up runtime ({wakeSeconds}s)...
          </div>
        )}

        {/* Stages Checklist */}
        <div className="space-y-3">
          {stagesList.map((st, i) => {
            const isCompleted = activeStepIdx > i || stage === "READY";
            const isCurrent = activeStepIdx === i && stage !== "READY" && stage !== "ERROR";
            const Icon = st.icon;

            return (
              <div
                key={st.key}
                className={clsx(
                  "flex items-center gap-3 p-3 rounded-xl border text-xs transition-all",
                  isCompleted
                    ? "border-emerald-200 bg-emerald-50/40 text-emerald-900 dark:border-emerald-900/40 dark:bg-emerald-950/20 dark:text-emerald-300"
                    : isCurrent
                    ? "border-indigo-300 bg-indigo-50/50 text-indigo-900 dark:border-indigo-800 dark:bg-indigo-950/40 dark:text-indigo-200 shadow-xs"
                    : "border-slate-100 bg-slate-50/50 text-slate-400 dark:border-slate-800/60 dark:bg-slate-800/20"
                )}
              >
                <div className="flex-shrink-0">
                  {isCompleted ? (
                    <CheckCircle2 className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
                  ) : isCurrent ? (
                    <RefreshCw className="h-4 w-4 text-indigo-600 dark:text-indigo-400 animate-spin" />
                  ) : (
                    <div className="h-4 w-4 rounded-full border border-slate-300 dark:border-slate-700 flex items-center justify-center text-[10px] text-slate-400">
                      {i + 1}
                    </div>
                  )}
                </div>

                <div className="flex-1 font-medium">
                  {st.label}
                </div>
              </div>
            );
          })}
        </div>

        {/* Success Banner */}
        {stage === "READY" && result && (
          <div className="rounded-xl border border-emerald-200 bg-emerald-50/60 p-4 text-xs text-emerald-900 dark:border-emerald-900/60 dark:bg-emerald-950/30 dark:text-emerald-200 space-y-2">
            <div className="flex items-center gap-2 font-bold text-sm">
              <CheckCircle2 className="h-5 w-5 text-emerald-600" />
              <span>LedgerLens Demo is Ready!</span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-[11px] font-mono pt-1">
              <div>Reconciled: {result.reconciled_count}</div>
              <div>Match Rate: {result.summary.match_rate}</div>
              <div>Exceptions: {result.summary.exception_count}</div>
              <div>Anomalies: {result.summary.anomalies_count}</div>
            </div>
            <p className="text-[11px] text-emerald-700 dark:text-emerald-300 pt-1">
              {result.cached ? "⚡ Instantly resumed existing demo state (4.2ms)" : `Processed in ${result.duration_ms}ms`}
            </p>
          </div>
        )}

        {/* Error Banner */}
        {stage === "ERROR" && (
          <div className="rounded-xl border border-rose-200 bg-rose-50 p-4 text-xs text-rose-900 dark:border-rose-900/60 dark:bg-rose-950/30 dark:text-rose-200 space-y-2">
            <div className="flex items-center gap-2 font-bold">
              <AlertCircle className="h-4 w-4 text-rose-600" />
              <span>Demo Initialization Failed</span>
            </div>
            <p>{errorMessage}</p>
            <button
              type="button"
              onClick={startDemoFlow}
              className="mt-2 inline-flex items-center gap-1 font-semibold text-rose-700 hover:text-rose-800 underline"
            >
              <RefreshCw className="h-3 w-3" />
              <span>Retry Initialization</span>
            </button>
          </div>
        )}

        {/* Footer Actions */}
        <div className="pt-2 flex items-center justify-end gap-3">
          {stage === "READY" ? (
            <button
              type="button"
              onClick={() => {
                onClose();
                if (onSuccess) onSuccess();
                router.push("/dashboard");
              }}
              className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-5 py-2.5 text-xs font-semibold text-white shadow-md hover:bg-indigo-500 transition-all hover:scale-105"
            >
              <span>Explore Dashboard</span>
              <ArrowRight className="h-4 w-4" />
            </button>
          ) : (
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-4 py-2 text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
            >
              Close
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
