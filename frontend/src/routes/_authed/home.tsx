import { useSupabaseStore } from "@/stores/useSupabaseStore";
import { createFileRoute } from "@tanstack/react-router";
import { redeemReward, completeTask } from "@/lib/mutations";
import { createAutoMutation } from "@/hooks/createAutoMutation";
import { useEffect, useState } from "react";

function HomeRoute() {
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  const { store, loading } = useSupabaseStore();
  const redeem = createAutoMutation(redeemReward, "Reward redeemed!");
  const complete = createAutoMutation(completeTask, "Task completed!");

  if (!isClient) return null;
  if (loading) return <p>Loading store...</p>;
  if (!store?.profile) return <p>No profile found.</p>;

  const handleRedeem = () => {
    const reward = store.rewards?.[0];
    if (reward?.id) redeem.mutate(reward.id);
  };

  const handleComplete = () => {
    const task = store.tasks?.[0];
    if (task?.id) complete.mutate(task.id);
  };

  return (
    <main>
      <h1>Debug Home</h1>
      <p>Logged in as: {store.profile.email}</p>
      <p>Partner: {store.partnerProfile?.email ?? "None"}</p>

      <h3>Tasks</h3>
      <ul>
        {store.tasks.map((t: any) => (
          <li key={t.id}>
            {t.title} — {t.status}
          </li>
        ))}
      </ul>

      <h3>Rewards</h3>
      <ul>
        {store.rewards.map((r: any) => (
          <li key={r.id}>
            {r.title} — {r.points} pts
          </li>
        ))}
      </ul>

      <button onClick={handleRedeem}>Redeem first reward</button>
      <button onClick={handleComplete}>Complete first task</button>
    </main>
  );
}

export const Route = createFileRoute("/_authed/home")({
  component: HomeRoute,
});
