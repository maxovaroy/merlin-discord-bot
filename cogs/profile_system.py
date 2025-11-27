import discord
from discord.ext import commands
import random
import asyncio
from datetime import datetime
import sys
import os

# 🚀 CRITICAL FIX: Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from storage import DataStorage
    from config import Config
    STORAGE_AVAILABLE = True
except ImportError as e:
    print(f"❌ Failed to import storage modules: {e}")
    STORAGE_AVAILABLE = False

class ProfileSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if STORAGE_AVAILABLE:
            self.storage = DataStorage()
            print("✅ Advanced Profile System loaded with storage!")
        else:
            self.storage = None
            print("❌ Profile System loaded WITHOUT storage - features limited")
        
        # 🎨 BANNER SYSTEM (REPLACING BACKGROUNDS)
        self.available_banners = {
            'assassin': {
                'name': 'Assassin', 
                'emoji': '🗡️', 
                'rarity': 'common',
                'banner_url': 'https://i.postimg.cc/XvP8qJZN/1000240088.png',
                'color': '#7289DA'
            },
            'aura_farmer': {
                'name': 'Aura Farmer', 
                'emoji': '🌟', 
                'rarity': 'rare',
                'banner_url': 'https://i.postimg.cc/fbSdHvLx/1000240087.png',
                'color': '#FFD700'
            },
            'unholy': {
                'name': 'Unholy', 
                'emoji': '☠️', 
                'rarity': 'common',
                'banner_url': 'https://i.postimg.cc/mk8LQhvz/1000240136.png',
                'color': '#1E90FF'
            },
            'guardian': {
                'name': 'Guardian', 
                'emoji': '🛡️', 
                'rarity': 'common',
                'banner_url': 'https://i.postimg.cc/rp1L1K4N/1000240138.png',
                'color': '#1E90FF'
            },
            'spartan': {
                'name': 'Spartan', 
                'emoji': '⚔️', 
                'rarity': 'common',
                'banner_url': 'https://i.postimg.cc/XqXhzJZy/1000240140.png',
                'color': '#1E90FF'
            },
            'berserker': {
                'name': 'Berserker', 
                'emoji': '⚡', 
                'rarity': 'rare',
                'banner_url': 'https://i.postimg.cc/fbTvKPtF/1000240134.png',
                'color': '#FFD700'
            },
            'russian_ghost': {
                'name': 'Russian Ghost', 
                'emoji': '🩸', 
                'rarity': 'rare',
                'banner_url': 'https://i.postimg.cc/5y5fLbH4/1000240210.png',
                'color': '#FF08DF'
            },
            'baddie': {
                'name': 'Baddie', 
                'emoji': '😈', 
                'rarity': 'uncommon',
                'banner_url': 'https://i.postimg.cc/fyR8jvyZ/1000240227.png',
                'color': '#C7C7C7'
            },
            'techno': {
                'name': 'Techno Blade', 
                'emoji': '💘', 
                'rarity': 'legendary',
                'banner_url': 'https://i.postimg.cc/QdGpjbDF/1000240218.png',
                'color': '#C20A0A'
            },
            'deadpool': {
                'name': 'Deadpool', 
                'emoji': '♦️', 
                'rarity': 'common',
                'banner_url': 'https://i.postimg.cc/BnRZrYGv/1000240221.png',
                'color': '#C20A0A'
            },
            'galaxy': {
                'name': 'Galaxy', 
                'emoji': '🌌', 
                'rarity': 'legendary',
                'banner_url': 'https://i.imgur.com/4Q2eX7n.png',
                'color': '#4B0082'
            },
            'space': {
                'name': 'Deep Space', 
                'emoji': '🚀', 
                'rarity': 'legendary',
                'banner_url': 'https://i.imgur.com/3Q3fZ8p.png',
                'color': '#000080'
            },
            'fire': {
                'name': 'Inferno', 
                'emoji': '🔥', 
                'rarity': 'epic',
                'banner_url': 'https://i.imgur.com/2Q4gY9q.png',
                'color': '#FF4500'
            },
            'ice': {
                'name': 'Frozen', 
                'emoji': '❄️', 
                'rarity': 'rare',
                'banner_url': 'https://i.imgur.com/1Q5hX0r.png',
                'color': '#00CED1'
            },
            'neon': {
                'name': 'Neon City', 
                'emoji': '💡', 
                'rarity': 'epic',
                'banner_url': 'https://i.imgur.com/0Q6jZ1s.png',
                'color': '#00FF00'
            }
        }
        
        # Enhanced Achievement System
        self.achievements_list = {
            'first_message': {
                'name': 'First Words',
                'description': 'Send your first message in the server',
                'icon': '💬',
                'rarity': 'common',
                'reward': {'xp': 100, 'banner': 'purple'}
            },
            'level_10': {
                'name': 'Rising Star',
                'description': 'Reach level 10',
                'icon': '⭐',
                'rarity': 'common',
                'reward': {'xp': 500, 'banner': 'purple'}
            },
            'level_50': {
                'name': 'Veteran',
                'description': 'Reach level 50',
                'icon': '🏆',
                'rarity': 'rare',
                'reward': {'xp': 2000, 'banner': 'gold'}
            },
            'married': {
                'name': 'Happily Married',
                'description': 'Get married to another user',
                'icon': '💍',
                'rarity': 'uncommon',
                'reward': {'xp': 300, 'banner': 'purple'}
            },
            'social_butterfly': {
                'name': 'Social Butterfly',
                'description': 'Have 25 friends',
                'icon': '🦋',
                'rarity': 'rare',
                'reward': {'xp': 800, 'banner': 'rainbow'}
            },
            'rep_legend': {
                'name': 'Respected Legend',
                'description': 'Reach 100 reputation points',
                'icon': '👑',
                'rarity': 'epic',
                'reward': {'xp': 1500, 'banner': 'gold'}
            },
            'gift_master': {
                'name': 'Generous Heart',
                'description': 'Send 50 gifts to others',
                'icon': '🎁',
                'rarity': 'rare',
                'reward': {'xp': 1000, 'banner': 'rainbow'}
            },
            'popular': {
                'name': 'Popular Person',
                'description': 'Get 500 profile views',
                'icon': '👀',
                'rarity': 'epic',
                'reward': {'xp': 1200, 'banner': 'neon'}
            },
            'chatty': {
                'name': 'Chatty Cathy',
                'description': 'Send 1000 messages',
                'icon': '💬',
                'rarity': 'uncommon',
                'reward': {'xp': 600, 'banner': 'purple'}
            },
            'rich': {
                'name': 'Wealthy',
                'description': 'Earn 10,000 XP total',
                'icon': '💰',
                'rarity': 'epic',
                'reward': {'xp': 2000, 'banner': 'gold'}
            }
        }

        # Profile Badges
        self.available_badges = {
            'early_supporter': {'name': 'Early Supporter', 'emoji': '🌟', 'description': 'Joined in early days'},
            'booster': {'name': 'Server Booster', 'emoji': '💎', 'description': 'Boosting the server'},
            'vip': {'name': 'VIP Member', 'emoji': '🎖️', 'description': 'Special VIP status'},
            'helper': {'name': 'Community Helper', 'emoji': '🛠️', 'description': 'Helped other members'},
            'creative': {'name': 'Creative Soul', 'emoji': '🎨', 'description': 'Creative content creator'},
            'friendly': {'name': 'Friendly Face', 'emoji': '😊', 'description': 'Always friendly and positive'},
        }

    @commands.Cog.listener()
    async def on_ready(self):
        """Called when cog is loaded and ready"""
        print(f"✅ {self.__class__.__name__} cog loaded successfully!")
        if not STORAGE_AVAILABLE:
            print("❌ Storage system not available - profile features limited")

    def create_progress_bar(self, percentage, length=20):
        """Create a visual progress bar"""
        filled = int(length * percentage / 100)
        empty = length - filled
        return '█' * filled + '░' * empty

    def find_banner_by_name(self, banner_name):
        """Find banner by name (case-insensitive and flexible matching)"""
        banner_name_lower = banner_name.lower().strip()
        
        # Exact match first
        for banner_id, banner_info in self.available_banners.items():
            if banner_id.lower() == banner_name_lower:
                return banner_id, banner_info
        
        # Flexible name matching
        for banner_id, banner_info in self.available_banners.items():
            if banner_info['name'].lower() == banner_name_lower:
                return banner_id, banner_info
            if banner_name_lower in banner_info['name'].lower():
                return banner_id, banner_info
            if banner_info['name'].lower().replace(' ', '_') == banner_name_lower:
                return banner_id, banner_info
            if banner_name_lower.replace(' ', '_') == banner_id:
                return banner_id, banner_info
        
        return None, None

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
        
        # Get current banner info
        current_banner_id = profile_data.get('banner', 'assassin')
        banner_info = self.available_banners.get(current_banner_id, self.available_banners['assassin'])
        
        # Create Koya-style profile embed
        embed = discord.Embed(
            title=f"👤 {target.display_name}'s Profile",
            color=discord.Color(int(banner_info['color'].replace('#', ''), 16)) if banner_info.get('color') else discord.Color.blue()
        )
        
        # Set banner image if available
        if banner_info.get('banner_url'):
            embed.set_image(url=banner_info['banner_url'])
        
        # Profile header with avatar and main info
        embed.set_thumbnail(url=target.avatar.url if target.avatar else target.default_avatar.url)
        
        # Main profile section
        embed.add_field(
            name="🎯 Profile Info",
            value=(
                f"**Title:** {profile_data.get('title', 'No title set')}\n"
                f"**Level:** {level} • **XP:** {xp}/{xp_needed}\n"
                f"**Banner:** {banner_info['emoji']} {banner_info['name']}\n"
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
    async def profilepreview(self, ctx, *, banner_name: str = None):
        """Preview your profile with different banners"""
        if not self.storage:
            await ctx.send("❌ Storage system not available. Please contact bot administrator.")
            return
            
        # If no banner specified, show current
        if not banner_name:
            await self.profile(ctx)
            return
            
        # Find banner by name using our improved function
        banner_id, banner_info = self.find_banner_by_name(banner_name)
        
        if not banner_id:
            await ctx.send("❌ Banner not found! Use `!banners` to see available options.")
            return
        
        # Check if user has this banner
        user_banners = self.storage.get_banners(ctx.author.id, ctx.guild.id)
        banner_unlocked = any(bg['id'] == banner_id for bg in user_banners)
        
        if not banner_unlocked and banner_id != 'assassin':
            await ctx.send(f"❌ You haven't unlocked the **{banner_info['name']}** banner yet!")
            return
        
        # Create preview embed with the selected banner
        embed = discord.Embed(
            title=f"🎨 Profile Preview: {banner_info['name']}",
            description=f"This is how your profile would look with the **{banner_info['name']}** banner!",
            color=discord.Color(int(banner_info['color'].replace('#', ''), 16)) if banner_info.get('color') else discord.Color.blue()
        )
        
        if banner_info.get('banner_url'):
            embed.set_image(url=banner_info['banner_url'])
        
        embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        
        embed.add_field(
            name="Profile Info",
            value=(
                f"**Name:** {ctx.author.display_name}\n"
                f"**Level:** 25 • **XP:** 1250/2500\n"
                f"**Title:** Preview Mode\n"
                f"**Banner:** {banner_info['emoji']} {banner_info['name']}\n"
                f"**Rarity:** {banner_info['rarity'].title()}"
            ),
            inline=False
        )
        
        progress_bar = self.create_progress_bar(50)  # 50% for preview
        embed.add_field(
            name="Level Progress",
            value=f"`{progress_bar}` 50.0%",
            inline=False
        )
        
        if banner_unlocked or banner_id == 'assassin':
            embed.add_field(
                name="Status",
                value="✅ **Unlocked** - Use `!setbanner` to apply this banner!",
                inline=False
            )
        else:
            embed.add_field(
                name="Status", 
                value="🔒 **Locked** - Complete achievements to unlock this banner!",
                inline=False
            )
        
        await ctx.send(embed=embed)

    @commands.command()
    async def setbio(self, ctx, *, bio: str):
        """Set your profile biography"""
        if not self.storage:
            await ctx.send("❌ Storage system not available. Please contact bot administrator.")
            return
            
        if len(bio) > 200:
            await ctx.send("❌ Biography too long! Maximum 200 characters.")
            return
        
        self.storage.update_user_profile(ctx.author.id, ctx.guild.id, {'bio': bio})
        
        embed = discord.Embed(
            title="📝 Biography Updated!",
            description=f"**New bio:** {bio}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def settitle(self, ctx, *, title: str):
        """Set your profile title"""
        if not self.storage:
            await ctx.send("❌ Storage system not available. Please contact bot administrator.")
            return
            
        if len(title) > 25:
            await ctx.send("❌ Title too long! Maximum 25 characters.")
            return
        
        self.storage.update_user_profile(ctx.author.id, ctx.guild.id, {'title': title})
        
        embed = discord.Embed(
            title="🎖️ Title Updated!",
            description=f"**New title:** {title}",
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed)

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
            await ctx.send("❌ Banner not found! Use `!banners` to see available options.")
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
            await ctx.send("❌ Banner not found! Use `!banners` to see available options.")
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
    async def achievements(self, ctx, member: discord.Member = None):
        """View your achievements or someone else's with enhanced display"""
        if not self.storage:
            await ctx.send("❌ Storage system not available. Please contact bot administrator.")
            return
            
        target = member or ctx.author
        achievements = self.storage.get_achievements(target.id, ctx.guild.id)
        
        if not achievements:
            if target == ctx.author:
                await ctx.send("🎯 You haven't unlocked any achievements yet! Keep being active to earn them!")
            else:
                await ctx.send(f"🎯 {target.display_name} hasn't unlocked any achievements yet!")
            return
        
        # Sort by rarity and date
        rarity_order = {'common': 1, 'uncommon': 2, 'rare': 3, 'epic': 4, 'legendary': 5}
        achievements.sort(key=lambda x: (rarity_order[x['rarity']], x['unlocked_at']), reverse=True)
        
        embed = discord.Embed(
            title=f"🏆 {target.display_name}'s Achievements",
            color=discord.Color.gold()
        )
        
        # Achievement statistics
        total_achievements = len(achievements)
        rare_count = len([a for a in achievements if a['rarity'] in ['rare', 'epic', 'legendary']])
        completion = (total_achievements / len(self.achievements_list)) * 100
        
        embed.description = f"**Completion:** {completion:.1f}% • **Rare+:** {rare_count} • **Total:** {total_achievements}"
        
        # Show top 6 achievements
        for achievement in achievements[:6]:
            unlocked_date = datetime.fromisoformat(achievement['unlocked_at'])
            embed.add_field(
                name=f"{achievement['icon']} {achievement['name']}",
                value=(
                    f"{achievement['description']}\n"
                    f"*{achievement['rarity'].title()} • {unlocked_date.strftime('%b %d, %Y')}*"
                ),
                inline=True
            )
        
        if total_achievements > 6:
            embed.set_footer(text=f"Showing 6 of {total_achievements} achievements • Use !allachievements to see all")
        
        await ctx.send(embed=embed)

    @commands.command()
    async def allachievements(self, ctx, member: discord.Member = None):
        """View all achievements in detail"""
        if not self.storage:
            await ctx.send("❌ Storage system not available. Please contact bot administrator.")
            return
            
        target = member or ctx.author
        unlocked_achievements = self.storage.get_achievements(target.id, ctx.guild.id)
        unlocked_ids = [a['id'] for a in unlocked_achievements]
        
        embed = discord.Embed(
            title=f"📋 All Achievements - {target.display_name}",
            color=discord.Color.blue()
        )
        
        # Group by rarity
        rarities = {
            'common': [],
            'uncommon': [],
            'rare': [],
            'epic': [],
            'legendary': []
        }
        
        for ach_id, ach_data in self.achievements_list.items():
            status = "✅" if ach_id in unlocked_ids else "🔒"
            rarities[ach_data['rarity']].append(f"{status} {ach_data['icon']} **{ach_data['name']}**")
        
        # Add fields for each rarity
        for rarity, achievement_list in rarities.items():
            if achievement_list:
                unlocked_count = len([a for a in achievement_list if '✅' in a])
                total_count = len(achievement_list)
                embed.add_field(
                    name=f"{rarity.title()} ({unlocked_count}/{total_count})",
                    value="\n".join(achievement_list),
                    inline=False
                )
        
        total_unlocked = len(unlocked_achievements)
        total_possible = len(self.achievements_list)
        completion = (total_unlocked / total_possible) * 100
        
        embed.set_footer(text=f"Total Progress: {total_unlocked}/{total_possible} ({completion:.1f}%)")
        await ctx.send(embed=embed)

    # OWNER COMMANDS (Enhanced)
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
            await ctx.send("❌ Banner not found! Use `!banners` to see available options.")
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
        rare_banners = ['space', 'galaxy', 'techno', 'neon', 'fire']
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

    @commands.command()
    async def givebadge(self, ctx, member: discord.Member, *, badge_name: str):
        """Give a badge to a user (Bot Owner Only)"""
        if ctx.author.id != 717689371293384766:
            await ctx.send("❌ This command is only available for the bot owner!")
            return
            
        if not self.storage:
            await ctx.send("❌ Storage system not available.")
            return
        
        # Find badge by name
        badge_id = None
        badge_info = None
        for bid, binfo in self.available_badges.items():
            if binfo['name'].lower() == badge_name.lower():
                badge_id = bid
                badge_info = binfo
                break
        
        if not badge_id:
            await ctx.send("❌ Badge not found! Available badges: " + ", ".join([b['name'] for b in self.available_badges.values()]))
            return
        
        # Add badge to user profile
        profile = self.storage.get_user_profile(member.id, ctx.guild.id)
        current_badges = profile.get('badges', [])
        if badge_id not in current_badges:
            current_badges.append(badge_id)
            self.storage.update_user_profile(member.id, ctx.guild.id, {'badges': current_badges})
        
        embed = discord.Embed(
            title="🎖️ Badge Granted!",
            description=f"{badge_info['emoji']} **{badge_info['name']}** badge has been given to {member.mention}!",
            color=discord.Color.gold()
        )
        embed.add_field(name="Description", value=badge_info['description'], inline=False)
        embed.add_field(name="Granted by", value=ctx.author.mention, inline=True)
        
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

    @commands.command()
    async def unlocktest(self, ctx, achievement_id: str = None):
        """Test achievement unlocking with rewards (Admin only)"""
        if not self.storage:
            await ctx.send("❌ Storage system not available. Please contact bot administrator.")
            return
            
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ You need administrator permissions to use this command!")
            return
        
        if not achievement_id:
            # Show available achievements
            embed = discord.Embed(
                title="🎯 Available Achievements for Testing",
                color=discord.Color.blue()
            )
            
            for ach_id, ach_data in self.achievements_list.items():
                embed.add_field(
                    name=f"{ach_data['icon']} {ach_data['name']}",
                    value=f"ID: `{ach_id}`\n{ach_data['description']}",
                    inline=False
                )
            
            embed.set_footer(text="Use !unlocktest <achievement_id> to unlock an achievement")
            await ctx.send(embed=embed)
            return
        
        if achievement_id not in self.achievements_list:
            await ctx.send("❌ Achievement ID not found! Use the command without arguments to see available IDs.")
            return
        
        achievement_data = self.achievements_list[achievement_id]
        unlocked = self.storage.add_achievement(ctx.author.id, ctx.guild.id, achievement_id, achievement_data)
        
        if unlocked:
            # Grant rewards
            rewards = achievement_data.get('reward', {})
            reward_text = []
            
            if 'xp' in rewards:
                # Add XP to user
                user_key = str(ctx.author.id)
                server_key = str(ctx.guild.id)
                if server_key not in self.storage.user_levels:
                    self.storage.user_levels[server_key] = {}
                if user_key not in self.storage.user_levels[server_key]:
                    self.storage.user_levels[server_key][user_key] = {'xp': 0, 'level': 1}
                
                self.storage.user_levels[server_key][user_key]['xp'] += rewards['xp']
                reward_text.append(f"**XP:** +{rewards['xp']}")
            
            if 'banner' in rewards:
                banner_id = rewards['banner']
                if banner_id in self.available_banners:
                    banner_info = self.available_banners[banner_id]
                    self.storage.unlock_banner(ctx.author.id, ctx.guild.id, banner_id, banner_info['name'])
                    reward_text.append(f"**Banner:** {banner_info['emoji']} {banner_info['name']}")
            
            embed = discord.Embed(
                title="🎉 Achievement Unlocked!",
                description=f"{achievement_data['icon']} **{achievement_data['name']}**",
                color=discord.Color.gold()
            )
            embed.add_field(name="Description", value=achievement_data['description'], inline=False)
            
            if reward_text:
                embed.add_field(name="🎁 Rewards", value="\n".join(reward_text), inline=False)
            
            embed.set_footer(text="Congratulations!")
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ You already have this achievement!")

    # 🆕 DEBUG COMMANDS
    @commands.command()
    async def debug_banners(self, ctx):
        """Debug command to check all banner definitions"""
        embed = discord.Embed(title="🔧 Banner Debug Info", color=discord.Color.orange())
        
        for banner_id, banner_info in self.available_banners.items():
            embed.add_field(
                name=banner_id,
                value=f"Name: {banner_info['name']}\nRarity: {banner_info['rarity']}",
                inline=True
            )
        
        await ctx.send(embed=embed)

    @commands.command()
    async def test_banner_search(self, ctx, *, banner_name: str):
        """Test banner search functionality"""
        banner_id, banner_info = self.find_banner_by_name(banner_name)
        
        if banner_id:
            embed = discord.Embed(
                title="✅ Banner Found!",
                description=f"**ID:** {banner_id}\n**Name:** {banner_info['name']}",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="❌ Banner Not Found",
                description=f"No banner found for: {banner_name}",
                color=discord.Color.red()
            )
        
        await ctx.send(embed=embed)

    # 🚀 BACKWARD COMPATIBILITY - KEEP OLD COMMANDS WORKING
    @commands.command()
    async def backgrounds(self, ctx):
        """Backward compatibility - use !banners instead"""
        await ctx.send("🔄 This command has been updated to `!banners`. Redirecting...")
        await self.banners(ctx)

    @commands.command()  
    async def setbackground(self, ctx, *, background_name: str):
        """Backward compatibility - use !setbanner instead"""
        await ctx.send("🔄 This command has been updated to `!setbanner`. Redirecting...")
        await self.setbanner(ctx, banner_name=background_name)

    @commands.command()
    async def userbackgrounds(self, ctx, member: discord.Member = None):
        """Backward compatibility - use !userbanners instead"""
        await ctx.send("🔄 This command has been updated to `!userbanners`. Redirecting...")
        await self.userbanners(ctx, member=member)

    @commands.command()
    async def givebackground(self, ctx, member: discord.Member, *, background_name: str):
        """Backward compatibility - use !givebanner instead"""
        await ctx.send("🔄 This command has been updated to `!givebanner`. Redirecting...")
        await self.givebanner(ctx, member, banner_name=background_name)

    @commands.command()
    async def giveallbackgrounds(self, ctx, member: discord.Member = None):
        """Backward compatibility - use !giveallbanners instead"""
        await ctx.send("🔄 This command has been updated to `!giveallbanners`. Redirecting...")
        await self.giveallbanners(ctx, member)

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
                "`!allachievements [@user]` - View all achievements"
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

async def setup(bot):
    await bot.add_cog(ProfileSystem(bot))
