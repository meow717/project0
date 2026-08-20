"use client";

import { Loader2 } from "lucide-react";

import { CrowdMeter } from "@/components/shared/crowd-meter";
import { ServingNumber } from "@/components/shared/serving-number";
import { WaitBadge } from "@/components/shared/wait-badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useTranslation } from "@/hooks/use-translation";
import { useSnapshot } from "@/hooks/use-live-queue";
import type { ServiceLiveStatus } from "@/lib/types";

/**
 * Public live board for a business: crowd level + per-service "now serving",
 * waiting count and estimated wait. Reads the shared queue store (fed by
 * `useLiveQueue`).
 */
export function LiveWidget({ businessId }: { businessId?: number | null }) {
  const { t } = useTranslation();
  const snapshot = useSnapshot(businessId ?? null);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between gap-2 text-base">
          <span>{t("queue.liveBoard")}</span>
          {snapshot ? (
            <CrowdMeter level={snapshot.crowd_level} />
          ) : (
            <Loader2 className="size-4 animate-spin text-muted-foreground" />
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {!snapshot ? (
          <p className="text-sm text-muted-foreground">{t("common.loading")}</p>
        ) : snapshot.services.length === 0 ? (
          <p className="text-sm text-muted-foreground">{t("browse.noServices")}</p>
        ) : (
          snapshot.services.map((service) => (
            <ServiceRow key={service.service_id} service={service} />
          ))
        )}
      </CardContent>
    </Card>
  );
}

function ServiceRow({ service }: { service: ServiceLiveStatus }) {
  const { t } = useTranslation();
  return (
    <div className="flex items-center justify-between gap-4 rounded-md border p-3">
      <div className="min-w-0">
        <p className="truncate text-sm font-medium">{service.name}</p>
        <p className="text-xs text-muted-foreground">
          {service.waiting_count} {t("dashboard.waiting")}
          {service.state === "busy" ? ` · ${t("queue.inProgress")}` : ""}
        </p>
      </div>
      <div className="flex items-center gap-3">
        <div className="text-center">
          <p className="text-[10px] uppercase tracking-wide text-muted-foreground">
            {t("queue.nowServing")}
          </p>
          <ServingNumber value={service.current_number} className="text-2xl sm:text-3xl" />
        </div>
        <WaitBadge minutes={service.est_wait_min} />
      </div>
    </div>
  );
}
