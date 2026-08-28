"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  getReconciliationResults,
  getReconciliationSummary,
  ReconciliationItem,
  ReconciliationSummary,
} from "@/lib/api";
import { StatusBadge } from "@/components/StatusBadge";
import {
  Search,
  Filter,
  RefreshCw,
  ArrowUpRight,
  Database,
  ArrowRight,
  SlidersHorizontal,
} from "lucide-react";
import { clsx } from "clsx";

export default function InvestigationsPage() {
  const [items, setItems] = useState<ReconciliationItem[]>([]);
  const [summary, setSummary] = useState<ReconciliationSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [statusFilter, setStatusFilter] = useState<string>("ALL");
  const [classificationFilter, setClassificationFilter] = useState<string>("ALL");
  const [hasDiscrepancyOnly, setHasDiscrepancyOnly] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState<string>("");

  async function loadItems() {
    setLoading(true);
    setError(null);
    try {
      const [results, sum] = await Promise.all([
        getReconciliationResults({
          status: statusFilter === "ALL" ? undefined : statusFilter,
          classification: classificationFilter === "ALL" ? undefined : classificationFilter,
          has_discrepancy: hasDiscrepancyOnly ? true : undefined,
          search: searchQuery.trim() || undefined,
          limit: 100,
        }),
        getReconciliationSummary().catch(() => null),
      ]);
      setItems(results);
      setSummary(sum);
    } catch (err: any) {
      setError(err.message || "Failed to load investigations");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadItems();
  }, [statusFilter, classificationFilter, hasDiscrepancyOnly]);

  const classifications = [
    "ALL",
    "FEE_MISMATCH",
    "TAX_MISMATCH",
    "MISSING_BANK_TRANSACTION",
    "MISSING_SETTLEMENT",
    "DUPLICATE_SETTLEMENT",
    "REFERENCE_ID_DISCREPANCY",
    "AMOUNT_MISMATCH",
    "SETTLEMENT_DELAY",
    "UNEXPLAINED_EXCEPTION",
  ];

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8 w-full">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 pb-6 border-b border-slate-200 dark:border-slate-800">
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            Audit & Exception Queue
          </span>
          <h1 className="text-2xl font-extrabold tracking-tight text-slate-900 dark:text-slate-50 sm:text-3xl">
            Financial Investigations
          </h1>
          <p className="mt-1 text-xs text-slate-500">
            Inspect observable evidence trails, root causes, and multi-factor confidence scores.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={loadItems}
            disabled={loading}
            className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-200 dark:hover:bg-slate-800 transition-colors shadow-xs"
          >
            <RefreshCw className={clsx("h-3.5 w-3.5", loading && "animate-spin")} />
            <span>Refresh Queue</span>
          </button>
        </div>
      </div>

      {/* Filter Tabs & Search Bar */}
      <div className="mt-6 space-y-4">
        {/* Status Pills */}
        <div className="flex flex-wrap items-center gap-2">
          {[
            { id: "ALL", label: "All Records" },
            { id: "EXCEPTION", label: "Exceptions" },
            { id: "REVIEW", label: "Needs Review" },
            { id: "MISSING_SETTLEMENT", label: "Missing Settlement" },
            { id: "MISSING_BANK_TRANSACTION", label: "Missing Bank Credit" },
            { id: "DUPLICATE", label: "Duplicates" },
            { id: "MATCHED", label: "Matched" },
          ].map((tab) => (
            <button
              key={tab.id}
              type="button"
              onClick={() => setStatusFilter(tab.id)}
              className={clsx(
                "rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors",
                statusFilter === tab.id
                  ? "bg-indigo-600 text-white shadow-xs"
                  : "bg-white text-slate-600 hover:bg-slate-100 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700"
              )}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Search and Dropdown Controls */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-white dark:bg-slate-900/80 p-3 rounded-xl border border-slate-200 dark:border-slate-800">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              loadItems();
            }}
            className="flex-1 w-full relative"
          >
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search by Payment ID (pay_*), Reference, or UTR..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-1.5 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 focus:outline-none focus:border-indigo-500 dark:text-slate-100"
            />
          </form>

          <div className="flex items-center gap-3 w-full sm:w-auto">
            {/* Classification selector */}
            <select
              value={classificationFilter}
              onChange={(e) => setClassificationFilter(e.target.value)}
              className="text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-3 py-2 text-slate-700 dark:text-slate-200 focus:outline-none"
            >
              {classifications.map((c) => (
                <option key={c} value={c}>
                  {c === "ALL" ? "All Classifications" : c.replace(/_/g, " ")}
                </option>
              ))}
            </select>

            {/* Discrepancy toggle */}
            <label className="flex items-center gap-1.5 text-xs text-slate-600 dark:text-slate-300 cursor-pointer whitespace-nowrap">
              <input
                type="checkbox"
                checked={hasDiscrepancyOnly}
                onChange={(e) => setHasDiscrepancyOnly(e.target.checked)}
                className="rounded text-indigo-600 focus:ring-0"
              />
              <span>Discrepancies Only</span>
            </label>
          </div>
        </div>
      </div>

      {/* Table */}
      {loading ? (
        <div className="mt-6 rounded-xl border border-slate-200 bg-white p-12 text-center text-xs text-slate-500 dark:border-slate-800 dark:bg-slate-900">
          <RefreshCw className="mx-auto h-6 w-6 animate-spin text-indigo-500 mb-2" />
          <span>Loading investigation queue...</span>
        </div>
      ) : items.length === 0 ? (
        <div className="mt-6 rounded-xl border border-dashed border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900/40 p-12 text-center">
          <p className="text-sm font-bold text-slate-700 dark:text-slate-300">
            No matching transactions found.
          </p>
          <p className="text-xs text-slate-500 mt-1">
            Try adjusting your search criteria or load the demo dataset from the Reconciliation Center.
          </p>
        </div>
      ) : (
        <div className="mt-6 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/80 shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 dark:bg-slate-800/60 text-slate-500 border-b border-slate-200 dark:border-slate-800 font-semibold">
                <tr>
                  <th className="py-3 px-4">Transaction / ID</th>
                  <th className="py-3 px-4">Expected Net</th>
                  <th className="py-3 px-4">Actual Bank Credit</th>
                  <th className="py-3 px-4">Discrepancy</th>
                  <th className="py-3 px-4">Classification</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800/80 font-mono">
                {items.map((item) => {
                  const disc = parseFloat(item.discrepancy_amount || "0");
                  const hasDisc = Math.abs(disc) > 0.001;

                  return (
                    <tr
                      key={item.id}
                      className="hover:bg-slate-50/80 dark:hover:bg-slate-800/40 transition-colors"
                    >
                      <td className="py-3 px-4 font-medium text-slate-900 dark:text-slate-100">
                        <div>{item.payment_reference || item.payment_id}</div>
                        <div className="text-[10px] font-sans text-slate-400">{item.id}</div>
                      </td>
                      <td className="py-3 px-4">
                        ₹{parseFloat(item.expected_settlement_amount || "0").toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                      </td>
                      <td className="py-3 px-4">
                        {item.actual_bank_amount ? (
                          `₹${parseFloat(item.actual_bank_amount).toLocaleString("en-IN", { minimumFractionDigits: 2 })}`
                        ) : (
                          <span className="text-rose-500 font-sans italic">Missing Credit</span>
                        )}
                      </td>
                      <td className={clsx("py-3 px-4 font-bold", hasDisc ? "text-rose-600 dark:text-rose-400" : "text-slate-500")}>
                        {hasDisc ? `₹${Math.abs(disc).toLocaleString("en-IN", { minimumFractionDigits: 2 })}` : "₹0.00"}
                      </td>
                      <td className="py-3 px-4 font-sans">
                        <span className="rounded bg-slate-100 dark:bg-slate-800 px-2 py-0.5 text-[11px] font-mono text-slate-700 dark:text-slate-300">
                          {item.classification}
                        </span>
                      </td>
                      <td className="py-3 px-4 font-sans">
                        <StatusBadge status={item.status} type="reconciliation" />
                      </td>
                      <td className="py-3 px-4 text-right font-sans">
                        <Link
                          href={`/investigations/${item.id}`}
                          className="inline-flex items-center gap-1 rounded bg-indigo-50 px-2.5 py-1 text-xs font-semibold text-indigo-700 hover:bg-indigo-100 dark:bg-indigo-950/60 dark:text-indigo-300 transition-colors"
                        >
                          <span>Investigate</span>
                          <ArrowUpRight className="h-3 w-3" />
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          <div className="p-3 bg-slate-50 dark:bg-slate-800/40 border-t border-slate-200 dark:border-slate-800 text-[11px] text-slate-500 flex justify-between items-center">
            <span>Showing {items.length} records</span>
            <span>All calculations use strict Decimal precision</span>
          </div>
        </div>
      )}
    </div>
  );
}
