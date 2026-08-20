"use client";

import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useTranslation } from "@/hooks/use-translation";
import { ApiError } from "@/lib/api-client";
import type { Service } from "@/lib/types";

import { bookingApi } from "../api/booking.api";

/**
 * New-booking form: pick a service, date and time, then create the booking.
 * Used on the business detail page for authenticated customers.
 */
export function BookingForm({ businessId, services }: { businessId: number; services: Service[] }) {
  const { t } = useTranslation();
  const [serviceId, setServiceId] = useState<string>("");
  const [date, setDate] = useState("");
  const [time, setTime] = useState("");
  const [notes, setNotes] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    if (!serviceId || !date || !time) {
      toast.error(t("common.error"));
      return;
    }
    const scheduled = new Date(`${date}T${time}`);
    if (Number.isNaN(scheduled.getTime())) {
      toast.error(t("common.error"));
      return;
    }
    setLoading(true);
    try {
      await bookingApi.create({
        business_id: businessId,
        service_id: Number(serviceId),
        scheduled_at: scheduled.toISOString(),
        notes,
      });
      toast.success(t("booking.created"));
      setNotes("");
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("common.error"));
    } finally {
      setLoading(false);
    }
  };

  const today = new Date().toISOString().slice(0, 10);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">{t("booking.new")}</CardTitle>
        <CardDescription>{t("booking.title")}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="space-y-1.5">
          <Label>{t("booking.service")}</Label>
          <Select value={serviceId} onValueChange={setServiceId}>
            <SelectTrigger className="w-full">
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
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-1.5">
            <Label>{t("booking.date")}</Label>
            <Input
              type="date"
              min={today}
              value={date}
              onChange={(e) => setDate(e.target.value)}
            />
          </div>
          <div className="space-y-1.5">
            <Label>{t("booking.time")}</Label>
            <Input type="time" value={time} onChange={(e) => setTime(e.target.value)} />
          </div>
        </div>

        <div className="space-y-1.5">
          <Label>{t("booking.notes")}</Label>
          <Input
            placeholder={t("booking.notesPlaceholder")}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
          />
        </div>

        <Button className="w-full" onClick={submit} disabled={loading}>
          {loading ? t("common.loading") : t("booking.create")}
        </Button>
      </CardContent>
    </Card>
  );
}
