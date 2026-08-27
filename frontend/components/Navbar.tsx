"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  BarChart3, 
  SearchCheck, 
  FileSpreadsheet, 
  Activity, 
  HelpCircle, 
  Info, 
  ShieldCheck,
  Zap
} from "lucide-react";
import { cn } from "@/lib/utils";

const navigationItems = [
  { name: "Dashboard", href: "/dashboard", icon: BarChart3 },
  { name: "Investigations", href: "/investigations", icon: SearchCheck },
  { name: "Reconciliation", href: "/reconciliation", icon: FileSpreadsheet },
  { name: "Evaluation", href: "/evaluation", icon: Activity },
  { name: "Help", href: "/help", icon: HelpCircle },
  { name: "About", href: "/about", icon: Info },
];

export default function Navbar() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-40 w-full border-b border-surface-200 bg-white/95 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-8">
          <Link href="/" className="flex items-center gap-2.5 transition-opacity hover:opacity-90">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary-700 text-white shadow-sm">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <div className="flex flex-col">
              <span className="text-base font-bold tracking-tight text-surface-900 leading-none">
                Ledger<span className="text-primary-700">Lens</span>
              </span>
              <span className="text-[10px] font-medium text-surface-500 uppercase tracking-wider mt-0.5">
                Financial Investigator
              </span>
            </div>
          </Link>

          <nav className="hidden md:flex items-center gap-1">
            {navigationItems.map((item) => {
              const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
              const Icon = item.icon;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-surface-100 text-primary-800 font-semibold"
                      : "text-surface-600 hover:bg-surface-50 hover:text-surface-900"
                  )}
                >
                  <Icon className={cn("h-4 w-4", isActive ? "text-primary-700" : "text-surface-400")} />
                  {item.name}
                </Link>
              );
            })}
          </nav>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href="/reconciliation"
            className="hidden sm:inline-flex items-center gap-1.5 rounded-lg border border-primary-200 bg-primary-50 px-3 py-1.5 text-xs font-semibold text-primary-800 hover:bg-primary-100 transition-colors shadow-sm"
          >
            <Zap className="h-3.5 w-3.5 text-primary-700" />
            Demo Mode
          </Link>
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-surface-100 border border-surface-200 text-[11px] font-medium text-surface-600">
            <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>API Online</span>
          </div>
        </div>
      </div>
    </header>
  );
}
