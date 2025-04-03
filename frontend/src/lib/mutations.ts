import { createBrowserClient } from "@supabase/ssr";

const supabase = createBrowserClient(
  import.meta.env.VITE_SUPABASE_URL!,
  import.meta.env.VITE_SUPABASE_ANON_KEY!
);

type Session = {
  access_token: string;
};

async function authedPOST<T = any>(
  url: string,
  session: Session,
  body?: any
): Promise<T> {
  const res = await fetch(url, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${session.access_token}`,
      "Content-Type": "application/json",
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err?.message || "Request failed");
  }

  return res.json();
}

async function authedPATCH<T = any>(
  url: string,
  session: Session,
  body: any
): Promise<T> {
  const res = await fetch(url, {
    method: "PATCH",
    headers: {
      Authorization: `Bearer ${session.access_token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err?.message || "Request failed");
  }

  return res.json();
}

export async function redeemReward(rewardId: string, session: Session) {
  return authedPOST(`/api/rewards/${rewardId}/redeem`, session);
}

export async function createReward(input: any, session: Session) {
  return authedPOST("/api/rewards/", session, input);
}

export async function updateReward(rewardId: string, input: any, session: Session) {
  return authedPATCH(`/api/rewards/${rewardId}`, session, input);
}

export async function createTask(input: any, session: Session) {
  return authedPOST("/api/tasks/", session, input);
}

export async function completeTask(taskId: string, session: Session) {
  return authedPOST(`/api/tasks/${taskId}/recipient/complete`, session);
}

export async function bidOnTask(taskId: string, bid: number, session: Session) {
  return authedPOST(`/api/tasks/${taskId}/recipient/bid?bid=${bid}`, session);
}
