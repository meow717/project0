/** Shared API contract types — mirror the backend django-ninja schemas. */

export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  is_staff: boolean;
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
