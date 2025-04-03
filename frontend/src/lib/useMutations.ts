import { useCallback } from "react";
import { toast } from "sonner";
import { createBrowserClient } from "@supabase/ssr";
import * as mutations from "@/lib/mutations";

const supabase = createBrowserClient(
  import.meta.env.VITE_SUPABASE_URL!,
  import.meta.env.VITE_SUPABASE_ANON_KEY!
);

export function useMutations() {
  const wrap = useCallback(
    (fn: Function) =>
      async (...args: any[]) => {
        const {
          data: { session },
        } = await supabase.auth.getSession();
        if (!session) {
          toast.error("You must be logged in.");
          return;
        }

        try {
          return await fn(...args, session);
        } catch (err: any) {
          const msg = err?.message || "Something went wrong";
          toast.error(msg);
          throw err;
        }
      },
    []
  );

  return {
    redeemReward: wrap(mutations.redeemReward),
    createReward: wrap(mutations.createReward),
    updateReward: wrap(mutations.updateReward),
    createTask: wrap(mutations.createTask),
    completeTask: wrap(mutations.completeTask),
    bidOnTask: wrap(mutations.bidOnTask),
  };
}
