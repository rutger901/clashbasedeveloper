import discord
from discord.ext import commands
from supabase_client import supabase_second
import random
import asyncio

# ⬇️ Start Button View – stuurt DM met dropdowns
class StartButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🚀 Start", style=discord.ButtonStyle.green, custom_id="start_button")
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.user.send(
                "**Welcome to Clash Base Finder! 🏰**\n\nSelect the type of base you're looking for:",
                view=BaseTypeView()
            )

            await interaction.response.send_message("📬 I just sent you a DM to get started!")
            msg = await interaction.original_response()
            await asyncio.sleep(10)
            await msg.delete()

        except discord.Forbidden:
            await interaction.response.send_message("❌ I couldn't send you a DM. Please enable DMs.", ephemeral=True)
        except discord.NotFound:
            pass  # interaction expired or message already deleted

# ⬇️ Base link knop
class BaseLinkButton(discord.ui.View):
    def __init__(self, url: str):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label="🔗 Get Base", url=url))

# ⬇️ Eerste dropdown: Home / Builder / Capital (alleen Home is actief)
class BaseTypeSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Home Base", value="homebase"),
            discord.SelectOption(label="Builder Base 🔒 (coming soon)", value="builderbase"),
            discord.SelectOption(label="Capital Base 🔒 (coming soon)", value="capitalbase")
        ]
        super().__init__(placeholder="Select a base category...", options=options, custom_id="base_type_select")

    async def callback(self, interaction: discord.Interaction):
        base_type = self.values[0]

        if base_type != "homebase":
            await interaction.response.send_message(
                "🚧 This base type is coming soon. Please select **Home Base** for now.",
                ephemeral=True
            )
            return

        await interaction.response.edit_message(
            content=f"You selected **{base_type}**. Now choose your level:",
            view=LevelSelectView(base_type)
        )

class BaseTypeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(BaseTypeSelect())

# ⬇️ Tweede dropdown: TH-niveaus
class LevelSelect(discord.ui.Select):
    def __init__(self, base_type: str):
        self.base_type = base_type

        options = [discord.SelectOption(label=f"TH{i}", value=f"th{i}") for i in range(4, 18)]

        super().__init__(placeholder="Select your level...", options=options, custom_id="level_select")

    async def callback(self, interaction: discord.Interaction):
        selected_level = self.values[0]
        await interaction.response.edit_message(
            content=f"Selected level: **{selected_level}**. Now choose your base type:",
            view=CategorySelectView(self.base_type, selected_level)
        )

class LevelSelectView(discord.ui.View):
    def __init__(self, base_type: str):
        super().__init__(timeout=None)
        self.add_item(LevelSelect(base_type))

# ⬇️ Derde dropdown: Farm / War / Trophy / Hybrid
class CategorySelect(discord.ui.Select):
    def __init__(self, base_type: str, level: str):
        self.base_type = base_type
        self.level = level

        options = [
            discord.SelectOption(label="Farm", value="farm"),
            discord.SelectOption(label="War", value="war"),
            discord.SelectOption(label="Trophy", value="trophy"),
            discord.SelectOption(label="Hybrid", value="hybrid")
        ]

        super().__init__(placeholder="Select base type...", options=options, custom_id="category_select")

    async def callback(self, interaction: discord.Interaction):
        cat = self.values[0]

        response = supabase_second.table("bases") \
            .select("slug") \
            .eq("level", self.level) \
            .eq("cat", cat) \
            .limit(50) \
            .execute()

        if not response.data:
            await interaction.response.edit_message(
                content=f"❌ No base found for **{self.level}** in category **{cat}**.",
                view=None
            )
            return

        base = random.choice(response.data)
        base_slug = base["slug"]
        url = f"https://www.baseforcoc.com/homebase/{self.level}/{base_slug}"

        await interaction.response.edit_message(
            content=f"🎯 Here's a **{cat}** base for **{self.level.upper()}**:\n{url}",
            view=BaseLinkButton(url)
        )

class CategorySelectView(discord.ui.View):
    def __init__(self, base_type: str, level: str):
        super().__init__(timeout=None)
        self.add_item(CategorySelect(base_type, level))

# ⬇️ Cog met commands
class GetBase(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="getbase")
    async def getbase_command(self, ctx):
        await ctx.send(
            "Please select the type of base you're looking for:",
            view=BaseTypeView()
        )

    @commands.command(name="sendstartbutton")
    @commands.has_permissions(administrator=True)
    async def send_start_button(self, ctx):
        channel_id = 1388587917940756530  # pas eventueel aan
        channel = self.bot.get_channel(channel_id)

        if not channel:
            await ctx.send("❌ Channel not found.")
            return

        message = await channel.send(
            "**Search for a Clash of Clans base!**",
            view=StartButtonView()
        )
        await message.pin()
        await ctx.send(f"📌 Start button sent and pinned in <#{channel_id}>")

# ⬇️ Register de cog
async def setup(bot):
    await bot.add_cog(GetBase(bot))
    print("✅ GetBase Cog loaded")
