import { create } from "zustand";

import type { LiveSnapshot, QueueEntry } from "@/lib/types";

/**
 * Session-scoped queue store: the single source of truth for live queue data
 * (shared by browse, ticket, and dashboard pages). Not persisted.
 *
 * `snapshots` is keyed by business id so parallel fetches on the browse page
 * don't clobber each other (last-write-wins race on a single slot).
 */
interface QueueState {
  snapshots: Record<number, LiveSnapshot>;
  activeEntry: QueueEntry | null;
  lastPolledAt: number | null;
  setSnapshot: (snapshot: LiveSnapshot) => void;
  setActiveEntry: (entry: QueueEntry | null) => void;
  clear: () => void;
}

export const useQueueStore = create<QueueState>()((set) => ({
  snapshots: {},
  activeEntry: null,
  lastPolledAt: null,
  setSnapshot: (snapshot) =>
    set((state) => ({
      snapshots: { ...state.snapshots, [snapshot.business_id]: snapshot },
      lastPolledAt: Date.now(),
    })),
  setActiveEntry: (entry) => set({ activeEntry: entry }),
  clear: () => set({ snapshots: {}, activeEntry: null, lastPolledAt: null }),
}));
