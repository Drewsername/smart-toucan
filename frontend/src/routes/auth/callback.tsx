import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { useEffect } from "react"
import { supabase } from "../../utils/supabase.client" // Import the browser client

// No longer need useSearch or the AuthCallbackSearch interface

// Keep the component simple
function AuthCallbackComponent() {
  const navigate = useNavigate()
  // We don't need useRouteContext here anymore

  useEffect(() => {
    // Listener for auth changes
    const { data: authListener } = supabase.auth.onAuthStateChange(
      (event, session) => {
        console.log('[AuthCallback] Auth state change:', event, !!session);
        // Once we have a session (SIGNED_IN event likely occurred server-side,
        // but this confirms client-side awareness), navigate away.
        if (session) {
          navigate({ to: "/", replace: true }); // Navigate to home/root
        }
        // Handle other events like SIGNED_OUT or USER_UPDATED if needed
      }
    );

    // Initial check in case the state is already available
    // (though the listener should catch it)
    supabase.auth.getSession().then(({ data: { session } }) => {
      console.log('[AuthCallback] Initial session check:', !!session);
      if (session) {
        navigate({ to: "/home", replace: true });
      }
    });

    // Cleanup listener on component unmount
    return () => {
      authListener?.subscription.unsubscribe();
    };
    // Run only once on mount
  }, [navigate]);

  // Render a simple loading state
  return (
    <div className="p-4 text-center">
      Finishing login...
    </div>
  )
}

export const Route = createFileRoute('/auth/callback')({
  component: AuthCallbackComponent,
  // No need for validateSearch anymore
})
