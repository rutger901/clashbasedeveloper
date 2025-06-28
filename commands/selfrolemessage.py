# commands/selfrolemessage.py

import asyncio
import discord
from discord.ext import commands
from supabase_client import supabase_main

# ───── CONSTANTEN ─────────────────────────────────────────────────────────────

SELFROLES_CATEGORY_ID = 1047161799730020442  # De categorie-id voor persoonlijke kanalen

# ───── HELPERS ─────────────────────────────────────────────────────────────────

async def get_all_th_roles():
    resp = supabase_main.table("th_roles").select("*").execute()
    return resp.data or []

async def get_all_bh_roles():
    resp = supabase_main.table("bh_roles").select("*").execute()
    return resp.data or []

def upsert_user_selection(user_id: int, th_ids=None, bh_ids=None, channel_id=None, message_id=None):
    payload = {"user_id": user_id}
    if th_ids is not None:
        payload["th_ids"] = th_ids
    if bh_ids is not None:
        payload["bh_ids"] = bh_ids
    if channel_id is not None:
        payload["channel_id"] = channel_id
    if message_id is not None:
        payload["message_id"] = message_id
    supabase_main.table("user_main_messages").upsert(payload).execute()

def get_user_selection(user_id: int):
    resp = (
        supabase_main
        .table("user_main_messages")
        .select("*")
        .eq("user_id", user_id)
        .maybe_single()
        .execute()
    )
    return resp.data

# ───── EMBED BUILDER ────────────────────────────────────────────────────────────

def build_role_overview_embed(member: discord.Member):
    row = get_user_selection(member.id) or {}
    th_ids = row.get("th_ids") or []
    bh_ids = row.get("bh_ids") or []

    # Haal emoji‐gegevens op uit Supabase in plaats van labels
    th_records = (
        supabase_main
        .table("th_roles")
        .select("emoji_id", "emoji_name")
        .in_("role_id", th_ids)
        .execute()
        .data
        or []
    )
    th_labels = [f"<:{r['emoji_name']}:{r['emoji_id']}>" for r in th_records]

    bh_records = (
        supabase_main
        .table("bh_roles")
        .select("emoji_id", "emoji_name")
        .in_("role_id", bh_ids)
        .execute()
        .data
        or []
    )
    bh_labels = [f"<:{r['emoji_name']}:{r['emoji_id']}>" for r in bh_records]

    embed = discord.Embed(
        title=f"{member.display_name}'s Role Overview",
        color=discord.Color.gold(),
        description="Below are the roles you chose:"
    )
    embed.add_field(name="🏠 Town Hall", value=" ".join(th_labels) or "None", inline=False)
    embed.add_field(name="🛠 Builder Hall", value=" ".join(bh_labels) or "None", inline=False)
    return embed

# ───── PERSOONSGEBONDEN KANAAL AANMAKEN ────────────────────────────────────────

async def create_personal_selfroles_channel(member: discord.Member):
    guild = member.guild
    category = guild.get_channel(SELFROLES_CATEGORY_ID)
    if category is None:
        return  # categorie bestaat niet of bot mist rechten

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        member: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
    }

    # Wissel bestaand kanaal uit
    existing = discord.utils.get(guild.text_channels, name=f"roles-{member.name}".lower())
    if existing:
        await existing.delete()

    channel = await guild.create_text_channel(
        name=f"roles-{member.name}".lower(),
        overwrites=overwrites,
        category=category
    )

    embed = build_role_overview_embed(member)
    view = OverviewView(member)
    msg = await channel.send(content=member.mention, embed=embed, view=view)

    upsert_user_selection(member.id, channel_id=channel.id, message_id=msg.id)

# ───── INITIAL DROPDOWNS (WELCOME‐KANAAL) ───────────────────────────────────────

class InitialTHSelect(discord.ui.Select):
    def __init__(self, member: discord.Member, th_options):
        options = []
        for r in th_options:
            label    = r["label"]
            role_id  = r["role_id"]
            emoji    = discord.PartialEmoji(id=r["emoji_id"], name=r["emoji_name"])
            role_obj = member.guild.get_role(role_id)
            default  = role_obj in member.roles if role_obj else False
            options.append(discord.SelectOption(label=label, value=str(role_id), emoji=emoji, default=default))

        super().__init__(
            placeholder="Select your Town Hall level(s)",
            min_values=1,
            max_values=len(options),
            options=options,
            custom_id="initial_th_role_selector"
        )
        self.member = member

    async def callback(self, interaction: discord.Interaction):
        member       = interaction.user
        selected_ids = [int(v) for v in self.values]

        # Rollen toekennen/verwijderen
        all_th     = await get_all_th_roles()
        all_th_ids = {r["role_id"] for r in all_th}

        to_add, to_remove = [], []
        for rid in all_th_ids:
            role_obj = interaction.guild.get_role(rid)
            if rid in selected_ids and role_obj not in member.roles:
                to_add.append(role_obj)
            if rid not in selected_ids and role_obj in member.roles:
                to_remove.append(role_obj)
        if to_add:
            await member.add_roles(*to_add)
        if to_remove:
            await member.remove_roles(*to_remove)

        # Bewaar in Supabase
        upsert_user_selection(member.id, th_ids=selected_ids)

        # **Stuur rechtstreeks de BH‐dropdown in hetzelfde kanaal**
        channel = interaction.channel
        await channel.send(
            "✅ Town Hall saved. Now select your Builder Hall level(s):",
            view=InitialBHSelectView(member, await get_all_bh_roles())
        )
        # Let op: we laten dit dropdown‐bericht in het kanaal staan totdat BH‐selectie is afgerond.

class InitialTHSelectView(discord.ui.View):
    def __init__(self, member: discord.Member, th_options):
        super().__init__(timeout=None)
        self.add_item(InitialTHSelect(member, th_options))

class InitialBHSelect(discord.ui.Select):
    def __init__(self, member: discord.Member, bh_options):
        options = []
        for r in bh_options:
            label    = r["label"]
            role_id  = r["role_id"]
            emoji    = discord.PartialEmoji(id=r["emoji_id"], name=r["emoji_name"])
            role_obj = member.guild.get_role(role_id)
            default  = role_obj in member.roles if role_obj else False
            options.append(discord.SelectOption(label=label, value=str(role_id), emoji=emoji, default=default))

        super().__init__(
            placeholder="Select your Builder Hall level(s)",
            min_values=1,
            max_values=len(options),
            options=options,
            custom_id="initial_bh_role_selector"
        )
        self.member = member

    async def callback(self, interaction: discord.Interaction):
        member       = interaction.user
        selected_ids = [int(v) for v in self.values]

        # Rollen toekennen/verwijderen
        all_bh     = await get_all_bh_roles()
        all_bh_ids = {r["role_id"] for r in all_bh}

        to_add, to_remove = [], []
        for rid in all_bh_ids:
            role_obj = interaction.guild.get_role(rid)
            if rid in selected_ids and role_obj not in member.roles:
                to_add.append(role_obj)
            if rid not in selected_ids and role_obj in member.roles:
                to_remove.append(role_obj)
        if to_add:
            await member.add_roles(*to_add)
        if to_remove:
            await member.remove_roles(*to_remove)

        # Bewaar in Supabase
        upsert_user_selection(member.id, bh_ids=selected_ids)

        # **Maak persoonlijk kanaal én stuur follow‐up**
        await interaction.response.send_message(
            "✅ All done! Your personal Role Overview channel has been created.",
            ephemeral=True
        )
        await create_personal_selfroles_channel(member)

        # **Vervolgens het welcome‐kanaal weggooien**
        try:
            await interaction.channel.delete()
        except (discord.Forbidden, discord.HTTPException):
            pass

class InitialBHSelectView(discord.ui.View):
    def __init__(self, member: discord.Member, bh_options):
        super().__init__(timeout=None)
        self.add_item(InitialBHSelect(member, bh_options))

# ───── EDIT‐DROPDOWNS (OVERVIEW‐KANAAL) ─────────────────────────────────────────

class EditTHSelect(discord.ui.Select):
    def __init__(self, member: discord.Member, th_options, dropdown_msg_id: int, dropdown_channel_id: int, overview_msg_id: int, overview_channel_id: int):
        options = []
        sel = get_user_selection(member.id) or {}
        saved_th_ids = set(sel.get("th_ids") or [])

        for r in th_options:
            label   = r["label"]
            role_id = r["role_id"]
            emoji   = discord.PartialEmoji(id=r["emoji_id"], name=r["emoji_name"])
            default = (role_id in saved_th_ids)
            options.append(discord.SelectOption(label=label, value=str(role_id), emoji=emoji, default=default))

        super().__init__(
            placeholder="Select your Town Hall level(s)",
            min_values=1,
            max_values=len(options),
            options=options,
            custom_id="edit_th_role_selector"
        )
        self.member              = member
        self.dropdown_msg_id     = dropdown_msg_id
        self.dropdown_channel_id = dropdown_channel_id
        self.overview_msg_id     = overview_msg_id
        self.overview_channel_id = overview_channel_id

    async def callback(self, interaction: discord.Interaction):
        member       = interaction.user
        selected_ids = [int(v) for v in self.values]

        # 1) Rollen toekennen / verwijderen
        all_th     = await get_all_th_roles()
        all_th_ids = {r["role_id"] for r in all_th}

        to_add, to_remove = [], []
        for rid in all_th_ids:
            role_obj = interaction.guild.get_role(rid)
            if rid in selected_ids and role_obj not in member.roles:
                to_add.append(role_obj)
            if rid not in selected_ids and role_obj in member.roles:
                to_remove.append(role_obj)
        if to_add:
            await member.add_roles(*to_add)
        if to_remove:
            await member.remove_roles(*to_remove)

        # 2) Bewaar nieuwe th_ids in Supabase
        upsert_user_selection(member.id, th_ids=selected_ids)

        # 3) Werk overview‐embed bij
        overview_chan = interaction.guild.get_channel(self.overview_channel_id)
        if overview_chan:
            try:
                overview_msg = await overview_chan.fetch_message(self.overview_msg_id)
                await overview_msg.edit(embed=build_role_overview_embed(member), view=OverviewView(member))
            except discord.NotFound:
                pass

        # 4) Verwijder de dropdown‐message uit personal kanaal
        dropdown_chan = interaction.guild.get_channel(self.dropdown_channel_id)
        if dropdown_chan:
            try:
                dropdown_msg = await dropdown_chan.fetch_message(self.dropdown_msg_id)
                await dropdown_msg.delete()
            except discord.NotFound:
                pass

        # 5) Stuur korte bevestiging in personal kanaal en verwijder na 3 seconden
        if overview_chan:
            temp = await overview_chan.send(f"{member.mention} ✅ Town Hall updated!")
            await asyncio.sleep(3)
            try:
                await temp.delete()
            except:
                pass

        # 6) ACK (wrapped in try/except om “Unknown interaction” te voorkomen)
        try:
            await interaction.response.defer()
        except discord.errors.NotFound:
            pass

class EditTHSelectView(discord.ui.View):
    def __init__(self, member: discord.Member, th_options, dropdown_msg_id: int, dropdown_channel_id: int, overview_msg_id: int, overview_channel_id: int):
        super().__init__(timeout=None)
        self.add_item(EditTHSelect(member, th_options, dropdown_msg_id, dropdown_channel_id, overview_msg_id, overview_channel_id))


class EditBHSelect(discord.ui.Select):
    def __init__(self, member: discord.Member, bh_options, dropdown_msg_id: int, dropdown_channel_id: int, overview_msg_id: int, overview_channel_id: int):
        options = []
        sel = get_user_selection(member.id) or {}
        saved_bh_ids = set(sel.get("bh_ids") or [])

        for r in bh_options:
            label   = r["label"]
            role_id = r["role_id"]
            emoji   = discord.PartialEmoji(id=r["emoji_id"], name=r["emoji_name"])
            default = (role_id in saved_bh_ids)
            options.append(discord.SelectOption(label=label, value=str(role_id), emoji=emoji, default=default))

        super().__init__(
            placeholder="Select your Builder Hall level(s)",
            min_values=1,
            max_values=len(options),
            options=options,
            custom_id="edit_bh_role_selector"
        )
        self.member              = member
        self.dropdown_msg_id     = dropdown_msg_id
        self.dropdown_channel_id = dropdown_channel_id
        self.overview_msg_id     = overview_msg_id
        self.overview_channel_id = overview_channel_id

    async def callback(self, interaction: discord.Interaction):
        member       = interaction.user
        selected_ids = [int(v) for v in self.values]

        # 1) Rollen toekennen / verwijderen
        all_bh     = await get_all_bh_roles()
        all_bh_ids = {r["role_id"] for r in all_bh}

        to_add, to_remove = [], []
        for rid in all_bh_ids:
            role_obj = interaction.guild.get_role(rid)
            if rid in selected_ids and role_obj not in member.roles:
                to_add.append(role_obj)
            if rid not in selected_ids and role_obj in member.roles:
                to_remove.append(role_obj)
        if to_add:
            await member.add_roles(*to_add)
        if to_remove:
            await member.remove_roles(*to_remove)

        # 2) Bewaar nieuwe bh_ids in Supabase
        upsert_user_selection(member.id, bh_ids=selected_ids)

        # 3) Werk overview‐embed bij
        overview_chan = interaction.guild.get_channel(self.overview_channel_id)
        if overview_chan:
            try:
                overview_msg = await overview_chan.fetch_message(self.overview_msg_id)
                await overview_msg.edit(embed=build_role_overview_embed(member), view=OverviewView(member))
            except discord.NotFound:
                pass

        # 4) Verwijder de dropdown‐message uit personal kanaal
        dropdown_chan = interaction.guild.get_channel(self.dropdown_channel_id)
        if dropdown_chan:
            try:
                dropdown_msg = await dropdown_chan.fetch_message(self.dropdown_msg_id)
                await dropdown_msg.delete()
            except discord.NotFound:
                pass

        # 5) Stuur korte bevestiging in personal kanaal en verwijder na 3 seconden
        if overview_chan:
            temp = await overview_chan.send(f"{member.mention} ✅ Builder Hall updated!")
            await asyncio.sleep(3)
            try:
                await temp.delete()
            except:
                pass

        # 6) ACK (wrapped in try/except om “Unknown interaction” te voorkomen)
        try:
            await interaction.response.defer()
        except discord.errors.NotFound:
            pass

class EditBHSelectView(discord.ui.View):
    def __init__(self, member: discord.Member, bh_options, dropdown_msg_id: int, dropdown_channel_id: int, overview_msg_id: int, overview_channel_id: int):
        super().__init__(timeout=None)
        self.add_item(EditBHSelect(member, bh_options, dropdown_msg_id, dropdown_channel_id, overview_msg_id, overview_channel_id))

# ───── OVERVIEW VIEW ───────────────────────────────────────────────────────────

class OverviewView(discord.ui.View):
    def __init__(self, member: discord.Member):
        super().__init__(timeout=None)
        self.member = member

    @discord.ui.button(label="Save Town Hall", style=discord.ButtonStyle.primary, custom_id="btn_edit_th")
    async def edit_th(self, interaction: discord.Interaction, button: discord.ui.Button):
        sel = get_user_selection(self.member.id)
        if not sel:
            return await interaction.response.send_message("❌ No overview found.", ephemeral=True)

        overview_channel_id = sel.get("channel_id")
        overview_msg_id     = sel.get("message_id")
        if not overview_channel_id or not overview_msg_id:
            return await interaction.response.send_message("❌ No overview message to edit.", ephemeral=True)

        overview_chan = interaction.guild.get_channel(overview_channel_id)
        if not overview_chan:
            return await interaction.response.send_message("❌ Could not find your personal channel.", ephemeral=True)

        # Haal opnieuw de meest recente TH‐opties
        th_opts = await get_all_th_roles()

        # 1) Maak de dropdown‐bericht in het persoonlijke kanaal
        dropdown_channel = overview_chan
        dropdown_msg = await dropdown_channel.send(
            "Please select your Town Hall level(s):",
            view=EditTHSelectView(
                self.member,
                th_opts,
                dropdown_msg_id=None,  # vul hieronder in na het versturen
                dropdown_channel_id=dropdown_channel.id,
                overview_msg_id=overview_msg_id,
                overview_channel_id=overview_channel_id
            )
        )
        # 2) Nu we know dropdown_msg.id, updaten we de view zodat de select weet wat te verwijderen
        await dropdown_msg.edit(
            view=EditTHSelectView(
                self.member,
                th_opts,
                dropdown_msg.id,
                dropdown_channel.id,
                overview_msg_id,
                overview_channel_id
            )
        )

        # ACK dat dropdown is gepost
        await interaction.response.defer()

    @discord.ui.button(label="Save Builder Hall", style=discord.ButtonStyle.secondary, custom_id="btn_edit_bh")
    async def edit_bh(self, interaction: discord.Interaction, button: discord.ui.Button):
        sel = get_user_selection(self.member.id)
        if not sel:
            return await interaction.response.send_message("❌ No overview found.", ephemeral=True)

        overview_channel_id = sel.get("channel_id")
        overview_msg_id     = sel.get("message_id")
        if not overview_channel_id or not overview_msg_id:
            return await interaction.response.send_message("❌ No overview message to edit.", ephemeral=True)

        overview_chan = interaction.guild.get_channel(overview_channel_id)
        if not overview_chan:
            return await interaction.response.send_message("❌ Could not find your personal channel.", ephemeral=True)

        # Haal opnieuw de meest recente BH‐opties
        bh_opts = await get_all_bh_roles()

        # 1) Maak de dropdown‐bericht in het persoonlijke kanaal
        dropdown_channel = overview_chan
        dropdown_msg = await dropdown_channel.send(
            "Please select your Builder Hall level(s):",
            view=EditBHSelectView(
                self.member,
                bh_opts,
                dropdown_msg_id=None,  # vul hieronder in na het versturen
                dropdown_channel_id=dropdown_channel.id,
                overview_msg_id=overview_msg_id,
                overview_channel_id=overview_channel_id
            )
        )
        # 2) Nu we know dropdown_msg.id, updaten we de view zodat de select weet wat te verwijderen
        await dropdown_msg.edit(
            view=EditBHSelectView(
                self.member,
                bh_opts,
                dropdown_msg.id,
                dropdown_channel.id,
                overview_msg_id,
                overview_channel_id
            )
        )

        # ACK dat dropdown is gepost
        await interaction.response.defer()

# ───── COG SETUP ──────────────────────────────────────────────────────────────

class SelfRoleMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild    = member.guild
        category = discord.utils.get(guild.categories, name="✅｜start")

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            member: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        channel = await guild.create_text_channel(
            name=f"welcome-{member.name}".lower(),
            overwrites=overwrites,
            category=category
        )

        welcome_embed = discord.Embed(
            title=f"👋 Welcome {member.display_name}!",
            description=(
                "First, please select your **Town Hall** level(s) below.\n"
                "Once you’ve chosen, you’ll be prompted to choose your **Builder Hall** level."
            ),
            color=discord.Color.blurple()
        )
        await channel.send(embed=welcome_embed)

        th_opts = await get_all_th_roles()
        await channel.send(content=member.mention, view=InitialTHSelectView(member, th_opts))

    @commands.command(name="rebuild_overview")
    @commands.has_permissions(administrator=True)
    async def rebuild_overview_command(self, ctx, member: discord.Member):
        sel = get_user_selection(member.id)
        if not sel or not sel.get("channel_id") or not sel.get("message_id"):
            return await ctx.send("❌ No overview found for that user.")
        chan = ctx.guild.get_channel(sel["channel_id"])
        try:
            msg = await chan.fetch_message(sel["message_id"])
            await msg.edit(embed=build_role_overview_embed(member), view=OverviewView(member))
            await ctx.send("✅ Overview rebuilt.")
        except discord.NotFound:
            await ctx.send("❌ Could not find the channel of message.")

async def setup(bot):
    await bot.add_cog(SelfRoleMessage(bot))
