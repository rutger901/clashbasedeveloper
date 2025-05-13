import discord
from discord.ext import commands

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

WELCOME_ROLE_ID = 1371646777094176959
MEMBER_ROLE_ID = 1047167712109006848
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


class THSelect(discord.ui.Select):
    def __init__(self):
        options = []
        for i in range(4, 18):
            value = f"th{i}"
            label = f"Town Hall {i}"
            emoji = None
            if value in TH_EMOJIS:
                emoji_data = TH_EMOJIS[value]
                emoji = discord.PartialEmoji(id=emoji_data["id"], name=emoji_data["name"])
            options.append(discord.SelectOption(label=label, value=value, emoji=emoji))

        super().__init__(
            placeholder="Select your Town Hall level(s)",
            options=options,
            custom_id="th_select",
            min_values=1,
            max_values=5
        )

    async def callback(self, interaction: discord.Interaction):
        added = []
        for value in self.values:
            role_id = TH_ROLES.get(value)
            role = interaction.guild.get_role(role_id)
            if role:
                await interaction.user.add_roles(role)
                added.append(role.name)

        if added:
            await interaction.response.send_message(f"✅ Added roles: **{', '.join(added)}**", ephemeral=True)
            await interaction.followup.send("Now select your Builder Hall level(s):", view=BHView(), ephemeral=True)
        else:
            await interaction.response.send_message("⚠️ No valid roles found.", ephemeral=True)


class BHSelect(discord.ui.Select):
    def __init__(self):
        options = []
        for i in range(4, 11):
            value = f"bh{i}"
            label = f"Builder Hall {i}"
            emoji = None
            if value in BH_EMOJIS:
                emoji_data = BH_EMOJIS[value]
                emoji = discord.PartialEmoji(id=emoji_data["id"], name=emoji_data["name"])
            options.append(discord.SelectOption(label=label, value=value, emoji=emoji))

        super().__init__(
            placeholder="Select your Builder Hall level(s)",
            options=options,
            custom_id="bh_select",
            min_values=1,
            max_values=5
        )

    async def callback(self, interaction: discord.Interaction):
        added = []
        for value in self.values:
            role_id = BH_ROLES.get(value)
            role = interaction.guild.get_role(role_id)
            if role:
                await interaction.user.add_roles(role)
                added.append(role.name)

        if added:
            await interaction.response.send_message(f"✅ Added roles: **{', '.join(added)}**", ephemeral=True)
            await interaction.followup.send(
                "You're almost in! Click the button below to unlock full server access. 🔓",
                view=AcceptButtonView(),
                ephemeral=True
            )
        else:
            await interaction.response.send_message("⚠️ No valid roles found.", ephemeral=True)


class AcceptButtonView(discord.ui.View):
    @discord.ui.button(label="Unlock Access ✅", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user
        welcome_role = guild.get_role(WELCOME_ROLE_ID)
        member_role = guild.get_role(MEMBER_ROLE_ID)

        if member_role:
            await user.add_roles(member_role)
        if welcome_role and welcome_role in user.roles:
            await user.remove_roles(welcome_role)

        await interaction.response.send_message("You're now a full member of the server. Enjoy! 🎉", ephemeral=True)
        await interaction.channel.delete(reason="Onboarding complete.")


class THView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(THSelect())


class BHView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(BHSelect())


class Onboarding(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="onboarding")
    @commands.has_permissions(manage_roles=True)
    async def onboarding(self, ctx):
        embed = discord.Embed(
            title=f"Welcome to Clash Base Developer! {LOGO_EMOJI}",
            description=(
                "Thanks for joining our community.\n\n"
                "Let’s get you set up before accessing the rest of the server.\n"
                "Start by selecting your **Town Hall** level(s) below."
            ),
            color=discord.Color.blurple()
        )
        await ctx.send(embed=embed, view=THView())


async def setup(bot):
    await bot.add_cog(Onboarding(bot))
