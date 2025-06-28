from dotenv import load_dotenv
import os
from supabase import create_client, Client

load_dotenv()

# MAIN: baseforcoc.com
SUPABASE_URL_MAIN = os.getenv("SUPABASE_URL_MAIN")
SUPABASE_KEY_MAIN = os.getenv("SUPABASE_KEY_MAIN")
supabase_main: Client = create_client(SUPABASE_URL_MAIN, SUPABASE_KEY_MAIN)

# SECONDARY: eventueel andere app
SUPABASE_URL_SECOND = os.getenv("SUPABASE_URL_SECOND")
SUPABASE_KEY_SECOND = os.getenv("SUPABASE_KEY_SECOND")
supabase_second: Client = create_client(SUPABASE_URL_SECOND, SUPABASE_KEY_SECOND)
