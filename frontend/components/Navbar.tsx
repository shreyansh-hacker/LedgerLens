"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { clsx } from "clsx";
import {
  Layers,
  LayoutDashboard,
  FileSpreadsheet,
  Search,
  BarChart3,
  HelpCircle,
  Info,
  Menu,
  X,
  Database,
  Sparkles,
} from "lucide-react";

export function Navbar() {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navLinks = [
    { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { name: "Reconciliation", href: "/reconciliation", icon: FileSpreadsheet },
    { name: "Investigations", href: "/investigations", icon: Search },
    { name: "Evaluation", href: "/evaluation", icon: BarChart3 },
    { name: "Help", href: "/help", icon: HelpCircle },
    { name: "About", href: "/about", icon: Info },
  ];

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-200/80 bg-white/90 backdrop-blur-md dark:border-slate-800/80 dark:bg-slate-900/90">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Logo */}
        <div className="flex items-center gap-6">
          <Link href="/" className="flex items-center gap-2.5 transition-opacity hover:opacity-90">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-slate-900 text-white dark:bg-indigo-600 shadow-sm">
              <Layers className="h-5 w-5" />
            </div>
            <div className="flex flex-col">
              <span className="text-base font-bold tracking-tight text-slate-900 dark:text-slate-50">
                Ledger<span className="text-indigo-600 dark:text-indigo-400">Lens</span>
              </span>
              <span className="text-[10px] font-medium tracking-wide text-slate-400">
                Financial Evidence Trail
              </span>
            </div>
          </Link>

          {/* Desktop Nav */}
          <nav className="hidden md:flex items-center gap-1">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const isActive = pathname === link.href || (link.href !== "/" && pathname.startsWith(link.href));
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={clsx(
                    "flex items-center gap-1.5 rounded-lg px-3 py-2 text-xs font-semibold transition-colors",
                    isActive
                      ? "bg-slate-100 text-slate-900 dark:bg-slate-800 dark:text-slate-50"
                      : "text-slate-600 hover:bg-slate-50 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800/50 dark:hover:text-slate-200"
                  )}
                >
                  <Icon className="h-3.5 w-3.5" />
                  <span>{link.name}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Right side status / CTA */}
        <div className="hidden md:flex items-center gap-3">
          {/* Demo Mode Badge */}
          <Link
            href="/reconciliation"
            className="flex items-center gap-1.5 rounded-full border border-indigo-200/80 bg-indigo-50/80 px-2.5 py-1 text-[11px] font-medium text-indigo-700 hover:bg-indigo-100/80 dark:border-indigo-800/60 dark:bg-indigo-950/40 dark:text-indigo-300 transition-colors shadow-xs"
          >
            <Database className="h-3 w-3 text-indigo-500" />
            <span>Demo Mode</span>
          </Link>
        </div>

        {/* Mobile menu button */}
        <div className="flex md:hidden">
          <button
            type="button"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="rounded-lg p-2 text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
          >
            {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Nav Dropdown */}
      {mobileMenuOpen && (
        <div className="md:hidden border-b border-slate-200 bg-white px-4 pt-2 pb-4 dark:border-slate-800 dark:bg-slate-900 shadow-lg">
          <div className="space-y-1">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const isActive = pathname === link.href;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className={clsx(
                    "flex items-center gap-2.5 rounded-lg px-3 py-2.5 text-sm font-medium",
                    isActive
                      ? "bg-slate-100 text-slate-900 dark:bg-slate-800 dark:text-slate-50"
                      : "text-slate-600 hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800"
                  )}
                >
                  <Icon className="h-4 w-4" />
                  <span>{link.name}</span>
                </Link>
              );
            })}
          </div>
        </div>
      )}
    </header>
  );
}
