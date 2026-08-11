"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";

import { useTranslation } from "@/hooks/use-translation";
import { ApiError } from "@/lib/api-client";
import { ROUTES } from "@/lib/constants";
import { useAuthStore } from "@/stores/auth.store";

import { authApi } from "../api/auth.api";
import type { LoginRequest, RegisterRequest } from "../types";

/** Auth actions bound to the global store + router + toasts. */
export function useAuth() {
  const router = useRouter();
  const { t } = useTranslation();
  const user = useAuthStore((s) => s.user);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const setSession = useAuthStore((s) => s.setSession);
  const clear = useAuthStore((s) => s.clear);
  const [loading, setLoading] = useState(false);

  const greet = (name: string) => toast.success(`${t("auth.welcome")} ${name}`);

  const login = async (data: LoginRequest): Promise<boolean> => {
    setLoading(true);
    try {
      const res = await authApi.login(data);
      setSession(res.user, res.tokens);
      greet(res.user.full_name || res.user.email);
      router.push(ROUTES.account);
      return true;
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("auth.loginError"));
      return false;
    } finally {
      setLoading(false);
    }
  };

  const signup = async (data: RegisterRequest): Promise<boolean> => {
    setLoading(true);
    try {
      await authApi.register(data);
      const res = await authApi.login({ email: data.email, password: data.password });
      setSession(res.user, res.tokens);
      greet(res.user.full_name || res.user.email);
      router.push(ROUTES.account);
      return true;
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("auth.signupError"));
      return false;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    clear();
    router.push(ROUTES.login);
  };

  return { user, isAuthenticated, loading, login, signup, logout };
}
