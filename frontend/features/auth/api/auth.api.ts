import { api } from "@/lib/api-client";
import type { AuthResponse, Tokens, User } from "@/lib/types";

import type { LoginRequest, RegisterRequest } from "../types";

/** All accounts endpoints in one place — every call goes through the api client. */
export const authApi = {
  login: (data: LoginRequest) => api.post<AuthResponse>("/auth/login", data, { auth: false }),
  register: (data: RegisterRequest) => api.post<User>("/auth/register", data, { auth: false }),
  refresh: (refresh_token: string) =>
    api.post<Tokens>("/auth/refresh", { refresh_token }, { auth: false }),
  me: () => api.get<User>("/auth/me"),
};
