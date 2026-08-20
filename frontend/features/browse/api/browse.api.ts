import { api } from "@/lib/api-client";
import type { Business, LiveSnapshot, Page, Service } from "@/lib/types";

/** Browse (directory) endpoints — all public. */
export const browseApi = {
  list: (search = "", page = 1, area = "", category = "") =>
    api.get<Page<Business>>(
      `/businesses?search=${encodeURIComponent(search)}&area=${encodeURIComponent(area)}` +
        `&category=${encodeURIComponent(category)}&page=${page}`,
      { auth: false },
    ),
  get: (slug: string) => api.get<Business>(`/businesses/${slug}`, { auth: false }),
  getLive: (slug: string) =>
    api.get<LiveSnapshot>(`/businesses/${slug}/live`, { auth: false }),
  servicesOf: (slug: string) =>
    api.get<Service[]>(`/businesses/${slug}/services`, { auth: false }),
};
