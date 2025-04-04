import { Button } from "@/components/ui/button"
import { Login } from "./Login"

export function Auth({
  actionText,
  onSubmit,
  status,
  afterSubmit,
}: {
  actionText: string
  onSubmit: (e: React.FormEvent<HTMLFormElement>) => void
  status: 'pending' | 'idle' | 'success' | 'error'
  afterSubmit?: React.ReactNode
}) {
  return (
    <div className="fixed inset-0 bg-background text-foreground flex items-center justify-center p-8">
      <Login/>
    </div>
  )
}
