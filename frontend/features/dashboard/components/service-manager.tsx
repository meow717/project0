"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useTranslation } from "@/hooks/use-translation";
import { ApiError } from "@/lib/api-client";
import type { Service } from "@/lib/types";

import { dashboardApi } from "../api/dashboard.api";

/** Staff service management: list + create/edit/delete via a dialog. */
export function ServiceManager() {
  const { t } = useTranslation();
  const [services, setServices] = useState<Service[]>([]);
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<Service | null>(null);
  const [name, setName] = useState("");
  const [prefix, setPrefix] = useState("");
  const [duration, setDuration] = useState("10");

  const load = async () => {
    const data = await dashboardApi.listServices();
    setServices(data);
  };

  // initial load
  useEffect(() => {
    let cancelled = false;
    dashboardApi
      .listServices()
      .then((data) => {
        if (!cancelled) setServices(data);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, []);

  const openCreate = () => {
    setEditing(null);
    setName("");
    setPrefix("");
    setDuration("10");
    setOpen(true);
  };

  const openEdit = (service: Service) => {
    setEditing(service);
    setName(service.name);
    setPrefix(service.ticket_prefix);
    setDuration(String(Math.round(service.avg_duration_sec / 60)));
    setOpen(true);
  };

  const save = async () => {
    try {
      if (editing) {
        await dashboardApi.updateService(editing.id, {
          name,
          avg_duration_sec: Number(duration) * 60,
        });
      } else {
        await dashboardApi.createService({
          name,
          ticket_prefix: prefix,
          avg_duration_sec: Number(duration) * 60,
        });
      }
      setOpen(false);
      await load();
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("common.error"));
    }
  };

  const remove = async (id: number) => {
    try {
      await dashboardApi.deleteService(id);
      await load();
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("common.error"));
    }
  };

  return (
    <div className="flex flex-1 flex-col gap-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">{t("dashboard.services")}</h2>
        <Button size="sm" onClick={openCreate}>
          {t("dashboard.addService")}
        </Button>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>{t("booking.service")}</TableHead>
              <TableHead>{t("dashboard.ticketPrefix")}</TableHead>
              <TableHead>{t("dashboard.avgDuration")}</TableHead>
              <TableHead className="text-end">{t("common.confirm")}</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {services.map((service) => (
              <TableRow key={service.id}>
                <TableCell>
                  <span className="font-medium">{service.name}</span>
                  {!service.is_active ? (
                    <Badge variant="secondary" className="ms-2">
                      {t("account.inactive")}
                    </Badge>
                  ) : null}
                </TableCell>
                <TableCell className="font-mono">{service.ticket_prefix}</TableCell>
                <TableCell>{Math.round(service.avg_duration_sec / 60)}</TableCell>
                <TableCell className="text-end">
                  <Button size="xs" variant="outline" onClick={() => openEdit(service)}>
                    {t("dashboard.editService")}
                  </Button>
                  <Button
                    size="xs"
                    variant="ghost"
                    className="ms-1.5"
                    onClick={() => remove(service.id)}
                  >
                    {t("common.delete")}
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {editing ? t("dashboard.editService") : t("dashboard.addService")}
            </DialogTitle>
            <DialogDescription>{t("dashboard.services")}</DialogDescription>
          </DialogHeader>
          <div className="space-y-3">
            <div className="space-y-1.5">
              <Label>{t("dashboard.serviceName")}</Label>
              <Input value={name} onChange={(e) => setName(e.target.value)} />
            </div>
            {!editing && (
              <div className="space-y-1.5">
                <Label>{t("dashboard.ticketPrefix")}</Label>
                <Input
                  maxLength={2}
                  value={prefix}
                  onChange={(e) => setPrefix(e.target.value.toUpperCase())}
                />
              </div>
            )}
            <div className="space-y-1.5">
              <Label>{t("dashboard.avgDuration")}</Label>
              <Input
                type="number"
                min={1}
                value={duration}
                onChange={(e) => setDuration(e.target.value)}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setOpen(false)}>
              {t("common.cancel")}
            </Button>
            <Button onClick={save} disabled={!name || (!editing && !prefix)}>
              {t("common.save")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
