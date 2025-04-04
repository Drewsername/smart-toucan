// src/components/Login.tsx (or wherever you define Login)

import { useRouter, Link } from '@tanstack/react-router';
import { useServerFn } from '@tanstack/react-start';
import { useMutation } from '../hooks/useMutation'; // Adjust path if needed
import { loginFn } from '../routes/_authed'; // Adjust path if needed
import { signupFn } from '../routes/signup'; // Adjust path if needed
import { cn } from "@/lib/utils"; // Adjust path if needed
import { Button } from "@/components/ui/button"; // Adjust path if needed
import { Input } from "@/components/ui/input"; // Adjust path if needed
import { Label } from "@/components/ui/label"; // Adjust path if needed
import { supabase } from '@/utils/supabase.client'; // Import browser client
import mascot from "@/assets/mascot/toucan-mascot-01.svg"; // Adjust path if needed
import React, { useState } from 'react'; // Import React and useState

export function Login() {
  const router = useRouter();
  const [errorMessage, setErrorMessage] = useState<string | null>(null); // Use local state for error display

  // --- Logic from Example Login.tsx ---
  const loginMutation = useMutation({
    fn: loginFn,
    onSuccess: async (ctx) => {
      setErrorMessage(null); // Clear error on new attempt success/processing
      // Check if ctx.data exists and then if error exists within it
      if (ctx.data && !ctx.data.error) {
        await router.invalidate(); // Refresh data potentially affected by login
        router.navigate({ to: '/' }); // Navigate to home on success
      } else if (ctx.data?.message) {
         // If loginFn returned an error object, display its message
         setErrorMessage(ctx.data.message);
      }
    },
    onError: (error) => {
       // Handle errors thrown by useMutation or network issues
       console.error("Login mutation failed:", error);
       setErrorMessage(error.message || 'Login failed due to an unexpected error.');
    },
  });

  // Signup mutation (ensure signupFn exists and path is correct)
  const signupMutation = useMutation({
    fn: useServerFn(signupFn),
    // Add onSuccess/onError for signup if needed
  });
  // --- End Logic ---

  // --- UI Structure from LoginForm.tsx ---
  return (
    // Decide if you need the outer fixed div from Auth.tsx here
    // <div className="fixed inset-0 bg-background text-foreground flex items-center justify-center p-8">
       <form
         className={cn("flex flex-col gap-6 w-full max-w-md border-1 p-4 border-foreground/10 rounded-lg bg-foreground/5")} // Adjust styling classes as needed
         onSubmit={(e) => {
           e.preventDefault();
           setErrorMessage(null); // Clear previous errors on submit
           const formData = new FormData(e.target as HTMLFormElement);
           loginMutation.mutate({
             data: {
               email: formData.get('email') as string,
               password: formData.get('password') as string,
             },
           });
         }}
       >
         {/* --- UI Copied from LoginForm.tsx --- */}
         <div className = "flex flex-row w-full justify-between items-center">
            <div className="flex flex-col items-center gap-2 text-center">
                <img src={mascot} alt="Mascot" className="w-32 h-32" />
            </div>
            <div className="flex flex-col items-center gap-2 text-center w-full">
              <h1 className="text-2xl font-bold">Welcome Back!</h1>
              <p className="text-muted-foreground text-sm text-balance">
                It's disappointing you were ever away.
              </p>
            </div>
          </div>

          <div className="grid gap-6">
            <div className="grid gap-3">
              <Label htmlFor="email">Email</Label>
              <Input id="email" name="email" type="email" placeholder="m@example.com" required disabled={loginMutation.status === 'pending'} />
            </div>
            <div className="grid gap-3">
              <div className="flex items-center">
                <Label htmlFor="password">Password</Label>
                <a
                  href="#" // TODO: Implement password reset flow
                  className="ml-auto text-sm underline-offset-4 hover:underline"
                >
                  Forgot your password?
                </a>
              </div>
              <Input id="password" name="password" type="password" required disabled={loginMutation.status === 'pending'} />
            </div>

            {/* Submit Button */}
            <Button
               type="submit"
               className="w-full"
               disabled={loginMutation.status === 'pending'}
             >
               {loginMutation.status === 'pending' ? 'Logging in...' : 'Login'}
             </Button>

            {/* Display Error Messages */}
            {errorMessage && (
               <div className="text-center text-sm text-red-500">{errorMessage}</div>
            )}

            {/* Conditionally show Signup Button */}
            {errorMessage === 'Invalid login credentials' && (
              <div className="text-center">
                 <Button
                   onClick={(e) => {
                     const formData = new FormData(
                       (e.target as HTMLButtonElement).form!,
                     );
                     signupMutation.mutate({
                       data: {
                         email: formData.get('email') as string,
                         password: formData.get('password') as string,
                       },
                     });
                   }}
                   type="button"
                   variant="secondary"
                   disabled={signupMutation.status === 'pending'}
                 >
                   {signupMutation.status === 'pending' ? 'Signing up...' : 'Sign up instead?'}
                 </Button>
               </div>
             )}
             {/* End Conditional Signup */}

            {/* OAuth Section */}
            <div className="after:border-border relative text-center text-sm after:absolute after:inset-0 after:top-1/2 after:z-0 after:flex after:items-center after:border-t">
              <span className=" text-muted-foreground relative z-10 px-2">
                Or continue with
              </span>
            </div>
            <Button
              variant="outline"
              className="w-full"
              type="button"
              onClick={async () => {
                // Use Browser client for OAuth
                const { error: oauthError } = await supabase.auth.signInWithOAuth({
                  provider: 'google',
                  options: {
                    // Ensure this matches your Supabase settings and handles the callback
                    redirectTo: window.location.origin + '/auth/callback',
                  },
                });
                if (oauthError) {
                   console.error("OAuth Error:", oauthError);
                   setErrorMessage(`OAuth Error: ${oauthError.message}`);
                }
              }}
            >
              <svg className="mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                   <path fill="currentColor" d="M21.35,11.1H12.18V13.83H18.69C18.36,17.64 15.19,19.27 12.19,19.27C8.36,19.27 5,16.25 5,12C5,7.9 8.2,4.73 12.19,4.73C15.29,4.73 17.1,6.7 17.1,6.7L19,4.72C19,4.72 16.56,2 12.19,2C6.42,2 2.03,6.8 2.03,12C2.03,17.05 6.16,22 12.19,22C17.6,22 21.5,18.33 21.5,12.91C21.5,11.76 21.35,11.1 21.35,11.1V11.1Z" />
               </svg>
              Login with Google
            </Button>
          </div>
          {/* --- End UI From LoginForm.tsx --- */}

          <div className="text-center text-sm">
            Don&apos;t have an account?{" "}
            <Link to="/signup" className="underline underline-offset-4">
              Sign up
            </Link>
          </div>
       </form>
    // </div> // End outer wrapper if you added one
  );
}