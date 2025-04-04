// src/router.tsx
import { createRouter as createTanStackRouter } from '@tanstack/react-router'
import { routeTree } from './routeTree.gen'
import type { User } from '@supabase/supabase-js'

// Define the shape of the router context
export type RouterContext = {
  user: User | null
}

// Modify createRouter to accept the initial context
export function createRouter(context?: RouterContext) {
  const router = createTanStackRouter({
    routeTree,
    scrollRestoration: true,
    context, // Pass the initial context here
  })

  return router
}

declare module '@tanstack/react-router' {
  interface Register {
    router: ReturnType<typeof createRouter>
    // Register the context type for type safety
    context: RouterContext
  }
}
