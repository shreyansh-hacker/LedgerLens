import type { Metadata } from "next";
import "./globals.css";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { BackendHealthBanner } from "@/components/BackendHealthBanner";
import { CopilotDrawer } from "@/components/CopilotDrawer";

export const metadata: Metadata = {
  title: "LedgerLens — AI Financial Reconciliation & Investigation Platform",
  description:
    "Every rupee gets an evidence trail. Automated multi-signal financial reconciliation, deterministic calculations, Isolation Forest anomaly detection, and Groq-powered AI investigation.",
  icons: {
    icon: "/favicon.ico",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="flex flex-col min-h-screen bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-50 antialiased font-sans">
        <BackendHealthBanner />
        <Navbar />
        <main className="flex-1 flex flex-col">{children}</main>
        <CopilotDrawer />
        <Footer />
      </body>
    </html>
  );
}
