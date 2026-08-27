import { ShieldCheck, Cpu, Database, Activity, GitBranch } from "lucide-react";

export default function AboutPage() {
  return (
    <div className="py-8 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto w-full">
      <div className="pb-6 border-b border-surface-200">
        <h1 className="text-2xl font-bold text-surface-900 tracking-tight">About LedgerLens</h1>
        <p className="text-sm text-surface-500 mt-1">
          The philosophy, architecture, and technology powering evidence-first financial reconciliation.
        </p>
      </div>

      <div className="mt-8 space-y-8">
        <section className="rounded-xl border border-surface-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-bold text-surface-900 mb-3">The Problem</h2>
          <p className="text-sm text-surface-600 leading-relaxed">
            Modern online merchants process thousands of transactions daily across multiple payment channels (UPI, cards, net banking). When reconciliation discrepancies occur — due to variable MDR rates, GST changes, timing delays, or missing bank UTRs — finance teams spend dozens of hours manually digging through spreadsheets to answer a simple question: <em>"Where did this money go?"</em>
          </p>
        </section>

        <section className="rounded-xl border border-surface-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-bold text-surface-900 mb-3">The Solution: Evidence-First AI</h2>
          <p className="text-sm text-surface-600 leading-relaxed">
            LedgerLens is designed on a core principle: <strong>Every rupee gets an evidence trail.</strong> Generic AI chatbots tend to hallucinate convenient explanations. LedgerLens separates concerns: deterministic code calculates ground truth with decimal precision, machine learning detects anomalies, and Groq LLMs reason strictly over structured, verified evidence. If evidence is missing, the system demonstrates <em>"I don't know"</em> and escalates to human review.
          </p>
        </section>

        <section className="rounded-xl border border-surface-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-bold text-surface-900 mb-4">Technology Stack</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div className="p-3 rounded-lg bg-surface-50 border border-surface-200">
              <span className="font-semibold text-surface-900 block mb-1">Frontend</span>
              <span className="text-surface-600">Next.js 14, TypeScript, Tailwind CSS, Lucide Icons</span>
            </div>
            <div className="p-3 rounded-lg bg-surface-50 border border-surface-200">
              <span className="font-semibold text-surface-900 block mb-1">Backend</span>
              <span className="text-surface-600">FastAPI, Python 3.11, Pydantic v2, SQLAlchemy</span>
            </div>
            <div className="p-3 rounded-lg bg-surface-50 border border-surface-200">
              <span className="font-semibold text-surface-900 block mb-1">Anomaly Engine</span>
              <span className="text-surface-600">Scikit-Learn Isolation Forest</span>
            </div>
            <div className="p-3 rounded-lg bg-surface-50 border border-surface-200">
              <span className="font-semibold text-surface-900 block mb-1">AI Investigator</span>
              <span className="text-surface-600">Groq API (Llama 3.3 70B Versatile)</span>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
