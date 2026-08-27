import Link from "next/link";
import StatusBadge from "@/components/StatusBadge";
import { 
  ArrowLeft, 
  CheckCircle2, 
  AlertCircle, 
  ShieldCheck, 
  Sparkles, 
  FileText, 
  Layers, 
  ArrowDown
} from "lucide-react";

export default function InvestigationDetailPage({ params }: { params: { id: string } }) {
  const txnId = params.id;

  return (
    <div className="py-8 px-4 sm:px-6 lg:px-8 max-w-6xl mx-auto w-full">
      {/* Back Link & Header */}
      <div className="mb-6">
        <Link
          href="/investigations"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-surface-500 hover:text-surface-900 transition-colors mb-3"
        >
          <ArrowLeft className="h-3.5 w-3.5" /> Back to Investigations Queue
        </Link>

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold font-mono text-surface-900">{txnId}</h1>
            <StatusBadge status="EXPLAINED" />
            <span className="inline-flex items-center gap-1 text-xs font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
              <ShieldCheck className="h-3.5 w-3.5" /> 97% Confidence
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button className="rounded-lg border border-surface-300 bg-white px-3 py-1.5 text-xs font-semibold text-surface-700 hover:bg-surface-50 shadow-sm transition-colors">
              Add Note
            </button>
            <button className="rounded-lg bg-emerald-600 px-3.5 py-1.5 text-xs font-semibold text-white hover:bg-emerald-700 shadow-sm transition-colors">
              Mark Resolved
            </button>
          </div>
        </div>
      </div>

      {/* Main Grid: Structured Evidence + AI Reasoning */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Financial Breakdown & Evidence Trail */}
        <div className="lg:col-span-2 space-y-6">
          {/* Card: Financial Reconciliation Math */}
          <div className="rounded-xl border border-surface-200 bg-white p-6 shadow-sm">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-surface-500 mb-4">
              Deterministic Amount Reconciliation
            </h2>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4 rounded-lg bg-surface-50 border border-surface-200 mb-4 text-center">
              <div>
                <span className="text-xs text-surface-500">Order Amount</span>
                <p className="text-base font-bold text-surface-900 mt-0.5">₹10,000.00</p>
              </div>
              <div>
                <span className="text-xs text-surface-500">Fee + Tax</span>
                <p className="text-base font-bold text-surface-900 mt-0.5">₹236.00</p>
              </div>
              <div>
                <span className="text-xs text-surface-500">Expected Settlement</span>
                <p className="text-base font-bold text-surface-900 mt-0.5">₹9,764.00</p>
              </div>
              <div>
                <span className="text-xs text-surface-500">Bank Credit</span>
                <p className="text-base font-bold text-emerald-600 mt-0.5">₹9,764.00</p>
              </div>
            </div>

            {/* Evidence Timeline */}
            <div className="mt-6">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-surface-500 mb-3">
                Evidence Audit Trail
              </h3>
              <div className="space-y-3 border-l-2 border-primary-200 pl-4 ml-2">
                <div className="relative">
                  <div className="absolute -left-[21px] top-1 h-2.5 w-2.5 rounded-full bg-primary-700"></div>
                  <p className="text-xs font-semibold text-surface-900">Payment Captured</p>
                  <p className="text-xs text-surface-500">Reference: pay_K8j21kLm90 | ₹10,000.00 UPI</p>
                </div>
                <div className="relative">
                  <div className="absolute -left-[21px] top-1 h-2.5 w-2.5 rounded-full bg-primary-700"></div>
                  <p className="text-xs font-semibold text-surface-900">Gateway Fee & GST Ingested</p>
                  <p className="text-xs text-surface-500">Fee: ₹200.00 (2.0%) + GST 18%: ₹36.00</p>
                </div>
                <div className="relative">
                  <div className="absolute -left-[21px] top-1 h-2.5 w-2.5 rounded-full bg-primary-700"></div>
                  <p className="text-xs font-semibold text-surface-900">Settlement Matched</p>
                  <p className="text-xs text-surface-500">Settlement ID: set_99a8bc | Net ₹9,764.00</p>
                </div>
                <div className="relative">
                  <div className="absolute -left-[21px] top-1 h-2.5 w-2.5 rounded-full bg-emerald-600"></div>
                  <p className="text-xs font-semibold text-surface-900">Bank Credit Confirmed</p>
                  <p className="text-xs text-surface-500">UTR: UTR9982711002 | Amount: ₹9,764.00</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right 1 Col: AI Investigator Insight & Action */}
        <div className="space-y-6">
          <div className="rounded-xl border border-primary-200 bg-gradient-to-b from-white to-primary-50/20 p-6 shadow-sm">
            <div className="flex items-center gap-2 text-primary-700 mb-3">
              <Sparkles className="h-4 w-4" />
              <h2 className="text-sm font-bold uppercase tracking-wider">AI Investigator Reasoning</h2>
            </div>
            <p className="text-xs text-surface-700 leading-relaxed">
              The ₹236.00 discrepancy between payment gross and net settlement is completely accounted for by the standard ₹200 gateway fee plus 18% GST (₹36.00). Bank credit exactly matches calculated net amount.
            </p>

            <div className="mt-4 pt-4 border-t border-surface-200 space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="text-surface-500">Ground Truth Scenario:</span>
                <span className="font-semibold text-surface-800">Normal Settled</span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-surface-500">Model Engine:</span>
                <span className="font-mono text-surface-800">Groq / llama-3.3-70b</span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-surface-500">Hallucination Guard:</span>
                <span className="text-emerald-700 font-medium">Passed (100% Cites)</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
