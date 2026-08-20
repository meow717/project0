export const APP_NAME = "SmartQueue";

export const ROUTES = {
  home: "/",
  login: "/login",
  signup: "/signup",
  account: "/account",
  businesses: "/businesses",
  ticket: "/ticket",
  bookings: "/bookings",
  notifications: "/notifications",
  dashboard: "/dashboard",
  dashboardServices: "/dashboard/services",
  dashboardBookings: "/dashboard/bookings",
  dashboardBusiness: "/dashboard/business",
} as const;

export type Direction = "rtl" | "ltr";
export const DEFAULT_DIRECTION: Direction = "rtl";
export const DEFAULT_LOCALE = "ar";

/** How often live queue data is polled (ms). */
export const POLL_INTERVAL_MS = 5000;

/** Search-input debounce delay (ms). */
export const DEBOUNCE_MS = 300;

/** Directory filter chips — "الكل" means "All" and is sent as empty string. */
export const AREA_FILTERS = ["الكل", "المنصور", "الحارثية", "الدورة", "زيونة"] as const;
export const CATEGORY_FILTERS = ["الكل", "مستشفيات", "بنوك", "مقاهي"] as const;
