import discord
from discord.ext import commands


class RoleID(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="role_id")
    @commands.has_permissions(manage_roles=True)
    async def role_id(self, ctx):
        """Toont een lijst met alle rollen + hun IDs"""

        roles = ctx.guild.roles[::-1]  # omdraaien zodat hoogste rollen eerst staan
        lines = []

        for role in roles:
            if role.name != "@everyone":
                lines.append(f"`{role.id}` - {role.name}")

        content = "\n".join(lines)
        if len(content) > 2000:
            await ctx.send("❌ Te veel rollen om te tonen.")
        else:
            await ctx.send(f"📋 **Rollen & ID's in deze server:**\n{content}")


async def setup(bot):
    await bot.add_cog(RoleID(bot))