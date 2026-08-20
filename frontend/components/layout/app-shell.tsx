"use client";

import {
  Bell,
  CalendarDays,
  LayoutDashboard,
  LogOut,
  Store,
  Ticket,
  User,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect } from "react";

import { DirectionToggle } from "@/components/shared/direction-toggle";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/features/auth";
import { notificationsApi } from "@/features/notifications";
import { useTranslation } from "@/hooks/use-translation";
import { APP_NAME, ROUTES } from "@/lib/constants";
import type { MessageKey } from "@/lib/i18n";
import { cn } from "@/lib/utils";
import { useNotificationsStore } from "@/stores/notifications.store";

const NAV = [
  { href: ROUTES.businesses, key: "nav.browse", icon: Store },
  { href: ROUTES.account, key: "nav.account", icon: User },
  { href: ROUTES.ticket, key: "nav.ticket", icon: Ticket },
  { href: ROUTES.bookings, key: "nav.bookings", icon: CalendarDays },
  { href: ROUTES.notifications, key: "nav.notifications", icon: Bell },
] as const satisfies ReadonlyArray<{ href: string; key: MessageKey; icon: typeof User }>;

const STAFF_NAV = [
  { href: ROUTES.dashboard, key: "nav.dashboard", icon: LayoutDashboard },
  { href: ROUTES.dashboardServices, key: "nav.dashboardServices", icon: Store },
  { href: ROUTES.dashboardBookings, key: "nav.dashboardBookings", icon: CalendarDays },
] as const satisfies ReadonlyArray<{ href: string; key: MessageKey; icon: typeof User }>;

/**
 * Authenticated application shell: persistent sidebar + topbar that wrap every
 * page under the `(app)` route group. Customer and staff nav groups.
 */
export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const { t } = useTranslation();
  const unreadCount = useNotificationsStore((s) => s.unreadCount);
  const setUnreadCount = useNotificationsStore((s) => s.setUnreadCount);

  // Poll the unread count while in the shell.
  useEffect(() => {
    let cancelled = false;
    let timer: ReturnType<typeof setInterval> | null = null;
    const poll = async () => {
      try {
        const { unread_count } = await notificationsApi.unread();
        if (!cancelled) setUnreadCount(unread_count);
      } catch {
        // transient
      }
    };
    void poll();
    timer = setInterval(poll, 30_000);
    return () => {
      cancelled = true;
      if (timer) clearInterval(timer);
    };
  }, [setUnreadCount]);

  const isStaff = user?.role === "staff" || user?.role === "admin";
  const navGroups = [
    { items: NAV },
    ...(isStaff ? [{ items: STAFF_NAV }] : []),
  ] as const;

  const renderLinks = (collapsed = false) =>
    navGroups.map((group, gi) => (
      <div key={gi} className="flex flex-col gap-1">
        {group.items.map(({ href, key, icon: Icon }) => {
          const active = pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                active
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground",
                collapsed && "flex-1 justify-center",
              )}
            >
              <Icon className="size-4" />
              {t(key)}
              {key === "nav.notifications" && unreadCount > 0 && (
                <span className="ms-auto rounded-full bg-primary px-1.5 text-[10px] font-bold text-primary-foreground">
                  {unreadCount}
                </span>
              )}
            </Link>
          );
        })}
      </div>
    ));

  return (
    <div className="flex min-h-full flex-1">
      <aside className="hidden w-60 shrink-0 flex-col border-e bg-muted/30 p-4 md:flex">
        <div className="px-2 py-3 text-lg font-bold">{APP_NAME}</div>
        <nav className="mt-4 flex flex-col gap-4">{renderLinks()}</nav>
      </aside>

      <div className="flex flex-1 flex-col">
        <header className="flex items-center justify-between border-b px-6 py-3">
          <span className="font-semibold md:hidden">{APP_NAME}</span>
          <div className="hidden text-sm text-muted-foreground md:block">{user?.email}</div>
          <div className="flex items-center gap-2">
            <DirectionToggle />
            <Button variant="outline" size="sm" onClick={logout}>
              <LogOut className="size-4" />
              {t("common.logout")}
            </Button>
          </div>
        </header>

        {/* Mobile nav */}
        <nav className="flex gap-1 overflow-x-auto border-b px-4 py-2 md:hidden">
          {renderLinks(true)}
        </nav>

        <main className="flex flex-1 flex-col">{children}</main>
      </div>
    </div>
  );
}
