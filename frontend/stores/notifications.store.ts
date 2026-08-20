import { create } from "zustand";

import type { AppNotification } from "@/lib/types";

/** Session-scoped notifications store (unread badge + list). Not persisted. */
interface NotificationsState {
  unreadCount: number;
  list: AppNotification[];
  setUnreadCount: (count: number) => void;
  setList: (list: AppNotification[]) => void;
  markRead: (id: number) => void;
  markAllRead: () => void;
}

export const useNotificationsStore = create<NotificationsState>()((set) => ({
  unreadCount: 0,
  list: [],
  setUnreadCount: (count) => set({ unreadCount: count }),
  setList: (list) => set({ list }),
  markRead: (id) =>
    set((state) => ({
      list: state.list.map((n) => (n.id === id ? { ...n, is_read: true } : n)),
      unreadCount: Math.max(0, state.unreadCount - 1),
    })),
  markAllRead: () =>
    set((state) => ({
      list: state.list.map((n) => ({ ...n, is_read: true })),
      unreadCount: 0,
    })),
}));
