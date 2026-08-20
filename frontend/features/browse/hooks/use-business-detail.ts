"use client";

import { useEffect, useState } from "react";

import { browseApi } from "../api/browse.api";
import type { Business, Service } from "@/lib/types";

/** Fetches a business + its active services (public). */
export function useBusinessDetail(slug: string) {
  const [business, setBusiness] = useState<Business | null>(null);
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<unknown>(null);

  useEffect(() => {
    if (!slug) return;
    let cancelled = false;
    Promise.all([browseApi.get(slug), browseApi.servicesOf(slug)])
      .then(([biz, svcs]) => {
        if (cancelled) return;
        setBusiness(biz);
        setServices(svcs);
      })
      .catch((err) => {
        if (!cancelled) setError(err);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [slug]);

  return { business, services, loading, error };
}
