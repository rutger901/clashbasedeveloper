import discord
from discord.ext import commands
from discord import app_commands
from supabase_client import supabase_main

class THLevelSelect(discord.ui.Select):
    def __init__(self, th_levels):
        options = [
            discord.SelectOption(label=th, value=th) for th in th_levels
        ]
        super().__init__(placeholder="Select your Town Hall level...", options=options)

    async def callback(self, interaction: discord.Interaction):
        th_level = self.values[0]
        response = supabase_main.table("army_links").select("strat").eq("th_level", th_level).execute()
        strats = sorted(set(item["strat"] for item in response.data))

        if not strats:
            await interaction.response.edit_message(
                content=f"❌ No army strats found for {th_level}.",
                view=None
            )
            return

        await interaction.response.edit_message(
            content=f"Select a strat for {th_level}:",
            view=StratSelectView(th_level, strats)
        )

class THLevelSelectView(discord.ui.View):
    def __init__(self, th_levels):
        super().__init__(timeout=None)
        self.add_item(THLevelSelect(th_levels))

class ArmyLinkButton(discord.ui.View):
    def __init__(self, url: str):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label="📲 Open in Game", url=url))

class StratSelect(discord.ui.Select):
    def __init__(self, th_level: str, strats: list):
        options = [discord.SelectOption(label=strat, value=strat) for strat in strats]
        super().__init__(placeholder="Select a strategy...", options=options)
        self.th_level = th_level

    async def callback(self, interaction: discord.Interaction):
        strat = self.values[0]
        response = supabase_main.table("army_links").select("link").eq("th_level", self.th_level).eq("strat", strat).execute()

        if not response.data:
            await interaction.response.edit_message(
                content="❌ No link found for this strat.",
                view=None
            )
            return

        army_link = response.data[0]["link"]
        await interaction.response.edit_message(
            content=f"🔗 Army link for {self.th_level} - {strat}: {army_link}",
            view=ArmyLinkButton(army_link)
        )

class StratSelectView(discord.ui.View):
    def __init__(self, th_level: str, strats: list):
        super().__init__(timeout=None)
        self.add_item(StratSelect(th_level, strats))

class GetArmy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="getarmy", description="Find an army link by TH level and strategy")
    async def getarmy_command(self, interaction: discord.Interaction):
        if interaction.channel.name != "search-a-army" or interaction.channel.category is None or interaction.channel.category.name != "ClashBaseDeveloper":
            await interaction.response.send_message(
                "❌ You can only use this command in the `search-a-army` channel under `ClashBaseDeveloper` category.",
                ephemeral=True
            )
            return

        # Dynamisch alle unieke th_levels ophalen
        response = supabase_main.table("army_links").select("th_level").execute()
        th_levels = sorted(set(item["th_level"] for item in response.data))

        if not th_levels:
            await interaction.response.send_message(
                "❌ No Town Hall levels found in the database.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            "Please select your Town Hall level:",
            view=THLevelSelectView(th_levels),
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(GetArmy(bot))
    print("✅ GetArmy Cog loaded")
