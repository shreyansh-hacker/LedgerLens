"use client";

import React, { useState } from "react";
import { HelpCircle, ChevronDown, ChevronUp, ShieldCheck, BrainCircuit, Cpu, Calculator, AlertTriangle } from "lucide-react";
import { clsx } from "clsx";

export default function HelpPage() {
  const [openFaq, setOpenFaq] = useState<number | null>(null);

  const faqs = [
    {
      q: "What is LedgerLens and how is it different from accounting software?",
      a: "LedgerLens is an AI-powered financial reconciliation and investigation engine designed specifically for digital commerce and payment aggregators. While accounting software records journals and balances, LedgerLens validates that every captured payment is mathematically and operationally accounted for by gateway settlements and bank statement credits.",
    },
    {
      q: "What is the difference between an Exception and an Anomaly?",
      a: "An Exception is a deterministic financial variance discovered by arithmetic rules (e.g. a gateway deducted a ₹63.55 fee instead of the scheduled ₹9.03 rate, or bank credit is missing). An Anomaly is a multi-dimensional statistical outlier discovered by unsupervised Machine Learning (Isolation Forest) across 14 observable features like volume shifts or 25-day settlement delays.",
    },
    {
      q: "Is the ML Anomaly Detector a fraud detection tool?",
      a: "No. LedgerLens treats anomalies strictly as statistical population outliers. An anomaly score indicates that a transaction pattern deviates significantly from the merchant baseline, signaling that deeper operational review is prudent—without making unsubstantiated fraud accusations.",
    },
    {
      q: "How does LedgerLens prevent AI hallucinations?",
      a: "The AI Investigator operates under strict anti-hallucination guardrails: (1) The LLM never invents financial figures, fees, or taxes. (2) Every claimed fact must cite explicit ledger entity IDs (e.g. pay_*, fee_*, set_*). (3) If a discrepancy cannot be explained by recorded evidence, the model is required to escalate to HUMAN_REVIEW_REQUIRED and state the missing evidence.",
    },
    {
      q: "How is the System Confidence score calculated?",
      a: "System Confidence is a composite score calculated from four observable factors: Deterministic Calculation Agreement (35%), Evidence Completeness (25%), Multi-Pass Matching Score (20%), and AI Fact Grounding (20%), minus an Anomaly Risk Penalty. It does not rely on LLM self-confidence alone.",
    },
    {
      q: "What is the SHA-256 Canonical Evidence Cache?",
      a: "Every assembled evidence payload is canonically sorted and hashed using SHA-256 (evidence_hash). If an identical financial state is investigated again, LedgerLens returns the cached investigation result in 0 milliseconds, saving API calls and ensuring 100% reproducible results.",
    },
  ];

  return (
    <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 py-8 w-full space-y-8">
      {/* Header */}
      <div className="pb-6 border-b border-slate-200 dark:border-slate-800">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
          Knowledge Base & User Manual
        </span>
        <h1 className="text-2xl font-extrabold tracking-tight text-slate-900 dark:text-slate-50 sm:text-3xl">
          LedgerLens Help Center
        </h1>
        <p className="mt-1 text-xs text-slate-500 max-w-2xl">
          Everything you need to know about deterministic matching, anomaly scoring, and evidence-grounded AI investigations.
        </p>
      </div>

      {/* Concept Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/80 p-5 shadow-sm space-y-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-50 text-emerald-600 dark:bg-emerald-950 dark:text-emerald-400">
            <Calculator className="h-4 w-4" />
          </div>
          <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100">Deterministic Rules</h3>
          <p className="text-xs text-slate-500 leading-relaxed">
            Exact Python Decimal math handles all fees, 18% GST tax rates, and net settlement equations. No floating-point rounding errors.
          </p>
        </div>

        <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/80 p-5 shadow-sm space-y-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-50 text-amber-600 dark:bg-amber-950 dark:text-amber-400">
            <Cpu className="h-4 w-4" />
          </div>
          <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100">Isolation Forest ML</h3>
          <p className="text-xs text-slate-500 leading-relaxed">
            Unsupervised outlier detection flags transactions with extreme latency, unusual fee percentages, or volume surges compared to merchant norms.
          </p>
        </div>

        <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/80 p-5 shadow-sm space-y-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600 dark:bg-indigo-950 dark:text-indigo-400">
            <BrainCircuit className="h-4 w-4" />
          </div>
          <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100">Groq AI Investigator</h3>
          <p className="text-xs text-slate-500 leading-relaxed">
            Receives sanitized evidence packets and explains discrepancies using only verified facts. Escalates gaps to human operators.
          </p>
        </div>
      </div>

      {/* FAQ Accordions */}
      <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/80 p-6 shadow-sm space-y-4">
        <h2 className="text-base font-bold text-slate-900 dark:text-slate-100">
          Frequently Asked Questions
        </h2>

        <div className="divide-y divide-slate-100 dark:divide-slate-800">
          {faqs.map((faq, index) => {
            const isOpen = openFaq === index;
            return (
              <div key={index} className="py-3">
                <button
                  type="button"
                  onClick={() => setOpenFaq(isOpen ? null : index)}
                  className="flex w-full items-center justify-between text-left text-xs font-semibold text-slate-900 dark:text-slate-100 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
                >
                  <span>{faq.q}</span>
                  {isOpen ? (
                    <ChevronUp className="h-4 w-4 text-slate-400 flex-shrink-0" />
                  ) : (
                    <ChevronDown className="h-4 w-4 text-slate-400 flex-shrink-0" />
                  )}
                </button>

                {isOpen && (
                  <p className="mt-2 text-xs text-slate-600 dark:text-slate-300 leading-relaxed pl-2 border-l-2 border-indigo-500">
                    {faq.a}
                  </p>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
