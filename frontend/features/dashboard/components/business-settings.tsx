"use client";

import { useEffect, useRef, useState } from "react";
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
import { useTranslation } from "@/hooks/use-translation";
import { ApiError } from "@/lib/api-client";
import type { Business } from "@/lib/types";

import { dashboardApi } from "../api/dashboard.api";

/** Business settings: edit name/description/address/phone/hours + logo. */
export function BusinessSettings() {
  const { t } = useTranslation();
  const [business, setBusiness] = useState<Business | null>(null);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    dashboardApi
      .getBusiness()
      .then(setBusiness)
      .catch(() => {});
  }, []);

  if (!business) return null;

  const patch = (field: keyof Business, value: string) =>
    setBusiness((prev) => (prev ? { ...prev, [field]: value } : prev));

  const save = async () => {
    setSaving(true);
    try {
      const updated = await dashboardApi.updateBusiness({
        name: business.name,
        description: business.description,
        area: business.area,
        category: business.category,
        address: business.address,
        phone: business.phone,
        timezone: business.timezone,
        opens_at: business.opens_at,
        closes_at: business.closes_at,
      });
      setBusiness(updated);
      toast.success(t("dashboard.updated"));
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("common.error"));
    } finally {
      setSaving(false);
    }
  };

  const onLogoChange = async (file: File | undefined) => {
    if (!file) return;
    setUploading(true);
    try {
      const { logo_url } = await dashboardApi.uploadLogo(business.id, file);
      setBusiness((prev) => (prev ? { ...prev, logo_url } : prev));
      toast.success(t("dashboard.logoUploaded"));
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("dashboard.logoUploadFailed"));
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  return (
    <Card className="max-w-xl">
      <CardHeader>
        <CardTitle className="text-base">{t("dashboard.settings")}</CardTitle>
        <CardDescription>{business.name}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex items-center gap-4">
          {business.logo_url ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={business.logo_url} alt="" className="size-14 rounded-md object-cover" />
          ) : null}
          <div className="space-y-1.5">
            <Label>{t("dashboard.logo")}</Label>
            <Input
              ref={fileRef}
              type="file"
              accept="image/*"
              disabled={uploading}
              onChange={(e) => onLogoChange(e.target.files?.[0])}
            />
          </div>
        </div>
        <div className="space-y-1.5">
          <Label>{t("dashboard.businessName")}</Label>
          <Input value={business.name} onChange={(e) => patch("name", e.target.value)} />
        </div>
        <div className="space-y-1.5">
          <Label>{t("dashboard.businessDescription")}</Label>
          <Input
            value={business.description}
            onChange={(e) => patch("description", e.target.value)}
          />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-1.5">
            <Label>{t("dashboard.businessArea")}</Label>
            <Input value={business.area} onChange={(e) => patch("area", e.target.value)} />
          </div>
          <div className="space-y-1.5">
            <Label>{t("dashboard.businessCategory")}</Label>
            <Input
              value={business.category}
              onChange={(e) => patch("category", e.target.value)}
            />
          </div>
        </div>
        <div className="space-y-1.5">
          <Label>{t("dashboard.businessAddress")}</Label>
          <Input value={business.address} onChange={(e) => patch("address", e.target.value)} />
        </div>
        <div className="space-y-1.5">
          <Label>{t("dashboard.businessPhone")}</Label>
          <Input
            dir="ltr"
            value={business.phone}
            onChange={(e) => patch("phone", e.target.value)}
          />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-1.5">
            <Label>{t("dashboard.opensAt")}</Label>
            <Input
              type="time"
              value={business.opens_at.slice(0, 5)}
              onChange={(e) => patch("opens_at", e.target.value)}
            />
          </div>
          <div className="space-y-1.5">
            <Label>{t("dashboard.closesAt")}</Label>
            <Input
              type="time"
              value={business.closes_at.slice(0, 5)}
              onChange={(e) => patch("closes_at", e.target.value)}
            />
          </div>
        </div>
        <Button onClick={save} disabled={saving}>
          {saving ? t("common.loading") : t("common.save")}
        </Button>
      </CardContent>
    </Card>
  );
}
