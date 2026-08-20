"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";

import { StatusBadge } from "@/components/shared/status-badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useTranslation } from "@/hooks/use-translation";
import { POLL_INTERVAL_MS } from "@/lib/constants";
import { ApiError } from "@/lib/api-client";
import type { QueueEntry, Service } from "@/lib/types";

import { dashboardApi } from "../api/dashboard.api";

/**
 * Staff queue board: active entries grouped by status, with call / start /
 * complete / no-show actions and walk-in creation. Polls every 5s.
 */
export function QueueBoard() {
  const { t } = useTranslation();
  const [entries, setEntries] = useState<QueueEntry[]>([]);
  const [services, setServices] = useState<Service[]>([]);
  const [selectedService, setSelectedService] = useState<string>("");
  const [walkInName, setWalkInName] = useState("");
  const [busy, setBusy] = useState(false);

  const load = async () => {
    const [board, svcs] = await Promise.all([
      dashboardApi.queueBoard(),
      dashboardApi.listServices(),
    ]);
    setEntries(board);
    setServices(svcs);
  };

  useEffect(() => {
    let cancelled = false;
    const run = async () => {
      try {
        const [board, svcs] = await Promise.all([
          dashboardApi.queueBoard(),
          dashboardApi.listServices(),
        ]);
        if (cancelled) return;
        setEntries(board);
        setServices(svcs);
      } catch {
        // transient
      }
    };
    void run();
    const timer = setInterval(run, POLL_INTERVAL_MS);
    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, []);

  const act = async (fn: () => Promise<unknown>) => {
    setBusy(true);
    try {
      await fn();
      await load();
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("common.error"));
    } finally {
      setBusy(false);
    }
  };

  const walkIn = () => {
    if (!selectedService) return;
    act(() => dashboardApi.walkIn(Number(selectedService), walkInName || undefined)).then(() => {
      setWalkInName("");
    });
  };

  const active = entries.filter((e) =>
    ["waiting", "called", "in_progress"].includes(e.status),
  );

  return (
    <div className="flex flex-1 flex-col gap-4">
      <div className="flex flex-wrap items-center gap-3">
        <Select value={selectedService} onValueChange={setSelectedService}>
          <SelectTrigger className="w-56">
            <SelectValue placeholder={t("booking.selectService")} />
          </SelectTrigger>
          <SelectContent>
            {services.map((service) => (
              <SelectItem key={service.id} value={String(service.id)}>
                {service.name} ({service.ticket_prefix})
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Input
          className="h-8 w-44"
          placeholder={t("dashboard.walkInName")}
          value={walkInName}
          onChange={(e) => setWalkInName(e.target.value)}
        />
        <Button size="sm" variant="outline" onClick={walkIn} disabled={!selectedService || busy}>
          {t("dashboard.walkIn")}
        </Button>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>{t("queue.yourCode")}</TableHead>
              <TableHead>{t("dashboard.waiting")}</TableHead>
              <TableHead>{t("account.status")}</TableHead>
              <TableHead className="text-end">{t("common.confirm")}</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {active.length === 0 ? (
              <TableRow>
                <TableCell colSpan={4} className="text-center text-muted-foreground">
                  {t("queue.noActive")}
                </TableCell>
              </TableRow>
            ) : (
              active.map((entry) => (
                <TableRow key={entry.id}>
                  <TableCell className="font-mono font-medium">{entry.ticket_code}</TableCell>
                  <TableCell>{entry.display_name || "—"}</TableCell>
                  <TableCell>
                    <StatusBadge status={entry.status} />
                  </TableCell>
                  <TableCell className="text-end">
                    <div className="flex justify-end gap-1.5">
                      {entry.status === "waiting" && (
                        <Button
                          size="xs"
                          variant="outline"
                          disabled={busy}
                          onClick={() => act(() => dashboardApi.callNext(entry.service_id))}
                        >
                          {t("dashboard.callNext")}
                        </Button>
                      )}
                      {entry.status === "called" && (
                        <Button
                          size="xs"
                          variant="outline"
                          disabled={busy}
                          onClick={() => act(() => dashboardApi.start(entry.id))}
                        >
                          {t("dashboard.start")}
                        </Button>
                      )}
                      {entry.status === "in_progress" && (
                        <Button
                          size="xs"
                          variant="outline"
                          disabled={busy}
                          onClick={() => act(() => dashboardApi.complete(entry.id))}
                        >
                          {t("dashboard.complete")}
                        </Button>
                      )}
                      {(entry.status === "waiting" || entry.status === "called") && (
                        <Button
                          size="xs"
                          variant="ghost"
                          disabled={busy}
                          onClick={() => act(() => dashboardApi.noShow(entry.id))}
                        >
                          {t("dashboard.noShow")}
                        </Button>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
