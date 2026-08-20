"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/features/auth";
import { useTranslation } from "@/hooks/use-translation";
import { ApiError } from "@/lib/api-client";
import { ROUTES } from "@/lib/constants";

import { dashboardApi } from "../api/dashboard.api";

/**
 * Create-a-business form for authenticated users. On success the owner is
 * promoted to staff server-side; we refresh the session so the new role /
 * business_id claims take effect immediately.
 */
export function BusinessCreateForm() {
  const { t } = useTranslation();
  const router = useRouter();
  const { refreshSession } = useAuth();
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    name: "",
    slug: "",
    description: "",
    area: "",
    category: "",
    address: "",
    phone: "",
    timezone: "Asia/Riyadh",
    opens_at: "09:00",
    closes_at: "17:00",
  });

  const patch = (field: keyof typeof form, value: string) =>
    setForm((prev) => ({ ...prev, [field]: value }));

  const submit = async () => {
    if (!form.name.trim() || !form.slug.trim()) {
      toast.error(t("common.error"));
      return;
    }
    setLoading(true);
    try {
      await dashboardApi.createBusiness(form);
      // Server promotes the creator to staff — refresh claims before routing.
      await refreshSession();
      toast.success(t("dashboard.businessCreated"));
      router.push(ROUTES.dashboard);
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("common.error"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="max-w-xl">
      <CardHeader>
        <CardTitle className="text-base">{t("dashboard.createBusiness")}</CardTitle>
        <CardDescription>{t("dashboard.settings")}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="space-y-1.5">
          <Label>{t("dashboard.businessName")}</Label>
          <Input value={form.name} onChange={(e) => patch("name", e.target.value)} />
        </div>
        <div className="space-y-1.5">
          <Label>{t("dashboard.businessSlug")}</Label>
          <Input
            dir="ltr"
            placeholder="my-clinic"
            value={form.slug}
            onChange={(e) => patch("slug", e.target.value)}
          />
        </div>
        <div className="space-y-1.5">
          <Label>{t("dashboard.businessDescription")}</Label>
          <Input
            value={form.description}
            onChange={(e) => patch("description", e.target.value)}
          />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-1.5">
            <Label>{t("dashboard.businessArea")}</Label>
            <Input value={form.area} onChange={(e) => patch("area", e.target.value)} />
          </div>
          <div className="space-y-1.5">
            <Label>{t("dashboard.businessCategory")}</Label>
            <Input value={form.category} onChange={(e) => patch("category", e.target.value)} />
          </div>
        </div>
        <div className="space-y-1.5">
          <Label>{t("dashboard.businessAddress")}</Label>
          <Input value={form.address} onChange={(e) => patch("address", e.target.value)} />
        </div>
        <div className="space-y-1.5">
          <Label>{t("dashboard.businessPhone")}</Label>
          <Input
            dir="ltr"
            value={form.phone}
            onChange={(e) => patch("phone", e.target.value)}
          />
        </div>
        <div className="space-y-1.5">
          <Label>{t("dashboard.businessTimezone")}</Label>
          <Input
            dir="ltr"
            value={form.timezone}
            onChange={(e) => patch("timezone", e.target.value)}
          />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-1.5">
            <Label>{t("dashboard.opensAt")}</Label>
            <Input
              type="time"
              value={form.opens_at}
              onChange={(e) => patch("opens_at", e.target.value)}
            />
          </div>
          <div className="space-y-1.5">
            <Label>{t("dashboard.closesAt")}</Label>
            <Input
              type="time"
              value={form.closes_at}
              onChange={(e) => patch("closes_at", e.target.value)}
            />
          </div>
        </div>
        <Button onClick={submit} disabled={loading}>
          {loading ? t("common.loading") : t("dashboard.createBusiness")}
        </Button>
      </CardContent>
    </Card>
  );
}
