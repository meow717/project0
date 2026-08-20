import { Badge } from "@/components/ui/badge";
import { useTranslation } from "@/hooks/use-translation";
import { cn } from "@/lib/utils";

/** Colored pill showing an estimated wait in minutes. */
export function WaitBadge({
  minutes,
  className,
}: {
  minutes: number;
  className?: string;
}) {
  const { t } = useTranslation();
  const tone =
    minutes <= 5
      ? "bg-emerald-100 text-emerald-800 yellow:bg-emerald-200/60 yellow:text-emerald-900 purple:bg-emerald-900/40 purple:text-emerald-200"
      : minutes <= 20
        ? "bg-amber-100 text-amber-800 yellow:bg-amber-200/60 yellow:text-amber-900 purple:bg-amber-900/40 purple:text-amber-200"
        : "bg-rose-100 text-rose-800 yellow:bg-rose-200/60 yellow:text-rose-900 purple:bg-rose-900/40 purple:text-rose-200";

  return (
    <Badge variant="outline" className={cn(tone, className)}>
      {minutes} {t("queue.minutes")}
    </Badge>
  );
}
