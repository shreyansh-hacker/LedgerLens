import { HelpCircle, CheckCircle2, ShieldAlert } from "lucide-react";

export default function HelpPage() {
  const sections = [
    {
      q: "What is LedgerLens?",
      a: "LedgerLens is an AI-powered financial reconciliation and investigation platform for merchants. It verifies that money flowing through orders, payment gateways, fees, taxes, refunds, and bank accounts matches precisely, and provides an auditable evidence trail for every rupee.",
    },
    {
      q: "What is reconciliation?",
      a: "Reconciliation is the accounting process of comparing two or more sets of financial records to ensure they agree. In e-commerce, it means ensuring that what a customer paid matches what the gateway collected minus fees and taxes, and matches what was credited to the merchant's bank account.",
    },
    {
      q: "What does LedgerLens check?",
      a: "LedgerLens verifies 7 interconnected financial components: Order Amount, Payment Captured, Payment Gateway MDR Fees, GST on Fees (18%), Customer Refunds, Settlement Batches, and Bank Statement Credits (UTR matching).",
    },
    {
      q: "How does AI investigation work?",
      a: "When a discrepancy is detected, deterministic code extracts verified facts and passes structured JSON to our Groq LLM investigator. The AI evaluates whether known fees, taxes, or adjustments explain the variance. It never calculates amounts itself and never invents unrecorded fees.",
    },
    {
      q: "What is confidence score?",
      a: "The confidence score (0–100%) is a composite metric reflecting record matching quality, evidence completeness, calculation agreement, and anomaly risk. Scores ≥90% are High Confidence, 60–89% are Medium, and <60% are escalated to Human Review.",
    },
    {
      q: "What does Human Review mean?",
      a: "When evidence is missing, contradictory, or unexplainable, LedgerLens refuses to guess and escalates the transaction to the Human Review Queue where finance operators can inspect, annotate, or override the decision.",
    },
    {
      q: "What data is used in the demo?",
      a: "The demo uses a 1,000-record synthetic dataset modeling authentic Indian merchant transaction patterns, standard payment gateway fees, 18% GST rates, and controlled real-world exceptions.",
    },
    {
      q: "What are the current limitations?",
      a: "Currency conversion for multi-currency transactions is currently simulated in INR. Complex rolling reserve deductions are planned for future releases.",
    },
  ];

  return (
    <div className="py-8 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto w-full">
      <div className="pb-6 border-b border-surface-200">
        <h1 className="text-2xl font-bold text-surface-900 tracking-tight">Help & Documentation</h1>
        <p className="text-sm text-surface-500 mt-1">
          Everything you need to know about LedgerLens, reconciliation mechanics, and AI investigation principles.
        </p>
      </div>

      <div className="mt-8 space-y-6">
        {sections.map((sec, idx) => (
          <div key={idx} className="rounded-xl border border-surface-200 bg-white p-6 shadow-sm">
            <h2 className="text-base font-semibold text-surface-900 flex items-center gap-2">
              <span className="flex h-6 w-6 items-center justify-center rounded bg-primary-50 text-primary-700 text-xs font-bold shrink-0">
                {idx + 1}
              </span>
              {sec.q}
            </h2>
            <p className="mt-3 text-sm text-surface-600 leading-relaxed pl-8">
              {sec.a}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
