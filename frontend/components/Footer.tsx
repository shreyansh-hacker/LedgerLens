import Link from "next/link";
import { ShieldCheck, ArrowUpRight } from "lucide-react";

export default function Footer() {
  return (
    <footer className="mt-auto border-t border-surface-200 bg-white py-8">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="flex h-6 w-6 items-center justify-center rounded bg-primary-700 text-white">
              <ShieldCheck className="h-3.5 w-3.5" />
            </div>
            <span className="text-sm font-semibold text-surface-900">LedgerLens</span>
            <span className="text-sm text-surface-400">|</span>
            <span className="text-xs text-surface-500">Every rupee gets an evidence trail.</span>
          </div>

          <div className="flex items-center gap-6 text-xs text-surface-500 font-medium">
            <Link href="/help" className="hover:text-surface-900 transition-colors">
              Documentation & FAQ
            </Link>
            <Link href="/evaluation" className="hover:text-surface-900 transition-colors">
              Benchmarks
            </Link>
            <a
              href="https://github.com/shreyansh-hacker/LedgerLens"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 hover:text-surface-900 transition-colors"
            >
              GitHub <ArrowUpRight className="h-3 w-3" />
            </a>
          </div>

          <div className="text-xs text-surface-400">
            © {new Date().getFullYear()} LedgerLens. Built for modern merchant finance teams.
          </div>
        </div>
      </div>
    </footer>
  );
}
