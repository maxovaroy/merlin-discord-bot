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
    """Calculate level based on XP - Improved version"""
    base_xp = 100
    multiplier = 1.5
    level = 0
    required_xp = 0
    
    # Calculate what level the user should be
    while xp >= required_xp:
        level += 1
        required_xp = base_xp * (multiplier ** (level - 1))
    
    # User is at level-1 (since we overshot in the loop)
    current_level = level - 1
    
    # Calculate XP for current level
    if current_level == 0:
        previous_xp = 0
        current_required_xp = base_xp
    else:
        previous_xp = base_xp * (multiplier ** (current_level - 1))
        current_required_xp = base_xp * (multiplier ** current_level) - previous_xp
    
    # Current XP in this level
    current_xp_in_level = xp - previous_xp
    
    # Progress percentage
    progress_percentage = min(100, int((current_xp_in_level / current_required_xp) * 100)) if current_required_xp > 0 else 100
    
    print(f"🔢 Level Calc: XP={xp}, Level={current_level}, CurrentXP={current_xp_in_level}, Required={current_required_xp}, Progress={progress_percentage}%")
    
    return {
        'level': current_level,
        'current_xp': int(current_xp_in_level),
        'required_xp': int(current_required_xp),
        'progress_percentage': progress_percentage,
        'total_xp': xp
    }

    @commands.command()
    async def test(self, ctx):
        """Simple test command"""
        await ctx.send("✅ Profile system is working!")

@commands.command()
async def profile(self, ctx, member: discord.Member = None):
    """Display user profile with banner"""
    try:
        print(f"🔍 PROFILE COMMAND TRIGGERED: {ctx.author} -> {member}")
        await ctx.send("🔄 Loading profile...")
        
        if not self.storage:
            await ctx.send("❌ Storage system not available. Please contact bot administrator.")
            return
            
        target = member or ctx.author
        print(f"🎯 Target user: {target}")
        
        # Get user profile data
        profile_data = self.storage.get_user_profile(target.id, ctx.guild.id)
        print(f"📊 Profile data: {bool(profile_data)}")
        
        if not profile_data:
            await ctx.send("❌ Profile not found! Start chatting to create your profile.")
            return
        
        # 🚀 FIX: Get XP data from level system
        try:
            # Try to get XP from level system cog
            level_cog = self.bot.get_cog('LevelSystem')
            if level_cog and hasattr(level_cog, 'get_user_level'):
                user_data = level_cog.get_user_level(target.id, ctx.guild.id)
                if user_data:
                    total_xp = user_data.get('xp', 0)
                    messages_sent = user_data.get('messages', 0)
                    print(f"📈 Got XP from LevelSystem: {total_xp}")
                else:
                    total_xp = 0
                    messages_sent = 0
            else:
                # Fallback: get from profile data
                total_xp = profile_data.get('xp', 0)
                messages_sent = profile_data.get('messages_sent', 0)
                print(f"📈 Using profile XP: {total_xp}")
        except Exception as e:
            print(f"⚠️ Level system error: {e}")
            total_xp = profile_data.get('xp', 0)
            messages_sent = profile_data.get('messages_sent', 0)
        
        # Get banner information
        banner_id = profile_data.get('banner', 'assassin')
        print(f"🎨 Banner ID: {banner_id}")
        
        # Try to import banner system to get banner info
        try:
            # Get the banner cog instance
            banner_cog = self.bot.get_cog('BannerSystem')
            print(f"🔧 Banner cog: {banner_cog}")
            
            if banner_cog:
                banner_info = banner_cog.available_banners.get(banner_id, banner_cog.available_banners['assassin'])
                banner_name = banner_info['name']
                banner_emoji = banner_info['emoji']
                banner_color = banner_info.get('color', '#7289DA')
                banner_url = banner_info.get('banner_url')
                print(f"🎨 Banner info: {banner_name}")
            else:
                banner_name = "Assassin"
                banner_emoji = "🗡️"
                banner_color = "#7289DA"
                banner_url = None
                print("⚠️ Using default banner info")
        except Exception as e:
            print(f"❌ Banner error: {e}")
            banner_name = "Assassin"
            banner_emoji = "🗡️"
            banner_color = "#7289DA"
            banner_url = None
        
        # Calculate level and progress
        print(f"📈 Total XP: {total_xp}")
        
        level_info = self.calculate_level(total_xp)
        current_level = level_info['level']
        current_xp = level_info['current_xp']
        required_xp = level_info['required_xp']
        progress_percentage = level_info['progress_percentage']
        
        print(f"🎯 Level: {current_level}, Progress: {progress_percentage}%")
        
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
            print("🖼️ Banner image set")
        
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
        
        print("✅ Sending profile embed...")
        await ctx.send(embed=embed)
        print("✅ Profile sent successfully!")
        
    except Exception as e:
        print(f"❌ PROFILE COMMAND ERROR: {e}")
        import traceback
        traceback.print_exc()
        await ctx.send(f"❌ Error displaying profile: {e}")

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


