from discord.ext import commands
import discord
from supabase_client import supabase_main

class ArmyLinkRemove(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def armylinkremove(self, ctx):
        if ctx.author.id != 358589790309842944:
            await ctx.send("❌ Alleen de eigenaar mag dit gebruiken.")
            return

        # TH-level opties ophalen
        response = supabase_main.table("army_links").select("th_level").execute()
        th_levels = sorted(set(item["th_level"] for item in response.data))

        if not th_levels:
            await ctx.send("❌ Geen TH-levels gevonden.")
            return

        th_options = [discord.SelectOption(label=th, value=th) for th in th_levels]

        class THSelect(discord.ui.Select):
            def __init__(self):
                super().__init__(placeholder="Selecteer een TH-level", options=th_options)

            async def callback(inner_self, interaction):
                th_level = inner_self.values[0]
                strat_response = supabase_main.table("army_links").select("strat").eq("th_level", th_level).execute()
                strats = sorted(set(item["strat"] for item in strat_response.data))

                if not strats:
                    await interaction.response.send_message("❌ Geen strategies gevonden voor dat TH-level.", ephemeral=True)
                    return

                strat_options = [discord.SelectOption(label=strat, value=strat) for strat in strats]

                class StratSelect(discord.ui.Select):
                    def __init__(self):
                        super().__init__(placeholder="Selecteer een strategy", options=strat_options)

                    async def callback(inner_self2, interaction2):
                        strat_name = inner_self2.values[0]
                        supabase_main.table("army_links").delete().eq("th_level", th_level).eq("strat", strat_name).execute()
                        await interaction2.response.edit_message(content=f"✅ Army link verwijderd: {th_level} - {strat_name}", view=None)

                await interaction.response.edit_message(content="Selecteer een strategy:", view=discord.ui.View().add_item(StratSelect()))

        await ctx.send("Selecteer een TH-level:", view=discord.ui.View().add_item(THSelect()))

async def setup(bot):
    await bot.add_cog(ArmyLinkRemove(bot))
    print("✅ ArmyLinkRemove Cog loaded")
