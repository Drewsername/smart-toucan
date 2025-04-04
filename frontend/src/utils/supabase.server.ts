import { parseCookies, setCookie } from '@tanstack/react-start/server'
import { createServerClient } from '@supabase/ssr'

export function getSupabaseServerClient() {
  console.log('[SupabaseServerClient] Initializing client. URL available:', !!process.env.SUPABASE_URL);
  return createServerClient(
    process.env.SUPABASE_URL!,
    process.env.SUPABASE_ANON_KEY!,
    {
      cookies: {
        // @ts-ignore Wait till Supabase overload works
        getAll() {
          const cookies = parseCookies();
          console.log('[SupabaseServerClient] Raw cookies object from parseCookies:', cookies); // Log the whole object

          // Find and log the value(s) of Supabase cookies
          const supabaseCookieEntries = Object.entries(cookies).filter(([name]) => name.startsWith('sb-'));
          let authCookieFound = false;
          if (supabaseCookieEntries.length > 0) {
            console.log('[SupabaseServerClient] Found Supabase cookie name/values:');
            supabaseCookieEntries.forEach(([name, value]) => {
              // For debugging, log the start and length. Be cautious in production.
              const valuePreview = value ? `${value.substring(0, 20)}... (length: ${value.length})` : 'VALUE IS NULL/UNDEFINED';
              console.log(`  ${name}: ${valuePreview}`);
              // Check if the value seems potentially valid
              if (value && value !== 'undefined' && value.length > 10) { // Basic sanity check
                authCookieFound = true; // Mark as found if at least one seems okay
              } else {
                 console.warn(`[SupabaseServerClient] Suspicious value for cookie: ${name}`);
              }
            });
          } else {
            console.warn('[SupabaseServerClient] No cookie found with name prefix "sb-"!');
          }
          // Log based on whether any cookie looked potentially valid
          console.log('[SupabaseServerClient] Potentially valid Supabase auth cookie value found:', authCookieFound);

          // Return the cookies for Supabase client
          return Object.entries(cookies).map(([name, value]) => ({
            name,
            value,
          }))
        },
        setAll(cookies) {
           console.log('[SupabaseServerClient] Setting cookies:', cookies.map(c => c.name));
          cookies.forEach((cookie) => {
            setCookie(cookie.name, cookie.value, cookie);
          })
        },
      },
    },
  )
}