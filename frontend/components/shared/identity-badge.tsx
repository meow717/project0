"use client";

import { LogIn, LogOut, User, UserRound } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useSyncExternalStore } from "react";

import { Button } from "@/components/ui/button";
import { useTranslation } from "@/hooks/use-translation";
import { ROUTES } from "@/lib/constants";
import { useAuthStore } from "@/stores/auth.store";

/** True once the persisted auth store has finished rehydrating from storage. */
function useStoreHydrated(): boolean {
  return useSyncExternalStore(
    (onChange) => useAuthStore.persist.onFinishHydration(onChange),
    () => useAuthStore.persist.hasHydrated(),
    () => false,
  );
}

/**
 * Identity control: a compact icon (user when signed in, guest icon when not)
 * that shows identity/guest status. With `showDetails` it renders the full
 * pill (name + logout) instead. Used on public pages (browse list + detail).
 */
export function IdentityBadge({ showDetails = false }: { showDetails?: boolean }) {
  const { t } = useTranslation();
  const router = useRouter();
  const hydrated = useStoreHydrated();
  const user = useAuthStore((s) => s.user);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const clear = useAuthStore((s) => s.clear);

  // Don't flash "guest" while the persisted session is still loading.
  if (!hydrated) return null;

  const logout = () => {
    clear();
    router.push(ROUTES.login);
  };

  if (isAuthenticated && user) {
    if (showDetails) {
      return (
        <div className="flex items-center gap-2 rounded-lg border bg-card/60 px-2 py-1 text-xs">
          <User className="size-3.5 text-primary" />
          <span className="font-semibold">{t("browse.signedInAs")}</span>
          <span className="text-muted-foreground">
            {user.full_name || user.email}
            {user.business_id ? ` · ${t("account.roleStaff")}` : ""}
          </span>
          <button
            onClick={logout}
            className="ms-1 inline-flex items-center gap-1 rounded px-1.5 py-0.5 font-medium text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
          >
            <LogOut className="size-3.5" />
            {t("common.logout")}
          </button>
        </div>
      );
    }

    return (
      <Button
        variant="outline"
        size="sm"
        asChild
        title={`${t("browse.signedInAs")} ${user.full_name || user.email}`}
        aria-label={t("browse.signedInAs")}
      >
        <Link href={ROUTES.account}>
          <User className="size-4" />
          <span>{user.full_name || user.email}</span>
        </Link>
      </Button>
    );
  }

  // Guest (not signed in)
  if (showDetails) {
    return (
      <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-dashed bg-card/40 px-4 py-3">
        <p className="text-sm text-muted-foreground">
          {t("browse.guest")} — {t("browse.loginCta")}
        </p>
        <Button asChild size="sm" variant="outline">
          <Link href={ROUTES.login}>
            <LogIn className="size-4" />
            {t("auth.loginBtn")}
          </Link>
        </Button>
      </div>
    );
  }

  return (
    <Button
      variant="outline"
      size="sm"
      asChild
      title={t("browse.guest")}
      aria-label={t("browse.guest")}
    >
      <Link href={ROUTES.login}>
        <UserRound className="size-4" />
        <span>{t("browse.guestShort")}</span>
      </Link>
    </Button>
  );
}
