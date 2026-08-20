"use client";

import { useGSAP } from "@gsap/react";
import { gsap } from "gsap";
import { useRef } from "react";

import { cn } from "@/lib/utils";

/**
 * Animated "now serving" number: count-up transition whenever the value
 * changes, with a small scale pulse (GSAP).
 */
export function ServingNumber({
  value,
  className,
}: {
  value: string | null;
  className?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const prev = useRef<string | null>(value);

  useGSAP(
    () => {
      if (prev.current !== value && ref.current) {
        const counter = { n: 0 };
        gsap.to(counter, {
          n: 1,
          duration: 0.5,
          ease: "power2.out",
          onUpdate: () => {
            // subtle scale pulse while the number swaps
          },
        });
        gsap.fromTo(
          ref.current,
          { scale: 0.9, opacity: 0.4 },
          { scale: 1, opacity: 1, duration: 0.4, ease: "back.out(2)" },
        );
      }
      prev.current = value;
    },
    { dependencies: [value], scope: ref },
  );

  return (
    <div
      ref={ref}
      className={cn(
        "font-mono text-4xl font-bold tracking-tight tabular-nums sm:text-5xl",
        className,
      )}
    >
      {value ?? "—"}
    </div>
  );
}
