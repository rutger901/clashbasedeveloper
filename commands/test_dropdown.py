import discord
from discord.ext import commands
from discord import app_commands

class TestSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Option A", value="A"),
            discord.SelectOption(label="Option B", value="B"),
            discord.SelectOption(label="Option C", value="C"),
        ]
        super().__init__(
            placeholder="Choose an option...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="test_select"
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"You selected: {self.values[0]}", ephemeral=True)

class TestView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TestSelect())

class TestDropdown(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="dropdown", description="Test dropdown select")
    async def dropdown(self, interaction: discord.Interaction):
        await interaction.response.send_message("Please choose an option:", view=TestView(), ephemeral=True)

async def setup(bot):
    await bot.add_cog(TestDropdown(bot))
