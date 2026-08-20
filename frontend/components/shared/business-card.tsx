"use client";

import { Ticket } from "lucide-react";
import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useTranslation } from "@/hooks/use-translation";
import type { Business } from "@/lib/types";
import { useQueueStore } from "@/stores/queue.store";

/**
 * Directory card for a business: name, area tag, current waiting count and a
 * "Get Ticket" button. Waiting count comes from the live snapshot in the
 * shared queue store (fed by the browse hook).
 */
export function BusinessCard({ business }: { business: Business }) {
  const { t } = useTranslation();
  const snapshot = useQueueStore((s) => s.snapshots[business.id] ?? null);
  const waiting = snapshot ? snapshot.services.reduce((sum, s) => sum + s.waiting_count, 0) : null;

  return (
    <Card className="flex h-full flex-col transition-all duration-200 hover:-translate-y-0.5 hover:shadow-lg hover:shadow-primary/10 hover:ring-primary/40">
      <CardHeader className="flex-row items-center justify-between gap-3">
        <CardTitle className="min-w-0 truncate text-base font-bold sm:text-lg">
          {business.name}
        </CardTitle>
        {business.area ? (
          <Badge
            variant="secondary"
            className="shrink-0 border border-primary/20 bg-primary/10 px-2.5 py-1 text-xs font-semibold text-primary-foreground"
          >
            {business.area}
          </Badge>
        ) : null}
      </CardHeader>
      <CardContent className="flex flex-1 flex-col justify-between gap-4">
        <div className="flex items-center gap-2.5">
          <span
            className="size-2.5 shrink-0 rounded-full bg-yellow-400 ring-2 ring-yellow-400/30 purple:bg-yellow-300 purple:ring-yellow-300/30"
            aria-hidden
          />
          <span className="text-sm font-medium text-muted-foreground">
            {waiting === null ? (
              t("common.loading")
            ) : (
              <>
                <strong className="text-lg font-bold text-foreground tabular-nums">
                  {waiting}
                </strong>{" "}
                {t("browse.waitingCount")}
              </>
            )}
          </span>
        </div>
        <Button asChild size="lg" className="mt-1 w-full text-sm font-bold shadow-sm">
          <Link href={`/businesses/${business.slug}`}>
            <Ticket className="size-4" />
            {t("browse.getTicket")}
          </Link>
        </Button>
      </CardContent>
    </Card>
  );
}
