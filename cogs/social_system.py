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

class SocialSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if STORAGE_AVAILABLE:
            self.storage = DataStorage()
            print("✅ Social System loaded with storage!")
        else:
            self.storage = None
            print("❌ Social System loaded WITHOUT storage - features limited")
        
        self.marriage_cooldowns = {}
        self.rep_cooldowns = {}
        self.adoption_cooldowns = {}

    @commands.Cog.listener()
    async def on_ready(self):
        """Called when cog is loaded and ready"""
        print(f"✅ {self.__class__.__name__} cog loaded successfully!")
        if not STORAGE_AVAILABLE:
            print("❌ Storage system not available - social features limited")

    # 💍 MARRIAGE COMMANDS
    @commands.command()
    async def marry(self, ctx, member: discord.Member):
        """Propose marriage to another user"""
        if not self.storage:
            await ctx.send("❌ Storage system not available. Please contact bot administrator.")
            return
            
        if member.bot:
            await ctx.send("❌ You can't marry a bot! They have no heart... 💔")
            return
        
        if member == ctx.author:
            await ctx.send("❌ You can't marry yourself! That's just sad...")
            return
        
        # Check cooldown
        if self.is_on_cooldown(ctx.author.id, self.marriage_cooldowns, 3600):
            await ctx.send("💔 Calm down! You can only propose once per hour.")
            return
        
        # Check if already married
        if self.storage.is_married(ctx.author.id, ctx.guild.id):
            marriage_info = self.storage.get_marriage(ctx.author.id, ctx.guild.id)
            await ctx.send(f"❌ You're already married to <@{marriage_info['partner']}>!")
            return
        
        if self.storage.is_married(member.id, ctx.guild.id):
            await ctx.send("❌ That user is already married! Don't be a homewrecker!")
            return
        
        # Create marriage proposal
        embed = discord.Embed(
            title="💍 Marriage Proposal!",
            description=f"{ctx.author.mention} has proposed to {member.mention}!",
            color=discord.Color.pink()
        )
        embed.add_field(
            name="Will you accept?",
            value="React with ✅ to accept or ❌ to reject",
            inline=False
        )
        embed.set_footer(text="Proposal expires in 2 minutes")
        
        proposal_msg = await ctx.send(embed=embed)
        await proposal_msg.add_reaction("✅")
        await proposal_msg.add_reaction("❌")
        
        # Wait for response
        def check(reaction, user):
            return user == member and str(reaction.emoji) in ["✅", "❌"] and reaction.message.id == proposal_msg.id
        
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=120.0, check=check)
            
            if str(reaction.emoji) == "✅":
                # Marriage accepted!
                self.storage.add_marriage(ctx.author.id, member.id, ctx.guild.id)
                
                success_embed = discord.Embed(
                    title="🎉 Congratulations!",
                    description=f"{ctx.author.mention} 💕 {member.mention}",
                    color=discord.Color.gold()
                )
                success_embed.add_field(
                    name="You are now married!",
                    value="May your love last forever! 💖",
                    inline=False
                )
                success_embed.set_footer(text=f"Married on {datetime.now().strftime('%Y-%m-%d')}")
                await ctx.send(embed=success_embed)
                
            else:
                await ctx.send(f"💔 {member.mention} rejected the proposal... Better luck next time!")
                
        except TimeoutError:
            await ctx.send("⏰ Marriage proposal expired... They took too long to decide!")

    @commands.command()
    async def divorce(self, ctx):
        """Divorce your current partner"""
        if not self.storage:
            await ctx.send("❌ Storage system not available. Please contact bot administrator.")
            return
            
        if not self.storage.is_married(ctx.author.id, ctx.guild.id):
            await ctx.send("❌ You're not married! You can't divorce nobody...")
            return
        
        marriage_info = self.storage.get_marriage(ctx.author.id, ctx.guild.id)
        partner_id = marriage_info['partner']
        
        embed = discord.Embed(
            title="💔 Divorce",
            description=f"Are you sure you want to divorce <@{partner_id}>?",
            color=discord.Color.red()
        )
        embed.add_field(
            name="This action cannot be undone!",
            value="React with 💔 to confirm divorce",
            inline=False
        )
        
        divorce_msg = await ctx.send(embed=embed)
        await divorce_msg.add_reaction("💔")
        
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) == "💔" and reaction.message.id == divorce_msg.id
        
        try:
            await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
            
            # Process divorce
            self.storage.remove_marriage(ctx.author.id, ctx.guild.id)
            
            await ctx.send(f"💔 **DIVORCE FINALIZED**\n{ctx.author.mention} and <@{partner_id}> are no longer married.")
            
        except TimeoutError:
            await ctx.send("✅ Divorce cancelled. Maybe give it another chance?")

    @commands.command()
    async def marriage(self, ctx, member: discord.Member = None):
        """Check marriage status"""
        if not self.storage:
            await ctx.send("❌ Storage system not available. Please contact bot administrator.")
            return
            
        target = member or ctx.author
        
        if not self.storage.is_married(target.id, ctx.guild.id):
            if target == ctx.author:
                await ctx.send("💔 You're not married! Use `!marry @user` to find love!")
            else:
                await ctx.send(f"💔 {target.display_name} is not married!")
            return
        
        marriage_info = self.storage.get_marriage(target.id, ctx.guild.id)
        married_at = datetime.fromisoformat(marriage_info['married_at'])
        days_married = (datetime.now() - married_at).days
        
        embed = discord.Embed(
            title="💑 Marriage Information",
            color=discord.Color.pink()
        )
        embed.add_field(name="Couple", value=f"{target.mention} 💕 <@{marriage_info['partner']}>", inline=False)
        embed.add_field(name="Married Since", value=married_at.strftime("%B %d, %Y"), inline=True)
        embed.add_field(name="Days Together", value=f"{days_married} days", inline=True)
        
        # Add anniversary message
        if days_married % 365 == 0 and days_married > 0:
            years = days_married // 365
            embed.add_field(name="🎊 Anniversary!", value=f"**{years} year{'s' if years > 1 else ''} together!**", inline=False)
        
        await ctx.send(embed=embed)

    # 👨‍👩‍👧‍👦 CHILDREN COMMANDS
    @commands.command()
    async def adopt(self, ctx, *, child_name: str):
        """Adopt a child (must be married)"""
        if not self.storage:
            await ctx.send("❌ Storage system not available. Please contact bot administrator.")
            return
            
        if not self.storage.is_married(ctx.author.id, ctx.guild.id):
            await ctx.send("❌ You need to be married to adopt a child! Find love first! 💕")
            return
        
        # Check cooldown (1 adoption per day)
        if self.is_on_cooldown(ctx.author.id, self.adoption_cooldowns, 86400):
            await ctx.send("❌ You can only adopt one child per day! Be responsible!")
            return
        
        marriage_info = self.storage.get_marriage(ctx.author.id, ctx.guild.id)
        partner_id = marriage_info['partner']
        
        self.storage.add_child(ctx.author.id, child_name, ctx.guild.id)
        
        embed = discord.Embed(
            title="👶 Congratulations!",
            description=f"**{child_name}** has been adopted!",
            color=discord.Color.light_grey()
        )
        embed.add_field(
            name="Parents",
            value=f"{ctx.author.mention} and <@{partner_id}>",
            inline=False
        )
        embed.add_field(
            name="Take good care of your new child!",
            value="Use `!children` to see your family",
            inline=False
        )
        
        await ctx.send(embed=embed)

    @commands.command()
    async def children(self, ctx, member: discord.Member = None):
        """View your children or someone else's"""
        if not self.storage:
            await ctx.send("❌ Storage system not available. Please contact bot administrator.")
            return
            
        target = member or ctx.author
        children = self.storage.get_children(target.id, ctx.guild.id)
        
        if not children:
            if target == ctx.author:
                await ctx.send("👶 You don't have any children! Use `!adopt <name>` to adopt one!")
            else:
                await ctx.send(f"👶 {target.display_name} doesn't have any children!")
            return
        
        embed = discord.Embed(
            title=f"👨‍👩‍👧‍👦 {target.display_name}'s Children",
            color=discord.Color.light_grey()
        )
        
        for i, child in enumerate(children[:10], 1):
            adopted_date = datetime.fromisoformat(child['adopted_at'])
            days_ago = (datetime.now() - adopted_date).days
            
            embed.add_field(
                name=f"{i}. {child['name']}",
                value=f"Level: {child['level']} | Happiness: {child['happiness']}% | Adopted {days_ago} days ago",
                inline=False
            )
        
        if len(children) > 10:
            embed.set_footer(text=f"Showing 10 of {len(children)} children")
        
        await ctx.send(embed=embed)

    # 👥 FRIEND COMMANDS
    @commands.command()
    async def addfriend(self, ctx, member: discord.Member):
        """Add a friend"""
        if not self.storage:
            await ctx.send("❌ Storage system not available. Please contact bot administrator.")
            return
            
        if member.bot:
            await ctx.send("❌ Bots can't be friends... they're just programs! 🤖")
            return
        
        if member == ctx.author:
            await ctx.send("❌ You can't add yourself as a friend! That's just sad...")
            return
        
        if member.id in self.storage.get_friends(ctx.author.id, ctx.guild.id):
            await ctx.send(f"❌ {member.display_name} is already your friend!")
            return
        
        self.storage.add_friend(ctx.author.id, member.id, ctx.guild.id)
        
        embed = discord.Embed(
            title="👥 Friend Added!",
            description=f"You are now friends with {member.mention}!",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def unfriend(self, ctx, member: discord.Member):
        """Remove a friend"""
        if not self.storage:
            await ctx.send("❌ Storage system not available. Please contact bot administrator.")
            return
            
        if member.id not in self.storage.get_friends(ctx.author.id, ctx.guild.id):
            await ctx.send(f"❌ {member.display_name} isn't your friend!")
            return
        
        self.storage.remove_friend(ctx.author.id, member.id, ctx.guild.id)
        await ctx.send(f"👥 **Unfriended** {member.display_name}... friendship over! 💔")

    @commands.command()
    async def friends(self, ctx, member: discord.Member = None):
        """View your friends list"""
        if not self.storage:
            await ctx.send("❌ Storage system not available. Please contact bot administrator.")
            return
            
        target = member or ctx.author
        friend_ids = self.storage.get_friends(target.id, ctx.guild.id)
        
        if not friend_ids:
            if target == ctx.author:
                await ctx.send("👥 You don't have any friends yet... Use `!addfriend @user` to make some!")
            else:
                await ctx.send(f"👥 {target.display_name} doesn't have any friends... how sad!")
            return
        
        embed = discord.Embed(
            title=f"👥 {target.display_name}'s Friends",
            color=discord.Color.blue()
        )
        
        friends_list = []
        for friend_id in friend_ids[:15]:
            try:
                friend_user = await self.bot.fetch_user(friend_id)
                friends_list.append(friend_user.display_name)
            except:
                friends_list.append(f"Unknown User ({friend_id})")
        
        embed.description = "\n".join([f"• {name}" for name in friends_list])
        embed.set_footer(text=f"Total friends: {len(friend_ids)}")
        
        await ctx.send(embed=embed)

    # ⭐ REPUTATION COMMANDS
    @commands.command()
    async def rep(self, ctx, member: discord.Member = None):
        """Give reputation to a user"""
        if not self.storage:
            await ctx.send("❌ Storage system not available. Please contact bot administrator.")
            return
            
        if not member:
            await ctx.send("❌ Please mention a user to give reputation to!")
            return
        
        if member.bot:
            await ctx.send("❌ You can't give reputation to bots!")
            return
        
        if member == ctx.author:
            await ctx.send("❌ You can't give reputation to yourself!")
            return
        
        # Check cooldown (12 hours between rep)
        if self.is_on_cooldown(ctx.author.id, self.rep_cooldowns, 43200):
            await ctx.send("⏰ You can only give reputation once every 12 hours!")
            return
        
        new_rep = self.storage.add_reputation(member.id, ctx.guild.id)
        
        embed = discord.Embed(
            title="⭐ Reputation Given!",
            description=f"{ctx.author.mention} gave reputation to {member.mention}!",
            color=discord.Color.gold()
        )
        embed.add_field(name="Total Reputation", value=f"**{new_rep}** points", inline=True)
        
        # Special messages for rep milestones
        if new_rep == 10:
            embed.add_field(name="🎉 Milestone!", value="**10 Reputation!**", inline=True)
        elif new_rep == 50:
            embed.add_field(name="🏆 Achievement!", value="**50 Reputation!**", inline=True)
        elif new_rep == 100:
            embed.add_field(name="🌟 Legendary!", value="**100 Reputation!**", inline=True)
        
        await ctx.send(embed=embed)

    @commands.command()
    async def reputation(self, ctx, member: discord.Member = None):
        """Check reputation points"""
        if not self.storage:
            await ctx.send("❌ Storage system not available. Please contact bot administrator.")
            return
            
        target = member or ctx.author
        rep_points = self.storage.get_reputation(target.id, ctx.guild.id)
        
        embed = discord.Embed(
            title=f"⭐ {target.display_name}'s Reputation",
            color=discord.Color.gold()
        )
        embed.add_field(name="Reputation Points", value=f"**{rep_points}**", inline=True)
        
        # Reputation rank based on points
        if rep_points == 0:
            rank = "Newcomer"
        elif rep_points < 10:
            rank = "Trusted"
        elif rep_points < 50:
            rank = "Respected"
        elif rep_points < 100:
            rank = "Famous"
        else:
            rank = "Legendary"
        
        embed.add_field(name="Rank", value=rank, inline=True)
        embed.set_footer(text="Use !rep @user to give reputation")
        
        await ctx.send(embed=embed)

    # 🎁 GIFT COMMANDS
    @commands.command()
    async def gift(self, ctx, member: discord.Member):
        """Send a gift to another user"""
        if not self.storage:
            await ctx.send("❌ Storage system not available. Please contact bot administrator.")
            return
            
        if member.bot:
            await ctx.send("❌ Bots don't need gifts! They prefer electricity! ⚡")
            return
        
        if member == ctx.author:
            await ctx.send("❌ You can't gift yourself! That's not how gifting works!")
            return
        
        gift_count = self.storage.add_gift(member.id, ctx.guild.id)
        
        gifts = ["💝", "🎁", "🎀", "💐", "🌸", "💖", "✨", "🌟"]
        gift_emoji = random.choice(gifts)
        
        embed = discord.Embed(
            title=f"{gift_emoji} Gift Sent!",
            description=f"{ctx.author.mention} sent a gift to {member.mention}!",
            color=discord.Color.pink()
        )
        embed.add_field(name="Total Gifts Received", value=f"**{gift_count}** gifts", inline=True)
        
        await ctx.send(embed=embed)

    # 📊 SOCIAL STATS COMMAND
    @commands.command()
    async def socialstats(self, ctx, member: discord.Member = None):
        """View comprehensive social statistics"""
        if not self.storage:
            await ctx.send("❌ Storage system not available. Please contact bot administrator.")
            return
            
        target = member or ctx.author
        
        embed = discord.Embed(
            title=f"📊 Social Stats - {target.display_name}",
            color=discord.Color.purple()
        )
        
        # Marriage status
        if self.storage.is_married(target.id, ctx.guild.id):
            marriage_info = self.storage.get_marriage(target.id, ctx.guild.id)
            married_at = datetime.fromisoformat(marriage_info['married_at'])
            days_married = (datetime.now() - married_at).days
            embed.add_field(name="💍 Married To", value=f"<@{marriage_info['partner']}>", inline=True)
            embed.add_field(name="Days Married", value=days_married, inline=True)
        else:
            embed.add_field(name="💍 Status", value="Single", inline=True)
        
        # Children count
        children = self.storage.get_children(target.id, ctx.guild.id)
        embed.add_field(name="👶 Children", value=len(children), inline=True)
        
        # Friends count
        friends = self.storage.get_friends(target.id, ctx.guild.id)
        embed.add_field(name="👥 Friends", value=len(friends), inline=True)
        
        # Reputation
        rep = self.storage.get_reputation(target.id, ctx.guild.id)
        embed.add_field(name="⭐ Reputation", value=rep, inline=True)
        
        # Gifts received
        gifts = self.storage.get_gifts(target.id, ctx.guild.id)
        embed.add_field(name="🎁 Gifts Received", value=gifts, inline=True)
        
        await ctx.send(embed=embed)

    # 🔧 HELPER METHODS
    def is_on_cooldown(self, user_id, cooldown_dict, seconds):
        """Check if user is on cooldown"""
        if user_id in cooldown_dict:
            time_diff = datetime.now() - cooldown_dict[user_id]
            if time_diff.total_seconds() < seconds:
                return True
        cooldown_dict[user_id] = datetime.now()
        return False

    @commands.command()
    async def socialhelp(self, ctx):
        """Show social system help"""
        embed = discord.Embed(
            title="💕 Social System Help",
            description="Make friends, find love, and build your social life!",
            color=discord.Color.pink()
        )
        
        embed.add_field(
            name="💍 Marriage Commands",
            value=(
                "`!marry @user` - Propose marriage\n"
                "`!divorce` - End your marriage\n"
                "`!marriage [@user]` - Check marriage status"
            ),
            inline=False
        )
        
        embed.add_field(
            name="👨‍👩‍👧‍👦 Family Commands",
            value=(
                "`!adopt <name>` - Adopt a child\n"
                "`!children [@user]` - View children"
            ),
            inline=False
        )
        
        embed.add_field(
            name="👥 Friend Commands",
            value=(
                "`!addfriend @user` - Add a friend\n"
                "`!unfriend @user` - Remove a friend\n"
                "`!friends [@user]` - View friends list"
            ),
            inline=False
        )
        
        embed.add_field(
            name="⭐ Reputation & Gifts",
            value=(
                "`!rep @user` - Give reputation\n"
                "`!reputation [@user]` - Check reputation\n"
                "`!gift @user` - Send a gift\n"
                "`!socialstats [@user]` - View all stats"
            ),
            inline=False
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(SocialSystem(bot))
