"use client";

import { ThemeProvider } from "next-themes";
import { useEffect } from "react";

import { useUIStore } from "@/stores/ui.store";

/** Keeps <html dir/lang> in sync with the UI store (locale ⇄ direction). */
function DirectionSync() {
  const direction = useUIStore((s) => s.direction);
  const locale = useUIStore((s) => s.locale);
  useEffect(() => {
    const el = document.documentElement;
    el.dir = direction;
    el.lang = locale;
  }, [direction, locale]);
  return null;
}

/** Custom color themes: "yellow" (default) ⇄ "purple". */
const THEMES = ["yellow", "purple"];

export function AppProviders({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="yellow"
      themes={THEMES}
      enableSystem={false}
      disableTransitionOnChange={false}
    >
      <DirectionSync />
      {children}
    </ThemeProvider>
  );
}
