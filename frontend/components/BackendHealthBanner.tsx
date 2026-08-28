"use client";

import React, { useEffect, useState } from "react";
import { checkBackendHealth } from "@/lib/api";
import { AlertCircle, CheckCircle2, RefreshCw, Server } from "lucide-react";

export function BackendHealthBanner() {
  const [status, setStatus] = useState<"checking" | "healthy" | "waking" | "error">("checking");
  const [retryCount, setRetryCount] = useState(0);

  useEffect(() => {
    let isMounted = true;
    let timer: NodeJS.Timeout;

    async function verifyHealth() {
      try {
        await checkBackendHealth();
        if (isMounted) {
          setStatus("healthy");
        }
      } catch (err) {
        if (isMounted) {
          setStatus("waking");
          // Retry with backoff
          timer = setTimeout(() => {
            setRetryCount((prev) => prev + 1);
          }, 4000);
        }
      }
    }

    verifyHealth();

    return () => {
      isMounted = false;
      if (timer) clearTimeout(timer);
    };
  }, [retryCount]);

  if (status === "healthy" || status === "checking") {
    return null;
  }

  return (
    <div className="bg-amber-500/10 border-b border-amber-500/20 px-4 py-2.5 text-xs text-amber-800 dark:text-amber-300">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4">
        <div className="flex items-center gap-2.5">
          <div className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-amber-500" />
          </div>
          <div>
            <span className="font-semibold">LedgerLens is connecting to backend services:</span>{" "}
            <span>Initializing database & intelligence pipeline...</span>
          </div>
        </div>

        <button
          type="button"
          onClick={() => setRetryCount((prev) => prev + 1)}
          className="flex items-center gap-1.5 rounded bg-amber-500/20 px-2.5 py-1 text-[11px] font-semibold text-amber-900 hover:bg-amber-500/30 dark:text-amber-200 transition-colors"
        >
          <RefreshCw className="h-3 w-3 animate-spin" />
          <span>Retry Now</span>
        </button>
      </div>
    </div>
  );
}
