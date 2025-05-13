import discord
from discord.ext import commands


class AcceptButton(discord.ui.View):
    def __init__(self, welcome_role_id, member_role_id):
        super().__init__(timeout=None)
        self.welcome_role_id = welcome_role_id
        self.member_role_id = member_role_id

    @discord.ui.button(label="✅ Klik hier om toegang te krijgen", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user

        welcome_role = guild.get_role(self.welcome_role_id)
        member_role = guild.get_role(self.member_role_id)

        if member_role:
            await user.add_roles(member_role)
        if welcome_role and welcome_role in user.roles:
            await user.remove_roles(welcome_role)

        await interaction.response.send_message("✅ Je hebt nu toegang tot de server!", ephemeral=True)


class StartMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog has been loaded.")

    @commands.command(name="startmessage")
    @commands.has_permissions(manage_roles=True)
    async def startmessage(self, ctx):
        """Stuur het startbericht met acceptatieknop"""

        welcome_role_id = 1371646777094176959  # ❗vervang door jouw 'welcome' rol-ID
        member_role_id = 1047167712109006848   # ❗vervang door jouw 'member' rol-ID

        embed = discord.Embed(
            title="👋 Welkom bij Clash Base Developer!",
            description="Klik op de knop hieronder om toegang te krijgen tot de server.\n"
                        "Je krijgt daarna automatisch de juiste rol toegewezen.",
            color=discord.Color.blurple()
        )
        embed.set_footer(text="Door te klikken ga je akkoord met de serverregels.")

        await ctx.send(embed=embed, view=AcceptButton(welcome_role_id, member_role_id))


async def setup(bot):
    await bot.add_cog(StartMessage(bot))
