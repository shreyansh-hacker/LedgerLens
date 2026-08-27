"use client";

import { useEffect, useState } from "react";
import { checkBackendHealth } from "@/lib/api";
import { CheckCircle2, Loader2, RefreshCw, AlertCircle } from "lucide-react";

export default function BackendHealthBanner() {
  const [status, setStatus] = useState<"checking" | "waking" | "ready" | "error">("checking");
  const [dbConnected, setDbConnected] = useState(false);
  const [retryCount, setRetryCount] = useState(0);

  useEffect(() => {
    let isMounted = true;
    let timer: NodeJS.Timeout;

    async function pollHealth() {
      try {
        const data = await checkBackendHealth();
        if (isMounted) {
          setDbConnected(data.database_connected);
          setStatus("ready");
        }
      } catch (err) {
        if (isMounted) {
          setStatus("waking");
          // Retry every 4 seconds if backend is spinning up
          timer = setTimeout(() => {
            setRetryCount((prev) => prev + 1);
          }, 4000);
        }
      }
    }

    pollHealth();

    return () => {
      isMounted = false;
      if (timer) clearTimeout(timer);
    };
  }, [retryCount]);

  if (status === "ready") {
    return null; // Silent when everything is normal and running smoothly
  }

  return (
    <div className="w-full bg-surface-900 text-white px-4 py-3 border-b border-surface-800 shadow-md">
      <div className="mx-auto max-w-7xl flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2.5">
          <Loader2 className="h-4 w-4 animate-spin text-primary-400" />
          <span className="font-semibold text-surface-100">
            Waking up the LedgerLens investigation engine...
          </span>
          <span className="text-surface-400 hidden md:inline">
            (Cold-start tolerant architecture)
          </span>
        </div>

        <div className="flex items-center gap-4 text-[11px] text-surface-300">
          <span className="flex items-center gap-1 text-emerald-400">
            <CheckCircle2 className="h-3.5 w-3.5" /> Frontend connected
          </span>
          <span className="flex items-center gap-1">
            <span className="h-2 w-2 rounded-full bg-amber-400 animate-ping"></span> Backend starting
          </span>
          <span className="flex items-center gap-1 text-surface-400">
            ● Database connecting
          </span>
        </div>

        <button
          onClick={() => setRetryCount((c) => c + 1)}
          className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-surface-800 hover:bg-surface-700 text-surface-200 text-[11px] font-medium transition-colors"
        >
          <RefreshCw className="h-3 w-3" /> Retry Now
        </button>
      </div>
    </div>
  );
}
