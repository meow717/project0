import { Badge } from "@/components/ui/badge";
import { useTranslation } from "@/hooks/use-translation";
import type { MessageKey } from "@/lib/i18n";
import type { BookingStatus } from "@/lib/types";
import { cn } from "@/lib/utils";

const TONE: Record<BookingStatus, string> = {
  pending:
    "bg-amber-100 text-amber-800 yellow:bg-amber-200/60 yellow:text-amber-900 purple:bg-amber-900/40 purple:text-amber-200",
  confirmed:
    "bg-sky-100 text-sky-800 yellow:bg-sky-200/60 yellow:text-sky-900 purple:bg-sky-900/40 purple:text-sky-200",
  completed:
    "bg-emerald-100 text-emerald-800 yellow:bg-emerald-200/60 yellow:text-emerald-900 purple:bg-emerald-900/40 purple:text-emerald-200",
  cancelled: "bg-muted text-muted-foreground",
  no_show:
    "bg-rose-100 text-rose-800 yellow:bg-rose-200/60 yellow:text-rose-900 purple:bg-rose-900/40 purple:text-rose-200",
};

const LABEL: Record<BookingStatus, MessageKey> = {
  pending: "booking.status.pending",
  confirmed: "booking.status.confirmed",
  completed: "booking.status.completed",
  cancelled: "booking.status.cancelled",
  no_show: "booking.status.no_show",
};

/** Localized status pill for a booking. */
export function BookingStatusBadge({
  status,
  className,
}: {
  status: BookingStatus;
  className?: string;
}) {
  const { t } = useTranslation();
  return (
    <Badge variant="outline" className={cn(TONE[status], className)}>
      {t(LABEL[status])}
    </Badge>
  );
}
