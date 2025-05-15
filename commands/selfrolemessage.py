import discord
from discord.ext import commands
from discord import app_commands

# Jouw bestaande role/emoji data blijft zoals het is
# (die moet in dit bestand beschikbaar zijn, of importeer uit aparte module)
# 🎯 ROLE IDs (update if needed)
TH_ROLES = {
    "th4": 1273251323055312978,
    "th5": 1144703356175130725,
    "th6": 1144703438274445342,
    "th7": 1158443301372964925,
    "th8": 1158443376006418492,
    "th9": 1130468090778505237,
    "th10": 1130468030883840121,
    "th11": 1130467969525366865,
    "th12": 1130467908062040145,
    "th13": 1130467849689891037,
    "th14": 1130467784799821824,
    "th15": 1130467588825169941,
    "th16": 1273251153701900411,
    "th17": 1336347775192797285
}

BH_ROLES = {
    "bh4": 1371658591530127451,
    "bh5": 1371658639072432138,
    "bh6": 1371658721557741649,
    "bh7": 1371658784803393567,
    "bh8": 1371658925224497286,
    "bh9": 1371658975572918294,
    "bh10": 1371659024411656245
}

LOGO_EMOJI = "<:logo:1371668120074190848>"

TH_EMOJIS = {
    "th4": {"id": 1371662629700898827, "name": "th4"},
    "th5": {"id": 1371662633010331838, "name": "th5"},
    "th6": {"id": 1371662634989916211, "name": "th6"},
    "th7": {"id": 1371662636621627462, "name": "th7"},
    "th8": {"id": 1371662639372963900, "name": "th8"},
    "th9": {"id": 1371662641290022943, "name": "th9"},
    "th10": {"id": 1371662650957762661, "name": "th10"},
    "th11": {"id": 1371662653965209650, "name": "th11"},
    "th12": {"id": 1371662656238391306, "name": "th12"},
    "th13": {"id": 1371662657777832096, "name": "th13"},
    "th14": {"id": 1371662660256534548, "name": "th14"},
    "th15": {"id": 1371662661493850173, "name": "th15"},
    "th16": {"id": 1371662663561777287, "name": "th16"},
    "th17": {"id": 1371662666426351818, "name": "th17"}
}

BH_EMOJIS = {
    "bh4": {"id": 1371662610927452200, "name": "bh4"},
    "bh5": {"id": 1371662613393702972, "name": "bh5"},
    "bh6": {"id": 1371662616023273573, "name": "bh6"},
    "bh7": {"id": 1371662617524830279, "name": "bh7"},
    "bh8": {"id": 1371662619370459287, "name": "bh8"},
    "bh9": {"id": 1371662620976873503, "name": "bh9"},
    "bh10": {"id": 1371662622923034686, "name": "bh10"}
}

# 🔽 TH Selector
class THSelect(discord.ui.Select):
    def __init__(self, member: discord.Member):
        options = []
        for th, role_id in TH_ROLES.items():
            role = member.guild.get_role(role_id)
            emoji = TH_EMOJIS.get(th)
            options.append(discord.SelectOption(
                label=th.upper(),
                value=str(role_id),
                emoji=discord.PartialEmoji(id=emoji["id"], name=emoji["name"]) if emoji else None,
                default=role in member.roles if role else False
            ))

        super().__init__(
            placeholder="Select your Town Hall level(s)",
            min_values=0,
            max_values=len(options),
            options=options,
            custom_id="th_role_selector"
        )

    async def callback(self, interaction: discord.Interaction):
        selected_ids = set(int(role_id) for role_id in self.values)
        all_ids = set(TH_ROLES.values())

        roles_to_add = []
        roles_to_remove = []

        for role_id in all_ids:
            role = interaction.guild.get_role(role_id)
            if role_id in selected_ids and role not in interaction.user.roles:
                roles_to_add.append(role)
            elif role_id not in selected_ids and role in interaction.user.roles:
                roles_to_remove.append(role)

        if roles_to_add:
            await interaction.user.add_roles(*roles_to_add)
        if roles_to_remove:
            await interaction.user.remove_roles(*roles_to_remove)

        await interaction.response.send_message("✅ Your Town Hall roles have been updated.", ephemeral=True)

class THSelectView(discord.ui.View):
    def __init__(self, member: discord.Member):
        super().__init__(timeout=None)
        self.add_item(THSelect(member))


# 🔽 BH Selector
class BHSelect(discord.ui.Select):
    def __init__(self, member: discord.Member):
        options = []
        for bh, role_id in BH_ROLES.items():
            role = member.guild.get_role(role_id)
            emoji = BH_EMOJIS.get(bh)
            options.append(discord.SelectOption(
                label=bh.upper(),
                value=str(role_id),
                emoji=discord.PartialEmoji(id=emoji["id"], name=emoji["name"]) if emoji else None,
                default=role in member.roles if role else False
            ))

        super().__init__(
            placeholder="Select your Builder Hall level(s)",
            min_values=0,
            max_values=len(options),
            options=options,
            custom_id="bh_role_selector"
        )

    async def callback(self, interaction: discord.Interaction):
        selected_ids = set(int(role_id) for role_id in self.values)
        all_ids = set(BH_ROLES.values())

        roles_to_add = []
        roles_to_remove = []

        for role_id in all_ids:
            role = interaction.guild.get_role(role_id)
            if role_id in selected_ids and role not in interaction.user.roles:
                roles_to_add.append(role)
            elif role_id not in selected_ids and role in interaction.user.roles:
                roles_to_remove.append(role)

        if roles_to_add:
            await interaction.user.add_roles(*roles_to_add)
        if roles_to_remove:
            await interaction.user.remove_roles(*roles_to_remove)

        await interaction.response.send_message("✅ Your Builder Hall roles have been updated.", ephemeral=True)

class BHSelectView(discord.ui.View):
    def __init__(self, member: discord.Member):
        super().__init__(timeout=None)
        self.add_item(BHSelect(member))


# 🔧 Command COG
class ClashRoleSelectors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="throles")
    @commands.has_permissions(manage_roles=True)
    async def throles_command(self, ctx):
        embed = discord.Embed(
            title="🏰 Select Your Town Hall Level",
            description="Choose your **Town Hall** roles using the dropdown below.\nUpdate them any time.",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed, view=THSelectView(ctx.author))

    @commands.command(name="bhroles")
    @commands.has_permissions(manage_roles=True)
    async def bhroles_command(self, ctx):
        embed = discord.Embed(
            title="🛠️ Select Your Builder Hall Level",
            description="Choose your **Builder Hall** roles using the dropdown below.\nUpdate them any time.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed, view=BHSelectView(ctx.author))


async def setup(bot):
    await bot.add_cog(ClashRoleSelectors(bot))
