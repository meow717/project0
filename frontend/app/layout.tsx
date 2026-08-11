import type { Metadata } from "next";
import { Cairo, Geist_Mono } from "next/font/google";

import "./globals.css";
import { Toaster } from "@/components/ui/sonner";
import { cn } from "@/lib/utils";
import { AppProviders } from "@/providers/app-providers";

// Arabic-first sans (covers Arabic + Latin). Maps to Tailwind's font-sans.
const cairo = Cairo({ subsets: ["arabic", "latin"], variable: "--font-sans" });
const geistMono = Geist_Mono({ subsets: ["latin"], variable: "--font-geist-mono" });

export const metadata: Metadata = {
  title: "Template",
  description: "Application template — Next.js + shadcn (RTL)",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    // dir/lang are the SSR defaults; AppProviders keeps them in sync after toggle.
    <html
      lang="ar"
      dir="rtl"
      suppressHydrationWarning
      className={cn("h-full", cairo.variable, geistMono.variable)}
    >
      <body className="min-h-full flex flex-col font-sans antialiased">
        <AppProviders>{children}</AppProviders>
        <Toaster richColors position="top-center" />
      </body>
    </html>
  );
}
