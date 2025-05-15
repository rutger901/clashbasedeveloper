import discord
import coc
from discord.ext import commands
from supabase_client import supabase
from coc_client import create_coc_client

class LinkModal(discord.ui.Modal, title="🔗 Link je Clash of Clans account"):
    player_tag = discord.ui.TextInput(
        label="Voer je Player Tag in (bijv. #ABC123)",
        placeholder="#...",
        required=True,
        max_length=15
    )

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        tag_input = str(self.player_tag).strip().upper()

        print(f"[DEBUG] Gebruikersinvoer: {self.player_tag}")
        print(f"[DEBUG] Verwerkte tag: {tag_input}")

        coc_client = await create_coc_client()

        if coc_client is None:
            print("[ERROR] CoC client kon niet worden aangemaakt.")
            await interaction.response.send_message("❌ Fout bij het verbinden met de CoC API. Check logs.", ephemeral=True)
            return

        try:
            player = await coc_client.get_player(tag_input)
        except coc.NotFound:
            print("[ERROR] Tag niet gevonden in CoC API")
            await interaction.response.send_message("❌ Ongeldige player tag.", ephemeral=True)
            return
        except Exception as e:
            print(f"[ERROR] Onverwachte fout: {e}")
            await interaction.response.send_message("❌ Onbekende fout bij koppelen.", ephemeral=True)
            return

        print(f"[SUCCESS] {interaction.user.name} heeft gekoppeld: {player.name} ({player.tag})")

        supabase.table("linked_accounts").upsert({
            "user_id": str(interaction.user.id),
            "player_tag": player.tag,
            "player_name": player.name,
            "town_hall": player.town_hall
        }).execute()

        embed = discord.Embed(
            title="✅ Account Gelinkt",
            description=f"Je hebt succesvol **{player.name}** gekoppeld!",
            color=discord.Color.green()
        )
        embed.add_field(name="Tag", value=player.tag)
        embed.add_field(name="Town Hall", value=str(player.town_hall))
        await interaction.response.send_message(embed=embed, ephemeral=True)

class LinkButton(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="🔗 Link Account", style=discord.ButtonStyle.blurple, custom_id="link_account_button")
    async def link_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(LinkModal(self.bot))

class ClashLink(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="link_account")
    async def link_account_command(self, ctx):
        embed = discord.Embed(
            title="🔗 Link je Clash of Clans account",
            description="Klik op de knop hieronder om je player tag in te voeren.",
            color=discord.Color.blurple()
        )
        await ctx.send(embed=embed, view=LinkButton(self.bot))

async def setup(bot):
    await bot.add_cog(ClashLink(bot))
