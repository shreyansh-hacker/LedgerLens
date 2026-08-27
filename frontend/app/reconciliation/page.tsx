import { FileSpreadsheet, UploadCloud, Zap, CheckCircle2 } from "lucide-react";

export default function ReconciliationPage() {
  return (
    <div className="py-8 px-4 sm:px-6 lg:px-8 max-w-5xl mx-auto w-full">
      <div className="pb-6 border-b border-surface-200">
        <h1 className="text-2xl font-bold text-surface-900 tracking-tight">Financial Reconciliation</h1>
        <p className="text-sm text-surface-500 mt-1">
          Import merchant transaction feeds or load the standard 1,000-record benchmark demo dataset.
        </p>
      </div>

      <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Card 1: 1-Click Demo */}
        <div className="rounded-xl border border-primary-200 bg-white p-6 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary-50 text-primary-700 mb-4">
              <Zap className="h-5 w-5" />
            </div>
            <h2 className="text-base font-bold text-surface-900">1-Click Demo Dataset</h2>
            <p className="mt-2 text-xs text-surface-600 leading-relaxed">
              Generates 1,000 synthetic records with controlled ground-truth labels: clean matches, fee mismatches, missing bank transactions, and unresolved exceptions.
            </p>
          </div>

          <div className="mt-6 pt-4 border-t border-surface-100">
            <button className="w-full inline-flex items-center justify-center gap-2 rounded-lg bg-primary-700 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-primary-800 transition-colors">
              <Zap className="h-4 w-4" /> Load Demo Dataset
            </button>
          </div>
        </div>

        {/* Card 2: Custom CSV Ingestion */}
        <div className="rounded-xl border border-surface-200 bg-white p-6 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-surface-100 text-surface-700 mb-4">
              <UploadCloud className="h-5 w-5" />
            </div>
            <h2 className="text-base font-bold text-surface-900">Upload Transaction CSVs</h2>
            <p className="mt-2 text-xs text-surface-600 leading-relaxed">
              Upload standard payment gateway exports (Razorpay, Stripe) and bank statement CSV files to run custom reconciliation.
            </p>
          </div>

          <div className="mt-6 pt-4 border-t border-surface-100">
            <label className="w-full inline-flex items-center justify-center gap-2 rounded-lg border border-surface-300 bg-white px-4 py-2.5 text-sm font-semibold text-surface-700 shadow-sm hover:bg-surface-50 cursor-pointer transition-colors">
              <UploadCloud className="h-4 w-4" /> Select CSV Files
              <input type="file" className="hidden" accept=".csv" />
            </label>
          </div>
        </div>
      </div>
    </div>
  );
}
