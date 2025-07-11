import discord
import os
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from keepalive import keep_alive
from commands.getbase import StartButtonView  # Zorg dat dit pad klopt
import time
from collections import defaultdict

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = "!"

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

user_action_times = defaultdict(list)

@bot.check
async def global_owner_only(ctx):
    return ctx.author.id == 358589790309842944 or isinstance(ctx.command, app_commands.Command)

@bot.check
async def global_rate_limit(ctx):
    now = time.time()
    user_action_times[ctx.author.id] = [t for t in user_action_times[ctx.author.id] if now - t < 10]
    if len(user_action_times[ctx.author.id]) >= 5:
        raise commands.CommandOnCooldown(commands.Cooldown(1, 10, commands.BucketType.user))
    user_action_times[ctx.author.id].append(now)
    return True

@bot.event
async def on_ready():
    await bot.tree.sync()
    bot.add_view(StartButtonView())  # Houd de knop persistent na restart
    print(f"\u2705 Bot is online als {bot.user}")

@bot.event
async def setup_hook():
    for filename in os.listdir("./commands"):
        if filename.endswith(".py") and filename != "__init__.py":
            try:
                await bot.load_extension(f"commands.{filename[:-3]}")
                print(f"\u2705 Loaded {filename}")
            except Exception as e:
                print(f"\u274c Failed to load {filename}: {e}")

@bot.command()
async def listslash(ctx):
    cmds = bot.tree.get_commands()
    if not cmds:
        await ctx.send("\u274c Geen slash commands geregistreerd.")
    else:
        msg = "\n".join(f"/{c.name} – {c.description}" for c in cmds)
        await ctx.send(f"\u2705 Geregistreerde slash commands:\n{msg}")

keep_alive()
bot.run(TOKEN)
