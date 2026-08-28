import React from "react";
import Link from "next/link";
import { Layers, ShieldCheck, Github, ExternalLink } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-950 py-10 text-xs text-slate-500">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-3">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-slate-900 text-white dark:bg-indigo-600">
              <Layers className="h-4 w-4" />
            </div>
            <div>
              <span className="font-bold text-slate-800 dark:text-slate-200 text-sm">
                LedgerLens
              </span>
              <p className="text-[11px] text-slate-400">
                Deterministic Reconciliation & AI Financial Investigation
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-6 text-slate-600 dark:text-slate-400 font-medium">
            <Link href="/dashboard" className="hover:text-slate-900 dark:hover:text-slate-100 transition-colors">
              Dashboard
            </Link>
            <Link href="/reconciliation" className="hover:text-slate-900 dark:hover:text-slate-100 transition-colors">
              Reconciliation
            </Link>
            <Link href="/investigations" className="hover:text-slate-900 dark:hover:text-slate-100 transition-colors">
              Investigations
            </Link>
            <Link href="/evaluation" className="hover:text-slate-900 dark:hover:text-slate-100 transition-colors">
              Benchmark
            </Link>
            <Link href="/help" className="hover:text-slate-900 dark:hover:text-slate-100 transition-colors">
              Help Center
            </Link>
            <Link href="/about" className="hover:text-slate-900 dark:hover:text-slate-100 transition-colors">
              Architecture
            </Link>
          </div>

          <div className="flex items-center gap-4 text-[11px] text-slate-400">
            <span className="flex items-center gap-1">
              <ShieldCheck className="h-3.5 w-3.5 text-emerald-500" />
              <span>Evidence-Grounded Engine</span>
            </span>
          </div>
        </div>

        <div className="mt-8 border-t border-slate-100 dark:border-slate-800/80 pt-6 text-center text-[11px] text-slate-400">
          <p>
            LedgerLens is designed for digital commerce merchants, payment aggregators, and fintech platforms. Every rupee gets an evidence trail.
          </p>
        </div>
      </div>
    </footer>
  );
}
