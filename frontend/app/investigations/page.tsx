import StatusBadge from "@/components/StatusBadge";
import Link from "next/link";
import { SearchCheck, Filter, ArrowUpRight } from "lucide-react";

export default function InvestigationsPage() {
  return (
    <div className="py-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-surface-200">
        <div>
          <h1 className="text-2xl font-bold text-surface-900 tracking-tight">Investigation Queue</h1>
          <p className="text-sm text-surface-500 mt-1">
            Review exceptions, AI-generated explanations, and human review escalations.
          </p>
        </div>

        {/* Filter Tabs */}
        <div className="flex items-center gap-1.5 p-1 bg-surface-100 rounded-lg border border-surface-200 text-xs font-medium">
          <button className="px-3 py-1.5 rounded-md bg-white text-surface-900 shadow-sm font-semibold">
            All (87)
          </button>
          <button className="px-3 py-1.5 rounded-md text-surface-600 hover:text-surface-900">
            Explained (61)
          </button>
          <button className="px-3 py-1.5 rounded-md text-surface-600 hover:text-surface-900">
            Human Review (26)
          </button>
        </div>
      </div>

      {/* Table Container */}
      <div className="mt-6 table-container">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr>
              <th className="table-header-cell">Transaction ID</th>
              <th className="table-header-cell">Order Ref</th>
              <th className="table-header-cell">Discrepancy</th>
              <th className="table-header-cell">Status</th>
              <th className="table-header-cell">Confidence</th>
              <th className="table-header-cell">AI Summary</th>
              <th className="table-header-cell text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-surface-100">
            <tr className="hover:bg-surface-50 transition-colors">
              <td className="table-row-cell font-mono font-medium text-surface-900">TXN-1021</td>
              <td className="table-row-cell font-mono text-surface-500">ORD-9428</td>
              <td className="table-row-cell font-semibold text-rose-600">₹800.00</td>
              <td className="table-row-cell">
                <StatusBadge status="EXPLAINED" />
              </td>
              <td className="table-row-cell">
                <span className="font-semibold text-emerald-600">97%</span> (High)
              </td>
              <td className="table-row-cell max-w-xs truncate text-surface-600">
                Explained by ₹680 gateway fee and ₹120 GST
              </td>
              <td className="table-row-cell text-right">
                <Link
                  href="/investigations/TXN-1021"
                  className="inline-flex items-center gap-1 text-xs font-semibold text-primary-700 hover:text-primary-800"
                >
                  Inspect <ArrowUpRight className="h-3 w-3" />
                </Link>
              </td>
            </tr>

            <tr className="hover:bg-surface-50 transition-colors">
              <td className="table-row-cell font-mono font-medium text-surface-900">TXN-1082</td>
              <td className="table-row-cell font-mono text-surface-500">ORD-9489</td>
              <td className="table-row-cell font-semibold text-rose-600">₹2,400.00</td>
              <td className="table-row-cell">
                <StatusBadge status="HUMAN_REVIEW" />
              </td>
              <td className="table-row-cell">
                <span className="font-semibold text-amber-600">41%</span> (Medium)
              </td>
              <td className="table-row-cell max-w-xs truncate text-surface-600">
                Settlement difference exceeds standard fee schedule
              </td>
              <td className="table-row-cell text-right">
                <Link
                  href="/investigations/TXN-1082"
                  className="inline-flex items-center gap-1 text-xs font-semibold text-primary-700 hover:text-primary-800"
                >
                  Inspect <ArrowUpRight className="h-3 w-3" />
                </Link>
              </td>
            </tr>

            <tr className="hover:bg-surface-50 transition-colors">
              <td className="table-row-cell font-mono font-medium text-surface-900">TXN-1104</td>
              <td className="table-row-cell font-mono text-surface-500">ORD-9512</td>
              <td className="table-row-cell font-semibold text-rose-600">Missing Bank</td>
              <td className="table-row-cell">
                <StatusBadge status="HUMAN_REVIEW" />
              </td>
              <td className="table-row-cell">
                <span className="font-semibold text-rose-600">18%</span> (Low)
              </td>
              <td className="table-row-cell max-w-xs truncate text-surface-600">
                Payment and settlement exist, no bank transaction found
              </td>
              <td className="table-row-cell text-right">
                <Link
                  href="/investigations/TXN-1104"
                  className="inline-flex items-center gap-1 text-xs font-semibold text-primary-700 hover:text-primary-800"
                >
                  Inspect <ArrowUpRight className="h-3 w-3" />
                </Link>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
