import discord
from discord.ext import commands

class WelcomeMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="sendwelcomemessage")
    @commands.has_permissions(administrator=True)
    async def send_welcome_message(self, ctx):
        embed = discord.Embed(
            title="📜 Welcome to Clash Base Developer!",
            description=(
                "We're excited to have you here in our thriving community of Clash strategists and developers!\n\n"
                "**Before you dive in, please take a moment to read and follow our rules.** "
                "These help keep the server safe, fun, and respectful for everyone. 🚀"
            ),
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="1️⃣ Be Respectful",
            value="Treat everyone with respect. No harassment, hate speech, or personal attacks will be tolerated.",
            inline=False
        )
        embed.add_field(
            name="2️⃣ No Spam or Self-Promotion",
            value="Don't advertise other servers, websites, or YouTube channels without permission. No mass invites or DM spam.",
            inline=False
        )
        embed.add_field(
            name="3️⃣ Use the Right Channels",
            value="Each channel has a purpose. Stick to it. For example, don't post memes in serious discussion threads.",
            inline=False
        )
        embed.add_field(
            name="4️⃣ Keep it Family-Friendly",
            value="No NSFW content. This includes usernames, profile pics, text, media, or anything else.",
            inline=False
        )
        embed.add_field(
            name="5️⃣ English Only",
            value="Please keep all messages in English to ensure moderators can understand and help everyone.",
            inline=False
        )
        embed.add_field(
            name="6️⃣ Respect Staff Decisions",
            value="Moderators and admins work hard to maintain a fair and safe space. Follow their guidance.",
            inline=False
        )

        embed.set_footer(text="By being here, you agree to follow these rules. Let’s build something epic together!")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(WelcomeMessage(bot))
