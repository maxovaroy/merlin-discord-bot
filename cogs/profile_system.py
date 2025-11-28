import discord
from discord.ext import commands
import sys
import os

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
    # FIXED LEVEL FORMULA
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

        progress_percentage = int((current_xp_in_level / current_required_xp) * 100)

        return {
            'level': current_level,
            'current_xp': int(current_xp_in_level),
            'required_xp': int(current_required_xp),
            'progress_percentage': progress_percentage,
            'total_xp': xp
        }

    def create_progress_bar(self, percentage, length=20):
        filled = int(length * percentage / 100)
        empty = length - filled
        return '█' * filled + '░' * empty

    # -----------------------------------------
    # FIXED !profile COMMAND
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

        # -------------------------------------------------------
        # ALWAYS get XP & messages from LEVEL SYSTEM JSON
        # -------------------------------------------------------
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

        # calculate level
        level_info = self.calculate_level(total_xp)

        banner = profile_data.get("banner", "assassin")

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


async def setup(bot):
    try:
        storage = DataStorage()
        await bot.add_cog(ProfileSystem(bot, storage))
    except:
        await bot.add_cog(ProfileSystem(bot, None))
        
    @commands.command()
    async def setbio(self, ctx, *, bio: str = None):
        """Set your profile biography"""
        if not self.storage:
            await ctx.send("❌ Storage system not available. Please contact bot administrator.")
            return
            
        if not bio:
            await ctx.send("❌ Please provide a biography! Example: `!setbio I love coding!`")
            return
            
        if len(bio) > 200:
            await ctx.send("❌ Biography too long! Maximum 200 characters.")
            return
        
        try:
            self.storage.update_user_profile(ctx.author.id, ctx.guild.id, {'bio': bio})
            
            embed = discord.Embed(
                title="📝 Biography Updated!",
                description=f"**New bio:** {bio}",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Error updating bio: {e}")

    @commands.command()
    async def settitle(self, ctx, *, title: str = None):
        """Set your profile title"""
        if not self.storage:
            await ctx.send("❌ Storage system not available. Please contact bot administrator.")
            return
            
        if not title:
            await ctx.send("❌ Please provide a title! Example: `!settitle Pro Coder`")
            return
            
        if len(title) > 25:
            await ctx.send("❌ Title too long! Maximum 25 characters.")
            return
        
        try:
            self.storage.update_user_profile(ctx.author.id, ctx.guild.id, {'title': title})
            
            embed = discord.Embed(
                title="🎖️ Title Updated!",
                description=f"**New title:** {title}",
                color=discord.Color.gold()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Error updating title: {e}")

    @commands.command()
    async def profilehelp(self, ctx):
        """Show enhanced profile system help"""
        embed = discord.Embed(
            title="👤 Advanced Profile System Help",
            description="Customize your profile with banners, achievements, and badges!",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="📊 Profile Commands",
            value=(
                "`!profile [@user]` - View enhanced profile\n"
                "`!setbio <text>` - Set your biography (200 chars)\n"
                "`!settitle <text>` - Set your title (25 chars)\n"
                "`!banners` - View available banners\n"
                "`!bannerpreview <name>` - Preview a banner\n"
                "`!setbanner <name>` - Change banner\n"
                "`!userbanners [@user]` - Check unlocked banners\n"
                "`!achievements [@user]` - View achievements\n"
                "`!allachievements [@user]` - View all achievements\n"
                "`!badges [@user]` - View user badges"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🎯 Achievement Rarities",
            value=(
                "**Common** 🏆 - Easy to get\n"
                "**Uncommon** 🌟 - Moderate effort\n" 
                "**Rare** 💎 - Hard to achieve\n"
                "**Epic** ✨ - Very challenging\n"
                "**Legendary** 🌈 - Nearly impossible!"
            ),
            inline=False
        )
        
        # Only show owner commands to you
        if ctx.author.id == 717689371293384766:
            embed.add_field(
                name="🔧 Owner Commands",
                value=(
                    "`!givebanner @user <name>` - Give banner\n"
                    "`!giveallbanners [@user]` - Give all banners\n"
                    "`!givebadge @user <name>` - Give special badge\n"
                    "`!unlocktest <id>` - Test achievement unlocking"
                ),
                inline=False
            )
        
        await ctx.send(embed=embed)

    # 🚀 BACKWARD COMPATIBILITY - KEEP OLD COMMANDS WORKING
    @commands.command()
    async def backgrounds(self, ctx):
        """Backward compatibility - use !banners instead"""
        await ctx.send("🔄 This command has been updated to `!banners`. Redirecting...")
        # This will be handled by banner system

    @commands.command()  
    async def setbackground(self, ctx, *, background_name: str):
        """Backward compatibility - use !setbanner instead"""
        await ctx.send("🔄 This command has been updated to `!setbanner`. Redirecting...")
        # This will be handled by banner system

    @commands.command()
    async def userbackgrounds(self, ctx, member: discord.Member = None):
        """Backward compatibility - use !userbanners instead"""
        await ctx.send("🔄 This command has been updated to `!userbanners`. Redirecting...")
        # This will be handled by banner system

    @commands.command()
    async def givebackground(self, ctx, member: discord.Member, *, background_name: str):
        """Backward compatibility - use !givebanner instead"""
        await ctx.send("🔄 This command has been updated to `!givebanner`. Redirecting...")
        # This will be handled by banner system

    @commands.command()
    async def giveallbackgrounds(self, ctx, member: discord.Member = None):
        """Backward compatibility - use !giveallbanners instead"""
        await ctx.send("🔄 This command has been updated to `!giveallbanners`. Redirecting...")
        # This will be handled by banner system

    @commands.command() 
    async def cmdcheck(self, ctx):
        """Check all registered commands"""
        commands_list = [cmd.name for cmd in self.get_commands()]
        await ctx.send(f"📋 Available commands: {', '.join(commands_list)}")

async def setup(bot):
    try:
        from storage import DataStorage
        storage = DataStorage()
        await bot.add_cog(ProfileSystem(bot, storage))
        print("✅ ProfileSystem cog loaded successfully!")
    except Exception as e:
        print(f"❌ Failed to load ProfileSystem: {e}")
        # Fallback without storage
        await bot.add_cog(ProfileSystem(bot, None))



