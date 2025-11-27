import discord
from discord.ext import commands
import asyncio
import sys
import os

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Try to import storage - but with a fallback
try:
    from storage import DataStorage
    STORAGE_AVAILABLE = True
    print("✅ Storage imported successfully!")
except ImportError as e:
    print(f"⚠️ Storage import failed: {e}")
    STORAGE_AVAILABLE = False
    
    # Create a simple fallback
    class FallbackStorage:
        def __init__(self):
            self.warnings = {}
            self.muted_users = {}
        
        def add_warning(self, user_id, server_id, reason):
            server_key = str(server_id)
            user_key = str(user_id)
            if server_key not in self.warnings:
                self.warnings[server_key] = {}
            if user_key not in self.warnings[server_key]:
                self.warnings[server_key][user_key] = []
            self.warnings[server_key][user_key].append({'reason': reason})
            return len(self.warnings[server_key][user_key])
        
        def get_warnings(self, user_id, server_id):
            server_key = str(server_id)
            user_key = str(user_id)
            return self.warnings.get(server_key, {}).get(user_key, [])
        
        def clear_warnings(self, user_id, server_id):
            server_key = str(server_id)
            user_key = str(user_id)
            if server_key in self.warnings and user_key in self.warnings[server_key]:
                del self.warnings[server_key][user_key]
    
    DataStorage = FallbackStorage

class AdvancedModeration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.storage = DataStorage()
        print(f"✅ Storage initialized: {type(self.storage).__name__}")

    @commands.command()
    async def teststorage(self, ctx):
        """Test if storage is working"""
        if STORAGE_AVAILABLE:
            warnings = self.storage.get_warnings(ctx.author.id, ctx.guild.id)
            await ctx.send(f"✅ Storage is WORKING! You have {len(warnings)} warnings.")
        else:
            await ctx.send("⚠️ Using fallback storage (no persistence)")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Warn a member with storage"""
        warning_count = self.storage.add_warning(member.id, ctx.guild.id, reason)
        
        embed = discord.Embed(
            title="⚠️ Member Warned",
            description=f"{member.mention} has been warned.",
            color=discord.Color.yellow()
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Total Warnings", value=warning_count, inline=False)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
        
        if not STORAGE_AVAILABLE:
            embed.set_footer(text="⚠️ Using temporary storage (will reset on restart)")
        
        await ctx.send(embed=embed)

    @commands.command()
    async def mywarnings(self, ctx, member: discord.Member = None):
        """Check your warnings or someone else's"""
        target = member or ctx.author
        warnings = self.storage.get_warnings(target.id, ctx.guild.id)
        
        embed = discord.Embed(
            title=f"📋 Warnings for {target.display_name}",
            color=discord.Color.gold()
        )
        
        if warnings:
            for i, warning in enumerate(warnings, 1):
                embed.add_field(
                    name=f"Warning #{i}",
                    value=warning['reason'],
                    inline=False
                )
        else:
            embed.description = "No warnings found. Good job! 🎉"
        
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Kick a member"""
        try:
            await member.kick(reason=reason)
            embed = discord.Embed(
                title="👢 Member Kicked",
                description=f"{member.mention} has been kicked.",
                color=discord.Color.orange()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Could not kick {member.mention}: {e}")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int = 5):
        """Clear messages"""
        if amount > 100:
            await ctx.send("❌ Cannot clear more than 100 messages at once.")
            return
        
        deleted = await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"🗑️ Cleared {len(deleted) - 1} messages.", delete_after=3)

async def setup(bot):
    await bot.add_cog(AdvancedModeration(bot))
    print("✅ Advanced Moderations cog loaded with storage!")
