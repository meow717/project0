/** Shared API contract types — mirror the backend django-ninja schemas. */

export type UserRole = "customer" | "staff" | "admin";

export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  is_staff: boolean;
  role: UserRole;
  business_id: number | null;
}

export interface Tokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface AuthResponse {
  user: User;
  tokens: Tokens;
}

export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

// --------------------------------------------------------------------------- //
// Businesses
// --------------------------------------------------------------------------- //
export interface Business {
  id: number;
  name: string;
  slug: string;
  description: string;
  area: string;
  category: string;
  address: string;
  phone: string;
  timezone: string;
  opens_at: string;
  closes_at: string;
  logo_url: string | null;
  is_active: boolean;
}

// --------------------------------------------------------------------------- //
// Services & queue entries
// --------------------------------------------------------------------------- //
export interface Service {
  id: number;
  business_id: number;
  name: string;
  description: string;
  ticket_prefix: string;
  avg_duration_sec: number;
  is_active: boolean;
}

export type QueueEntryStatus =
  | "waiting"
  | "called"
  | "in_progress"
  | "served"
  | "no_show"
  | "cancelled";

export interface QueueEntry {
  id: number;
  business_id: number;
  service_id: number;
  ticket_code: string;
  ticket_number: number;
  status: QueueEntryStatus;
  position: number;
  est_wait_seconds: number;
  display_name: string | null;
  created_at: string | null;
  called_at: string | null;
  started_at: string | null;
  served_at: string | null;
}

export interface WaitEstimate {
  position: number;
  est_seconds: number;
}

// --------------------------------------------------------------------------- //
// Live snapshot
// --------------------------------------------------------------------------- //
export type CrowdLevel = "low" | "medium" | "high";
export type ServiceState = "closed" | "idle" | "busy";

export interface ServiceLiveStatus {
  service_id: number;
  name: string;
  prefix: string;
  current_number: string | null;
  waiting_count: number;
  est_wait_min: number;
  state: ServiceState;
}

export interface LiveSnapshot {
  business_id: number;
  generated_at: string;
  crowd_level: CrowdLevel;
  services: ServiceLiveStatus[];
}

// --------------------------------------------------------------------------- //
// Bookings
// --------------------------------------------------------------------------- //
export type BookingStatus =
  | "pending"
  | "confirmed"
  | "completed"
  | "cancelled"
  | "no_show";

export interface Booking {
  id: number;
  business_id: number;
  service_id: number;
  service_name: string;
  scheduled_at: string;
  duration_sec: number;
  status: BookingStatus;
  notes: string;
}

// --------------------------------------------------------------------------- //
// Notifications
// --------------------------------------------------------------------------- //
export interface AppNotification {
  id: number;
  title: string;
  body: string;
  kind: "in_app" | "email" | "sms";
  ref_kind: string;
  ref_id: number | null;
  is_read: boolean;
  created_at: string | null;
}

// --------------------------------------------------------------------------- //
// Staff analytics (mirrors backend StatsReportOut)
// --------------------------------------------------------------------------- //
export interface ServedPerDay {
  date: string;
  count: number;
}

export interface ServedPerHour {
  hour: number;
  count: number;
}

export interface ServiceStat {
  service_id: number;
  name: string;
  served: number;
  avg_wait_min: number;
}

export interface StatsReport {
  served_per_day: ServedPerDay[];
  served_per_hour: ServedPerHour[];
  by_service: ServiceStat[];
}
