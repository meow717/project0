import { Button } from "@/components/ui/button";
import { useTranslation } from "@/hooks/use-translation";
import { cn } from "@/lib/utils";

/**
 * Horizontal filter chips for the directory: one row of areas, one of
 * categories. The "الكل" (All) option is represented by an empty string
 * and clears the filter.
 */
export function FilterChips({
  areas,
  categories,
  activeArea,
  activeCategory,
  onAreaChange,
  onCategoryChange,
}: {
  areas: readonly string[];
  categories: readonly string[];
  activeArea: string;
  activeCategory: string;
  onAreaChange: (value: string) => void;
  onCategoryChange: (value: string) => void;
}) {
  const { t } = useTranslation();

  return (
    <div className="flex flex-col gap-2.5">
      <div className="flex flex-wrap items-center gap-2">
        <span className="me-1 text-sm font-semibold uppercase tracking-wide text-muted-foreground">
          {t("browse.filterAreas")}
        </span>
        {areas.map((value) => {
          const active = (value === "الكل" && activeArea === "") || value === activeArea;
          return (
            <FilterChip
              key={value}
              label={value}
              active={active}
              onClick={() => onAreaChange(value === "الكل" ? "" : value)}
            />
          );
        })}
      </div>
      <div className="flex flex-wrap items-center gap-2">
        <span className="me-1 text-sm font-semibold uppercase tracking-wide text-muted-foreground">
          {t("browse.filterCategories")}
        </span>
        {categories.map((value) => {
          const active = (value === "الكل" && activeCategory === "") || value === activeCategory;
          return (
            <FilterChip
              key={value}
              label={value}
              active={active}
              onClick={() => onCategoryChange(value === "الكل" ? "" : value)}
            />
          );
        })}
      </div>
    </div>
  );
}

function FilterChip({
  label,
  active,
  onClick,
}: {
  label: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <Button
      type="button"
      size="sm"
      variant={active ? "default" : "outline"}
      onClick={onClick}
      aria-pressed={active}
      className={cn(
        "h-8 min-w-10 rounded-full px-3.5 text-sm font-semibold shadow-sm transition-all",
        active &&
          "bg-yellow-400 text-yellow-950 shadow-md shadow-yellow-400/30 hover:bg-yellow-300 purple:bg-yellow-300 purple:text-yellow-950 purple:hover:bg-yellow-200",
      )}
    >
      {label}
    </Button>
  );
}
