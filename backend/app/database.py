import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load env variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
# Use service_role key to bypass Row Level Security in background workers if needed,
# or use anon key if policies permit.
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    # Fallbacks or warning
    print("Warning: SUPABASE_URL and SUPABASE_KEY environment variables are not set yet.")

def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)
