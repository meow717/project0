"use client";

import Link from "next/link";

import { AnimatedHeading } from "@/components/shared/animated-heading";
import { DirectionToggle } from "@/components/shared/direction-toggle";
import { Button } from "@/components/ui/button";
import { useTranslation } from "@/hooks/use-translation";
import { ROUTES } from "@/lib/constants";

export default function Home() {
  const { t } = useTranslation();

  return (
    <div className="relative flex flex-1 flex-col">
      <header className="absolute top-4 end-4 z-10">
        <DirectionToggle />
      </header>

      <main className="flex flex-1 flex-col items-center justify-center gap-10 px-6 text-center">
        <div className="space-y-4">
          <AnimatedHeading
            text={t("landing.title")}
            className="text-balance text-6xl font-bold tracking-tight sm:text-7xl"
          />
          <p className="text-balance text-2xl font-medium text-muted-foreground sm:text-3xl">
            {t("landing.subtitle")}
          </p>
        </div>

        <div className="flex flex-wrap items-center justify-center gap-4">
          <Button asChild size="lg" variant="outline">
            <Link href={ROUTES.businesses}>{t("landing.browse")}</Link>
          </Button>
          <Button asChild size="lg">
            <Link href={ROUTES.login}>{t("landing.login")}</Link>
          </Button>
        </div>
      </main>
    </div>
  );
}
