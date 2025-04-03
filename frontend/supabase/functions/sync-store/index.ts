import { serve } from "https://deno.land/std/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

serve(async (req) => {
    if (req.method === "OPTIONS") {
        return new Response("ok", {
          headers: {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
          },
        });
      }
      
  const supabase = createClient(
    Deno.env.get("SUPABASE_URL")!,
    Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
    {
      global: {
        headers: { Authorization: req.headers.get("Authorization")! },
      },
    }
  );

  const {
    data: { user },
    error: userError,
  } = await supabase.auth.getUser();

  if (userError || !user) {
    return new Response("Unauthorized", {
      status: 401,
      headers: { "Access-Control-Allow-Origin": "*" },
    });
  }
  console.log("User ID:", user.id);

  const { data: profile, error: profileError } = await supabase
    .from("Profile")
    .select("*")
    .eq("id", user.id)
    .single();

  if (profileError || !profile) {
    return new Response("Profile not found", {
      status: 404,
      headers: { "Access-Control-Allow-Origin": "*" },
    });
  }

  const userId = profile.id;
  const partnerId = profile.partnerId;

  const [partnerProfile, rewards, tasks, redemptions, notifications] = await Promise.all([
    partnerId
      ? supabase.from("Profile").select("*").eq("id", partnerId).single().then((r) => r.data)
      : Promise.resolve(null),

    supabase
      .from("Reward")
      .select("*")
      .or(
        `creatorId.eq.${userId},recipientId.eq.${userId}${
          partnerId ? `,creatorId.eq.${partnerId},recipientId.eq.${partnerId}` : ""
        }`
      )
      .then((r) => r.data ?? []),

    supabase
      .from("Task")
      .select("*")
      .or(
        `creatorId.eq.${userId},recipientId.eq.${userId}${
          partnerId ? `,creatorId.eq.${partnerId},recipientId.eq.${partnerId}` : ""
        }`
      )
      .then((r) => r.data ?? []),

    supabase
      .from("Redemption")
      .select("*")
      .or(`userId.eq.${userId}${partnerId ? `,userId.eq.${partnerId}` : ""}`)
      .then((r) => r.data ?? []),

    supabase
      .from("Notification")
      .select("*")
      .eq("userId", userId)
      .then((r) => r.data ?? []),
  ]);

  return new Response(
    JSON.stringify({
      profile,
      partnerProfile,
      rewards,
      tasks,
      redemptions,
      notifications,
    }),
    {
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*", // ← key line
      },
    }
  );
});
