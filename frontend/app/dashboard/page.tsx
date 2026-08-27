import MetricCard from "@/components/MetricCard";
import { 
  FileSpreadsheet, 
  CheckCircle2, 
  AlertCircle, 
  UserCheck, 
  Percent, 
  IndianRupee,
  Clock,
  Sparkles
} from "lucide-react";
import Link from "next/link";

export default function DashboardPage() {
  return (
    <div className="py-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-surface-200">
        <div>
          <h1 className="text-2xl font-bold text-surface-900 tracking-tight">Reconciliation Dashboard</h1>
          <p className="text-sm text-surface-500 mt-1">
            Real-time financial matching metrics across orders, payments, fees, and bank transactions.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href="/reconciliation"
            className="inline-flex items-center gap-2 rounded-lg bg-primary-700 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-800 transition-colors"
          >
            <Sparkles className="h-4 w-4" /> Load Demo Data
          </Link>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          title="Records Processed"
          value="1,000"
          subtitle="Orders, settlements & bank rows"
          icon={FileSpreadsheet}
        />
        <MetricCard
          title="Reconciled"
          value="913"
          subtitle="Clean deterministic matches"
          icon={CheckCircle2}
          highlight={true}
        />
        <MetricCard
          title="Exceptions"
          value="61"
          subtitle="Flagged for AI investigation"
          icon={AlertCircle}
        />
        <MetricCard
          title="Human Review"
          value="26"
          subtitle="Unresolved / low confidence"
          icon={UserCheck}
        />
      </div>

      {/* Secondary Metrics Row */}
      <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-3">
        <MetricCard
          title="Match Rate"
          value="91.3%"
          subtitle="Target: ≥ 90.0%"
          icon={Percent}
        />
        <MetricCard
          title="Total Financial Difference"
          value="₹32,450.00"
          subtitle="₹28,100 explained by AI"
          icon={IndianRupee}
        />
        <MetricCard
          title="Avg Processing Time"
          value="42ms"
          subtitle="Deterministic pipeline speed"
          icon={Clock}
        />
      </div>

      {/* Overview Card */}
      <div className="mt-8 rounded-xl border border-surface-200 bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between pb-4 border-b border-surface-100">
          <h2 className="text-base font-semibold text-surface-900">Recent Investigation Activity</h2>
          <Link href="/investigations" className="text-xs font-semibold text-primary-700 hover:text-primary-800">
            View full queue →
          </Link>
        </div>
        <div className="mt-4 text-center py-12 text-surface-400 text-sm">
          Run reconciliation or load demo data in Phase 2 to populate live activity records.
        </div>
      </div>
    </div>
  );
}
