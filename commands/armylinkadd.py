from discord.ext import commands
import discord
from supabase_client import supabase_main

class ArmyLinkAdd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def armylinkadd(self, ctx):
        if ctx.author.id != 358589790309842944:
            await ctx.send("❌ Alleen de eigenaar mag dit gebruiken.")
            return

        response = supabase_main.table("army_links").select("th_level").execute()
        th_levels = sorted(set(item["th_level"] for item in response.data))

        if not th_levels:
            th_levels = ["th4", "th5", "th6"]  # Fallback opties

        th_options = [discord.SelectOption(label=th, value=th) for th in th_levels if th]

        class THSelect(discord.ui.Select):
            def __init__(self):
                super().__init__(placeholder="Selecteer een TH-level", options=th_options)

            async def callback(inner_self, interaction):
                th_level = inner_self.values[0]
                await interaction.response.send_message("Type de strategy naam:")
                strat_msg = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
                strat_name = strat_msg.content.strip()

                await ctx.send("Plak de army link:")
                link_msg = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
                army_link = link_msg.content.strip()

                data = {"th_level": th_level, "strat": strat_name, "link": army_link}
                supabase_main.table("army_links").insert(data).execute()

                await ctx.send(f"✅ Army link toegevoegd: {th_level} - {strat_name}")

        if th_options:
            view = discord.ui.View(timeout=60)
            view.add_item(THSelect())
            await ctx.send("Selecteer een TH-level:", view=view)
        else:
            await ctx.send("❌ Geen TH-levels beschikbaar.")

async def setup(bot):
    await bot.add_cog(ArmyLinkAdd(bot))
    print("✅ ArmyLinkAdd Cog loaded")
