import discord
from discord.ext import commands

class ChannelSelect(discord.ui.Select):
    def __init__(self, bot):
        self.bot = bot
        options = [
            discord.SelectOption(label=channel.name, value=str(channel.id))
            for channel in bot.get_all_channels()
            if isinstance(channel, discord.TextChannel)
        ]

        super().__init__(
            placeholder="Kies een kanaal om een bericht in te sturen...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        channel_id = int(self.values[0])
        await interaction.response.send_modal(MessageModal(channel_id))


class ChannelSelectView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=60)
        self.add_item(ChannelSelect(bot))


class MessageModal(discord.ui.Modal, title="Stuur een bericht"):
    def __init__(self, channel_id):
        super().__init__()
        self.channel_id = channel_id

    message = discord.ui.TextInput(
        label="Typ je bericht",
        placeholder="Wat wil je versturen?",
        style=discord.TextStyle.paragraph,
        max_length=2000
    )

    async def on_submit(self, interaction: discord.Interaction):
        channel = interaction.guild.get_channel(self.channel_id)
        if channel:
            await channel.send(self.message.value)
            await interaction.response.send_message("✅ Bericht verzonden!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Kanaal niet gevonden.", ephemeral=True)


class SendMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="sendmessage")
    @commands.has_permissions(manage_messages=True)
    async def sendmessage(self, ctx):
        await ctx.send("📨 Kies het kanaal waar je het bericht naartoe wilt sturen:", view=ChannelSelectView(self.bot))


async def setup(bot):
    await bot.add_cog(SendMessage(bot))
