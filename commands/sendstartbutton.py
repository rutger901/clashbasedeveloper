from discord.ext import commands
from discord.ui import View, Button
import discord

class StartButtonView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(
            Button(label="🚀 Start", style=discord.ButtonStyle.green, custom_id="start_button")
        )

class StartButtonCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="sendstartbutton")
    @commands.has_permissions(administrator=True)
    async def send_start_button(self, ctx):
        channel_id = 1388587917940756530  # jouw kanaal-ID
        channel = self.bot.get_channel(channel_id)

        if not channel:
            await ctx.send("❌ Kanaal niet gevonden.")
            return

        msg = await channel.send(
            "**Click the button to search for a Clash of Clans base!**",
            view=StartButtonView()
        )
        await msg.pin()
        await ctx.send(f"📌 Start-knop geplaatst in <#{channel_id}>")

async def setup(bot):
    await bot.add_cog(StartButtonCog(bot))
    print("✅ StartButton Cog geladen")
