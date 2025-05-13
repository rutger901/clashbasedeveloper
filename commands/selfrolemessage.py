import discord
from discord.ext import commands

# ⚙️ Button configuratie — pas hier labels, emoji's, kleuren en role_id's aan
ROLE_BUTTONS = [
    {
        "label": "Town Hall 15",
        "emoji": "🏰",
        "role_id": 123456789012345678,
        "style": discord.ButtonStyle.success
    },
    {
        "label": "Builder Hall 10",
        "emoji": "🛠️",
        "role_id": 234567890123456789,
        "style": discord.ButtonStyle.primary
    },
    {
        "label": "Clan Leader",
        "emoji": "👑",
        "role_id": 345678901234567890,
        "style": discord.ButtonStyle.danger
    }
]


# 🔘 Eén knop per rol
class RoleButton(discord.ui.Button):
    def __init__(self, label, emoji, role_id, style):
        super().__init__(
            label=label,
            emoji=emoji,
            custom_id=str(role_id),
            style=style
        )
        self.role_id = role_id

    async def callback(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(self.role_id)
        if not role:
            await interaction.response.send_message("❌ Role not found.", ephemeral=True)
            return

        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"❌ Removed role: `{role.name}`", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"✅ Added role: `{role.name}`", ephemeral=True)


# 📦 De view met alle buttons
class SelfRoleView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        for btn in ROLE_BUTTONS:
            self.add_item(RoleButton(
                label=btn["label"],
                emoji=btn["emoji"],
                role_id=btn["role_id"],
                style=btn.get("style", discord.ButtonStyle.secondary)
            ))


class SelfRoleMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="selfrolemessage")
    @commands.has_permissions(manage_roles=True)
    async def selfrolemessage(self, ctx):
        """Send the self-role message with styled embed and buttons"""

        embed = discord.Embed(
            title="📋 Choose Your Roles",
            description="Click the buttons below to assign or remove roles.\nYou can toggle them at any time.",
            color=discord.Color.blurple()  # Je kunt ook .green(), .red(), .gold(), of zelf `discord.Color.from_rgb(r,g,b)`
        )
        embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed, view=SelfRoleView())


async def setup(bot):
    await bot.add_cog(SelfRoleMessage(bot))
