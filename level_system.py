import discord
from discord.ext import commands
import random
import json
import os
from datetime import datetime, timedelta

class LevelSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_file = "level_data.json"
        self.user_data = self.load_data()
        self.cooldowns = {}
        self.debug_mode = True  # Set to False to disable debug messages

    def load_data(self):
        """Load level data from file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_data(self):
        """Save level data to file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.user_data, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving level data: {e}")

    def calculate_level(self, xp):
        """Calculate level based on XP"""
        return int((xp / 100) ** 0.5) + 1

    def calculate_xp_for_level(self, level):
        """Calculate XP needed for a specific level"""
        return (level - 1) ** 2 * 100

    def get_user_data(self, user_id, server_id):
        """Get or create user data"""
        if str(server_id) not in self.user_data:
            self.user_data[str(server_id)] = {}
        
        if str(user_id) not in self.user_data[str(server_id)]:
            self.user_data[str(server_id)][str(user_id)] = {
                'xp': 0,
                'messages': 0,
                'last_message': None,
                'level_up_notifications': True
            }
        
        return self.user_data[str(server_id)][str(user_id)]

    def get_level_up_gif(self, level):
        """Get appropriate GIF URL for level up"""
        # Replace these with actual DIRECT GIF URLs from tenor/giphy
        level_gifs = {
            5: "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExMWhrajA3bG5oemVuMWYwbW5iODFlODNnbm1kMWRzN2ViOHMzY2s1aiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/LSLhspQ1g7dzG/giphy.gif",
            10: "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExdDE5M2E0NGF5ajVnZzVxMmZrMXNvdTFhZGJicHhseGl4a3BiNGFpbiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/8ydNXUthhXP018PLrC/giphy.gif", 
            20: "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHhjc29kMTU1NTIwcHQ1b2p1cnVsYzMyMzQ0ajU0aTNpM2RobDFhcyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/lQrLkfJdrD7SU/giphy.gif",
            50: "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExM29uajU4a3NzcGtleGFqdWw2ZGJlNjlpbmZjbTFhd2FhZHF3a2VueiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/LqfTaNPDBs8GiKy2am/giphy.gif",
        }
        
        default_gifs = [
            "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExcTBmYXFhOHZ4cWRyd2E5NGFhMHFtaDFoaWgzZnl0YXR5ZXNiZ2k4biZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/11sBLVxNs7v6WA/giphy.gif",
            "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExZnc1aTg4aGQwOHMzcTlqZHhrcHNsZHptaHN0eTc5ZDY4N2pzNmpjbiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/gizNN8vCaotYA/giphy.gif",
        ]
        
        if level in level_gifs:
            return level_gifs[level]
        elif level % 10 == 0:
            return random.choice(default_gifs)
        
        return random.choice(default_gifs)

    def create_level_up_embed(self, user, new_level, user_data):
        """Create level up embed with progress bar AND GIF"""
        
        # Get GIF
        gif_url = self.get_level_up_gif(new_level)
        
        # Calculate progress for next level
        current_xp = user_data['xp']
        current_level_xp = self.calculate_xp_for_level(new_level)
        next_level_xp = self.calculate_xp_for_level(new_level + 1)
        xp_progress = current_xp - current_level_xp
        xp_needed = next_level_xp - current_level_xp
        progress_percentage = (xp_progress / xp_needed) * 100 if xp_needed > 0 else 0
        
        # Create progress bar
        bars = 10
        filled_bars = int(progress_percentage / (100 / bars))
        progress_bar = "█" * filled_bars + "░" * (bars - filled_bars)
        
        embed = discord.Embed(
            title="🎉 LEVEL UP!",
            description=f"**{user.mention}** reached **Level {new_level}**!",
            color=discord.Color.gold()
        )
        
        # Set GIF as main image (large display)
        embed.set_image(url=gif_url)
        
        # Add progress bar to fields
        embed.add_field(
            name=f"Progress to Level {new_level + 1}",
            value=f"`{progress_bar}` **{progress_percentage:.1f}%**",
            inline=False
        )
        
        embed.add_field(name="Total XP", value=f"**{current_xp}** XP", inline=True)
        embed.add_field(name="Messages", value=f"**{user_data['messages']}**", inline=True)
        embed.add_field(name="XP to Next", value=f"**{xp_progress}** / **{xp_needed}**", inline=True)
        
        # Add special rewards for certain levels
        rewards = []
        if new_level == 5:
            rewards.append("🎨 Custom color role (soon™)")
        elif new_level == 10:
            rewards.append("🌟 Special badge in profile")
        elif new_level == 20:
            rewards.append("⚡ XP Boost unlocked")
        elif new_level == 50:
            rewards.append("👑 Legendary status")
        
        if rewards:
            embed.add_field(name="🎁 Rewards Unlocked", value="\n".join(rewards), inline=False)
        
        return embed

    def add_xp(self, user_id, server_id, xp_amount):
        """Add XP to user and check for level up"""
        user_data = self.get_user_data(user_id, server_id)
        old_level = self.calculate_level(user_data['xp'])
        
        user_data['xp'] += xp_amount
        user_data['messages'] += 1
        
        new_level = self.calculate_level(user_data['xp'])
        
        self.save_data()
        return old_level, new_level

    @commands.Cog.listener()
    async def on_message(self, message):
        """Give XP for messages"""
        if message.author.bot:
            return
        
        # Debug: Print message info
        if self.debug_mode:
            print(f"🔍 DEBUG - Message from {message.author} in #{message.channel}: '{message.content}'")
        
        # Check cooldown (prevent spam)
        user_id = message.author.id
        server_id = message.guild.id if message.guild else None
        
        if not server_id:
            if self.debug_mode:
                print("❌ DEBUG - No server ID (DM message), skipping XP")
            return
        
        current_time = datetime.now()
        if user_id in self.cooldowns:
            time_diff = current_time - self.cooldowns[user_id]
            if time_diff < timedelta(seconds=3):
                if self.debug_mode:
                    print(f"⏰ DEBUG - Cooldown active for {message.author}, {60 - time_diff.seconds}s remaining")
                return
        
        self.cooldowns[user_id] = current_time
        
        # Give random XP between 15-25 per message
        xp_gain = random.randint(15, 25)
        old_level, new_level = self.add_xp(user_id, server_id, xp_gain)
        
        # Debug: Print XP gain
        if self.debug_mode:
            user_data = self.get_user_data(user_id, server_id)
            print(f"🎯 DEBUG - {message.author} gained {xp_gain} XP")
            print(f"📊 DEBUG - Total: {user_data['xp']} XP, Level: {new_level}, Messages: {user_data['messages']}")
        
        # Check for level up
        if new_level > old_level:
            user_data = self.get_user_data(user_id, server_id)
            if user_data['level_up_notifications']:
                if self.debug_mode:
                    print(f"🎉 DEBUG - LEVEL UP! {message.author} reached level {new_level}")
                
                # Create and send level up embed with progress bar
                embed = self.create_level_up_embed(message.author, new_level, user_data)
                await message.channel.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def testlevelup(self, ctx, level: int = 5):
        """Test level-up messages with GIFs and progress bar (Admin only)"""
        # Simulate user data for testing
        test_user_data = {
            'xp': self.calculate_xp_for_level(level),
            'messages': level * 10,
            'level_up_notifications': True
        }
        
        # Create test embed
        embed = self.create_level_up_embed(ctx.author, level, test_user_data)
        embed.set_footer(text="🎯 TEST MODE - This is a level-up preview")
        
        await ctx.send(embed=embed)

    @commands.command()
    async def level(self, ctx, member: discord.Member = None):
        """Check your level or someone else's"""
        target = member or ctx.author
        user_data = self.get_user_data(target.id, ctx.guild.id)
        
        xp = user_data['xp']
        level = self.calculate_level(xp)
        messages = user_data['messages']
        
        # Calculate progress to next level
        current_level_xp = self.calculate_xp_for_level(level)
        next_level_xp = self.calculate_xp_for_level(level + 1)
        xp_progress = xp - current_level_xp
        xp_needed = next_level_xp - current_level_xp
        progress_percentage = (xp_progress / xp_needed) * 100
        
        # Create progress bar
        bars = 10
        filled_bars = int(progress_percentage / (100 / bars))
        progress_bar = "█" * filled_bars + "░" * (bars - filled_bars)
        
        embed = discord.Embed(
            title=f"📊 Level Stats - {target.display_name}",
            color=target.color
        )
        
        embed.set_thumbnail(url=target.avatar.url if target.avatar else target.default_avatar.url)
        embed.add_field(name="Level", value=f"**{level}**", inline=True)
        embed.add_field(name="XP", value=f"**{xp}**", inline=True)
        embed.add_field(name="Messages", value=f"**{messages}**", inline=True)
        
        embed.add_field(
            name=f"Progress to Level {level + 1}",
            value=f"`{progress_bar}` {progress_percentage:.1f}%",
            inline=False
        )
        
        embed.add_field(
            name="XP Needed",
            value=f"**{xp_progress}** / **{xp_needed}** XP",
            inline=False
        )
        
        # Add rank if available
        server_data = self.user_data.get(str(ctx.guild.id), {})
        if server_data:
            sorted_users = sorted(
                server_data.items(),
                key=lambda x: x[1]['xp'],
                reverse=True
            )
            rank = next((i + 1 for i, (uid, _) in enumerate(sorted_users) if uid == str(target.id)), None)
            if rank:
                embed.add_field(name="Server Rank", value=f"**#{rank}**", inline=True)
        
        await ctx.send(embed=embed)

    @commands.command()
    async def leaderboard(self, ctx):
        """Show server leaderboard"""
        server_data = self.user_data.get(str(ctx.guild.id), {})
        
        if not server_data:
            await ctx.send("❌ No level data available for this server yet!")
            return
        
        # Get top 10 users
        sorted_users = sorted(
            server_data.items(),
            key=lambda x: x[1]['xp'],
            reverse=True
        )[:10]
        
        embed = discord.Embed(
            title="🏆 Server Leaderboard",
            color=discord.Color.gold()
        )
        
        description = ""
        for i, (user_id, data) in enumerate(sorted_users, 1):
            try:
                user = await self.bot.fetch_user(int(user_id))
                level = self.calculate_level(data['xp'])
                description += f"**{i}. {user.display_name}** - Level {level} ({data['xp']} XP)\n"
            except:
                description += f"**{i}. Unknown User** - Level {level} ({data['xp']} XP)\n"
        
        embed.description = description
        embed.set_footer(text=f"Total users: {len(server_data)}")
        
        await ctx.send(embed=embed)

    @commands.command()
    async def rank(self, ctx, member: discord.Member = None):
        """Show your rank in the server"""
        target = member or ctx.author
        server_data = self.user_data.get(str(ctx.guild.id), {})
        
        if not server_data:
            await ctx.send("❌ No level data available for this server yet!")
            return
        
        sorted_users = sorted(
            server_data.items(),
            key=lambda x: x[1]['xp'],
            reverse=True
        )
        
        rank = next((i + 1 for i, (uid, _) in enumerate(sorted_users) if uid == str(target.id)), None)
        
        if rank:
            user_data = self.get_user_data(target.id, ctx.guild.id)
            level = self.calculate_level(user_data['xp'])
            total_users = len(server_data)
            
            embed = discord.Embed(
                title=f"📈 Rank - {target.display_name}",
                color=discord.Color.blue()
            )
            embed.add_field(name="Rank", value=f"**#{rank}** / {total_users}", inline=True)
            embed.add_field(name="Level", value=f"**{level}**", inline=True)
            embed.add_field(name="XP", value=f"**{user_data['xp']}**", inline=True)
            
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ User not found in leaderboard!")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def givexp(self, ctx, member: discord.Member, xp_amount: int):
        """Give XP to a user (Admin only)"""
        old_level, new_level = self.add_xp(member.id, ctx.guild.id, xp_amount)
        
        embed = discord.Embed(
            title="🎁 XP Given",
            color=discord.Color.green()
        )
        embed.add_field(name="User", value=member.mention, inline=True)
        embed.add_field(name="XP Given", value=xp_amount, inline=True)
        embed.add_field(name="New Level", value=new_level, inline=True)
        
        if new_level > old_level:
            embed.add_field(name="Level Up!", value="🎉 User leveled up!", inline=False)
        
        await ctx.send(embed=embed)

    @commands.command()
    async def togglenotifications(self, ctx):
        """Toggle level-up notifications on/off"""
        user_data = self.get_user_data(ctx.author.id, ctx.guild.id)
        user_data['level_up_notifications'] = not user_data['level_up_notifications']
        
        status = "enabled" if user_data['level_up_notifications'] else "disabled"
        await ctx.send(f"✅ Level-up notifications **{status}**!")

    @commands.command()
    async def levelsystem(self, ctx):
        """Show level system information"""
        embed = discord.Embed(
            title="📈 Level System",
            description="Earn XP by being active in the server!",
            color=discord.Color.purple()
        )
        
        embed.add_field(
            name="🎯 How to earn XP",
            value=(
                "• Send messages: 15-25 XP per message\n"
                "• 1 minute cooldown between XP gains\n"
                "• Stay active to level up faster!"
            ),
            inline=False
        )
        
        embed.add_field(
            name="📊 Commands",
            value=(
                "`!level [@user]` - Check level\n"
                "`!leaderboard` - Server top 10\n"
                "`!rank [@user]` - Check rank\n"
                "`!togglenotifications` - Toggle level-up messages\n"
                "`!levelsystem` - This info"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🏆 Level Rewards",
            value=(
                "• **Level 5**: Custom color role\n"
                "• **Level 10**: Special badge\n"
                "• **Level 20**: XP Boost\n"
                "• **Level 50**: Legendary status"
            ),
            inline=False
        )
        
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def xpdebug(self, ctx, user: discord.Member = None):
        """Debug XP information for a user (Admin only)"""
        target = user or ctx.author
        user_data = self.get_user_data(target.id, ctx.guild.id)
        
        embed = discord.Embed(
            title=f"🐛 XP Debug - {target.display_name}",
            color=discord.Color.orange()
        )
        
        embed.add_field(name="User ID", value=target.id, inline=True)
        embed.add_field(name="Server ID", value=ctx.guild.id, inline=True)
        embed.add_field(name="Total XP", value=user_data['xp'], inline=True)
        embed.add_field(name="Messages", value=user_data['messages'], inline=True)
        embed.add_field(name="Current Level", value=self.calculate_level(user_data['xp']), inline=True)
        embed.add_field(name="Notifications", value="On" if user_data['level_up_notifications'] else "Off", inline=True)
        
        # Check cooldown status
        current_time = datetime.now()
        if target.id in self.cooldowns:
            time_diff = current_time - self.cooldowns[target.id]
            cooldown_remaining = max(0, 60 - time_diff.seconds)
            embed.add_field(name="Cooldown", value=f"{cooldown_remaining}s remaining", inline=True)
        else:
            embed.add_field(name="Cooldown", value="No cooldown", inline=True)
        
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def toggledebug(self, ctx):
        """Toggle debug mode on/off (Admin only)"""
        self.debug_mode = not self.debug_mode
        status = "ON" if self.debug_mode else "OFF"
        await ctx.send(f"🔧 Debug mode **{status}**")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def xpstats(self, ctx):
        """Show server XP statistics (Admin only)"""
        server_data = self.user_data.get(str(ctx.guild.id), {})
        
        if not server_data:
            await ctx.send("❌ No level data available for this server yet!")
            return
        
        total_users = len(server_data)
        total_xp = sum(data['xp'] for data in server_data.values())
        total_messages = sum(data['messages'] for data in server_data.values())
        avg_xp = total_xp / total_users if total_users > 0 else 0
        avg_level = sum(self.calculate_level(data['xp']) for data in server_data.values()) / total_users if total_users > 0 else 0
        
        embed = discord.Embed(
            title="📈 Server XP Statistics",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="Total Users", value=total_users, inline=True)
        embed.add_field(name="Total XP", value=total_xp, inline=True)
        embed.add_field(name="Total Messages", value=total_messages, inline=True)
        embed.add_field(name="Average XP", value=f"{avg_xp:.1f}", inline=True)
        embed.add_field(name="Average Level", value=f"{avg_level:.1f}", inline=True)
        embed.add_field(name="Debug Mode", value="ON" if self.debug_mode else "OFF", inline=True)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(LevelSystem(bot))