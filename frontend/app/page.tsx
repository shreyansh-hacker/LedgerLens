"use client";

import React from "react";
import Link from "next/link";
import {
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  FileSpreadsheet,
  BrainCircuit,
  Search,
  Sparkles,
  Database,
  BarChart3,
  Cpu,
  Lock,
} from "lucide-react";

export default function LandingPage() {
  const steps = [
    {
      num: "01",
      title: "Ingest Financial Records",
      desc: "Connect gateway webhooks, batch settlement files, and nodal bank statements via API or CSV.",
    },
    {
      num: "02",
      title: "Deterministic Reconciliation",
      desc: "Multi-pass matching engine validates exact fees, 18% GST tax schedules, and net settlement arithmetic.",
    },
    {
      num: "03",
      title: "ML Anomaly Scoring",
      desc: "Unsupervised Isolation Forest scores population-level outliers across volume, fee ratios, and latency.",
    },
    {
      num: "04",
      title: "Evidence-Grounded AI",
      desc: "Groq LLaMA-3.3-70B investigates discrepancies citing only verified ledger facts with zero hallucinations.",
    },
    {
      num: "05",
      title: "Audit & Human Decision",
      desc: "Controllers review high-confidence explanations or take action on flagged variances with complete audit logs.",
    },
  ];

  return (
    <div className="flex flex-col">
      {/* Hero Section */}
      <section className="relative overflow-hidden border-b border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900/60 py-20 sm:py-28">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-3xl text-center">
            {/* Pill */}
            <div className="inline-flex items-center gap-2 rounded-full border border-indigo-200/80 bg-indigo-50/60 px-3.5 py-1 text-xs font-semibold text-indigo-700 dark:border-indigo-800/80 dark:bg-indigo-950/40 dark:text-indigo-300 mb-6">
              <Sparkles className="h-3.5 w-3.5 text-indigo-500" />
              <span>Evidence-First Financial Intelligence</span>
            </div>

            <h1 className="text-4xl font-extrabold tracking-tight text-slate-900 dark:text-slate-50 sm:text-5xl lg:text-6xl">
              Every rupee gets an{" "}
              <span className="text-indigo-600 dark:text-indigo-400 underline decoration-indigo-200 dark:decoration-indigo-900 underline-offset-8">
                evidence trail
              </span>
              .
            </h1>

            <p className="mt-6 text-lg leading-8 text-slate-600 dark:text-slate-300">
              LedgerLens reconciles payments, settlements, and bank statements with exact decimal math, scores multi-dimensional anomalies with Isolation Forest, and explains discrepancies using verifiable evidence.
            </p>

            {/* CTA Buttons */}
            <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
              <Link
                href="/reconciliation"
                className="flex items-center gap-2 rounded-xl bg-indigo-600 px-6 py-3.5 text-sm font-semibold text-white shadow-lg hover:bg-indigo-500 transition-all hover:scale-105"
              >
                <Database className="h-4 w-4" />
                <span>Try Live Demo</span>
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                href="/dashboard"
                className="flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-6 py-3.5 text-sm font-semibold text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700 transition-all"
              >
                <span>View Dashboard</span>
              </Link>
              <Link
                href="/evaluation"
                className="flex items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 px-5 py-3.5 text-sm font-semibold text-slate-600 hover:bg-slate-100 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 transition-all"
              >
                <BarChart3 className="h-4 w-4" />
                <span>Benchmark</span>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* 3-Tier Architecture Section */}
      <section className="py-16 bg-slate-50 dark:bg-slate-950 border-b border-slate-200 dark:border-slate-800">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-indigo-600 dark:text-indigo-400">
              Separation of Responsibilities
            </h2>
            <p className="mt-2 text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-100 sm:text-3xl">
              The Right Technology for the Right Job
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Card 1 */}
            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900/80">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600 dark:bg-emerald-950/60 dark:text-emerald-400 mb-4">
                <FileSpreadsheet className="h-5 w-5" />
              </div>
              <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">
                1. Deterministic Engine
              </h3>
              <p className="mt-2 text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                Calculates exact rupee balances using strict Python <code className="text-indigo-600 dark:text-indigo-400">Decimal</code> math. Multi-pass matcher links payments to settlements and bank UTRs without probabilistic guesswork.
              </p>
              <ul className="mt-4 space-y-1.5 text-xs text-slate-500">
                <li className="flex items-center gap-1.5">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                  <span>Exact MDR fee & GST 18% math</span>
                </li>
                <li className="flex items-center gap-1.5">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                  <span>Pass 1 reference & Pass 2 ID link</span>
                </li>
              </ul>
            </div>

            {/* Card 2 */}
            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900/80">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-50 text-amber-600 dark:bg-amber-950/60 dark:text-amber-400 mb-4">
                <Cpu className="h-5 w-5" />
              </div>
              <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">
                2. ML Anomaly Detection
              </h3>
              <p className="mt-2 text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                Scikit-Learn <code className="text-indigo-600 dark:text-indigo-400">IsolationForest</code> models population baselines on 14 observable features, assigning 0–100 normalized anomaly risk scores.
              </p>
              <ul className="mt-4 space-y-1.5 text-xs text-slate-500">
                <li className="flex items-center gap-1.5">
                  <CheckCircle2 className="h-3.5 w-3.5 text-amber-500" />
                  <span>Unsupervised multi-dimensional scoring</span>
                </li>
                <li className="flex items-center gap-1.5">
                  <CheckCircle2 className="h-3.5 w-3.5 text-amber-500" />
                  <span>Zero synthetic ground-truth leakage</span>
                </li>
              </ul>
            </div>

            {/* Card 3 */}
            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900/80">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600 dark:bg-indigo-950/60 dark:text-indigo-400 mb-4">
                <BrainCircuit className="h-5 w-5" />
              </div>
              <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">
                3. Groq AI Investigator
              </h3>
              <p className="mt-2 text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                LLaMA-3.3-70B analyzes verified evidence packages to explain root causes. Strict anti-hallucination rules mandate human review whenever evidence is missing.
              </p>
              <ul className="mt-4 space-y-1.5 text-xs text-slate-500">
                <li className="flex items-center gap-1.5">
                  <CheckCircle2 className="h-3.5 w-3.5 text-indigo-500" />
                  <span>Every fact cited to entity IDs</span>
                </li>
                <li className="flex items-center gap-1.5">
                  <CheckCircle2 className="h-3.5 w-3.5 text-indigo-500" />
                  <span>SHA-256 canonical evidence caching</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* How it Works Workflow */}
      <section className="py-16 bg-white dark:bg-slate-900/60 border-b border-slate-200 dark:border-slate-800">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-500">
              End-to-End Workflow
            </h2>
            <p className="mt-2 text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-100 sm:text-3xl">
              From Raw Statement to Verifiable Resolution
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            {steps.map((s) => (
              <div
                key={s.num}
                className="rounded-xl border border-slate-200 dark:border-slate-800 p-4 bg-slate-50/50 dark:bg-slate-800/30 flex flex-col justify-between"
              >
                <div>
                  <span className="font-mono text-lg font-extrabold text-indigo-600 dark:text-indigo-400">
                    {s.num}
                  </span>
                  <h4 className="mt-2 text-xs font-bold text-slate-900 dark:text-slate-100">
                    {s.title}
                  </h4>
                  <p className="mt-1.5 text-[11px] text-slate-500 leading-relaxed">
                    {s.desc}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Footer Banner */}
      <section className="py-14 bg-indigo-900 text-white text-center">
        <div className="mx-auto max-w-4xl px-4">
          <h2 className="text-2xl font-bold tracking-tight sm:text-3xl">
            Experience the 1-Click Financial Demo
          </h2>
          <p className="mt-3 text-sm text-indigo-200 max-w-xl mx-auto">
            Load 1,000 synthetic transaction clusters spanning 10 controlled scenarios, run reconciliation, and inspect live AI investigations in seconds.
          </p>
          <div className="mt-6">
            <Link
              href="/reconciliation"
              className="inline-flex items-center gap-2 rounded-xl bg-white px-6 py-3 text-sm font-bold text-indigo-900 shadow-md hover:bg-indigo-50 transition-all hover:scale-105"
            >
              <span>Launch Demo Center</span>
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
