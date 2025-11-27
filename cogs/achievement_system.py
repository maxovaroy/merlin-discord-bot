import discord
from discord.ext import commands
from datetime import datetime

class AchievementSystem(commands.Cog):
    def __init__(self, bot, storage):
        self.bot = bot
        self.storage = storage
        
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

    @commands.command()
    async def badges(self, ctx, member: discord.Member = None):
        """View user badges"""
        if not self.storage:
            await ctx.send("❌ Storage system not available.")
            return
            
        target = member or ctx.author
        profile_data = self.storage.get_user_profile(target.id, ctx.guild.id)
        user_badges = profile_data.get('badges', [])
        
        embed = discord.Embed(
            title=f"🎖️ {target.display_name}'s Badges",
            color=discord.Color.gold()
        )
        
        if user_badges:
            badge_text = ""
            for badge_id in user_badges:
                if badge_id in self.available_badges:
                    badge_info = self.available_badges[badge_id]
                    badge_text += f"{badge_info['emoji']} **{badge_info['name']}** - {badge_info['description']}\n"
            
            embed.description = badge_text
        else:
            embed.description = "No badges earned yet! Keep being active to earn special badges!"
        
        await ctx.send(embed=embed)

async def setup(bot):
    from storage import DataStorage
    storage = DataStorage()
    await bot.add_cog(AchievementSystem(bot, storage))
