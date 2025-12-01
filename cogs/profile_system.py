# profile_system.py
import discord
from discord.ext import commands
from typing import Optional

class ProfileSystem(commands.Cog):
    """Profile System with XP, Levels, Banners, Bio, and Title"""

    available_banners = {
        "assassin": {"name": "Assassin", "emoji": "🗡️", "color": "#7289DA"},
        "warrior": {"name": "Warrior", "emoji": "🛡️", "color": "#FF0000"},
        "mage": {"name": "Mage", "emoji": "🔮", "color": "#9400D3"},
    }

    def __init__(self, bot, storage):
        self.bot = bot
        self.storage = storage  # Make sure this is your main DataStorage

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"✅ {self.__class__.__name__} loaded successfully!")

    def calculate_level(self, total_xp: int):
        base_xp = 100
        multiplier = 1.5
        level = 0
        required_xp = 0

        while total_xp >= required_xp:
            level += 1
            required_xp = base_xp * (multiplier ** (level - 1))

        current_level = level - 1
        previous_xp = base_xp * (multiplier ** (current_level - 1)) if current_level > 0 else 0
        current_required_xp = (base_xp * (multiplier ** current_level)) - previous_xp if current_level > 0 else base_xp
        current_xp_in_level = total_xp - previous_xp
        progress_percentage = min(100, int((current_xp_in_level / current_required_xp) * 100)) if current_required_xp > 0 else 100

        return {
            "level": current_level,
            "current_xp": int(current_xp_in_level),
            "required_xp": int(current_required_xp),
            "progress_percentage": progress_percentage,
            "total_xp": total_xp
        }

    def create_progress_bar(self, percentage: int, length: int = 20):
        filled = int(length * percentage / 100)
        empty = length - filled
        return "█" * filled + "░" * empty

    # -----------------------------
    # PROFILE COMMAND
    # -----------------------------
    @commands.command()
    async def profile(self, ctx, member: Optional[discord.Member] = None):
        target = member or ctx.author
        if not self.storage:
            return await ctx.send("❌ Storage not available.")

        # Fetch user profile
        profile_data = self.storage.get_user_profile(target.id, ctx.guild.id)
        if profile_data is None:
            return await ctx.send(f"⚠️ No profile found for {target.display_name}. Start interacting!")

        # If your leveling system is separate, merge XP/messages from it:
        try:
            total_xp = self.storage.leveling.get_xp(target.id)  # replace with your method
            messages = self.storage.leveling.get_messages(target.id)
        except Exception:
            total_xp = profile_data.get("total_xp", 0)
            messages = profile_data.get("messages", 0)

        level_info = self.calculate_level(total_xp)
        progress_bar = self.create_progress_bar(level_info["progress_percentage"])

        # Banner info
        current_banner_id = profile_data.get("banner", "assassin")
        banner_info = self.available_banners.get(current_banner_id, self.available_banners["assassin"])
        banner_name = banner_info["name"]
        banner_emoji = banner_info["emoji"]
        banner_color = int(banner_info["color"].replace("#", ""), 16)

        embed = discord.Embed(
            title=f"📜 Profile: {target.display_name}",
            color=banner_color
        )
        embed.add_field(name="Level", value=f"{level_info['level']} ({level_info['current_xp']}/{level_info['required_xp']})", inline=True)
        embed.add_field(name="Messages Sent", value=messages, inline=True)
        embed.add_field(name="Progress", value=progress_bar, inline=False)
        embed.add_field(name="Current Banner", value=f"{banner_emoji} {banner_name}", inline=False)
        embed.set_footer(text=f"ID: {target.id}")

        await ctx.send(embed=embed)

    # -----------------------------
    # BIO / TITLE COMMANDS
    # -----------------------------
    @commands.command()
    async def setbio(self, ctx, *, bio: str):
        if not self.storage:
            return await ctx.send("❌ Storage unavailable.")
        if not bio or len(bio) > 200:
            return await ctx.send("❌ Bio max 200 characters.")
        self.storage.update_user_profile(ctx.author.id, ctx.guild.id, {"bio": bio})
        await ctx.send(f"✅ Bio updated.")

    @commands.command()
    async def settitle(self, ctx, *, title: str):
        if not self.storage:
            return await ctx.send("❌ Storage unavailable.")
        if not title or len(title) > 25:
            return await ctx.send("❌ Title max 25 characters.")
        self.storage.update_user_profile(ctx.author.id, ctx.guild.id, {"title": title})
        await ctx.send(f"✅ Title updated.")

    # -----------------------------
    # BANNER COMMANDS
    # -----------------------------
    @commands.command(name="showbanners")
    async def show_banners(self, ctx):
        msg = "\n".join([f"{info['emoji']} {info['name']}" for info in self.available_banners.values()])
        await ctx.send(f"📜 Available Banners:\n{msg}")

    @commands.command(name="setbanner")
    async def set_banner(self, ctx, banner_name: str):
        banner_name_lower = banner_name.lower()
        for key, info in self.available_banners.items():
            if banner_name_lower == key or banner_name_lower == info["name"].lower():
                self.storage.update_user_profile(ctx.author.id, ctx.guild.id, {"banner": key})
                return await ctx.send(f"✅ Banner updated to {info['emoji']} {info['name']}")
        await ctx.send("❌ Banner not found. Use `!showbanners`.")

# -----------------------------
# COG SETUP
# -----------------------------
async def setup(bot, storage=None):
    if storage is None:
        storage = getattr(bot, "storage", None)
    await bot.add_cog(ProfileSystem(bot, storage))
