import Link from "next/link";
import { 
  ShieldCheck, 
  ArrowRight, 
  CheckCircle2, 
  SearchCheck, 
  Cpu, 
  FileCheck2, 
  Scale, 
  AlertTriangle,
  Zap
} from "lucide-react";

export default function LandingPage() {
  return (
    <div className="flex flex-col">
      {/* Hero Section */}
      <section className="relative overflow-hidden border-b border-surface-200 bg-white py-20 lg:py-28">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col items-center text-center">
            {/* Pill Badge */}
            <div className="inline-flex items-center gap-2 rounded-full border border-primary-200 bg-primary-50 px-3.5 py-1 text-xs font-semibold text-primary-800 shadow-sm mb-6">
              <ShieldCheck className="h-3.5 w-3.5 text-primary-700" />
              <span>Deterministic Precision + Evidence-First AI</span>
            </div>

            {/* Main Headline */}
            <h1 className="max-w-4xl text-4xl font-extrabold tracking-tight text-surface-900 sm:text-5xl lg:text-6xl">
              Every rupee gets an <span className="text-primary-700 underline decoration-primary-300 decoration-wavy decoration-2">evidence trail</span>.
            </h1>

            {/* Subtitle */}
            <p className="mt-6 max-w-2xl text-base sm:text-lg text-surface-600 leading-relaxed">
              LedgerLens cross-verifies orders, payments, gateway fees, GST taxes, refunds, and bank settlements. It mathematically proves discrepancies and uses AI to inspect anomalies with 100% auditable citations.
            </p>

            {/* CTA Buttons */}
            <div className="mt-10 flex flex-col sm:flex-row items-center gap-4">
              <Link
                href="/reconciliation"
                className="inline-flex h-11 items-center justify-center gap-2 rounded-lg bg-primary-700 px-6 text-sm font-semibold text-white shadow-sm hover:bg-primary-800 transition-all"
              >
                <Zap className="h-4 w-4" />
                Try Live Demo
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                href="/dashboard"
                className="inline-flex h-11 items-center justify-center rounded-lg border border-surface-300 bg-white px-6 text-sm font-semibold text-surface-700 shadow-sm hover:bg-surface-50 transition-all"
              >
                View Dashboard
              </Link>
            </div>

            {/* Trust Highlights */}
            <div className="mt-12 grid grid-cols-2 md:grid-cols-4 gap-6 text-left border-t border-surface-100 pt-8 w-full max-w-3xl">
              <div className="flex items-center gap-2 text-xs font-medium text-surface-600">
                <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0" />
                <span>Zero Hallucination Guardrails</span>
              </div>
              <div className="flex items-center gap-2 text-xs font-medium text-surface-600">
                <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0" />
                <span>Decimal Precision Math</span>
              </div>
              <div className="flex items-center gap-2 text-xs font-medium text-surface-600">
                <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0" />
                <span>Isolation Forest Anomaly ML</span>
              </div>
              <div className="flex items-center gap-2 text-xs font-medium text-surface-600">
                <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0" />
                <span>Auditable Review Queue</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How it Works Section */}
      <section className="py-16 bg-surface-50 border-b border-surface-200">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-2xl font-bold text-surface-900">How LedgerLens Reconciles</h2>
            <p className="mt-2 text-sm text-surface-500">The right technology for the right job — deterministic code for money, AI for investigation.</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="rounded-xl bg-white p-6 border border-surface-200 shadow-sm">
              <div className="h-10 w-10 rounded-lg bg-primary-50 text-primary-700 flex items-center justify-center font-bold text-sm mb-4">
                1
              </div>
              <h3 className="font-semibold text-surface-900 text-base mb-2">Deterministic Ingestion & Matching</h3>
              <p className="text-sm text-surface-600 leading-relaxed">
                Connects orders, payment gateway events, platform fees, GST calculations, and bank UTRs via multi-signal matching algorithms.
              </p>
            </div>

            <div className="rounded-xl bg-white p-6 border border-surface-200 shadow-sm">
              <div className="h-10 w-10 rounded-lg bg-primary-50 text-primary-700 flex items-center justify-center font-bold text-sm mb-4">
                2
              </div>
              <h3 className="font-semibold text-surface-900 text-base mb-2">Anomaly Detection Engine</h3>
              <p className="text-sm text-surface-600 leading-relaxed">
                Scikit-Learn Isolation Forest scores transactions across fee ratios, settlement delays, and volume deviations to spot subtle leakages.
              </p>
            </div>

            <div className="rounded-xl bg-white p-6 border border-surface-200 shadow-sm">
              <div className="h-10 w-10 rounded-lg bg-primary-50 text-primary-700 flex items-center justify-center font-bold text-sm mb-4">
                3
              </div>
              <h3 className="font-semibold text-surface-900 text-base mb-2">Evidence-First AI Investigator</h3>
              <p className="text-sm text-surface-600 leading-relaxed">
                Groq LLM evaluates verified facts to construct transparent explanations. If evidence is missing, it explicitly yields to human review.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
