import { api } from "@/lib/api-client";
import type { Booking, BookingStatus } from "@/lib/types";

/** Booking endpoints (customer + staff). */
export const bookingApi = {
  create: (data: {
    business_id: number;
    service_id: number;
    scheduled_at: string;
    notes?: string;
  }) => api.post<Booking>("/bookings", data),
  mine: () => api.get<Booking[]>("/bookings/mine"),
  cancel: (id: number) => api.delete<void>(`/bookings/${id}`),
  staffList: (date?: string) =>
    api.get<Booking[]>(`/staff/bookings${date ? `?date=${encodeURIComponent(date)}` : ""}`),
  staffSetStatus: (id: number, status: BookingStatus) =>
    api.patch<Booking>(`/staff/bookings/${id}`, { status }),
};
