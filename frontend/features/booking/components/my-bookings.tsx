"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";

import { BookingStatusBadge } from "@/components/shared/booking-status-badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useTranslation } from "@/hooks/use-translation";
import type { Booking } from "@/lib/types";

import { bookingApi } from "../api/booking.api";

/** "My bookings" — list with cancel for pending/confirmed. */
export function MyBookings() {
  const { t } = useTranslation();
  const [bookings, setBookings] = useState<Booking[] | null>(null);

  useEffect(() => {
    let cancelled = false;
    bookingApi
      .mine()
      .then((data) => {
        if (!cancelled) setBookings(data);
      })
      .catch(() => {
        if (!cancelled) setBookings([]);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (!bookings) {
    return (
      <div className="flex flex-1 flex-col gap-4 p-6">
        <Skeleton className="h-10 w-48" />
        <Skeleton className="h-32" />
      </div>
    );
  }

  const cancellable = bookings.filter((b) => b.status === "pending" || b.status === "confirmed");

  const cancel = async (id: number) => {
    try {
      await bookingApi.cancel(id);
      setBookings((prev) => prev?.filter((b) => b.id !== id) ?? null);
      toast.success(t("booking.cancelledMsg"));
    } catch {
      toast.error(t("common.error"));
    }
  };

  return (
    <div className="flex flex-1 flex-col gap-6 p-6">
      <h1 className="text-2xl font-bold">{t("booking.my")}</h1>

      {bookings.length === 0 ? (
        <p className="text-muted-foreground">{t("booking.empty")}</p>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {bookings.map((booking) => (
            <Card key={booking.id}>
              <CardHeader>
                <div className="flex items-center justify-between gap-2">
                  <CardTitle className="text-base">{booking.service_name}</CardTitle>
                  <BookingStatusBadge status={booking.status} />
                </div>
                <CardDescription>
                  {t("booking.scheduledFor")} {new Date(booking.scheduled_at).toLocaleString()}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => cancel(booking.id)}
                  disabled={!cancellable.some((b) => b.id === booking.id)}
                >
                  {t("booking.cancel")}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
