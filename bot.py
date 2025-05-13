import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

# Load env variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("WELCOME_CHANNEL_ID", 0))
PREFIX = "!"

# Set up intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# Create the bot instance
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)


# Dropdown generators
def get_th_menu():
    return discord.ui.Select(
        placeholder="Select your Town Hall level(s)",
        min_values=1,
        max_values=5,  # Pas dit aan als je meer of minder toelaat
        options=[discord.SelectOption(label=f"Town Hall {i}", value=f"th_{i}") for i in range(4, 18)],
        custom_id="th_menu"
    )


def get_bh_menu():
    return discord.ui.Select(
        placeholder="Select your Builder Hall level(s)",
        min_values=1,
        max_values=5,
        options=[discord.SelectOption(label=f"Builder Hall {i}", value=f"bh_{i}") for i in range(4, 11)],
        custom_id="bh_menu"
    )


# Views
class THView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(get_th_menu())

    @discord.ui.select(custom_id="th_menu")
    async def select_th(self, interaction: discord.Interaction, select: discord.ui.Select):
        level = select.values[0].replace("th_", "")
        await interaction.response.send_message(f"You selected Town Hall {level}.", ephemeral=True)
        await interaction.followup.send("Now select your Builder Hall level:", view=BHView(), ephemeral=True)


class BHView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(get_bh_menu())

    @discord.ui.select(custom_id="bh_menu")
    async def select_bh(self, interaction: discord.Interaction, select: discord.ui.Select):
        level = select.values[0].replace("bh_", "")
        await interaction.response.send_message(f"You selected Builder Hall {level}. All set! ✅", ephemeral=True)


# Events
@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user}")


@bot.event
async def on_member_join(member):
    guild = member.guild
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        member: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
    }

    # Maak een persoonlijk kanaal aan
    channel = await guild.create_text_channel(
        name=f"welkom-{member.name}".lower(),
        overwrites=overwrites,
        category=discord.utils.get(guild.categories, name="✅｜start")  # pas naam aan indien nodig
    )

    embed = discord.Embed(
        title=f"👋 Welkom {member.display_name}!",
        description="Laten we je even instellen voor de server.\nSelecteer eerst je **Town Hall** level.",
        color=discord.Color.blurple()
    )

    await channel.send(content=member.mention, embed=embed, view=THView())


# Load all command cogs from /commands folder (if you have one)
@bot.event
async def setup_hook():
    for filename in os.listdir('./commands'):
        if filename.endswith('.py') and filename != '__init__.py':
            await bot.load_extension(f'commands.{filename[:-3]}')



# Start the bot
bot.run(TOKEN)
