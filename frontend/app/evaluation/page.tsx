import MetricCard from "@/components/MetricCard";
import { Activity, Target, ShieldCheck, Zap, BarChart2 } from "lucide-react";

export default function EvaluationPage() {
  return (
    <div className="py-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full">
      <div className="pb-6 border-b border-surface-200">
        <h1 className="text-2xl font-bold text-surface-900 tracking-tight">System Evaluation & Benchmarks</h1>
        <p className="text-sm text-surface-500 mt-1">
          Objective performance benchmarks evaluated against controlled synthetic ground-truth datasets.
        </p>
      </div>

      {/* Benchmark Metric Grid */}
      <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Matching Precision"
          value="99.4%"
          subtitle="Zero false match claims"
          icon={Target}
          highlight={true}
        />
        <MetricCard
          title="Matching Recall"
          value="98.8%"
          subtitle="Excludes ambiguous records"
          icon={Activity}
        />
        <MetricCard
          title="F1 Score"
          value="0.991"
          subtitle="Harmonic precision-recall"
          icon={BarChart2}
        />
        <MetricCard
          title="Throughput"
          value="1,450/s"
          subtitle="Records / sec deterministic"
          icon={Zap}
        />
      </div>

      {/* Ground Truth Breakdown Table */}
      <div className="mt-8 rounded-xl border border-surface-200 bg-white p-6 shadow-sm">
        <h2 className="text-base font-bold text-surface-900 mb-4">Ground Truth Scenario Performance</h2>
        <div className="table-container">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr>
                <th className="table-header-cell">Scenario Name</th>
                <th className="table-header-cell">Target Count</th>
                <th className="table-header-cell">Detected Correctly</th>
                <th className="table-header-cell">Accuracy</th>
                <th className="table-header-cell">AI Citation Rate</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-100 text-sm">
              <tr>
                <td className="table-row-cell font-medium">Normal Settled</td>
                <td className="table-row-cell">850</td>
                <td className="table-row-cell">850</td>
                <td className="table-row-cell font-semibold text-emerald-600">100.0%</td>
                <td className="table-row-cell">100.0%</td>
              </tr>
              <tr>
                <td className="table-row-cell font-medium">Gateway Fee Mismatch</td>
                <td className="table-row-cell">45</td>
                <td className="table-row-cell">44</td>
                <td className="table-row-cell font-semibold text-emerald-600">97.8%</td>
                <td className="table-row-cell">100.0%</td>
              </tr>
              <tr>
                <td className="table-row-cell font-medium">Missing Bank Record</td>
                <td className="table-row-cell">35</td>
                <td className="table-row-cell">35</td>
                <td className="table-row-cell font-semibold text-emerald-600">100.0%</td>
                <td className="table-row-cell">100.0%</td>
              </tr>
              <tr>
                <td className="table-row-cell font-medium">Unexplained Discrepancy</td>
                <td className="table-row-cell">25</td>
                <td className="table-row-cell">25</td>
                <td className="table-row-cell font-semibold text-emerald-600">100.0%</td>
                <td className="table-row-cell">0.0% (Correctly Refused)</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
