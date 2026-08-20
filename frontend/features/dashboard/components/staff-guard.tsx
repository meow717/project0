"use client";

import { useAuth } from "@/features/auth";
import { useTranslation } from "@/hooks/use-translation";

/**
 * Client-side staff guard: renders children only for users with the staff role.
 * (The JWT lives in the persisted store, so route protection is client-side.)
 */
export function StaffGuard({ children }: { children: React.ReactNode }) {
  const { user } = useAuth();
  const { t } = useTranslation();

  if (user?.role !== "staff" && user?.role !== "admin") {
    return (
      <div className="flex flex-1 items-center justify-center p-6 text-center text-muted-foreground">
        {t("dashboard.staffOnly")}
      </div>
    );
  }

  return <>{children}</>;
}
