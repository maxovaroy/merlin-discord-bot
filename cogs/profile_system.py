import discord
from discord.ext import commands
import sys
import os

# 🚀 CRITICAL FIX: Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from storage import DataStorage
    STORAGE_AVAILABLE = True
except ImportError as e:
    print(f"❌ Failed to import storage modules: {e}")
    STORAGE_AVAILABLE = False

class ProfileSystem(commands.Cog):
    def __init__(self, bot, storage):
        self.bot = bot
        self.storage = storage

    @commands.Cog.listener()
    async def on_ready(self):
        """Called when cog is loaded and ready"""
        print(f"✅ {self.__class__.__name__} cog loaded successfully!")

    def create_progress_bar(self, percentage, length=20):
        """Create a visual progress bar"""
        filled = int(length * percentage / 100)
        empty = length - filled
        return '█' * filled + '░' * empty

    def calculate_level(self, xp):
        """Calculate level based on XP"""
        base_xp = 100
        multiplier = 1.5
        level = 0
        required_xp = 0
        
        while xp >= required_xp:
            level += 1
            required_xp = base_xp * (multiplier ** (level - 1))
        
        # Adjust for current level
        previous_xp = base_xp * (multiplier ** (level - 2)) if level > 1 else 0
        current_xp = xp - previous_xp
        current_required_xp = required_xp - previous_xp
        
        progress_percentage = min(100, int((current_xp / current_required_xp) * 100)) if current_required_xp > 0 else 100
        
        return {
            'level': level - 1,
            'current_xp': int(current_xp),
            'required_xp': int(current_required_xp),
            'progress_percentage': progress_percentage,
            'total_xp': xp
        }

    @commands.command()
    async def profile(self, ctx, member: discord.Member = None):
        """Display user profile with banner"""
        if not self.storage:
            await ctx.send("❌ Storage system not available. Please contact bot administrator.")
            return
            
        target = member or ctx.author
        
        # Get user profile data
        profile_data = self.storage.get_user_profile(target.id, ctx.guild.id)
        
        if not profile_data:
            await ctx.send("❌ Profile not found! Start chatting to create your profile.")
            return
        
        # Get banner information
        banner_id = profile_data.get('banner', 'assassin')  # Default to assassin banner
        
        # Try to import banner system to get banner info
        try:
            # Get the banner cog instance
            banner_cog = self.bot.get_cog('BannerSystem')
            if banner_cog:
                banner_info = banner_cog.available_banners.get(banner_id, banner_cog.available_banners['assassin'])
                banner_name = banner_info['name']
                banner_emoji = banner_info['emoji']
                banner_color = banner_info.get('color', '#7289DA')
                banner_url = banner_info.get('banner_url')
            else:
                banner_name = "Assassin"
                banner_emoji = "🗡️"
                banner_color = "#7289DA"
                banner_url = None
        except:
            banner_name = "Assassin"
            banner_emoji = "🗡️"
            banner_color = "#7289DA"
            banner_url = None
        
        # Calculate level and progress
        total_xp = profile_data.get('xp', 0)
        level_info = self.calculate_level(total_xp)
        current_level = level_info['level']
        current_xp = level_info['current_xp']
        required_xp = level_info['required_xp']
        progress_percentage = level_info['progress_percentage']
        
        # Create progress bar
        progress_bar = self.create_progress_bar(progress_percentage)
        
        # Create embed
        embed_color = discord.Color(int(banner_color.replace('#', ''), 16)) if banner_color else discord.Color.blue()
        
        embed = discord.Embed(
            title=f"{banner_emoji} {target.display_name}'s Profile",
            color=embed_color
        )
        
        # Add banner image if available
        if banner_url:
            embed.set_image(url=banner_url)
        
        # Add profile fields
        embed.add_field(
            name="🎯 Level & XP",
            value=f"**Level {current_level}**\n{progress_bar}\n{current_xp}/{required_xp} XP ({progress_percentage}%)",
            inline=True
        )
        
        embed.add_field(
            name="🎨 Banner",
            value=f"{banner_emoji} **{banner_name}**",
            inline=True
        )
        
        # Add other profile stats
        messages_sent = profile_data.get('messages_sent', 0)
        join_date = profile_data.get('join_date', 'Unknown')
        reputation = profile_data.get('reputation', 0)
        
        embed.add_field(
            name="📊 Stats",
            value=f"**Messages:** {messages_sent:,}\n**Reputation:** {reputation}\n**Joined:** {join_date}",
            inline=False
        )
        
        # Add achievements if available
        try:
            achievement_cog = self.bot.get_cog('AchievementSystem')
            if achievement_cog:
                user_achievements = self.storage.get_achievements(target.id, ctx.guild.id)
                if user_achievements:
                    completed = len([a for a in user_achievements if a.get('completed', False)])
                    embed.add_field(
                        name="🏆 Achievements",
                        value=f"**{completed}/{len(user_achievements)}** completed",
                        inline=True
                    )
        except:
            pass
        
        # Set thumbnail as user avatar
        embed.set_thumbnail(url=target.display_avatar.url)
        
        # Add footer with banner info
        embed.set_footer(text=f"Use !banners to see available banners | !setbanner to change")
        
        await ctx.send(embed=embed)

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

async def setup(bot):
    try:
        from storage import DataStorage
        storage = DataStorage()
        await bot.add_cog(ProfileSystem(bot, storage))
        print("✅ ProfileSystem cog loaded successfully!")
    except Exception as e:
        print(f"❌ Failed to load ProfileSystem: {e}")
        # Fallback: add cog without storage
        await bot.add_cog(ProfileSystem(bot, None))
