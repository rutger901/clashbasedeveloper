from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="commands")
    async def show_commands(self, ctx):
        """Displays a list of available commands."""
        await ctx.send(
            "**🛠 Available Commands:**\n"
            "`!commands` - Show this command list\n"
            "`!ping` - Check if the bot is alive\n"
            "`!setup` - Start the TH/BH role selector (coming soon)\n"
        )

async def setup(bot):
    await bot.add_cog(Help(bot))
