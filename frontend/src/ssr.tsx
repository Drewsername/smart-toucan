// src/ssr.tsx
/// <reference types="vinxi/types/server" />
// CSS is now imported via __root.tsx to avoid duplicate imports
import {
  createStartHandler,
  defaultStreamHandler,
} from '@tanstack/react-start/server'
import { getRouterManifest } from '@tanstack/react-start/router-manifest'
import { getSupabaseServerClient } from './utils/supabase.server' // Import server client
import type { H3Event } from 'h3' // Import H3Event type for event typing

import { createRouter, type RouterContext } from './router' // Import RouterContext type

// Define the function to fetch context on the server
async function getContext(event: H3Event): Promise<RouterContext> {
  const supabase = await getSupabaseServerClient() // Initialize client without event context
  const { data } = await supabase.auth.getUser() // Fetch user session
  console.log('[SSR ssr.tsx] Fetched user:', data.user?.email); // Add server-side log
  return {
    user: data.user, // Return context matching RouterContext shape
  }
}

export default createStartHandler({
  createRouter, // createRouter will now receive the context from getContext
  getRouterManifest,
  getContext, // Provide the getContext function
})(defaultStreamHandler)
