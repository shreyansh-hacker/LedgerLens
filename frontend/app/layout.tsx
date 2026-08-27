import type { Metadata } from "next";
import "./globals.css";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import BackendHealthBanner from "@/components/BackendHealthBanner";

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
      <body className="flex flex-col min-h-screen bg-surface-50 text-surface-900 antialiased font-sans">
        <BackendHealthBanner />
        <Navbar />
        <main className="flex-1 flex flex-col">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
