import coc
import os
from dotenv import load_dotenv

load_dotenv()

async def create_coc_client():
    token = os.getenv("COC_API_TOKEN")

    if not token:
        print("[ERROR] Geen token gevonden in .env!")
        return None

    print(f"[DEBUG] ✅ Token geladen: {token[:15]}...")

    try:
        client = await coc.login(
            key_names="clashbasedeveloper",
            key_count=1,
            token=token
        )
        print("[DEBUG] ✅ Client object succesvol aangemaakt.")
        return client
    except Exception as e:
        print(f"[ERROR] 🔥 Fout bij client login: {e}")
        return None
