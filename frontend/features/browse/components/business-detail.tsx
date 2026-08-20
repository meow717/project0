"use client";

import { Home } from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";

import { LiveWidget } from "@/components/shared/live-widget";
import { DirectionToggle } from "@/components/shared/direction-toggle";
import { IdentityBadge } from "@/components/shared/identity-badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useTranslation } from "@/hooks/use-translation";
import { useLiveQueue } from "@/hooks/use-live-queue";
import { ApiError } from "@/lib/api-client";
import { ROUTES } from "@/lib/constants";
import type { Service } from "@/lib/types";
import { useAuthStore } from "@/stores/auth.store";

import { BookingForm } from "../../booking/components/booking-form";
import { JoinQueueButton } from "../../queue/components/join-queue-button";
import { useBusinessDetail } from "../hooks/use-business-detail";

/** Public business detail page: info, live widget, services + join/book CTAs. */
export function BusinessDetailView() {
  const { t } = useTranslation();
  const params = useParams<{ slug: string }>();
  const slug = params?.slug ?? "";
  const { business, services, loading, error } = useBusinessDetail(slug);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  useLiveQueue(slug);

  if (loading) {
    return (
      <div className="flex flex-1 flex-col gap-6 p-6">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-40" />
      </div>
    );
  }

  if (error || !business) {
    return (
      <div className="flex flex-1 items-center justify-center p-6 text-muted-foreground">
        {error instanceof ApiError ? error.message : t("common.error")}
      </div>
    );
  }

  return (
    <div className="flex flex-1 flex-col gap-6 p-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold sm:text-3xl">{business.name}</h1>
          <p className="mt-1 text-muted-foreground">
            {business.address ? `${business.address} · ` : ""}
            {t("browse.opensAt")} {business.opens_at} — {t("browse.closesAt")}{" "}
            {business.closes_at}
          </p>
          {business.description ? (
            <p className="mt-3 max-w-2xl">{business.description}</p>
          ) : null}
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" asChild title={t("common.home")} aria-label={t("common.home")}>
            <Link href={ROUTES.home}>
              <Home className="size-4" />
            </Link>
          </Button>
          <IdentityBadge />
          <DirectionToggle />
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <LiveWidget businessId={business.id} />

        <div className="grid gap-6">
          <Card>
            <CardHeader>
              <CardTitle>{t("queue.join")}</CardTitle>
              <CardDescription>{t("browse.view")}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {services.length === 0 ? (
                <p className="text-sm text-muted-foreground">{t("browse.noServices")}</p>
              ) : (
                services.map((service: Service) => (
                  <div
                    key={service.id}
                    className="flex items-center justify-between gap-3 rounded-md border p-3"
                  >
                    <div>
                      <p className="text-sm font-medium">{service.name}</p>
                      <p className="text-xs text-muted-foreground">
                        {service.ticket_prefix} · {Math.round(service.avg_duration_sec / 60)}{" "}
                        {t("queue.minutes")}
                      </p>
                    </div>
                    <JoinQueueButton serviceId={service.id} />
                  </div>
                ))
              )}
            </CardContent>
          </Card>

          {isAuthenticated ? (
            <BookingForm businessId={business.id} services={services} />
          ) : null}
        </div>
      </div>
    </div>
  );
}
