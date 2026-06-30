import { createClient } from '@supabase/supabase-js'

// Retrieve values from Vite environmental configuration (.env)
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || ""
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || ""

if (!supabaseUrl || !supabaseAnonKey) {
  console.warn("Supabase env parameters missing! Ensure VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY exist in frontend/.env")
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
