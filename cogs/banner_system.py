# app.py - Merlin Discord Bot (Rewritten)
import discord
from discord.ext import commands
import asyncio
import sys
from datetime import datetime

# -----------------------------
# Config import
# -----------------------------
try:
    import config
    print("✅ Config imported successfully!")
except ImportError as e:
    print(f"❌ Failed to import config: {e}")
    sys.exit(1)

# -----------------------------
# Storage import
# -----------------------------
try:
    from storage import DataStorage
    STORAGE = DataStorage()
    print("✅ Storage instance created (async load deferred)")
except ImportError as e:
    STORAGE = None
    print(f"❌ Storage module not found: {e}")


# -----------------------------
# Leveling system import
# -----------------------------
try:
    from discordLevelingSystem import DiscordLevelingSystem, errors as leveling_errors
except ImportError as e:
    print(f"❌ Leveling system import failed: {e}")
    DiscordLevelingSystem = None
    leveling_errors = None

# -----------------------------
# Banner System Cog
# -----------------------------
class BannerSystem(commands.Cog):
    def __init__(self, bot, storage=None):
        self.bot = bot
        self.storage = storage

        # 🎨 BANNERS
        self.available_banners = {
            'assassin': {'name': 'Assassin', 'emoji': '🗡️', 'rarity': 'common', 'banner_url': 'https://i.postimg.cc/XvP8qJZN/1000240088.png', 'color': '#7289DA'},
            'aura_farmer': {'name': 'Aura Farmer', 'emoji': '🌟', 'rarity': 'rare', 'banner_url': 'https://i.postimg.cc/fbSdHvLx/1000240087.png', 'color': '#FFD700'},
            'unholy': {'name': 'Unholy', 'emoji': '☠️', 'rarity': 'common', 'banner_url': 'https://i.postimg.cc/mk8LQhvz/1000240136.png', 'color': '#1E90FF'},
            'guardian': {'name': 'Guardian', 'emoji': '🛡️', 'rarity': 'common', 'banner_url': 'https://i.postimg.cc/rp1L1K4N/1000240138.png', 'color': '#1E90FF'},
            'spartan': {'name': 'Spartan', 'emoji': '⚔️', 'rarity': 'common', 'banner_url': 'https://i.postimg.cc/XqXhzJZy/1000240140.png', 'color': '#1E90FF'},
            'berserker': {'name': 'Berserker', 'emoji': '⚡', 'rarity': 'rare', 'banner_url': 'https://i.postimg.cc/fbTvKPtF/1000240134.png', 'color': '#FFD700'},
            'russian_ghost': {'name': 'Russian Ghost', 'emoji': '🩸', 'rarity': 'rare', 'banner_url': 'https://i.postimg.cc/5y5fLbH4/1000240210.png', 'color': '#FF08DF'},
            'baddie': {'name': 'Baddie', 'emoji': '😈', 'rarity': 'uncommon', 'banner_url': 'https://i.postimg.cc/fyR8jvyZ/1000240227.png', 'color': '#C7C7C7'},
            'techno': {'name': 'Techno Blade', 'emoji': '💘', 'rarity': 'legendary', 'banner_url': 'https://i.postimg.cc/QdGpjbDF/1000240218.png', 'color': '#C20A0A'},
            'deadpool': {'name': 'Deadpool', 'emoji': '♦️', 'rarity': 'common', 'banner_url': 'https://i.postimg.cc/BnRZrYGv/1000240221.png', 'color': '#C20A0A'},
            'mikey': {'name': 'Mikey', 'emoji': '👽', 'rarity': 'legendary', 'banner_url': 'https://i.postimg.cc/yYy3mzcz/1000240143.png', 'color': '#C2540A'},
            'space': {'name': 'Deep Space', 'emoji': '🚀', 'rarity': 'legendary', 'banner_url': 'https://i.imgur.com/3Q3fZ8p.png', 'color': '#000080'},
            'fire': {'name': 'Inferno', 'emoji': '🔥', 'rarity': 'epic', 'banner_url': 'https://i.imgur.com/2Q4gY9q.png', 'color': '#FF4500'},
            'ice': {'name': 'Frozen', 'emoji': '❄️', 'rarity': 'rare', 'banner_url': 'https://i.imgur.com/1Q5hX0r.png', 'color': '#00CED1'},
            'neon': {'name': 'Neon City', 'emoji': '💡', 'rarity': 'epic', 'banner_url': 'https://i.imgur.com/0Q6jZ1s.png', 'color': '#00FF00'}
        }

    def find_banner_by_name(self, banner_name):
        if not banner_name:
            return None, None

        name_lower = banner_name.lower().strip()
        for bid, binfo in self.available_banners.items():
            if bid.lower() == name_lower or binfo['name'].lower() == name_lower:
                return bid, binfo

        for bid, binfo in self.available_banners.items():
            display_name = binfo['name'].lower().replace(' ', '').replace('_', '').replace('-', '')
            search_name = name_lower.replace(' ', '').replace('_', '').replace('-', '')
            if search_name in display_name or display_name in search_name:
                return bid, binfo

        return None, None

    # -----------------------------
    # Commands (simplified example)
    # -----------------------------
    @commands.command()
    async def banners(self, ctx):
        embed = discord.Embed(title="🎨 Available Banners", description="Check your banners!", color=discord.Color.purple())
        for bid, binfo in self.available_banners.items():
            embed.add_field(name=f"{binfo['emoji']} {binfo['name']}", value=f"Rarity: {binfo['rarity'].title()}", inline=False)
        await ctx.send(embed=embed)

# -----------------------------
# Merlin Bot Class
# -----------------------------
class MerlinBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=config.PREFIX,
            intents=discord.Intents.all(),
            help_command=None,
            owner_ids=set(getattr(config, "OWNER_IDS", []))
        )
        self.user_data = {}
        self.levelsystem = DiscordLevelingSystem(rate=1, per=60.0) if DiscordLevelingSystem else None

    async def setup_hook(self):
        if self.levelsystem:
            loop = asyncio.get_running_loop()
            try:
                await loop.run_in_executor(None, self.levelsystem.connect_to_database_file, "./leveling.db")
                print("✅ Leveling database connected!")
            except leveling_errors.ConnectionFailure:
                print("❌ Failed to connect leveling database!")

        if STORAGE:
            try:
                await STORAGE.load_data_async()
                print("✅ Storage loaded successfully!")
            except Exception as e:
                print(f"❌ Storage load failed: {e}")

        # Load BannerSystem cog
        try:
            await self.add_cog(BannerSystem(self, STORAGE))
            print("✅ BannerSystem cog loaded!")
        except Exception as e:
            print(f"❌ Failed to load BannerSystem cog: {e}")

    async def on_ready(self):
        print(f"\n🎉 {self.user} is online | Connected to {len(self.guilds)} guild(s)")
        activity = discord.Activity(type=discord.ActivityType.watching, name=f"{len(self.guilds)} servers | {config.PREFIX}help")
        await self.change_presence(activity=activity)

    async def on_message(self, message):
        if message.author.bot:
            return await self.process_commands(message)

        if STORAGE:
            STORAGE.get_user_profile(message.author.id, message.guild.id)

        if self.levelsystem:
            await self.levelsystem.award_xp(amount=[15, 25], message=message)

        user_id = message.author.id
        if user_id not in self.user_data:
            joined_date = message.author.joined_at.isoformat() if message.author.joined_at else datetime.now().isoformat()
            self.user_data[user_id] = {"username": str(message.author), "joined_at": joined_date, "messages": 0}
        self.user_data[user_id]["messages"] += 1
        await self.process_commands(message)

# -----------------------------
# Main Entry
# -----------------------------
async def main():
    print("="*50)
    print("🤖 Starting Merlin Discord Bot...")
    print("="*50)

    if not getattr(config, "BOT_TOKEN", None) or config.BOT_TOKEN == "YOUR_ACTUAL_BOT_TOKEN_HERE":
        print("❌ Bot token not configured!")
        return

    bot = MerlinBot()
    try:
        await bot.start(config.BOT_TOKEN)
    except discord.LoginFailure:
        print("❌ Invalid bot token!")
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(main())

    @commands.command()
    async def banners(self, ctx):
        """View available banners with improved display"""
        if not self.storage:
            await ctx.send("❌ Storage system not available. Please contact bot administrator.")
            return
            
        embed = discord.Embed(
            title="🎨 Available Banners",
            description="Unlock banners by achieving milestones or through special events!",
            color=discord.Color.purple()
        )
        
        # Group banners by rarity
        rarities = {
            'common': [],
            'uncommon': [], 
            'rare': [],
            'epic': [],
            'legendary': []
        }
        
        # Get user's current banner and unlocked banners
        profile_data = self.storage.get_user_profile(ctx.author.id, ctx.guild.id)
        current_banner_id = profile_data.get('banner', 'assassin')
        user_banners = self.storage.get_banners(ctx.author.id, ctx.guild.id)
        unlocked_banner_ids = [bg['id'] for bg in user_banners]
        
        # Include ALL banners in the display
        for banner_id, banner_info in self.available_banners.items():
            # Skip default banner from the main list (users already have it)
            if banner_id == 'assassin':
                continue
                
            rarity = banner_info['rarity']
            is_unlocked = banner_id in unlocked_banner_ids
            is_current = banner_id == current_banner_id
            
            status = " ✅" if is_unlocked else " 🔒"
            current_indicator = " 🎯" if is_current else ""
            
            banner_display = f"{banner_info['emoji']} **{banner_info['name']}**{status}{current_indicator}"
            rarities[rarity].append(banner_display)
        
        # Add fields for each rarity
        for rarity, banners in rarities.items():
            if banners:
                embed.add_field(
                    name=f"{rarity.title()} Banners ({len(banners)})",
                    value="\n".join(banners),
                    inline=False
                )
        
        # Show user's current banner
        current_banner_info = self.available_banners.get(current_banner_id, self.available_banners['assassin'])
        embed.add_field(
            name="🎯 Your Current Banner",
            value=f"{current_banner_info['emoji']} **{current_banner_info['name']}**",
            inline=False
        )
        
        embed.set_footer(text="Use !bannerpreview <name> to see a banner | !setbanner <name> to equip")
        await ctx.send(embed=embed)

    @commands.command()
    async def bannerpreview(self, ctx, *, banner_name: str):
        """Preview a specific banner with improved search"""
        if not self.storage:
            await ctx.send("❌ Storage system not available. Please contact bot administrator.")
            return
            
        # Find banner by name using our improved function
        banner_id, banner_info = self.find_banner_by_name(banner_name)
        
        if not banner_id or not banner_info:
            # Show available banners to help user
            available_names = [b['name'] for b in self.available_banners.values()]
            await ctx.send(f"❌ Banner '{banner_name}' not found! Available banners: {', '.join(available_names)}")
            return
        
        embed = discord.Embed(
            title=f"🎨 {banner_info['name']} Preview",
            description=f"**Rarity:** {banner_info['rarity'].title()}\n**Emoji:** {banner_info['emoji']}",
            color=discord.Color(int(banner_info['color'].replace('#', ''), 16)) if banner_info.get('color') else discord.Color.blue()
        )
        
        if banner_info.get('banner_url'):
            embed.set_image(url=banner_info['banner_url'])
        
        # Check if user has this banner
        user_banners = self.storage.get_banners(ctx.author.id, ctx.guild.id)
        has_banner = any(bg['id'] == banner_id for bg in user_banners)
        
        if has_banner or banner_id == 'assassin':
            embed.add_field(name="Status", value="✅ Unlocked - You can use this banner!", inline=True)
            embed.add_field(name="Action", value=f"Use `!setbanner {banner_info['name']}` to equip it!", inline=True)
        else:
            embed.add_field(name="Status", value="🔒 Locked - Complete achievements to unlock!", inline=True)
        
        await ctx.send(embed=embed)

    @commands.command()
    async def setbanner(self, ctx, *, banner_name: str):
        """Set your profile banner with improved search"""
        if not self.storage:
            await ctx.send("❌ Storage system not available. Please contact bot administrator.")
            return
            
        # Find banner by name using our improved function
        banner_id, banner_info = self.find_banner_by_name(banner_name)
        
        if not banner_id:
            # Show available banners to help user
            available_names = [b['name'] for b in self.available_banners.values()]
            await ctx.send(f"❌ Banner '{banner_name}' not found! Available banners: {', '.join(available_names)}")
            return
        
        # Check if user has unlocked this banner
        user_banners = self.storage.get_banners(ctx.author.id, ctx.guild.id)
        banner_unlocked = any(bg['id'] == banner_id for bg in user_banners)
        
        if not banner_unlocked and banner_id != 'assassin':
            await ctx.send(f"❌ You haven't unlocked the **{banner_info['name']}** banner yet!")
            return
        
        self.storage.update_user_banner(ctx.author.id, ctx.guild.id, banner_id)
        
        embed = discord.Embed(
            title="🎨 Banner Updated!",
            description=f"Your profile banner is now **{banner_info['name']}** {banner_info['emoji']}",
            color=discord.Color(int(banner_info['color'].replace('#', ''), 16)) if banner_info.get('color') else discord.Color.blue()
        )
        
        if banner_info.get('banner_url'):
            embed.set_image(url=banner_info['banner_url'])
        
        await ctx.send(embed=embed)

    @commands.command()
    async def userbanners(self, ctx, member: discord.Member = None):
        """Check what banners a user has unlocked with previews"""
        if not self.storage:
            await ctx.send("❌ Storage system not available.")
            return
            
        target = member or ctx.author
        user_banners = self.storage.get_banners(target.id, ctx.guild.id)
        current_profile = self.storage.get_user_profile(target.id, ctx.guild.id)
        current_banner = current_profile.get('banner', 'assassin')
        
        embed = discord.Embed(
            title=f"🎨 {target.display_name}'s Banner Collection",
            color=discord.Color.blue()
        )
        
        if user_banners:
            # Group by rarity
            rarities = {
                'common': [],
                'uncommon': [], 
                'rare': [],
                'epic': [],
                'legendary': []
            }
            
            for banner_data in user_banners:
                banner_id = banner_data['id']
                if banner_id in self.available_banners:
                    banner_info = self.available_banners[banner_id]
                    display = f"{banner_info['emoji']} **{banner_info['name']}**"
                    if banner_id == current_banner:
                        display += " ✅ (Active)"
                    rarities[banner_info['rarity']].append(display)
            
            # Add fields for each rarity
            for rarity, banners in rarities.items():
                if banners:
                    embed.add_field(
                        name=f"{rarity.title()} ({len(banners)})",
                        value="\n".join(banners),
                        inline=False
                    )
        else:
            embed.description = "No banners unlocked yet! Start by achieving some milestones!"
        
        embed.set_footer(text=f"Total unlocked: {len(user_banners)}/{len(self.available_banners)} banners")
        await ctx.send(embed=embed)

    # OWNER COMMANDS
    @commands.command()
    async def givebanner(self, ctx, member: discord.Member, *, banner_name: str):
        """Give a banner to a user (Bot Owner Only)"""
        if ctx.author.id != 717689371293384766:
            await ctx.send("❌ This command is only available for the bot owner!")
            return
            
        if not self.storage:
            await ctx.send("❌ Storage system not available.")
            return
        
        # Find banner by name using our improved function
        banner_id, banner_info = self.find_banner_by_name(banner_name)
        
        if not banner_id:
            # Show available banners to help user
            available_names = [b['name'] for b in self.available_banners.values()]
            await ctx.send(f"❌ Banner '{banner_name}' not found! Available banners: {', '.join(available_names)}")
            return
        
        # Unlock the banner for the user
        self.storage.unlock_banner(member.id, ctx.guild.id, banner_id, banner_info['name'])
        
        # Also set it as their current banner
        self.storage.update_user_banner(member.id, ctx.guild.id, banner_id)
        
        embed = discord.Embed(
            title="🎨 Banner Granted!",
            description=f"**{banner_info['name']}** {banner_info['emoji']} banner has been given to {member.mention}!",
            color=discord.Color(int(banner_info['color'].replace('#', ''), 16)) if banner_info.get('color') else discord.Color.blue()
        )
        
        if banner_info.get('banner_url'):
            embed.set_image(url=banner_info['banner_url'])
        
        embed.add_field(name="Granted by", value=ctx.author.mention, inline=True)
        embed.add_field(name="Rarity", value=banner_info['rarity'].title(), inline=True)
        
        await ctx.send(embed=embed)

    @commands.command()
    async def giveallbanners(self, ctx, member: discord.Member = None):
        """Give all banners to a user (Bot Owner Only)"""
        if ctx.author.id != 717689371293384766:
            await ctx.send("❌ This command is only available for the bot owner!")
            return
            
        if not self.storage:
            await ctx.send("❌ Storage system not available.")
            return
        
        target = member or ctx.author
        
        # Unlock all banners
        for banner_id, banner_info in self.available_banners.items():
            self.storage.unlock_banner(target.id, ctx.guild.id, banner_id, banner_info['name'])
        
        # Set the most rare banner as current
        rare_banners = ['space', 'techno', 'mikey', 'neon', 'fire']
        for banner_id in rare_banners:
            if banner_id in self.available_banners:
                self.storage.update_user_banner(target.id, ctx.guild.id, banner_id)
                break
        
        embed = discord.Embed(
            title="🎨 All Banners Unlocked!",
            description=f"All available banners have been granted to {target.mention}!",
            color=discord.Color.purple()
        )
        embed.add_field(name="Total Unlocked", value=f"{len(self.available_banners)} banners", inline=True)
        embed.add_field(name="Granted by", value=ctx.author.mention, inline=True)
        
        # Show preview of the rarest banner
        rarest_banner = self.available_banners.get('techno', self.available_banners['space'])
        if rarest_banner.get('banner_url'):
            embed.set_image(url=rarest_banner['banner_url'])
        
        embed.set_footer(text="Use !setbanner <name> to change your banner")
        
        await ctx.send(embed=embed)

async def setup(bot):
    try:
        from storage import DataStorage
        storage = DataStorage()
        await bot.add_cog(BannerSystem(bot, storage))
        print("✅ BannerSystem cog loaded successfully!")
    except Exception as e:
        print(f"❌ Failed to load BannerSystem: {e}")
        # Fallback without storage
        await bot.add_cog(BannerSystem(bot, None))
