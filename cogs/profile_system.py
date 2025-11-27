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

    @commands.command()
    async def profile(self, ctx, member: discord.Member = None):
        """View your enhanced Koya-style profile card"""
        if not self.storage:
            await ctx.send("❌ Storage system not available. Please contact bot administrator.")
            return
            
        target = member or ctx.author
        
        # Increment profile views
        self.storage.increment_profile_views(target.id, ctx.guild.id)
        
        # Get all user data
        profile_data = self.storage.get_user_profile(target.id, ctx.guild.id)
        
        # Get level data
        try:
            user_key = str(target.id)
            server_key = str(ctx.guild.id)
            if (server_key in self.storage.user_levels and 
                user_key in self.storage.user_levels[server_key]):
                level_data = self.storage.user_levels[server_key][user_key]
                level = level_data.get('level', 1)
                xp = level_data.get('xp', 0)
            else:
                level = 1
                xp = 0
        except:
            level = 1
            xp = 0
        
        # Get social data
        marriage_data = self.storage.get_marriage(target.id, ctx.guild.id)
        children_count = len(self.storage.get_children(target.id, ctx.guild.id))
        friends_count = len(self.storage.get_friends(target.id, ctx.guild.id))
        rep_data = self.storage.get_reputation(target.id, ctx.guild.id)
        gifts_data = self.storage.get_gifts(target.id, ctx.guild.id)
        
        # Calculate XP for next level
        xp_needed = level * 100
        xp_progress = min((xp / xp_needed) * 100, 100) if xp_needed > 0 else 0
        
        # Get current banner info (you'll need to import banner system or access it differently)
        current_banner_id = profile_data.get('banner', 'assassin')
        # Note: You'll need to access banners from the banner system
        
        # Create Koya-style profile embed
        embed = discord.Embed(
            title=f"👤 {target.display_name}'s Profile",
            color=discord.Color.blue()
        )
        
        # Profile header with avatar and main info
        embed.set_thumbnail(url=target.avatar.url if target.avatar else target.default_avatar.url)
        
        # Main profile section
        embed.add_field(
            name="🎯 Profile Info",
            value=(
                f"**Title:** {profile_data.get('title', 'No title set')}\n"
                f"**Level:** {level} • **XP:** {xp}/{xp_needed}\n"
                f"**Bio:** {profile_data.get('bio', 'No bio set')}"
            ),
            inline=False
        )
        
        # Stats section
        embed.add_field(
            name="📊 Statistics",
            value=(
                f"⭐ **Reputation:** {rep_data}\n"
                f"👀 **Profile Views:** {profile_data.get('profile_views', 0)}\n"
                f"👥 **Friends:** {friends_count}\n"
                f"🎁 **Gifts Sent:** {gifts_data}"
            ),
            inline=True
        )
        
        # Social section
        social_text = ""
        if marriage_data:
            partner_id = marriage_data['partner']
            partner = ctx.guild.get_member(partner_id)
            partner_name = partner.display_name if partner else f"User {partner_id}"
            social_text += f"💍 **Married to:** {partner_name}\n"
        
        if children_count > 0:
            social_text += f"👶 **Children:** {children_count}\n"
        
        if social_text:
            embed.add_field(
                name="💕 Social",
                value=social_text,
                inline=True
            )
        
        # Progress bar for XP
        progress_bar = self.create_progress_bar(xp_progress)
        embed.add_field(
            name="📈 Level Progress",
            value=f"`{progress_bar}` {xp_progress:.1f}%",
            inline=False
        )
        
        # Footer with member info
        member_since = target.joined_at.strftime('%b %d, %Y') if target.joined_at else "Unknown"
        embed.set_footer(
            text=f"Member since: {member_since} • WEICO PROFILE • PLS CHECK #ROLES",
            icon_url=target.avatar.url if target.avatar else target.default_avatar.url
        )
        
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
    from storage import DataStorage
    storage = DataStorage()
    await bot.add_cog(ProfileSystem(bot, storage))
