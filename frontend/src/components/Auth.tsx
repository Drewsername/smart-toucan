import { LoginForm } from "@/components/login-form"
import { Button } from "@/components/ui/button"

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
      <LoginForm
        className="w-full max-w-md border-1 p-4 border-foreground/10 rounded-lg bg-foreground/5"
        onSubmit={(e) => {
          e.preventDefault()
          onSubmit(e)
        }}
      >
        <Button
          type="submit"
          className="w-full"
          disabled={status === 'pending'}
          variant="default"
        >
          {status === 'pending' ? '...' : actionText}
        </Button>
        {afterSubmit}
      </LoginForm>
    </div>
  )
}
