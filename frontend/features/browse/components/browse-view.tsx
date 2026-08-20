"use client";

import { Home, Search } from "lucide-react";
import Link from "next/link";

import { BusinessCard } from "@/components/shared/business-card";
import { DirectionToggle } from "@/components/shared/direction-toggle";
import { IdentityBadge } from "@/components/shared/identity-badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { useTranslation } from "@/hooks/use-translation";
import { AREA_FILTERS, CATEGORY_FILTERS, ROUTES } from "@/lib/constants";

import { useBusinesses } from "../hooks/use-businesses";
import { FilterChips } from "./filter-chips";

/** The public directory: search box + filter chips + paginated grid of businesses. */
export function BrowseView() {
  const { t } = useTranslation();
  const { query, setQuery, area, setArea, category, setCategory, page, setPage, result, loading } =
    useBusinesses();

  const totalPages = result ? Math.max(1, Math.ceil(result.total / result.page_size)) : 1;

  return (
    <div className="flex flex-1 flex-col gap-6 p-6">
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-2 self-start">
          <Button variant="outline" size="sm" asChild title={t("common.home")} aria-label={t("common.home")}>
            <Link href={ROUTES.home}>
              <Home className="size-4" />
            </Link>
          </Button>
          <IdentityBadge />
          <DirectionToggle />
        </div>
      </div>

      <div>
        <h1 className="text-3xl font-extrabold tracking-tight sm:text-4xl">{t("browse.title")}</h1>
        <p className="mt-1.5 text-base text-muted-foreground">{t("browse.subtitle")}</p>
      </div>

      <div className="relative max-w-xl">
        <Search className="absolute start-3.5 top-1/2 size-5 -translate-y-1/2 text-muted-foreground" />
        <Input
          className="h-11 rounded-xl ps-11 text-base shadow-sm md:text-base"
          placeholder={t("common.searchPlaceholder")}
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setPage(1);
          }}
        />
      </div>

      <FilterChips
        areas={AREA_FILTERS}
        categories={CATEGORY_FILTERS}
        activeArea={area}
        activeCategory={category}
        onAreaChange={(value) => {
          setArea(value);
          setPage(1);
        }}
        onCategoryChange={(value) => {
          setCategory(value);
          setPage(1);
        }}
      />

      {loading && !result ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <Skeleton key={i} className="h-40 rounded-xl" />
          ))}
        </div>
      ) : result && result.items.length === 0 ? (
        <div className="flex flex-col items-center justify-center gap-2 rounded-xl border border-dashed border-primary/30 bg-card/60 px-6 py-16 text-center">
          <p className="text-lg font-semibold text-foreground">{t("browse.empty")}</p>
          <p className="text-sm text-muted-foreground">{t("browse.emptyHint")}</p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {result?.items.map((business) => (
            <BusinessCard key={business.id} business={business} />
          ))}
        </div>
      )}

      {totalPages > 1 && (
        <div className="mt-auto flex items-center justify-center gap-3 pt-2">
          <Button
            variant="outline"
            size="sm"
            disabled={page <= 1}
            onClick={() => setPage((p) => Math.max(1, p - 1))}
          >
            {t("common.back")}
          </Button>
          <span className="min-w-16 text-center text-sm font-semibold tabular-nums text-muted-foreground">
            {page} / {totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            disabled={page >= totalPages}
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
          >
            {t("common.confirm")}
          </Button>
        </div>
      )}
    </div>
  );
}
