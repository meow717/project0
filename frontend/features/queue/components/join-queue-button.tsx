"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { useTranslation } from "@/hooks/use-translation";
import { ApiError } from "@/lib/api-client";
import { ROUTES } from "@/lib/constants";
import { useQueueStore } from "@/stores/queue.store";

import { queueApi } from "../api/queue.api";

/**
 * "Join queue" button. Only renders for signed-in customers; joins the queue
 * and stores the active entry so the ticket page can show it.
 */
export function JoinQueueButton({ serviceId }: { serviceId: number }) {
  const { t } = useTranslation();
  const router = useRouter();
  const setActiveEntry = useQueueStore((s) => s.setActiveEntry);
  const [loading, setLoading] = useState(false);

  const join = async () => {
    setLoading(true);
    try {
      const entry = await queueApi.join(serviceId);
      setActiveEntry(entry);
      toast.success(t("queue.joinedMsg"));
      router.push(ROUTES.ticket);
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("queue.alreadyJoined"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Button size="sm" onClick={join} disabled={loading}>
      {loading ? t("common.loading") : t("queue.join")}
    </Button>
  );
}
