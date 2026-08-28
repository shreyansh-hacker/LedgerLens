import React from "react";
import { clsx } from "clsx";
import { LucideIcon } from "lucide-react";

interface MetricCardProps {
  title: string;
  value: string | number;
  subtext?: string;
  trend?: {
    value: string;
    positive?: boolean;
  };
  icon?: LucideIcon;
  variant?: "default" | "success" | "warning" | "danger" | "info";
  className?: string;
  badge?: string;
}

export function MetricCard({
  title,
  value,
  subtext,
  trend,
  icon: Icon,
  variant = "default",
  className,
  badge,
}: MetricCardProps) {
  const variantStyles = {
    default: "border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60",
    success: "border-emerald-200 dark:border-emerald-900/40 bg-emerald-50/30 dark:bg-emerald-950/20",
    warning: "border-amber-200 dark:border-amber-900/40 bg-amber-50/30 dark:bg-amber-950/20",
    danger: "border-rose-200 dark:border-rose-900/40 bg-rose-50/30 dark:bg-rose-950/20",
    info: "border-sky-200 dark:border-sky-900/40 bg-sky-50/30 dark:bg-sky-950/20",
  };

  const iconStyles = {
    default: "text-slate-500 dark:text-slate-400 bg-slate-100 dark:bg-slate-800",
    success: "text-emerald-600 dark:text-emerald-400 bg-emerald-100 dark:bg-emerald-900/40",
    warning: "text-amber-600 dark:text-amber-400 bg-amber-100 dark:bg-amber-900/40",
    danger: "text-rose-600 dark:text-rose-400 bg-rose-100 dark:bg-rose-900/40",
    info: "text-sky-600 dark:text-sky-400 bg-sky-100 dark:bg-sky-900/40",
  };

  return (
    <div
      className={clsx(
        "rounded-xl border p-5 shadow-sm transition-all hover:shadow-md",
        variantStyles[variant],
        className
      )}
    >
      <div className="flex items-center justify-between gap-2">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
          {title}
        </span>
        <div className="flex items-center gap-2">
          {badge && (
            <span className="rounded bg-slate-100 px-1.5 py-0.5 text-[10px] font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-300">
              {badge}
            </span>
          )}
          {Icon && (
            <div className={clsx("rounded-lg p-2 flex items-center justify-center", iconStyles[variant])}>
              <Icon className="h-4 w-4" />
            </div>
          )}
        </div>
      </div>

      <div className="mt-3 flex items-baseline justify-between gap-2">
        <div className="text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-50">
          {value}
        </div>
        {trend && (
          <span
            className={clsx(
              "text-xs font-medium",
              trend.positive ? "text-emerald-600 dark:text-emerald-400" : "text-rose-600 dark:text-rose-400"
            )}
          >
            {trend.value}
          </span>
        )}
      </div>

      {subtext && (
        <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
          {subtext}
        </p>
      )}
    </div>
  );
}
