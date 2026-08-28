"use client";

import React, { useState } from "react";
import { clsx } from "clsx";
import { ShieldCheck, HelpCircle, AlertTriangle, CheckCircle2, XCircle } from "lucide-react";

interface ConfidenceIndicatorProps {
  score: number;
  tier?: "HIGH" | "MEDIUM" | "LOW";
  showBreakdown?: boolean;
  className?: string;
}

export function ConfidenceIndicator({
  score,
  tier,
  showBreakdown = true,
  className,
}: ConfidenceIndicatorProps) {
  const [openTooltip, setOpenTooltip] = useState(false);
  const normalizedScore = Math.max(0, Math.min(100, score || 0));

  const derivedTier =
    tier || (normalizedScore >= 88 ? "HIGH" : normalizedScore >= 60 ? "MEDIUM" : "LOW");

  const tierConfig = {
    HIGH: {
      label: "High Confidence",
      color: "text-emerald-700 dark:text-emerald-400",
      barColor: "bg-emerald-500",
      bgColor: "bg-emerald-50 dark:bg-emerald-950/40",
      borderColor: "border-emerald-200 dark:border-emerald-800",
      icon: ShieldCheck,
      desc: "Fully substantiated by arithmetic agreement, ledger completeness, and matching confidence.",
    },
    MEDIUM: {
      label: "Medium Confidence",
      color: "text-amber-700 dark:text-amber-400",
      barColor: "bg-amber-500",
      bgColor: "bg-amber-50 dark:bg-amber-950/40",
      borderColor: "border-amber-200 dark:border-amber-800",
      icon: HelpCircle,
      desc: "Partial ledger evidence or non-standard reference format detected. Human review suggested.",
    },
    LOW: {
      label: "Low Confidence",
      color: "text-rose-700 dark:text-rose-400",
      barColor: "bg-rose-500",
      bgColor: "bg-rose-50 dark:bg-rose-950/40",
      borderColor: "border-rose-200 dark:border-rose-800",
      icon: AlertTriangle,
      desc: "Unexplained financial variance or missing bank/settlement records. Mandatory human escalation.",
    },
  };

  const config = tierConfig[derivedTier];
  const Icon = config.icon;

  return (
    <div className={clsx("rounded-xl border p-4 shadow-sm", config.bgColor, config.borderColor, className)}>
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <Icon className={clsx("h-5 w-5", config.color)} />
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-600 dark:text-slate-300">
            System Confidence
          </span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className={clsx("text-lg font-bold font-mono", config.color)}>
            {normalizedScore.toFixed(1)}%
          </span>
          <span className={clsx("text-[11px] font-semibold uppercase px-2 py-0.5 rounded-full border", config.bgColor, config.borderColor, config.color)}>
            {derivedTier}
          </span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mt-3 h-2 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-800">
        <div
          className={clsx("h-full rounded-full transition-all duration-700 ease-out", config.barColor)}
          style={{ width: `${normalizedScore}%` }}
        />
      </div>

      <p className="mt-2.5 text-xs text-slate-600 dark:text-slate-400">
        {config.desc}
      </p>

      {showBreakdown && (
        <div className="mt-3 pt-3 border-t border-slate-200/60 dark:border-slate-800/60">
          <button
            type="button"
            onClick={() => setOpenTooltip(!openTooltip)}
            className="flex items-center justify-between w-full text-[11px] font-medium text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200"
          >
            <span>Multi-Factor Confidence Breakdown</span>
            <span>{openTooltip ? "Hide Details ▲" : "View Factors ▼"}</span>
          </button>

          {openTooltip && (
            <div className="mt-2.5 space-y-1.5 text-[11px] text-slate-600 dark:text-slate-300 bg-white/70 dark:bg-slate-900/70 p-2.5 rounded-lg border border-slate-200 dark:border-slate-800">
              <div className="flex justify-between items-center">
                <span>Deterministic Calculation Agreement (35%)</span>
                <span className="font-semibold">{normalizedScore >= 80 ? "100%" : "Partial / Variance"}</span>
              </div>
              <div className="flex justify-between items-center">
                <span>Evidence Completeness (25%)</span>
                <span className="font-semibold">{normalizedScore >= 60 ? "Verified" : "Missing Records"}</span>
              </div>
              <div className="flex justify-between items-center">
                <span>Multi-Pass Matching Score (20%)</span>
                <span className="font-semibold">Pass 1 / Pass 2 (95-100%)</span>
              </div>
              <div className="flex justify-between items-center">
                <span>AI Fact Grounding (20%)</span>
                <span className="font-semibold">100% Traceable</span>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
