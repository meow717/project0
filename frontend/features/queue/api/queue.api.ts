import { api } from "@/lib/api-client";
import type { QueueEntry, WaitEstimate } from "@/lib/types";

/** Customer queue endpoints. */
export const queueApi = {
  join: (serviceId: number) => api.post<QueueEntry>(`/services/${serviceId}/join`),
  mine: () => api.get<QueueEntry[]>("/queue/mine"),
  get: (entryId: number) => api.get<QueueEntry>(`/queue/entries/${entryId}`),
  wait: (entryId: number) => api.get<WaitEstimate>(`/queue/entries/${entryId}/wait`),
  cancel: (entryId: number) => api.delete<void>(`/queue/entries/${entryId}`),
};
