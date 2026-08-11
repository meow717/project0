export const APP_NAME = "Template";

export const ROUTES = {
  home: "/",
  login: "/login",
  signup: "/signup",
  account: "/account",
} as const;

export type Direction = "rtl" | "ltr";
export const DEFAULT_DIRECTION: Direction = "rtl";
export const DEFAULT_LOCALE = "ar";
