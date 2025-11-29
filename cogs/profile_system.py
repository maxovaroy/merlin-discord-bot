import discord
from discord.ext import commands
import sys
import os
from database import get_user


# Add parent directory to sys.path (for storage import)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from storage import DataStorage
    STORAGE_AVAILABLE = True
except ImportError as e:
    print(f"❌ Storage module not found: {e}")
    STORAGE_AVAILABLE = False


class ProfileSystem(commands.Cog):
    """Enhanced profile system with XP, levels, banners, bio, and titles."""

    def __init__(self, bot, storage=None):
        self.bot = bot
        self.storage = storage

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"✅ {self.__class__.__name__} cog loaded successfully!")

    # -----------------------------------------
    # LEVEL CALCULATION & PROGRESS BAR
    # -----------------------------------------
    def calculate_level(self, xp: int):
        base_xp = 100
        multiplier = 1.5
        level = 0
        required_xp = 0

        while xp >= required_xp:
            level += 1
            required_xp = base_xp * (multiplier ** (level - 1))

        current_level = level - 1
        previous_xp = base_xp * (multiplier ** (current_level - 1)) if current_level > 0 else 0
        current_required_xp = (base_xp * (multiplier ** current_level)) - previous_xp if current_level > 0 else base_xp
        current_xp_in_level = xp - previous_xp
        progress_percentage = min(100, int((current_xp_in_level / current_required_xp) * 100)) if current_required_xp > 0 else 100

        return {
            "level": current_level,
            "current_xp": int(current_xp_in_level),
            "required_xp": int(current_required_xp),
            "progress_percentage": progress_percentage,
            "total_xp": xp
        }

    def create_progress_bar(self, percentage: int, length: int = 20):
        filled = int(length * percentage / 100)
        empty = length - filled
        return "█" * filled + "░" * empty

    # -----------------------------------------
    # PROFILE COMMAND
    # -----------------------------------------
    @commands.command()
    async def profile(self, ctx, member: discord.Member = None):
        """Display a user's profile with XP, level, banners, and stats."""
        target = member or ctx.author

        if not self.storage:
            await ctx.send("❌ Storage system unavailable.")
            return

        profile_data = self.storage.get_user_profile(target.id, ctx.guild.id)
        if not profile_data:
            await ctx.send("❌ Profile not found. Start chatting to create your profile!")
            return

        db_user = await get_user(target.id)
        
        if db_user:
            total_xp = db_user[0]
            level = db_user[1]
            messages_sent = db_user[2]
        else:
            total_xp = 0
            level = 0
            messages_sent = 0

        level_info = self.calculate_level(total_xp)
        progress_bar = self.create_progress_bar(level_info["progress_percentage"])

        # Banner info
        banner_id = profile_data.get("banner", "assassin")
        banner_name = "Assassin"
        banner_emoji = "🗡️"
        banner_color = "#7289DA"
        banner_url = None

        banner_cog = self.bot.get_cog("BannerSystem")
        if banner_cog and hasattr(banner_cog, "available_banners"):
            banner_info = banner_cog.available_banners.get(banner_id, None)
            if banner_info:
                banner_name = banner_info.get("name", banner_name)
                banner_emoji = banner_info.get("emoji", banner_emoji)
                banner_color = banner_info.get("color", banner_color)
                banner_url = banner_info.get("banner_url", None)

        # Embed
        embed_color = discord.Color(int(banner_color.strip("#"), 16)) if banner_color else discord.Color.blue()
        embed = discord.Embed(
            title=f"{banner_emoji} {target.display_name}'s Profile",
            color=embed_color
        )
        if banner_url:
            embed.set_image(url=banner_url)

        embed.add_field(
            name="🎯 Level & XP",
            value=f"**Level {level_info['level']}**\n{progress_bar}\n{level_info['current_xp']}/{level_info['required_xp']} XP",
            inline=True
        )

        embed.add_field(
            name="🎨 Banner",
            value=f"{banner_emoji} **{banner_name}**",
            inline=True
        )

        # Additional stats
        reputation = profile_data.get("reputation", 0)
        join_date = profile_data.get("join_date", "Unknown")
        embed.add_field(
            name="📊 Stats",
            value=f"**Messages:** {messages_sent:,}\n**Reputation:** {reputation}\n**Joined:** {join_date}",
            inline=False
        )

        # Achievements
        try:
            achievement_cog = self.bot.get_cog("AchievementSystem")
            if achievement_cog:
                user_achievements = self.storage.get_achievements(target.id, ctx.guild.id)
                if user_achievements:
                    completed = len([a for a in user_achievements if a.get("completed", False)])
                    embed.add_field(
                        name="🏆 Achievements",
                        value=f"**{completed}/{len(user_achievements)}** completed",
                        inline=True
                    )
        except:
            pass

        embed.set_thumbnail(url=target.display_avatar.url)
        embed.set_footer(text="Use !banners to view available banners | !setbanner to change")

        await ctx.send(embed=embed)

    # -----------------------------------------
    # BIO & TITLE COMMANDS
    # -----------------------------------------
    @commands.command()
    async def setbio(self, ctx, *, bio: str = None):
        if not self.storage:
            await ctx.send("❌ Storage unavailable.")
            return
        if not bio:
            await ctx.send("❌ Provide a bio: `!setbio I love coding!`")
            return
        if len(bio) > 200:
            await ctx.send("❌ Bio too long (max 200 chars).")
            return
        self.storage.update_user_profile(ctx.author.id, ctx.guild.id, {"bio": bio})
        embed = discord.Embed(title="📝 Bio Updated!", description=bio, color=discord.Color.green())
        await ctx.send(embed=embed)

    @commands.command()
    async def settitle(self, ctx, *, title: str = None):
        if not self.storage:
            await ctx.send("❌ Storage unavailable.")
            return
        if not title:
            await ctx.send("❌ Provide a title: `!settitle Pro Coder`")
            return
        if len(title) > 25:
            await ctx.send("❌ Title too long (max 25 chars).")
            return
        self.storage.update_user_profile(ctx.author.id, ctx.guild.id, {"title": title})
        embed = discord.Embed(title="🎖️ Title Updated!", description=title, color=discord.Color.gold())
        await ctx.send(embed=embed)

    # -----------------------------------------
    # HELP COMMAND
    # -----------------------------------------
    @commands.command()
    async def profilehelp(self, ctx):
        embed = discord.Embed(title="👤 Profile Help", description="Manage your profile!", color=discord.Color.blue())
        embed.add_field(
            name="Commands",
            value=(
                "`!profile [@user]`\n"
                "`!setbio <text>`\n"
                "`!settitle <text>`\n"
                "`!banners`\n"
                "`!setbanner <name>`\n"
                "`!achievements [@user]`"
            ),
            inline=False
        )
        await ctx.send(embed=embed)

    # -----------------------------------------
    # BACKWARD COMPATIBILITY
    # -----------------------------------------
    @commands.command()
    async def backgrounds(self, ctx):
        await ctx.send("🔄 Use `!banners` instead.")

    @commands.command()
    async def setbackground(self, ctx, *, background_name: str):
        await ctx.send("🔄 Use `!setbanner` instead.")

    @commands.command()
    async def userbackgrounds(self, ctx, member: discord.Member = None):
        await ctx.send("🔄 Use `!userbanners` instead.")

    @commands.command()
    async def givebackground(self, ctx, member: discord.Member, *, background_name: str):
        await ctx.send("🔄 Use `!givebanner` instead.")

    @commands.command()
    async def giveallbackgrounds(self, ctx, member: discord.Member = None):
        await ctx.send("🔄 Use `!giveallbanners` instead.")

    @commands.command()
    async def cmdcheck(self, ctx):
        commands_list = [cmd.name for cmd in self.get_commands()]
        await ctx.send(f"📋 Commands: {', '.join(commands_list)}")


# -----------------------------------------
# COG SETUP
# -----------------------------------------
async def setup(bot):
    try:
        storage = DataStorage() if STORAGE_AVAILABLE else None
        await bot.add_cog(ProfileSystem(bot, storage))
        print("✅ ProfileSystem loaded successfully!")
    except Exception as e:
        print(f"❌ Failed to load ProfileSystem: {e}")
        await bot.add_cog(ProfileSystem(bot, None))

