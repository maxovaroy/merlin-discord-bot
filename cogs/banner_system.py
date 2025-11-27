import discord
from discord.ext import commands
import random

class BannerSystem(commands.Cog):
    def __init__(self, bot, storage):
        self.bot = bot
        self.storage = storage
        
        # 🎨 BANNER SYSTEM
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
            'mikey': {
                'name': 'Mikey', 
                'emoji': '👽', 
                'rarity': 'legendary',
                'banner_url': 'https://i.postimg.cc/yYy3mzcz/1000240143.png',
                'color': '#C2540A'
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

    def find_banner_by_name(self, banner_name):
        """Find banner by name (case-insensitive and flexible matching)"""
        if not banner_name:
            return None, None
            
        banner_name_lower = banner_name.lower().strip()
        
        # First, check exact matches
        for banner_id, banner_info in self.available_banners.items():
            # Exact ID match
            if banner_id.lower() == banner_name_lower:
                return banner_id, banner_info
            
            # Exact name match
            if banner_info['name'].lower() == banner_name_lower:
                return banner_id, banner_info
        
        # Then check partial matches
        for banner_id, banner_info in self.available_banners.items():
            banner_name_display = banner_info['name'].lower()
            
            # Remove spaces and special characters for better matching
            search_term = banner_name_lower.replace(' ', '').replace('_', '').replace('-', '')
            banner_term = banner_name_display.replace(' ', '').replace('_', '').replace('-', '')
            
            # Partial match in display name
            if banner_name_lower in banner_name_display:
                return banner_id, banner_info
            
            # Partial match in ID
            if banner_name_lower in banner_id.lower():
                return banner_id, banner_info
            
            # Fuzzy match without spaces
            if search_term in banner_term or banner_term in search_term:
                return banner_id, banner_info
        
        return None, None

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
    from storage import DataStorage
    storage = DataStorage()
    await bot.add_cog(BannerSystem(bot, storage))
