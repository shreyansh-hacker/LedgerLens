import { cn } from "@/lib/utils";

interface StatusBadgeProps {
  status: string;
  type?: "reconciliation" | "investigation" | "confidence" | "anomaly";
  className?: string;
}

export default function StatusBadge({ status, type = "reconciliation", className }: StatusBadgeProps) {
  const normalized = status.toUpperCase();

  let colorClasses = "bg-surface-100 text-surface-700 border-surface-200";

  if (normalized === "MATCHED" || normalized === "EXPLAINED" || normalized === "RESOLVED" || normalized === "HIGH") {
    colorClasses = "bg-emerald-50 text-emerald-700 border-emerald-200";
  } else if (normalized === "HUMAN_REVIEW" || normalized === "HUMAN_REVIEW_REQUIRED" || normalized === "MEDIUM") {
    colorClasses = "bg-amber-50 text-amber-700 border-amber-200";
  } else if (normalized === "EXCEPTION" || normalized === "UNRESOLVED" || normalized === "LOW" || normalized === "ANOMALY") {
    colorClasses = "bg-rose-50 text-rose-700 border-rose-200";
  } else if (normalized === "MANUALLY_OVERRIDDEN") {
    colorClasses = "bg-indigo-50 text-indigo-700 border-indigo-200";
  }

  const formatText = (text: string) => {
    return text.replace(/_/g, " ");
  };

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold border capitalize tracking-wide",
        colorClasses,
        className
      )}
    >
      <span className="h-1.5 w-1.5 rounded-full bg-current opacity-75"></span>
      {formatText(status)}
    </span>
  );
}
