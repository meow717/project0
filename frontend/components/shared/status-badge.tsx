import { Badge } from "@/components/ui/badge";
import { useTranslation } from "@/hooks/use-translation";
import type { MessageKey } from "@/lib/i18n";
import type { QueueEntryStatus } from "@/lib/types";
import { cn } from "@/lib/utils";

const TONE: Record<QueueEntryStatus, string> = {
  waiting:
    "bg-sky-100 text-sky-800 yellow:bg-sky-200/60 yellow:text-sky-900 purple:bg-sky-900/40 purple:text-sky-200",
  called:
    "bg-amber-100 text-amber-800 yellow:bg-amber-200/60 yellow:text-amber-900 purple:bg-amber-900/40 purple:text-amber-200",
  in_progress:
    "bg-violet-100 text-violet-800 yellow:bg-violet-200/60 yellow:text-violet-900 purple:bg-violet-900/40 purple:text-violet-200",
  served:
    "bg-emerald-100 text-emerald-800 yellow:bg-emerald-200/60 yellow:text-emerald-900 purple:bg-emerald-900/40 purple:text-emerald-200",
  no_show:
    "bg-rose-100 text-rose-800 yellow:bg-rose-200/60 yellow:text-rose-900 purple:bg-rose-900/40 purple:text-rose-200",
  cancelled: "bg-muted text-muted-foreground",
};

const LABEL: Record<QueueEntryStatus, MessageKey> = {
  waiting: "queue.waiting",
  called: "queue.called",
  in_progress: "queue.inProgress",
  served: "queue.served",
  no_show: "queue.noShow",
  cancelled: "queue.cancelled",
};

/** Localized status pill for a queue entry. */
export function StatusBadge({
  status,
  className,
}: {
  status: QueueEntryStatus;
  className?: string;
}) {
  const { t } = useTranslation();
  return (
    <Badge variant="outline" className={cn(TONE[status], className)}>
      {t(LABEL[status])}
    </Badge>
  );
}
