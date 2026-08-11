"use client";

import { IdentificationCard } from "@phosphor-icons/react";

import { AnimatedHeading } from "@/components/shared/animated-heading";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useAuth } from "@/features/auth";
import { useTranslation } from "@/hooks/use-translation";

function Row({ label, value, dir }: { label: string; value: string; dir?: "ltr" | "rtl" }) {
  return (
    <div className="flex items-center justify-between gap-4 border-b py-2 last:border-b-0">
      <span className="text-muted-foreground">{label}</span>
      <span className="font-medium" dir={dir}>
        {value}
      </span>
    </div>
  );
}

/** Post-login screen: a simple message describing the signed-in account. */
export function AccountView() {
  const { user } = useAuth();
  const { t } = useTranslation();

  const isAdmin = !!user?.is_staff;
  const role = isAdmin ? t("account.roleAdmin") : t("account.roleUser");
  const summary = isAdmin ? t("account.summaryAdmin") : t("account.summaryUser");

  return (
    <div className="flex flex-1 flex-col gap-6 p-6">
      <AnimatedHeading
        text={`${t("auth.welcome")} ${user?.full_name || user?.email || ""}`}
        className="text-2xl font-bold sm:text-3xl"
      />

      <Card className="max-w-lg">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <IdentificationCard size={22} weight="duotone" />
            {t("account.thisAccount")}
          </CardTitle>
          <CardDescription>{summary}</CardDescription>
        </CardHeader>
        <CardContent className="text-sm">
          <Row label={t("account.name")} value={user?.full_name || "—"} />
          <Row label={t("account.email")} value={user?.email || "—"} dir="ltr" />
          <Row label={t("account.role")} value={role} />
          <Row
            label={t("account.status")}
            value={user?.is_active ? t("account.active") : t("account.inactive")}
          />
        </CardContent>
      </Card>
    </div>
  );
}
