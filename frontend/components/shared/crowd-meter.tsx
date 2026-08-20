import { Badge } from "@/components/ui/badge";
import { useTranslation } from "@/hooks/use-translation";
import type { MessageKey } from "@/lib/i18n";
import type { CrowdLevel } from "@/lib/types";
import { cn } from "@/lib/utils";

const TONE: Record<CrowdLevel, string> = {
  low: "bg-emerald-100 text-emerald-800 yellow:bg-emerald-200/60 yellow:text-emerald-900 purple:bg-emerald-900/40 purple:text-emerald-200",
  medium:
    "bg-amber-100 text-amber-800 yellow:bg-amber-200/60 yellow:text-amber-900 purple:bg-amber-900/40 purple:text-amber-200",
  high: "bg-rose-100 text-rose-800 yellow:bg-rose-200/60 yellow:text-rose-900 purple:bg-rose-900/40 purple:text-rose-200",
};

const LABEL: Record<CrowdLevel, MessageKey> = {
  low: "browse.crowdLow",
  medium: "browse.crowdMedium",
  high: "browse.crowdHigh",
};

/** Crowd-level indicator (low / medium / high). */
export function CrowdMeter({
  level,
  className,
}: {
  level: CrowdLevel;
  className?: string;
}) {
  const { t } = useTranslation();
  return (
    <Badge variant="outline" className={cn(TONE[level], className)}>
      {t(LABEL[level])}
    </Badge>
  );
}
