import {
  HeadContent,
  Link,
  Outlet,
  Scripts,
  createRootRoute,
} from '@tanstack/react-router'
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools'
import { createServerFn } from '@tanstack/react-start'
import appCss from "../styles/app.css?url"
import * as React from 'react'
import { DefaultCatchBoundary } from '../components/DefaultCatchBoundary'
import { NotFound } from '../components/NotFound'
import { seo } from '../utils/seo'
import { getSupabaseServerClient } from '../utils/supabase.server'

const fetchUser = createServerFn({ method: 'GET' }).handler(async () => {
  try { // Add try...catch for safety
    const supabase = await getSupabaseServerClient()
    console.log('[fetchUser handler] Calling supabase.auth.getUser()');
    const { data, error } = await supabase.auth.getUser(); // Capture both data and error
    // Log the full raw response from Supabase
    console.log('[fetchUser handler] supabase.auth.getUser() raw response:', JSON.stringify({ data, error }, null, 2));

    if (error) {
      console.error('[fetchUser handler] Error explicitly returned by supabase.auth.getUser():', error);
      return null;
    }
    if (!data?.user) {
      console.warn('[fetchUser handler] No user data returned by supabase.auth.getUser(), even without error.');
      return null;
    }

    console.log('[fetchUser handler] Successfully returning user:', data.user.email);
    return data.user;
  } catch (e) {
    console.error('[fetchUser handler] Exception caught during execution:', e);
    return null; // Ensure null is returned on exception
  }
})

export const Route = createRootRoute({
  head: () => {
    // Remove any timestamp query parameter to ensure consistent CSS URL
    const cssUrl = appCss.split('?')[0];
    
    return {
      meta: [
        {
          charSet: 'utf-8',
        },
        {
          name: 'viewport',
          content: 'width=device-width, initial-scale=1',
        },
        ...seo({
          title:
            'TanStack Start | Type-Safe, Client-First, Full-Stack React Framework',
          description: `TanStack Start is a type-safe, client-first, full-stack React framework. `,
        }),
      ],
      links: [
        // CSS needs to be first to match client-side rendering order
        { rel: 'stylesheet', href: cssUrl, suppressHydrationWarning: true },
        {
          rel: 'apple-touch-icon',
          sizes: '180x180',
          href: '/apple-touch-icon.png',
        },
        {
          rel: 'icon',
          type: 'image/png',
          sizes: '32x32',
          href: '/favicon-32x32.png',
        },
        {
          rel: 'icon',
          type: 'image/png',
          sizes: '16x16',
          href: '/favicon-16x16.png',
        },
        { rel: 'icon', href: '/favicon.ico' },
      ],
    };
  },
  beforeLoad: async ({ context }) => {
    // Simplified to avoid TypeScript errors
    try {
      console.log('[SSR __root.tsx] Loading route');
    } catch (e) { console.error('Error logging'); }
    
    const user = await fetchUser(); // Ensure fetchUser uses the latest getSupabaseServerClient
    console.log('[SSR __root.tsx] Fetched user:', user?.email); // Check this again
    return { user };
  },
  errorComponent: (props) => {
    return (
      <RootDocument>
        <DefaultCatchBoundary {...props} />
      </RootDocument>
    )
  },
  notFoundComponent: () => <NotFound />,
  component: RootComponent,
})

function RootComponent() {
  return (
    <RootDocument>
      <Outlet />
    </RootDocument>
  )
}

function RootDocument({ children }: { children: React.ReactNode }) {
  const { user } = Route.useRouteContext()

  return (
    <html className="light">
      <head>
        <HeadContent />
      </head>
      <body>
        <div className="p-2 flex gap-2 text-lg">
          <Link
            to="/"
            activeProps={{
              className: 'font-bold',
            }}
            activeOptions={{ exact: true }}
          >
            Home
          </Link>{' '}
          <Link
            to="/posts"
            activeProps={{
              className: 'font-bold',
            }}
          >
            Posts
          </Link>
          <div className="ml-auto">
            {user ? (
              <>
                <span className="mr-2">{user.email}</span>
                <Link to="/logout">Logout</Link>
              </>
            ) : (
              <Link to="/login">Login</Link>
            )}
          </div>
        </div>
        <hr />
        {children}
        <TanStackRouterDevtools position="bottom-right" />
        <Scripts />
      </body>
    </html>
  )
}
