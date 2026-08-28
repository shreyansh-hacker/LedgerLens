"use client";

import React from "react";
import Link from "next/link";
import {
  Layers,
  ShieldCheck,
  Code2,
  BrainCircuit,
  Database,
  Cpu,
  ArrowRight,
  Sparkles,
  Server,
  Lock,
} from "lucide-react";

export default function AboutPage() {
  const techStack = [
    { name: "FastAPI & Python 3.11", role: "High-performance asynchronous backend & exact Decimal calculation engine" },
    { name: "SQLAlchemy & SQLite/PostgreSQL", role: "Relational persistence layer for multi-entity financial ledgers" },
    { name: "Scikit-Learn (Isolation Forest)", role: "Unsupervised population anomaly detection across 14 observable features" },
    { name: "Groq Cloud (LLaMA-3.3-70B)", role: "Evidence-grounded structured AI investigator with sub-second LPU inference" },
    { name: "Next.js 14 (App Router)", role: "Modern, responsive server-rendered fintech user interface" },
    { name: "Tailwind CSS & Lucide Icons", role: "Restrained, typography-first fintech design system" },
  ];

  return (
    <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 py-8 w-full space-y-8">
      {/* Header */}
      <div className="pb-6 border-b border-slate-200 dark:border-slate-800">
        <span className="text-xs font-semibold uppercase tracking-wider text-indigo-600 dark:text-indigo-400">
          Architecture & System Design
        </span>
        <h1 className="text-2xl font-extrabold tracking-tight text-slate-900 dark:text-slate-50 sm:text-3xl">
          About LedgerLens
        </h1>
        <p className="mt-1 text-sm text-slate-600 dark:text-slate-300 font-medium">
          Every rupee gets an evidence trail.
        </p>
      </div>

      {/* Mission Section */}
      <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/80 p-6 shadow-sm space-y-3">
        <h2 className="text-base font-bold text-slate-900 dark:text-slate-100">
          The Problem in Digital Commerce Reconciliation
        </h2>
        <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
          High-volume e-commerce merchants and fintech aggregators handle millions of payments daily across cards, UPI, net banking, and wallets. Small discrepancies—such as unannounced gateway fee tier changes, omitted 18% GST tax deductions, or settlement batch delays—routinely compound into significant financial leakages.
        </p>
        <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
          Traditional reconciliation depends on fragile spreadsheets or rigid black-box scripts that cannot explain why a variance occurred. Generic chatbots, on the other hand, frequently hallucinate plausible-sounding explanations.
        </p>
        <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed font-semibold text-indigo-700 dark:text-indigo-300">
          LedgerLens solves this by uniting exact deterministic arithmetic, unsupervised ML anomaly detection, and evidence-grounded generative reasoning.
        </p>
      </div>

      {/* Tech Stack Matrix */}
      <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/80 p-6 shadow-sm space-y-4">
        <h2 className="text-base font-bold text-slate-900 dark:text-slate-100">
          Production Technology Stack
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {techStack.map((t, i) => (
            <div key={i} className="p-3.5 rounded-xl border border-slate-200/70 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30">
              <div className="font-bold text-xs text-slate-900 dark:text-slate-100 font-mono">
                {t.name}
              </div>
              <div className="text-[11px] text-slate-500 mt-1 leading-relaxed">
                {t.role}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Core Engineering Principles */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/80 p-4 space-y-1.5">
          <ShieldCheck className="h-5 w-5 text-emerald-600" />
          <h4 className="text-xs font-bold text-slate-900 dark:text-slate-100">Exact Decimal Arithmetic</h4>
          <p className="text-[11px] text-slate-500">
            Never use floating-point types for monetary values. PostgreSQL NUMERIC and Python Decimal guarantee penny-exact ledger calculations.
          </p>
        </div>

        <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/80 p-4 space-y-1.5">
          <Cpu className="h-5 w-5 text-amber-600" />
          <h4 className="text-xs font-bold text-slate-900 dark:text-slate-100">Zero-Leakage ML</h4>
          <p className="text-[11px] text-slate-500">
            Isolation Forest models population baseline distributions purely on observable features without accessing synthetic ground truth.
          </p>
        </div>

        <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/80 p-4 space-y-1.5">
          <BrainCircuit className="h-5 w-5 text-indigo-600" />
          <h4 className="text-xs font-bold text-slate-900 dark:text-slate-100">Strict Anti-Hallucination</h4>
          <p className="text-[11px] text-slate-500">
            LLM operates strictly over structured verified evidence. Every claimed fact references real entity IDs; unexplainable variances escalate to human review.
          </p>
        </div>
      </div>

      {/* CTA Box */}
      <div className="rounded-2xl bg-indigo-900 p-6 text-white text-center">
        <h3 className="text-base font-bold">Ready to inspect live financial reconciliation?</h3>
        <p className="text-xs text-indigo-200 mt-1 max-w-md mx-auto">
          Load the 1,000-cluster benchmark dataset or explore the interactive Copilot.
        </p>
        <div className="mt-4">
          <Link
            href="/reconciliation"
            className="inline-flex items-center gap-1.5 rounded-xl bg-white px-4 py-2 text-xs font-bold text-indigo-900 hover:bg-indigo-50 shadow-sm transition-all"
          >
            <span>Go to Reconciliation Center</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>
      </div>
    </div>
  );
}
