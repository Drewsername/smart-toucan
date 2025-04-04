// src/utils/supabase.client.ts

import { createBrowserClient } from '@supabase/ssr';

// Make sure these are in your .env file and accessible to Vite/Vinxi
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL!;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY!;

// Create a singleton Supabase client for browser use
export const supabase= createBrowserClient(supabaseUrl, supabaseAnonKey);