"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";

import { BookingStatusBadge } from "@/components/shared/booking-status-badge";
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
import { useTranslation } from "@/hooks/use-translation";
import { ApiError } from "@/lib/api-client";
import type { Booking, BookingStatus } from "@/lib/types";

import { dashboardApi } from "../api/dashboard.api";

/** Staff bookings view: list by date, confirm / complete / no-show. */
export function BookingsManage() {
  const { t } = useTranslation();
  const [date, setDate] = useState(new Date().toISOString().slice(0, 10));
  const [bookings, setBookings] = useState<Booking[]>([]);

  useEffect(() => {
    let cancelled = false;
    dashboardApi
      .bookings(date)
      .then((data) => {
        if (!cancelled) setBookings(data);
      })
      .catch(() => {
        if (!cancelled) setBookings([]);
      });
    return () => {
      cancelled = true;
    };
  }, [date]);

  const setStatus = async (id: number, status: BookingStatus) => {
    try {
      await dashboardApi.setBookingStatus(id, status);
      const updated = await dashboardApi.bookings(date);
      setBookings(updated);
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("common.error"));
    }
  };

  return (
    <div className="flex flex-1 flex-col gap-4">
      <div className="flex items-center gap-3">
        <h2 className="text-lg font-semibold">{t("dashboard.bookings")}</h2>
        <Input
          type="date"
          className="w-44"
          value={date}
          onChange={(e) => setDate(e.target.value)}
        />
      </div>

      {bookings.length === 0 ? (
        <p className="text-muted-foreground">{t("dashboard.noBookings")}</p>
      ) : (
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t("booking.service")}</TableHead>
                <TableHead>{t("booking.scheduledFor")}</TableHead>
                <TableHead>{t("account.status")}</TableHead>
                <TableHead className="text-end">{t("common.confirm")}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {bookings.map((booking) => (
                <TableRow key={booking.id}>
                  <TableCell className="font-medium">{booking.service_name}</TableCell>
                  <TableCell dir="ltr">
                    {new Date(booking.scheduled_at).toLocaleTimeString()}
                  </TableCell>
                  <TableCell>
                    <BookingStatusBadge status={booking.status} />
                  </TableCell>
                  <TableCell className="text-end">
                    <div className="flex justify-end gap-1.5">
                      {booking.status === "pending" && (
                        <Button
                          size="xs"
                          variant="outline"
                          onClick={() => setStatus(booking.id, "confirmed")}
                        >
                          {t("dashboard.confirmBooking")}
                        </Button>
                      )}
                      {booking.status === "confirmed" && (
                        <>
                          <Button
                            size="xs"
                            variant="outline"
                            onClick={() => setStatus(booking.id, "completed")}
                          >
                            {t("dashboard.complete")}
                          </Button>
                          <Button
                            size="xs"
                            variant="ghost"
                            onClick={() => setStatus(booking.id, "no_show")}
                          >
                            {t("dashboard.noShow")}
                          </Button>
                        </>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  );
}
