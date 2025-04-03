// src/hooks/createAutoMutation.ts
import { useMutation } from "./useMutation";
import { toast } from "sonner";
import { createBrowserClient } from "@supabase/ssr";

const supabase = createBrowserClient(
  import.meta.env.VITE_SUPABASE_URL!,
  import.meta.env.VITE_SUPABASE_ANON_KEY!
);

export function createAutoMutation<TVariables, TData>(
  apiFn: (vars: TVariables, session: any) => Promise<TData>,
  successMessage?: string
) {
  return useMutation<TVariables, TData>({
    fn: async (vars: TVariables) => {
      const {
        data: { session },
      } = await supabase.auth.getSession();
      if (!session) throw new Error("Not authenticated");
      return apiFn(vars, session);
    },
    onSuccess: () => {
      if (successMessage) toast.success(successMessage);
    },
  });
}
