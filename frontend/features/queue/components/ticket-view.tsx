"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";

import { StatusBadge } from "@/components/shared/status-badge";
import { WaitBadge } from "@/components/shared/wait-badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useTranslation } from "@/hooks/use-translation";
import { POLL_INTERVAL_MS } from "@/lib/constants";
import type { QueueEntry } from "@/lib/types";

import { queueApi } from "../api/queue.api";

/**
 * My ticket: the big animated ticket code, live position/wait, a status
 * timeline, and cancel. Polls the backend every 5s while the page is open.
 */
export function TicketView() {
  const { t } = useTranslation();
  const [entry, setEntry] = useState<QueueEntry | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    let timer: ReturnType<typeof setInterval> | null = null;

    const poll = async () => {
      try {
        const mine = await queueApi.mine();
        const active = mine.find(
          (e) => e.status === "waiting" || e.status === "called" || e.status === "in_progress",
        );
        if (!cancelled) {
          setEntry(active ?? mine[0] ?? null);
          setLoading(false);
        }
      } catch {
        if (!cancelled) setLoading(false);
      }
    };

    void poll();
    timer = setInterval(poll, POLL_INTERVAL_MS);
    return () => {
      cancelled = true;
      if (timer) clearInterval(timer);
    };
  }, []);

  if (loading) {
    return (
      <div className="flex flex-1 flex-col gap-6 p-6">
        <Skeleton className="h-10 w-56" />
        <Skeleton className="h-48" />
      </div>
    );
  }

  if (!entry) {
    return (
      <div className="flex flex-1 flex-col gap-4 p-6">
        <h1 className="text-2xl font-bold">{t("queue.myTicket")}</h1>
        <p className="text-muted-foreground">{t("queue.noActive")}</p>
      </div>
    );
  }

  return (
    <div className="flex flex-1 flex-col gap-6 p-6">
      <div className="flex items-center justify-between gap-3">
        <h1 className="text-2xl font-bold">{t("queue.myTicket")}</h1>
        <StatusBadge status={entry.status} />
      </div>

      <Card className="overflow-hidden">
        <CardHeader className="bg-primary text-primary-foreground">
          <CardTitle className="font-mono text-5xl font-bold tracking-widest tabular-nums sm:text-6xl">
            {entry.ticket_code}
          </CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap items-center gap-6 pt-6">
          <div>
            <p className="text-xs uppercase tracking-wide text-muted-foreground">
              {t("queue.position")}
            </p>
            <p className="text-3xl font-bold tabular-nums">
              {entry.position > 0 ? entry.position : "—"}
            </p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-wide text-muted-foreground">
              {t("queue.estWait")}
            </p>
            <div className="mt-1">
              <WaitBadge minutes={Math.max(1, Math.round(entry.est_wait_seconds / 60))} />
            </div>
          </div>
          <div className="ms-auto">
            <Button
              variant="outline"
              size="sm"
              disabled={entry.status !== "waiting"}
              onClick={async () => {
                try {
                  await queueApi.cancel(entry.id);
                  toast.success(t("queue.cancelledMsg"));
                  setEntry(null);
                } catch {
                  toast.error(t("common.error"));
                }
              }}
            >
              {t("queue.cancelTicket")}
            </Button>
          </div>
        </CardContent>
      </Card>

      <TicketTimeline status={entry.status} />
    </div>
  );
}

/** Simple 4-step timeline: joined → called → in progress → served. */
function TicketTimeline({ status }: { status: QueueEntry["status"] }) {
  const { t } = useTranslation();
  const steps = [
    { key: "waiting", label: "queue.waiting" },
    { key: "called", label: "queue.called" },
    { key: "in_progress", label: "queue.inProgress" },
    { key: "served", label: "queue.served" },
  ] as const;
  const activeIndex = steps.findIndex((s) => s.key === status);

  return (
    <ol className="flex items-center gap-2">
      {steps.map((step, i) => {
        const done = i <= activeIndex;
        return (
          <li key={step.key} className="flex flex-1 flex-col items-center gap-1">
            <span
              className={`flex size-6 items-center justify-center rounded-full text-xs font-medium ${
                done ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"
              }`}
            >
              {i + 1}
            </span>
            <span
              className={`text-center text-xs ${
                done ? "text-foreground" : "text-muted-foreground"
              }`}
            >
              {t(step.label)}
            </span>
          </li>
        );
      })}
    </ol>
  );
}
