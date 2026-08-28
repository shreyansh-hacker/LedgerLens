"use client";

import React, { useState } from "react";
import { clsx } from "clsx";
import { ArrowDown, CreditCard, Receipt, Building2, Landmark, CheckCircle, AlertCircle, HelpCircle } from "lucide-react";

interface EvidenceTimelineProps {
  payment: {
    id: string;
    reference: string | null;
    amount: string;
    method?: string;
    gateway?: string;
    captured_at?: string;
  };
  fees?: Array<{ id: string; type: string; amount: string; rate?: string }>;
  taxes?: Array<{ id: string; type: string; amount: string }>;
  refunds?: Array<{ id: string; reference: string; amount: string }>;
  settlement?: {
    id: string;
    reference: string | null;
    gross_amount?: string;
    fee_amount?: string;
    tax_amount?: string;
    net_amount: string;
    settled_at?: string;
  } | null;
  bank?: {
    id: string;
    reference: string | null;
    utr_number: string | null;
    credit_amount: string;
    transaction_date?: string;
  } | null;
  className?: string;
}

export function EvidenceTimeline({
  payment,
  fees = [],
  taxes = [],
  refunds = [],
  settlement,
  bank,
  className,
}: EvidenceTimelineProps) {
  const [selectedNode, setSelectedNode] = useState<string | null>(null);

  const totalFees = fees.reduce((acc, f) => acc + parseFloat(f.amount || "0"), 0);
  const totalTaxes = taxes.reduce((acc, t) => acc + parseFloat(t.amount || "0"), 0);
  const totalRefunds = refunds.reduce((acc, r) => acc + parseFloat(r.amount || "0"), 0);

  const nodes = [
    {
      id: "payment",
      title: "1. Customer Payment",
      subtitle: payment.reference || payment.id,
      amount: `₹${parseFloat(payment.amount).toLocaleString("en-IN", { minimumFractionDigits: 2 })}`,
      icon: CreditCard,
      status: "VERIFIED",
      statusColor: "text-emerald-600 bg-emerald-50 border-emerald-200 dark:bg-emerald-950/40 dark:border-emerald-800",
      details: {
        "Payment ID": payment.id,
        "Payment Reference": payment.reference || "N/A",
        "Gross Amount": `₹${payment.amount}`,
        "Gateway": payment.gateway || "Razorpay",
        "Captured At": payment.captured_at ? new Date(payment.captured_at).toLocaleString() : "N/A",
      },
    },
    {
      id: "deductions",
      title: "2. Fees, Tax & Refunds",
      subtitle: `${fees.length} Fees, ${taxes.length} GST, ${refunds.length} Refunds`,
      amount: `-₹${(totalFees + totalTaxes + totalRefunds).toLocaleString("en-IN", { minimumFractionDigits: 2 })}`,
      icon: Receipt,
      status: (fees.length > 0 || taxes.length > 0) ? "VERIFIED" : "NO_DEDUCTIONS",
      statusColor: "text-slate-700 bg-slate-50 border-slate-200 dark:bg-slate-800/40 dark:border-slate-700",
      details: {
        "Gateway Fees": fees.map((f) => `${f.type}: ₹${f.amount} (${f.id})`).join(", ") || "None recorded",
        "GST Taxes (18%)": taxes.map((t) => `${t.type}: ₹${t.amount} (${t.id})`).join(", ") || "None recorded",
        "Refunds": refunds.map((r) => `${r.reference}: ₹${r.amount}`).join(", ") || "None recorded",
      },
    },
    {
      id: "settlement",
      title: "3. Gateway Settlement",
      subtitle: settlement ? (settlement.reference || settlement.id) : "Missing Settlement Batch",
      amount: settlement ? `₹${parseFloat(settlement.net_amount).toLocaleString("en-IN", { minimumFractionDigits: 2 })}` : "Unsettled",
      icon: Building2,
      status: settlement ? "VERIFIED" : "MISSING",
      statusColor: settlement
        ? "text-emerald-600 bg-emerald-50 border-emerald-200 dark:bg-emerald-950/40 dark:border-emerald-800"
        : "text-rose-600 bg-rose-50 border-rose-200 dark:bg-rose-950/40 dark:border-rose-800",
      details: settlement
        ? {
            "Settlement ID": settlement.id,
            "Settlement Reference": settlement.reference || "N/A",
            "Net Settlement": `₹${settlement.net_amount}`,
            "Fee Deducted": `₹${settlement.fee_amount || "0.00"}`,
            "Tax Deducted": `₹${settlement.tax_amount || "0.00"}`,
            "Settled At": settlement.settled_at ? new Date(settlement.settled_at).toLocaleString() : "N/A",
          }
        : {
            "Status": "Payment captured but gateway settlement record is absent from batch statements.",
          },
    },
    {
      id: "bank",
      title: "4. Bank Statement Credit",
      subtitle: bank ? (bank.utr_number || bank.reference || bank.id) : "Uncredited at Bank",
      amount: bank ? `₹${parseFloat(bank.credit_amount).toLocaleString("en-IN", { minimumFractionDigits: 2 })}` : "₹0.00 Credit",
      icon: Landmark,
      status: bank ? "VERIFIED" : "MISSING",
      statusColor: bank
        ? "text-emerald-600 bg-emerald-50 border-emerald-200 dark:bg-emerald-950/40 dark:border-emerald-800"
        : "text-rose-600 bg-rose-50 border-rose-200 dark:bg-rose-950/40 dark:border-rose-800",
      details: bank
        ? {
            "Bank Txn ID": bank.id,
            "UTR Number": bank.utr_number || "N/A",
            "Bank Reference": bank.reference || "N/A",
            "Credit Amount": `₹${bank.credit_amount}`,
            "Transaction Date": bank.transaction_date ? new Date(bank.transaction_date).toLocaleString() : "N/A",
          }
        : {
            "Status": "Settlement generated but corresponding credit is missing from nodal bank statement.",
          },
    },
  ];

  return (
    <div className={clsx("rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 p-5 shadow-sm", className)}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-200">
          Verifiable Evidence Chain
        </h3>
        <span className="text-xs text-slate-500 dark:text-slate-400">
          Click any step to inspect raw ledger IDs
        </span>
      </div>

      <div className="space-y-3">
        {nodes.map((node, index) => {
          const Icon = node.icon;
          const isSelected = selectedNode === node.id;
          const isMissing = node.status === "MISSING";

          return (
            <React.Fragment key={node.id}>
              <div
                onClick={() => setSelectedNode(isSelected ? null : node.id)}
                className={clsx(
                  "cursor-pointer rounded-lg border p-3.5 transition-all",
                  isSelected
                    ? "border-indigo-400 bg-indigo-50/20 dark:border-indigo-600 dark:bg-indigo-950/20 shadow-sm"
                    : "border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 hover:bg-slate-50/50 dark:hover:bg-slate-800/30"
                )}
              >
                <div className="flex items-center justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className={clsx("rounded-lg p-2 border flex items-center justify-center", node.statusColor)}>
                      <Icon className="h-4 w-4" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-slate-900 dark:text-slate-100">
                          {node.title}
                        </span>
                        {isMissing ? (
                          <span className="rounded bg-rose-100 px-1.5 py-0.2 text-[10px] font-semibold text-rose-700 dark:bg-rose-950/60 dark:text-rose-300">
                            Missing
                          </span>
                        ) : (
                          <span className="rounded bg-emerald-100 px-1.5 py-0.2 text-[10px] font-semibold text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300">
                            Verified
                          </span>
                        )}
                      </div>
                      <p className="text-[11px] font-mono text-slate-500 dark:text-slate-400 truncate max-w-xs md:max-w-md">
                        {node.subtitle}
                      </p>
                    </div>
                  </div>

                  <div className="text-right">
                    <span className={clsx("text-sm font-bold font-mono", isMissing ? "text-rose-600 dark:text-rose-400" : "text-slate-900 dark:text-slate-100")}>
                      {node.amount}
                    </span>
                  </div>
                </div>

                {isSelected && (
                  <div className="mt-3.5 pt-3 border-t border-slate-200 dark:border-slate-800 grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
                    {Object.entries(node.details).map(([k, v]) => (
                      <div key={k} className="flex flex-col bg-slate-50 dark:bg-slate-800/60 p-2 rounded">
                        <span className="text-[10px] font-medium uppercase text-slate-400">{k}</span>
                        <span className="font-mono text-slate-800 dark:text-slate-200 text-xs break-all">{v}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {index < nodes.length - 1 && (
                <div className="flex justify-center my-0.5">
                  <ArrowDown className="h-3.5 w-3.5 text-slate-300 dark:text-slate-600" />
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}
