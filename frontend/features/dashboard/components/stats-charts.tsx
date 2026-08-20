"use client";

import { useEffect, useState } from "react";

import { ApexChart } from "@/components/shared/apex-chart";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useTranslation } from "@/hooks/use-translation";
import { NUMBER_LOCALE } from "@/lib/i18n";
import type { StatsReport } from "@/lib/types";

import { dashboardApi } from "../api/dashboard.api";

/**
 * Staff analytics: served-per-hour bar, served-per-day line, and by-service
 * donut — all through the shared ApexChart wrapper.
 */
export function StatsCharts() {
  const { t, locale } = useTranslation();
  const [stats, setStats] = useState<StatsReport | null>(null);

  useEffect(() => {
    let cancelled = false;
    dashboardApi
      .stats()
      .then((data) => {
        if (!cancelled) setStats(data);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, []);

  if (!stats) return null;

  const hourSeries = {
    categories: stats.served_per_hour.map((h) => `${String(h.hour).padStart(2, "0")}:00`),
    values: stats.served_per_hour.map((h) => h.count),
  };
  const daySeries = {
    categories: stats.served_per_day.map((d) => d.date),
    values: stats.served_per_day.map((d) => d.count),
  };
  const serviceSeries = {
    labels: stats.by_service.map((s) => s.name),
    values: stats.by_service.map((s) => s.served),
  };

  const localeNumber = NUMBER_LOCALE[locale];

  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">{t("dashboard.servedPerHour")}</CardTitle>
        </CardHeader>
        <CardContent>
          <ApexChart
            type="bar"
            height={260}
            series={[{ name: t("dashboard.served"), data: hourSeries.values }]}
            options={{
              chart: { toolbar: { show: false } },
              plotOptions: { bar: { borderRadius: 4 } },
              xaxis: { categories: hourSeries.categories },
              yaxis: { labels: { formatter: (v: number) => v.toLocaleString(localeNumber) } },
              dataLabels: { enabled: false },
              colors: ["hsl(var(--primary))"],
            }}
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">{t("dashboard.servedPerDay")}</CardTitle>
        </CardHeader>
        <CardContent>
          <ApexChart
            type="line"
            height={260}
            series={[{ name: t("dashboard.served"), data: daySeries.values }]}
            options={{
              chart: { toolbar: { show: false } },
              stroke: { curve: "smooth" },
              xaxis: { categories: daySeries.categories },
              dataLabels: { enabled: false },
              colors: ["hsl(var(--primary))"],
            }}
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">{t("dashboard.byService")}</CardTitle>
        </CardHeader>
        <CardContent>
          <ApexChart
            type="donut"
            height={260}
            series={serviceSeries.values}
            options={{
              labels: serviceSeries.labels,
              legend: { position: "bottom" },
              dataLabels: { formatter: (v: number) => v.toFixed(0) },
              colors: ["hsl(var(--primary))", "hsl(var(--secondary))", "hsl(25 95% 53%)", "hsl(262 83% 58%)"],
            }}
          />
        </CardContent>
      </Card>
    </div>
  );
}
