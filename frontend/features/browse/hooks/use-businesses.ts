"use client";

import { useEffect, useState } from "react";

import { ApiError } from "@/lib/api-client";
import { DEBOUNCE_MS } from "@/lib/constants";
import type { Business, Page } from "@/lib/types";
import { useQueueStore } from "@/stores/queue.store";

import { browseApi } from "../api/browse.api";

/**
 * Directory browsing state: debounced search + area/category filters +
 * pagination, plus live waiting snapshots for the visible page of businesses.
 */
export function useBusinesses() {
  const [query, setQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [area, setArea] = useState("");
  const [category, setCategory] = useState("");
  const [page, setPage] = useState(1);
  const [result, setResult] = useState<Page<Business> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const setSnapshot = useQueueStore((s) => s.setSnapshot);

  // Debounce the search input so we don't hit the API on every keystroke.
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedQuery(query), DEBOUNCE_MS);
    return () => clearTimeout(timer);
  }, [query]);

  useEffect(() => {
    let cancelled = false;
    browseApi
      .list(debouncedQuery, page, area, category)
      .then((data) => {
        if (!cancelled) setResult(data);
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof ApiError ? err.message : "error");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [debouncedQuery, area, category, page]);

  // Fetch live snapshots for the visible businesses into the shared store.
  useEffect(() => {
    if (!result || result.items.length === 0) return;
    let cancelled = false;
    result.items.forEach((business) => {
      browseApi
        .getLive(business.slug)
        .then((snapshot) => {
          if (!cancelled) setSnapshot(snapshot);
        })
        .catch(() => {
          // transient — card falls back to no waiting data
        });
    });
    return () => {
      cancelled = true;
    };
  }, [result, setSnapshot]);

  return { query, setQuery, area, setArea, category, setCategory, page, setPage, result, loading, error };
}
