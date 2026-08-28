"use client";

import React, { useState } from "react";
import { MessageSquare, X, Send, Sparkles, Bot, ArrowRight, ShieldCheck, CornerDownLeft } from "lucide-react";
import { queryFinanceAssistant, AssistantResponse } from "@/lib/api";
import { clsx } from "clsx";

export function CopilotDrawer() {
  const [isOpen, setIsOpen] = useState(false);
  const [queryText, setQueryText] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<
    Array<{ sender: "user" | "assistant"; text: string; data?: any; sources?: string[] }>
  >([
    {
      sender: "assistant",
      text: "Hello! I am your **LedgerLens Finance Copilot**. Ask me anything about your reconciliation summary, delayed settlements, or specific transaction discrepancies.",
      sources: ["LedgerLens Database"],
    },
  ]);

  const quickPrompts = [
    "How much money is currently unresolved?",
    "Which settlements are delayed?",
    "Show me the largest discrepancies.",
    "What is our overall reconciliation match rate?",
  ];

  async function handleSend(customQuery?: string) {
    const q = (customQuery || queryText).trim();
    if (!q || loading) return;

    const userMsg = { sender: "user" as const, text: q };
    setMessages((prev) => [...prev, userMsg]);
    setQueryText("");
    setLoading(true);

    try {
      const res: AssistantResponse = await queryFinanceAssistant(q);
      setMessages((prev) => [
        ...prev,
        {
          sender: "assistant",
          text: res.answer,
          data: res.retrieved_data_summary,
          sources: res.evidence_sources,
        },
      ]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          sender: "assistant",
          text: `⚠️ Error fetching assistant response: ${err.message || "Failed to query backend"}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      {/* Floating Trigger Button */}
      <button
        type="button"
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 z-40 flex items-center gap-2.5 rounded-full bg-slate-900 px-4 py-3 text-sm font-semibold text-white shadow-xl hover:bg-slate-800 dark:bg-indigo-600 dark:hover:bg-indigo-500 transition-all hover:scale-105 border border-slate-700/50"
      >
        <Sparkles className="h-4 w-4 text-indigo-400 dark:text-indigo-200" />
        <span>Ask Copilot</span>
      </button>

      {/* Drawer Overlay */}
      {isOpen && (
        <div className="fixed inset-0 z-50 flex justify-end bg-slate-950/40 backdrop-blur-sm transition-opacity">
          <div className="flex h-full w-full max-w-lg flex-col bg-white shadow-2xl dark:bg-slate-900 border-l border-slate-200 dark:border-slate-800 animate-in slide-in-from-right duration-200">
            {/* Header */}
            <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 p-4">
              <div className="flex items-center gap-2.5">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600 dark:bg-indigo-950 dark:text-indigo-400">
                  <Bot className="h-5 w-5" />
                </div>
                <div>
                  <h2 className="text-sm font-bold text-slate-900 dark:text-slate-100">
                    Finance Copilot
                  </h2>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400">
                    Evidence-Grounded Query Assistant
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setIsOpen(false)}
                className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-slate-800 dark:hover:text-slate-200"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Chat History */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs">
              {messages.map((m, idx) => (
                <div
                  key={idx}
                  className={clsx(
                    "flex flex-col max-w-[88%]",
                    m.sender === "user" ? "ml-auto items-end" : "mr-auto items-start"
                  )}
                >
                  <div
                    className={clsx(
                      "rounded-xl p-3.5 leading-relaxed",
                      m.sender === "user"
                        ? "bg-indigo-600 text-white rounded-br-none"
                        : "bg-slate-100 dark:bg-slate-800/80 text-slate-800 dark:text-slate-200 rounded-bl-none border border-slate-200 dark:border-slate-700"
                    )}
                  >
                    <div className="prose prose-xs dark:prose-invert max-w-none whitespace-pre-wrap">
                      {m.text}
                    </div>
                  </div>

                  {m.sources && m.sources.length > 0 && (
                    <div className="mt-1 flex flex-wrap gap-1 items-center">
                      <span className="text-[10px] text-slate-400">Sources:</span>
                      {m.sources.map((s, si) => (
                        <span
                          key={si}
                          className="rounded bg-slate-200/60 dark:bg-slate-800 px-1.5 py-0.2 text-[10px] font-mono text-slate-600 dark:text-slate-300"
                        >
                          {s}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}

              {loading && (
                <div className="flex items-center gap-2 text-slate-400 text-xs py-2">
                  <div className="h-2 w-2 rounded-full bg-indigo-500 animate-pulse" />
                  <div className="h-2 w-2 rounded-full bg-indigo-500 animate-pulse delay-75" />
                  <div className="h-2 w-2 rounded-full bg-indigo-500 animate-pulse delay-150" />
                  <span className="text-[11px]">Querying database tools & reasoning...</span>
                </div>
              )}
            </div>

            {/* Quick Prompts */}
            <div className="px-4 py-2 border-t border-slate-100 dark:border-slate-800/60 flex flex-wrap gap-1.5">
              {quickPrompts.map((qp, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => handleSend(qp)}
                  disabled={loading}
                  className="rounded-full border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-2.5 py-1 text-[10px] font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
                >
                  {qp}
                </button>
              ))}
            </div>

            {/* Input Box */}
            <div className="p-4 border-t border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50">
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSend();
                }}
                className="flex items-center gap-2"
              >
                <input
                  type="text"
                  value={queryText}
                  onChange={(e) => setQueryText(e.target.value)}
                  placeholder="Ask a question about transactions or summaries..."
                  disabled={loading}
                  className="flex-1 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 px-3.5 py-2.5 text-xs text-slate-900 dark:text-slate-100 focus:border-indigo-500 focus:outline-none dark:focus:border-indigo-400"
                />
                <button
                  type="submit"
                  disabled={loading || !queryText.trim()}
                  className="rounded-lg bg-indigo-600 p-2.5 text-white hover:bg-indigo-500 disabled:opacity-50 transition-all flex items-center justify-center"
                >
                  <Send className="h-4 w-4" />
                </button>
              </form>
              <p className="mt-2 text-[10px] text-center text-slate-400">
                Safe tool-based execution. Zero arbitrary SQL injection.
              </p>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
