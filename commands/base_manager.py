# commands/base_manager.py
import discord
from discord.ext import commands
from supabase_client import supabase

class BaseManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def use_base(self, ctx, base_id: str):
        user_id = str(ctx.author.id)

        # Check of gebruiker al een actieve base heeft
        result = supabase.table("user_bases") \
            .select("*") \
            .eq("user_id", user_id) \
            .is_("end_date", None) \
            .execute()

        if result.data:
            await ctx.send("Je hebt al een base gekoppeld. Gebruik `!stop_base` om deze eerst te stoppen.")
            return

        # Base toevoegen
        supabase.table("user_bases").insert({
            "user_id": user_id,
            "base_id": base_id
        }).execute()

        await ctx.send(f"✅ Je hebt base `{base_id}` gekoppeld. We houden vanaf nu stats bij!")

async def setup(bot):
    await bot.add_cog(BaseManager(bot))
