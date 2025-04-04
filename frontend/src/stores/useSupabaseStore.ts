import { useEffect, useState, useCallback, useRef } from "react";
import { supabase } from "../utils/supabase.client";
import { RealtimeManager } from "@/lib/RealtimeManager";


const EDGE_FUNCTION_URL = `https://${import.meta.env.VITE_SUPABASE_PROJECT_REF}.supabase.co/functions/v1`;

export function useSupabaseStore() {
  const [store, setStore] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const managerRef = useRef<RealtimeManager | null>(null);

  const fetchInitialData = useCallback(async () => {
    const {
      data: { session },
    } = await supabase.auth.getSession();

    if (!session) {
      setLoading(false);
      return;
    }

    const res = await fetch(`${EDGE_FUNCTION_URL}/sync-store`, {
      headers: {
        Authorization: `Bearer ${session.access_token}`,
      },
    });

    if (!res.ok) {
      console.error("Failed to fetch sync-store:", await res.text());
      setLoading(false);
      return;
    }

    const data = await res.json();
    setStore(data);
    setLoading(false);
  }, []);

  useEffect(() => {
    fetchInitialData();
  }, [fetchInitialData]);

  useEffect(() => {
    if (!store?.profile?.id) return;

    const userId = store.profile.id;
    const partnerId = store.partnerProfile?.id;

    const manager = new RealtimeManager(userId, partnerId);
    managerRef.current = manager;

    const updateStore = (table: string) => (payload: any) => {
      setStore((prev: any) => {
        if (!prev) return prev;
        const updated = [...(prev[table] ?? [])];

        switch (payload.eventType) {
          case "INSERT":
            updated.push(payload.new);
            break;
          case "UPDATE":
            return {
              ...prev,
              [table]: updated.map((r) =>
                r.id === payload.new.id ? payload.new : r
              ),
            };
          case "DELETE":
            return {
              ...prev,
              [table]: updated.filter((r) => r.id !== payload.old.id),
            };
        }

        return { ...prev, [table]: updated };
      });
    };

    manager.subscribeToTable("tasks", ["creatorId", "recipientId"], updateStore("tasks"));
    manager.subscribeToTable("rewards", ["creatorId", "recipientId"], updateStore("rewards"));
    manager.subscribeToTable("notifications", ["userId"], updateStore("notifications"));
    manager.subscribeToTable("redemptions", ["userId"], updateStore("redemptions"));

    return () => {
      managerRef.current?.unsubscribeAll();
    };
  }, [store?.profile?.id, store?.partnerProfile?.id]);

  return { store, loading };
}
