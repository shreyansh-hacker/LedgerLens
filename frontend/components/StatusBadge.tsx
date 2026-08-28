import React from "react";
import { clsx } from "clsx";

interface StatusBadgeProps {
  status: string;
  type?: "reconciliation" | "investigation" | "anomaly" | "confidence";
  className?: string;
  size?: "sm" | "md";
}

export function StatusBadge({ status, type = "reconciliation", className, size = "sm" }: StatusBadgeProps) {
  const s = (status || "").toUpperCase();

  let colorClasses = "bg-slate-100 text-slate-700 border-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:border-slate-700";
  let dotColor = "bg-slate-400";
  let label = status;

  if (type === "reconciliation") {
    switch (s) {
      case "MATCHED":
      case "RESOLVED":
        colorClasses = "bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800";
        dotColor = "bg-emerald-500";
        label = "Matched";
        break;
      case "EXCEPTION":
      case "FEE_MISMATCH":
      case "TAX_MISMATCH":
      case "AMOUNT_MISMATCH":
      case "UNEXPLAINED_EXCEPTION":
        colorClasses = "bg-rose-50 text-rose-700 border-rose-200 dark:bg-rose-950/40 dark:text-rose-300 dark:border-rose-800";
        dotColor = "bg-rose-500";
        label = s.replace(/_/g, " ");
        break;
      case "MISSING_SETTLEMENT":
      case "MISSING_BANK_TRANSACTION":
        colorClasses = "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-800";
        dotColor = "bg-amber-500";
        label = s.replace(/_/g, " ");
        break;
      case "DUPLICATE":
      case "DUPLICATE_SETTLEMENT":
        colorClasses = "bg-purple-50 text-purple-700 border-purple-200 dark:bg-purple-950/40 dark:text-purple-300 dark:border-purple-800";
        dotColor = "bg-purple-500";
        label = "Duplicate";
        break;
      case "REVIEW":
      case "REFERENCE_ID_DISCREPANCY":
        colorClasses = "bg-sky-50 text-sky-700 border-sky-200 dark:bg-sky-950/40 dark:text-sky-300 dark:border-sky-800";
        dotColor = "bg-sky-500";
        label = "Review Needed";
        break;
    }
  } else if (type === "investigation") {
    switch (s) {
      case "EXPLAINED":
        colorClasses = "bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800";
        dotColor = "bg-emerald-500";
        label = "Explained";
        break;
      case "PARTIALLY_EXPLAINED":
        colorClasses = "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-800";
        dotColor = "bg-amber-500";
        label = "Partially Explained";
        break;
      case "HUMAN_REVIEW_REQUIRED":
      case "UNRESOLVED":
        colorClasses = "bg-rose-50 text-rose-700 border-rose-200 dark:bg-rose-950/40 dark:text-rose-300 dark:border-rose-800";
        dotColor = "bg-rose-500";
        label = "Human Review Required";
        break;
      case "CONFLICTING_EVIDENCE":
        colorClasses = "bg-purple-50 text-purple-700 border-purple-200 dark:bg-purple-950/40 dark:text-purple-300 dark:border-purple-800";
        dotColor = "bg-purple-500";
        label = "Conflicting Evidence";
        break;
      case "MANUALLY_OVERRIDDEN":
        colorClasses = "bg-indigo-50 text-indigo-700 border-indigo-200 dark:bg-indigo-950/40 dark:text-indigo-300 dark:border-indigo-800";
        dotColor = "bg-indigo-500";
        label = "Overridden";
        break;
    }
  } else if (type === "anomaly") {
    switch (s) {
      case "LOW":
        colorClasses = "bg-slate-100 text-slate-700 border-slate-200 dark:bg-slate-800 dark:text-slate-300";
        dotColor = "bg-slate-400";
        label = "Low Anomaly";
        break;
      case "MEDIUM":
        colorClasses = "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/40 dark:text-amber-300";
        dotColor = "bg-amber-500";
        label = "Medium Anomaly";
        break;
      case "HIGH":
        colorClasses = "bg-rose-50 text-rose-700 border-rose-200 dark:bg-rose-950/40 dark:text-rose-300";
        dotColor = "bg-rose-500";
        label = "High Anomaly";
        break;
    }
  } else if (type === "confidence") {
    switch (s) {
      case "HIGH":
        colorClasses = "bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300";
        dotColor = "bg-emerald-500";
        label = "High Confidence";
        break;
      case "MEDIUM":
        colorClasses = "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/40 dark:text-amber-300";
        dotColor = "bg-amber-500";
        label = "Medium Confidence";
        break;
      case "LOW":
        colorClasses = "bg-rose-50 text-rose-700 border-rose-200 dark:bg-rose-950/40 dark:text-rose-300";
        dotColor = "bg-rose-500";
        label = "Low Confidence";
        break;
    }
  }

  const sizeClasses = size === "sm" ? "px-2 py-0.5 text-xs" : "px-2.5 py-1 text-xs font-medium";

  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1.5 font-medium rounded-full border transition-colors",
        sizeClasses,
        colorClasses,
        className
      )}
    >
      <span className={clsx("w-1.5 h-1.5 rounded-full flex-shrink-0", dotColor)} />
      <span className="capitalize">{label}</span>
    </span>
  );
}
