"use client";

import Link from "next/link";

import { DirectionToggle } from "@/components/shared/direction-toggle";
import { Button } from "@/components/ui/button";
import { useTranslation } from "@/hooks/use-translation";
import { APP_NAME, ROUTES } from "@/lib/constants";

export default function Home() {
  const { t } = useTranslation();

  return (
    <div className="flex flex-1 flex-col">
      <header className="flex items-center justify-between border-b px-6 py-4">
        <span className="text-lg font-bold">{APP_NAME}</span>
        <DirectionToggle />
      </header>

      <main className="flex flex-1 flex-col items-center justify-center gap-8 px-6 text-center">
        <div className="space-y-4">
          <h1 className="text-balance text-4xl font-bold tracking-tight sm:text-5xl">
            {t("landing.title")}
          </h1>
          <p className="mx-auto max-w-xl text-balance text-lg text-muted-foreground">
            {t("landing.subtitle")}
          </p>
        </div>

        <div className="flex flex-wrap items-center justify-center gap-3">
          <Button asChild size="lg">
            <Link href={ROUTES.login}>{t("landing.login")}</Link>
          </Button>
          <Button asChild size="lg" variant="outline">
            <Link href={ROUTES.account}>{t("landing.enterApp")}</Link>
          </Button>
        </div>
      </main>
    </div>
  );
}
