"use client";

import { useEffect } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useTranslation } from "@/hooks/use-translation";
import { cn } from "@/lib/utils";
import { useNotificationsStore } from "@/stores/notifications.store";

import { notificationsApi } from "../api/notification.api";

/** Notification center: list, mark read, mark all read. */
export function NotificationList() {
  const { t } = useTranslation();
  const { list, setList, unreadCount, setUnreadCount, markRead, markAllRead } =
    useNotificationsStore();

  useEffect(() => {
    let cancelled = false;
    Promise.all([notificationsApi.mine(), notificationsApi.unread()])
      .then(([items, { unread_count }]) => {
        if (cancelled) return;
        setList(items);
        setUnreadCount(unread_count);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [setList, setUnreadCount]);

  const read = async (id: number) => {
    try {
      await notificationsApi.markRead(id);
      markRead(id);
    } catch {
      toast.error(t("common.error"));
    }
  };

  const readAll = async () => {
    try {
      await notificationsApi.markAllRead();
      markAllRead();
    } catch {
      toast.error(t("common.error"));
    }
  };

  return (
    <div className="flex flex-1 flex-col gap-4 p-6">
      <div className="flex items-center justify-between gap-3">
        <h1 className="text-2xl font-bold">{t("notification.title")}</h1>
        {unreadCount > 0 && (
          <Button variant="outline" size="sm" onClick={readAll}>
            {t("notification.markAllRead")}
          </Button>
        )}
      </div>

      {list.length === 0 ? (
        <p className="text-muted-foreground">{t("notification.empty")}</p>
      ) : (
        <div className="space-y-2">
          {list.map((notification) => (
            <button
              key={notification.id}
              type="button"
              className="block w-full text-start"
              onClick={() => {
                if (!notification.is_read) void read(notification.id);
              }}
            >
              <Card className={cn(!notification.is_read && "border-primary/40")}>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-base">
                    {notification.title}
                    {!notification.is_read && (
                      <span className="size-2 rounded-full bg-primary" aria-hidden />
                    )}
                  </CardTitle>
                  <CardDescription>{new Date(notification.created_at ?? "").toLocaleString()}</CardDescription>
                </CardHeader>
                {notification.body ? (
                  <CardContent className="pt-0 text-sm text-muted-foreground">
                    {notification.body}
                  </CardContent>
                ) : null}
              </Card>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
