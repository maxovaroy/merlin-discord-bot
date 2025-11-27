import discord
from discord.ext import commands
import random
from config import Config
import json
import os
from datetime import datetime

class AutoReply(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mute_data_file = "mute_data.json"
        self.muted_users = self.load_mute_data()

    def load_mute_data(self):
        """Load mute data from file"""
        if os.path.exists(self.mute_data_file):
            try:
                with open(self.mute_data_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_mute_data(self):
        """Save mute data to file"""
        try:
            with open(self.mute_data_file, 'w') as f:
                json.dump(self.muted_users, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving mute data: {e}")

    def is_user_muted(self, user_id, server_id):
        """Check if user has auto-replies muted"""
        server_key = str(server_id)
        user_key = str(user_id)
        return (server_key in self.muted_users and 
                user_key in self.muted_users[server_key])

    def mute_user(self, user_id, server_id):
        """Mute auto-replies for a user"""
        server_key = str(server_id)
        user_key = str(user_id)
        
        if server_key not in self.muted_users:
            self.muted_users[server_key] = {}
        
        self.muted_users[server_key][user_key] = {
            'muted_at': datetime.now().isoformat(),
            'muted_by': user_key  # For self-mute, it's the user themselves
        }
        self.save_mute_data()

    def unmute_user(self, user_id, server_id):
        """Unmute auto-replies for a user"""
        server_key = str(server_id)
        user_key = str(user_id)
        
        if (server_key in self.muted_users and 
            user_key in self.muted_users[server_key]):
            del self.muted_users[server_key][user_key]
            self.save_mute_data()

    @commands.Cog.listener()
    async def on_message(self, message):
        """Handle auto-reply to messages"""
        if message.author.bot:
            return
        
        # NEW: Check if user has muted auto-replies
        if message.guild and self.is_user_muted(message.author.id, message.guild.id):
            return
        
        # Don't reply to commands
        if message.content.startswith(Config.PREFIX):
            return
        
        content = message.content.lower()
        
        # Check special replies first
        for trigger, reply in Config.SPECIAL_REPLIES.items():
            if trigger in content:
                await message.reply(reply)
                return
        
        # Check regular auto-replies
        for trigger, replies in Config.AUTO_REPLIES.items():
            if trigger in content:
                if random.random() < Config.AUTO_REPLY_CHANCE:
                    response = random.choice(replies)
                    await message.reply(response)
                    return

    # NEW: Mute Commands
    @commands.command()
    async def muteautoreply(self, ctx):
        """Mute auto-replies for yourself"""
        if self.is_user_muted(ctx.author.id, ctx.guild.id):
            embed = discord.Embed(
                title="🔇 Already Muted",
                description="You already have auto-replies muted!",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            return
        
        self.mute_user(ctx.author.id, ctx.guild.id)
        
        embed = discord.Embed(
            title="🔇 Auto-Replies Muted",
            description="I won't auto-reply to your messages anymore!",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="To unmute:",
            value=f"Use `{Config.PREFIX}unmuteautoreply`",
            inline=False
        )
        embed.add_field(
            name="Note:",
            value="This only affects auto-replies, not command responses",
            inline=False
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def unmuteautoreply(self, ctx):
        """Unmute auto-replies for yourself"""
        if not self.is_user_muted(ctx.author.id, ctx.guild.id):
            embed = discord.Embed(
                title="🔊 Already Unmuted",
                description="Auto-replies are already active for you!",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            return
        
        self.unmute_user(ctx.author.id, ctx.guild.id)
        
        embed = discord.Embed(
            title="🔊 Auto-Replies Unmuted",
            description="I'll auto-reply to your messages again!",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def autoreplystatus(self, ctx):
        """Check your auto-reply mute status"""
        is_muted = self.is_user_muted(ctx.author.id, ctx.guild.id)
        
        if is_muted:
            embed = discord.Embed(
                title="🔇 Auto-Replies: MUTED",
                description="I won't auto-reply to your messages",
                color=discord.Color.orange()
            )
            # Get mute timestamp
            server_key = str(ctx.guild.id)
            user_key = str(ctx.author.id)
            mute_info = self.muted_users[server_key][user_key]
            muted_at = datetime.fromisoformat(mute_info['muted_at'])
            embed.add_field(
                name="Muted since:",
                value=f"<t:{int(muted_at.timestamp())}:R>",
                inline=False
            )
        else:
            embed = discord.Embed(
                title="🔊 Auto-Replies: ACTIVE", 
                description="I might auto-reply to your messages (30% chance)",
                color=discord.Color.green()
            )
        
        embed.add_field(
            name="Commands:",
            value=(
                f"`{Config.PREFIX}muteautoreply` - Mute auto-replies\n"
                f"`{Config.PREFIX}unmuteautoreply` - Unmute auto-replies\n"
                f"`{Config.PREFIX}autoreplystatus` - Check status"
            ),
            inline=False
        )
        
        await ctx.send(embed=embed)

    # Admin commands for muting other users
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def muteautoreplyuser(self, ctx, member: discord.Member):
        """Mute auto-replies for another user (Admin only)"""
        if member.bot:
            await ctx.send("❌ You can't mute auto-replies for bots!")
            return
            
        if self.is_user_muted(member.id, ctx.guild.id):
            embed = discord.Embed(
                title="🔇 Already Muted",
                description=f"{member.mention} already has auto-replies muted!",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            return
        
        self.mute_user(member.id, ctx.guild.id)
        
        embed = discord.Embed(
            title="🔇 Auto-Replies Muted",
            description=f"Auto-replies muted for {member.mention}",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Muted by:",
            value=ctx.author.mention,
            inline=True
        )
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unmuteautoreplyuser(self, ctx, member: discord.Member):
        """Unmute auto-replies for another user (Admin only)"""
        if not self.is_user_muted(member.id, ctx.guild.id):
            embed = discord.Embed(
                title="🔊 Already Unmuted",
                description=f"{member.mention} already has auto-replies active!",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            return
        
        self.unmute_user(member.id, ctx.guild.id)
        
        embed = discord.Embed(
            title="🔊 Auto-Replies Unmuted",
            description=f"Auto-replies unmuted for {member.mention}",
            color=discord.Color.green()
        )
        embed.add_field(
            name="Unmuted by:",
            value=ctx.author.mention,
            inline=True
        )
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def autoreplystats(self, ctx):
        """Show auto-reply statistics for this server (Admin only)"""
        server_key = str(ctx.guild.id)
        muted_count = 0
        
        if server_key in self.muted_users:
            muted_count = len(self.muted_users[server_key])
        
        total_members = ctx.guild.member_count
        active_percentage = ((total_members - muted_count) / total_members) * 100
        
        embed = discord.Embed(
            title="📊 Auto-Reply Statistics",
            color=discord.Color.purple()
        )
        
        embed.add_field(
            name="Server Members",
            value=f"**{total_members}** total",
            inline=True
        )
        embed.add_field(
            name="Muted Users", 
            value=f"**{muted_count}** users",
            inline=True
        )
        embed.add_field(
            name="Active Users",
            value=f"**{total_members - muted_count}** ({active_percentage:.1f}%)",
            inline=True
        )
        
        if muted_count > 0:
            muted_list = []
            for user_id in list(self.muted_users[server_key].keys())[:5]:  # Show first 5
                try:
                    user = await self.bot.fetch_user(int(user_id))
                    muted_list.append(f"• {user.display_name}")
                except:
                    muted_list.append(f"• Unknown User ({user_id})")
            
            if muted_list:
                embed.add_field(
                    name=f"Recently Muted ({len(muted_list)})",
                    value="\n".join(muted_list),
                    inline=False
                )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AutoReply(bot))