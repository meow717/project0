import { api } from "@/lib/api-client";
import type { AppNotification } from "@/lib/types";

/** Notification center endpoints. */
export const notificationsApi = {
  mine: () => api.get<AppNotification[]>("/notifications/mine"),
  unread: () => api.get<{ unread_count: number }>("/notifications/unread"),
  markRead: (id: number) => api.patch<void>(`/notifications/${id}/read`),
  markAllRead: () => api.post<void>("/notifications/read-all"),
};
