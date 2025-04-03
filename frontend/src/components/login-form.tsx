import { Link } from "@tanstack/react-router"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { supabaseBrowserClient } from "@/utils/supabase.client"

import mascot from "@/assets/mascot/toucan-mascot-01.svg"


export function LoginForm({
  className,
  children,
  ...props
}: React.ComponentProps<"form"> & { children?: React.ReactNode }) {
  return (
    <form className={cn("flex flex-col gap-6", className)} {...props}>
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
          <Input id="email" name="email" type="email" placeholder="m@example.com" required />
        </div>
        <div className="grid gap-3">
          <div className="flex items-center">
            <Label htmlFor="password">Password</Label>
            <a
              href="#"
              className="ml-auto text-sm underline-offset-4 hover:underline"
            >
              Forgot your password?
            </a>
          </div>
          <Input id="password" name="password" type="password" required />
        </div>
        {children || (
          <Button type="submit" className="w-full">
            Login
          </Button>
        )}
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
            await supabaseBrowserClient.auth.signInWithOAuth({
              provider: 'google',
              options: {
                redirectTo: window.location.origin,
              },
            })
          }}
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
            {/* You might want to add a Google icon SVG here */}
          </svg>
          Login with Google
        </Button>
      </div>
      <div className="text-center text-sm">
        Don&apos;t have an account?{" "}
        <Link to="/signup" className="underline underline-offset-4">
          Sign up
        </Link>
      </div>
    </form>
  )
}
