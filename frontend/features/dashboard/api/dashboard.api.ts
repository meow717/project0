import { api } from "@/lib/api-client";
import type { Booking, BookingStatus, Business, QueueEntry, Service, StatsReport } from "@/lib/types";

/** Staff dashboard endpoints. */
export const dashboardApi = {
  // business
  getBusiness: () => api.get<Business>("/staff/businesses/me"),
  updateBusiness: (data: Partial<Business>) => api.patch<Business>("/staff/businesses/me", data),
  createBusiness: (data: {
    name: string;
    slug: string;
    description?: string;
    area?: string;
    category?: string;
    address?: string;
    phone?: string;
    timezone?: string;
    opens_at?: string;
    closes_at?: string;
  }) => api.post<Business>("/staff/businesses", data),
  uploadLogo: (businessId: number, file: File) => {
    const form = new FormData();
    form.append("file", file);
    return api.post<{ logo_url: string }>(`/staff/businesses/${businessId}/logo`, form);
  },

  // services
  listServices: () => api.get<Service[]>("/staff/services"),
  createService: (data: {
    name: string;
    ticket_prefix: string;
    description?: string;
    avg_duration_sec: number;
  }) => api.post<Service>("/staff/services", data),
  updateService: (id: number, data: Partial<Service>) =>
    api.patch<Service>(`/staff/services/${id}`, data),
  deleteService: (id: number) => api.delete<void>(`/staff/services/${id}`),

  // queue board
  queueBoard: () => api.get<QueueEntry[]>("/staff/queue"),
  callNext: (serviceId: number) => api.post<QueueEntry>(`/staff/services/${serviceId}/call`),
  start: (entryId: number) => api.post<QueueEntry>(`/staff/entries/${entryId}/start`),
  complete: (entryId: number) => api.post<QueueEntry>(`/staff/entries/${entryId}/complete`),
  noShow: (entryId: number) => api.post<QueueEntry>(`/staff/entries/${entryId}/no-show`),
  walkIn: (serviceId: number, displayName?: string) =>
    api.post<QueueEntry>("/staff/entries", { service_id: serviceId, display_name: displayName }),

  // stats
  stats: () => api.get<StatsReport>("/staff/stats"),

  // bookings
  bookings: (date?: string) =>
    api.get<Booking[]>(`/staff/bookings${date ? `?date=${encodeURIComponent(date)}` : ""}`),
  setBookingStatus: (id: number, status: BookingStatus) =>
    api.patch<Booking>(`/staff/bookings/${id}`, { status }),
};
