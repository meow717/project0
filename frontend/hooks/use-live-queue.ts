"use client";

import { useEffect } from "react";

import { POLL_INTERVAL_MS } from "@/lib/constants";
import type { LiveSnapshot } from "@/lib/types";
import { useQueueStore } from "@/stores/queue.store";

import { browseApi } from "../features/browse/api/browse.api";

/**
 * Polls a business's live snapshot into the shared queue store. Stops polling
 * while the tab is hidden and cleans up on unmount. Only one poller per
 * business should be active — components share the store.
 */
export function useLiveQueue(slug: string | null) {
  const setSnapshot = useQueueStore((s) => s.setSnapshot);

  useEffect(() => {
    if (!slug) return;

    let cancelled = false;
    let timer: ReturnType<typeof setInterval> | null = null;

    const poll = async () => {
      try {
        const data = await browseApi.getLive(slug);
        if (!cancelled) setSnapshot(data);
      } catch {
        // transient polling failure — keep the last snapshot
      }
    };

    const schedule = () => {
      void poll();
      timer = setInterval(poll, POLL_INTERVAL_MS);
    };

    const onVisibility = () => {
      if (document.hidden) {
        if (timer) clearInterval(timer);
        timer = null;
      } else if (!timer) {
        schedule();
      }
    };

    document.addEventListener("visibilitychange", onVisibility);
    schedule();

    return () => {
      cancelled = true;
      if (timer) clearInterval(timer);
      document.removeEventListener("visibilitychange", onVisibility);
    };
  }, [slug, setSnapshot]);
}

/** Convenience selector for a business's snapshot. */
export function useSnapshot(businessId: number | null): LiveSnapshot | null {
  return useQueueStore((s) => (businessId ? (s.snapshots[businessId] ?? null) : null));
}
