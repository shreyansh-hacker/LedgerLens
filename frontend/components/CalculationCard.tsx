import React from "react";
import { clsx } from "clsx";
import { Calculator, CheckCircle2, AlertCircle } from "lucide-react";

interface CalculationCardProps {
  grossAmount: string;
  fees: Array<{ name: string; amount: string; id?: string }>;
  taxes: Array<{ name: string; amount: string; id?: string }>;
  refunds?: Array<{ name: string; amount: string }>;
  expectedSettlement: string;
  actualSettlement?: string | null;
  actualBankAmount?: string | null;
  discrepancyAmount: string;
  className?: string;
}

export function CalculationCard({
  grossAmount,
  fees = [],
  taxes = [],
  refunds = [],
  expectedSettlement,
  actualSettlement,
  actualBankAmount,
  discrepancyAmount,
  className,
}: CalculationCardProps) {
  const numGross = parseFloat(grossAmount || "0");
  const numExpected = parseFloat(expectedSettlement || "0");
  const numActualBank = actualBankAmount ? parseFloat(actualBankAmount) : null;
  const numDiscrepancy = parseFloat(discrepancyAmount || "0");
  const hasDiscrepancy = Math.abs(numDiscrepancy) > 0.001;

  const totalFee = fees.reduce((acc, f) => acc + parseFloat(f.amount || "0"), 0);
  const totalTax = taxes.reduce((acc, t) => acc + parseFloat(t.amount || "0"), 0);
  const totalRefund = refunds.reduce((acc, r) => acc + parseFloat(r.amount || "0"), 0);

  return (
    <div className={clsx("rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 p-5 shadow-sm", className)}>
      <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-100 dark:border-slate-800">
        <div className="flex items-center gap-2">
          <div className="rounded-lg p-1.5 bg-indigo-50 dark:bg-indigo-950/50 text-indigo-600 dark:text-indigo-400">
            <Calculator className="h-4 w-4" />
          </div>
          <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-800 dark:text-slate-200">
            Deterministic Settlement Math
          </h3>
        </div>
        <span className="text-[11px] font-mono font-medium text-slate-400">
          Strict Decimal / NUMERIC
        </span>
      </div>

      <div className="space-y-2.5 text-xs font-mono">
        {/* Gross */}
        <div className="flex justify-between items-center py-1 text-slate-800 dark:text-slate-200">
          <span className="font-sans font-medium text-slate-600 dark:text-slate-400">Customer Payment (Gross)</span>
          <span className="font-bold text-sm">₹{numGross.toLocaleString("en-IN", { minimumFractionDigits: 2 })}</span>
        </div>

        {/* Fees */}
        {fees.map((f, i) => (
          <div key={i} className="flex justify-between items-center text-slate-500 dark:text-slate-400 pl-3">
            <span className="font-sans">− {f.name}</span>
            <span>₹{parseFloat(f.amount).toLocaleString("en-IN", { minimumFractionDigits: 2 })}</span>
          </div>
        ))}
        {fees.length === 0 && (
          <div className="flex justify-between items-center text-slate-400 pl-3">
            <span className="font-sans">− Gateway Fee</span>
            <span>₹0.00</span>
          </div>
        )}

        {/* Taxes */}
        {taxes.map((t, i) => (
          <div key={i} className="flex justify-between items-center text-slate-500 dark:text-slate-400 pl-3">
            <span className="font-sans">− {t.name} (GST 18%)</span>
            <span>₹{parseFloat(t.amount).toLocaleString("en-IN", { minimumFractionDigits: 2 })}</span>
          </div>
        ))}
        {taxes.length === 0 && (
          <div className="flex justify-between items-center text-slate-400 pl-3">
            <span className="font-sans">− Tax (GST)</span>
            <span>₹0.00</span>
          </div>
        )}

        {/* Refunds */}
        {refunds.map((r, i) => (
          <div key={i} className="flex justify-between items-center text-rose-500 dark:text-rose-400 pl-3">
            <span className="font-sans">− Refund ({r.name})</span>
            <span>₹{parseFloat(r.amount).toLocaleString("en-IN", { minimumFractionDigits: 2 })}</span>
          </div>
        ))}

        {/* Divider */}
        <div className="border-t border-slate-200 dark:border-slate-700 my-2" />

        {/* Expected Net */}
        <div className="flex justify-between items-center py-1 text-slate-900 dark:text-slate-100 font-bold">
          <span className="font-sans">Expected Net Settlement</span>
          <span className="text-sm">₹{numExpected.toLocaleString("en-IN", { minimumFractionDigits: 2 })}</span>
        </div>

        {/* Actual Bank Credit */}
        <div className="flex justify-between items-center py-1 text-slate-700 dark:text-slate-300">
          <span className="font-sans text-slate-600 dark:text-slate-400">Actual Bank Credit</span>
          <span className="text-sm font-semibold">
            {numActualBank !== null ? `₹${numActualBank.toLocaleString("en-IN", { minimumFractionDigits: 2 })}` : "None (Missing Credit)"}
          </span>
        </div>

        {/* Net Discrepancy Alert */}
        <div
          className={clsx(
            "mt-3 p-3 rounded-lg border flex items-center justify-between font-sans",
            hasDiscrepancy
              ? "bg-rose-50 border-rose-200 text-rose-800 dark:bg-rose-950/30 dark:border-rose-900 dark:text-rose-200"
              : "bg-emerald-50 border-emerald-200 text-emerald-800 dark:bg-emerald-950/30 dark:border-emerald-900 dark:text-emerald-200"
          )}
        >
          <div className="flex items-center gap-2">
            {hasDiscrepancy ? <AlertCircle className="h-4 w-4 text-rose-600 flex-shrink-0" /> : <CheckCircle2 className="h-4 w-4 text-emerald-600 flex-shrink-0" />}
            <span className="text-xs font-semibold">
              {hasDiscrepancy ? "Financial Discrepancy" : "Balanced (Zero Discrepancy)"}
            </span>
          </div>
          <span className="font-mono font-bold text-sm">
            {hasDiscrepancy ? `₹${Math.abs(numDiscrepancy).toLocaleString("en-IN", { minimumFractionDigits: 2 })}` : "₹0.00"}
          </span>
        </div>
      </div>
    </div>
  );
}
