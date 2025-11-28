import discord
from discord.ext import commands
import os, sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from storage import DataStorage
except:
    DataStorage = None


class ProfileSystem(commands.Cog):
    def __init__(self, bot, storage):
        self.bot = bot
        self.storage = storage

    @commands.Cog.listener()
    async def on_ready(self):
        print("✅ ProfileSystem Loaded")

    # -----------------------------------------
    # LEVEL FORMULA
    # -----------------------------------------
    def calculate_level(self, xp):
        base_xp = 100
        multiplier = 1.5
        level = 0
        required_xp = 0

        while xp >= required_xp:
            level += 1
            required_xp = base_xp * (multiplier ** (level - 1))

        current_level = level - 1

        if current_level == 0:
            previous_xp = 0
            current_required_xp = base_xp
        else:
            previous_xp = base_xp * (multiplier ** (current_level - 1))
            current_required_xp = base_xp * (multiplier ** current_level) - previous_xp

        current_xp_in_level = xp - previous_xp

        return {
            'level': current_level,
            'current_xp': int(current_xp_in_level),
            'required_xp': int(current_required_xp),
            'progress_percentage': int((current_xp_in_level / current_required_xp) * 100),
            'total_xp': xp
        }

    def create_progress_bar(self, percentage, length=20):
        filled = int(length * percentage / 100)
        empty = length - filled
        return '█' * filled + '░' * empty

    # -----------------------------------------
    # PROFILE COMMAND
    # -----------------------------------------
    @commands.command()
    async def profile(self, ctx, member: discord.Member = None):

        target = member or ctx.author

        if not self.storage:
            await ctx.send("❌ Storage not loaded.")
            return

        profile_data = self.storage.get_user_profile(target.id, ctx.guild.id)

        if not profile_data:
            await ctx.send("❌ No profile data found.")
            return

        # XP FROM LEVEL SYSTEM
        level_cog = self.bot.get_cog("LevelSystem")

        guild_id = str(ctx.guild.id)
        user_id = str(target.id)

        if level_cog and hasattr(level_cog, "user_data"):
            total_xp = level_cog.user_data.get(guild_id, {}) \
                .get(user_id, {}).get("xp", 0)
            messages_sent = level_cog.user_data.get(guild_id, {}) \
                .get(user_id, {}).get("messages", 0)
        else:
            total_xp = 0
            messages_sent = 0

        level_info = self.calculate_level(total_xp)
        progress_bar = self.create_progress_bar(level_info["progress_percentage"])

        embed = discord.Embed(
            title=f"{target.display_name}'s Profile",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="Level",
            value=(
                f"**Level {level_info['level']}**\n"
                f"{progress_bar}\n"
                f"{level_info['current_xp']}/{level_info['required_xp']} XP"
            ),
            inline=False
        )

        embed.add_field(
            name="Messages",
            value=f"{messages_sent:,}"
        )

        embed.set_thumbnail(url=target.display_avatar.url)

        await ctx.send(embed=embed)

    # ---------------------------------------------------------------------
    # CUSTOMIZATION COMMANDS
    # ---------------------------------------------------------------------

    @commands.command()
    async def setbio(self, ctx, *, bio: str = None):

        if not self.storage:
            await ctx.send("❌ Storage unavailable.")
            return

        if not bio:
            await ctx.send("❌ Usage: !setbio <text>")
            return

        if len(bio) > 200:
            await ctx.send("❌ Bio too long (200 chars max).")
            return

        self.storage.update_user_profile(ctx.author.id, ctx.guild.id, {'bio': bio})

        embed = discord.Embed(
            title="📝 Bio updated!",
            description=bio,
            color=discord.Color.green(),
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def settitle(self, ctx, *, title: str = None):

        if not self.storage:
            await ctx.send("❌ Storage unavailable.")
            return

        if not title:
            await ctx.send("❌ Usage: !settitle <text>")
            return

        if len(title) > 25:
            await ctx.send("❌ Title too long (25 chars max).")
            return

        self.storage.update_user_profile(ctx.author.id, ctx.guild.id, {'title': title})

        embed = discord.Embed(
            title="🎖️ Title updated!",
            description=title,
            color=discord.Color.gold(),
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def profilehelp(self, ctx):
        embed = discord.Embed(
            title="👤 Profile Commands",
            color=discord.Color.blue(),
        )

        embed.add_field(
            name="Commands",
            value=(
                "`!profile [@user]`\n"
                "`!setbio <text>`\n"
                "`!settitle <text>`\n"
                "`!banners`\n"
                "`!setbanner`\n"
            ),
            inline=False
        )

        await ctx.send(embed=embed)


# ---------------------------------------------------------------------
# COG SETUP
# ---------------------------------------------------------------------

async def setup(bot):
    try:
        storage = DataStorage()
    except:
        storage = None

    await bot.add_cog(ProfileSystem(bot, storage))
    print("✅ ProfileSystem cog loaded successfully!")
