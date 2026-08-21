"""
Test PostgreSQL Connection and DDL Migration Execution via pg8000
"""
import os
import sys
import pg8000.native
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(__file__))
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
# Extract project ref from URL (e.g. https://zgsfghvrpmeektzavycj.supabase.co -> zgsfghvrpmeektzavycj)
project_ref = SUPABASE_URL.replace("https://", "").replace(".supabase.co", "").strip()

print(f"Project Reference: {project_ref}")

# Try connecting via pooler host or direct host
hosts_to_try = [
    f"db.{project_ref}.supabase.co",
    "aws-0-ap-south-1.pooler.supabase.com"
]

sql_ddl = """
CREATE TABLE IF NOT EXISTS public.research_notes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE public.research_notes ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Users can access own research notes" ON public.research_notes;
CREATE POLICY "Users can access own research notes" ON public.research_notes FOR ALL USING (auth.uid() = user_id);
GRANT ALL ON public.research_notes TO postgres, anon, authenticated, service_role;
"""

connected = False
for host in hosts_to_try:
    print(f"Attempting to connect to host: {host}...")
    try:
        # Note: Default port 5432 or 6543
        conn = pg8000.native.Connection(
            user=f"postgres.{project_ref}",
            host=host,
            database="postgres",
            port=6543 if "pooler" in host else 5432,
            ssl_context=True
        )
        print("Connected via pg8000 successfully!")
        conn.run(sql_ddl)
        print("DDL Migration executed successfully via pg8000!")
        connected = True
        break
    except Exception as err:
        print(f"  Note connecting to {host}: {err}")

if not connected:
    print("\n[INFO] Direct TCP Postgres connection requires DB password or SQL Editor execution.")
