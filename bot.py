import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
from keepalive import keep_alive
from commands.getbase import StartButtonView  # Zorg dat dit pad klopt

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = "!"

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

@bot.event
async def on_ready():
    await bot.tree.sync()
    bot.add_view(StartButtonView())  # Zorgt dat de start-knop blijft werken na reboot
    print(f"✅ Bot is online as {bot.user}")

@bot.event  # <- DIT WAS VEROORZAKER VAN JE PROBLEEM
async def setup_hook():
    for filename in os.listdir("./commands"):
        if filename.endswith(".py") and filename != "__init__.py":
            try:
                await bot.load_extension(f"commands.{filename[:-3]}")
                print(f"✅ Loaded {filename}")
            except Exception as e:
                print(f"❌ Failed to load {filename}: {e}")

@bot.command()
async def listslash(ctx):
    cmds = bot.tree.get_commands()
    if not cmds:
        await ctx.send("❌ Geen slash commands geregistreerd.")
    else:
        msg = "\n".join(f"/{c.name} – {c.description}" for c in cmds)
        await ctx.send(f"✅ Geregistreerde slash commands:\n{msg}")

keep_alive()
bot.run(TOKEN)
