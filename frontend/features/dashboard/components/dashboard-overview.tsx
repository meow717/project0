"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useTranslation } from "@/hooks/use-translation";
import { ApiError } from "@/lib/api-client";
import { ROUTES } from "@/lib/constants";

import { dashboardApi } from "../api/dashboard.api";
import { QueueBoard } from "./queue-board";
import { StatsCharts } from "./stats-charts";

/** Dashboard overview: live queue board + analytics charts, or the create form. */
export function DashboardOverview() {
  const { t } = useTranslation();
  const [hasBusiness, setHasBusiness] = useState<boolean | null>(null);

  useEffect(() => {
    let cancelled = false;
    dashboardApi
      .getBusiness()
      .then(() => {
        if (!cancelled) setHasBusiness(true);
      })
      .catch((err: unknown) => {
        // 404 = no business linked yet -> show the creation form.
        if (!cancelled) setHasBusiness(!(err instanceof ApiError && err.status === 404));
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (hasBusiness === null) return null;

  if (!hasBusiness) {
    return (
      <div className="flex flex-1 flex-col items-center gap-6 p-6">
        <Card className="max-w-xl w-full">
          <CardHeader>
            <CardTitle className="text-base">{t("dashboard.createBusiness")}</CardTitle>
            <CardDescription>{t("dashboard.settings")}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <p className="text-sm text-muted-foreground">{t("dashboard.noBusiness")}</p>
            <Button asChild>
              <Link href={ROUTES.dashboardBusiness}>{t("dashboard.createBusiness")}</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="flex flex-1 flex-col gap-6">
      <h2 className="text-lg font-semibold">{t("dashboard.overview")}</h2>
      <QueueBoard />
      <StatsCharts />
    </div>
  );
}
