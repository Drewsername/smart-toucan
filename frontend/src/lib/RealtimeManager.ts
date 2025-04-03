import { createBrowserClient } from "@supabase/ssr";

const supabase = createBrowserClient(
  import.meta.env.VITE_SUPABASE_URL!,
  import.meta.env.VITE_SUPABASE_ANON_KEY!
);

type FilterKey = "creatorId" | "recipientId" | "userId";
type Callback = (payload: any) => void;

export class RealtimeManager {
  private subscriptions: any[] = [];

  constructor(private userId: string, private partnerId?: string) {}

  subscribeToTable(table: string, keys: FilterKey[], callback: Callback) {
    const ids = [this.userId];
    if (this.partnerId) ids.push(this.partnerId);

    for (const key of keys) {
      for (const id of ids) {
        const channelName = `realtime:${table}:${key}:${id}`;

        const channel = supabase
          .channel(channelName)
          .on(
            "postgres_changes",
            {
              event: "*",
              schema: "public",
              table,
              filter: `${key}=eq.${id}`,
            },
            callback
          )
          .subscribe();

        this.subscriptions.push(channel);
      }
    }
  }

  unsubscribeAll() {
    for (const channel of this.subscriptions) {
      supabase.removeChannel(channel);
    }
    this.subscriptions = [];
  }
}
