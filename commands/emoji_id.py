import discord
from discord.ext import commands


class EmojiID(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="emoji_id")
    @commands.has_permissions(manage_emojis=True)
    async def emoji_id(self, ctx):
        """Toont een lijst met alle custom emoji's + hun IDs"""

        if not ctx.guild.emojis:
            return await ctx.send("😶 Deze server heeft geen custom emoji's.")

        lines = [f"{str(emoji)} — `{emoji.name}` • ID: `{emoji.id}`" for emoji in ctx.guild.emojis]
        content = "\n".join(lines)

        if len(content) > 2000:
            await ctx.send("❌ Te veel emoji's om in één bericht te tonen.")
        else:
            await ctx.send(f"🎨 **Emoji’s in deze server:**\n{content}")


async def setup(bot):
    await bot.add_cog(EmojiID(bot))
