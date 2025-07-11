import discord
from discord.ext import commands
from discord import app_commands

class SetupCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setup", description="Setup ClashBaseDeveloper category and channels")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_command(self, interaction: discord.Interaction):
        guild = interaction.guild
        created_something = False

        category = discord.utils.get(guild.categories, name="ClashBaseDeveloper")
        if not category:
            category = await guild.create_category("ClashBaseDeveloper")
            created_something = True
        
        created_base = await self.create_channel_if_missing(guild, category, "search-a-base")
        created_army = await self.create_channel_if_missing(guild, category, "search-a-army")
        
        if created_something or created_base or created_army:
            await interaction.response.send_message("✅ Setup complete!", ephemeral=True)
        else:
            await interaction.response.send_message("⚠️ Everything already exists.", ephemeral=True)

    async def create_channel_if_missing(self, guild, category, channel_name):
        channel = discord.utils.get(category.channels, name=channel_name)
        if not channel:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(send_messages=False),
                guild.me: discord.PermissionOverwrite(send_messages=True)
            }
            channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)

            if channel_name == "search-a-base":
                await channel.send("Use `/getbase` below to search for a base layout! 🏰")
            elif channel_name == "search-a-army":
                await channel.send("Use `/getarmy` below to search for an army composition! ⚔️")
            return True
        return False

async def setup(bot):
    await bot.add_cog(SetupCog(bot))
    print("✅ SetupCog loaded")
