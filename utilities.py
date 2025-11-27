import discord
from discord.ext import commands
import datetime

class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
        """Show all available commands"""
        embed = discord.Embed(
            title="🤖 Troll Moderator Bot Help",
            description="A moderation bot with fun auto-reply features!",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="👤 Profile System",
             value=(
                f"`{ctx.prefix}profile [@user]` - View profile\n"
                f"`{ctx.prefix}setbio <text>` - Set biography\n"
                f"`{ctx.prefix}settitle <text>` - Set title\n"
                f"`{ctx.prefix}backgrounds` - Available backgrounds\n"
                f"`{ctx.prefix}setbackground <name>` - Change background\n"
                f"`{ctx.prefix}achievements [@user]` - View achievements\n"
                f"`{ctx.prefix}profilehelp` - Profile system help"
            ),
            inline=False
        )

        embed.add_field(
            name="💕 Social System",
             value=(
                f"`{ctx.prefix}marry @user` - Propose marriage\n"
                f"`{ctx.prefix}divorce` - End marriage\n"
                f"`{ctx.prefix}marriage [@user]` - Check status\n"
                f"`{ctx.prefix}adopt <name>` - Adopt child\n"
                f"`{ctx.prefix}children` - View children\n"
                f"`{ctx.prefix}addfriend @user` - Add friend\n"
                f"`{ctx.prefix}rep @user` - Give reputation\n"
                f"`{ctx.prefix}socialstats` - View all stats\n"
                f"`{ctx.prefix}socialhelp` - Social system help"
            ),
            inline=False
        )

        embed.add_field(
            name="🔇 Auto-Reply Controls",
            value=(
                f"`{ctx.prefix}muteautoreply` - Stop auto-replies to you\n"
                f"`{ctx.prefix}unmuteautoreply` - Allow auto-replies again\n"
                f"`{ctx.prefix}autoreplystatus` - Check your status\n"
                f"`{ctx.prefix}muteautoreplyuser @user` - Mute for user (Admin)\n"
                f"`{ctx.prefix}unmuteautoreplyuser @user` - Unmute for user (Admin)"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🛡️ Moderation Commands",
            value=(
                f"`{ctx.prefix}kick @user [reason]` - Kick a member\n"
                f"`{ctx.prefix}ban @user [reason]` - Ban a member\n"
                f"`{ctx.prefix}mute @user [reason]` - Mute a member\n"
                f"`{ctx.prefix}unmute @user` - Unmute a member\n"
                f"`{ctx.prefix}warn @user [reason]` - Warn a member\n"
                f"`{ctx.prefix}warnings [@user]` - Check warnings\n"
                f"`{ctx.prefix}clearwarns @user` - Clear warnings\n"
                f"`{ctx.prefix}clear [amount]` - Clear messages (max 100)"
            ),
            inline=False
        )
        
        embed.add_field(
            name="📊 Level System",
            value=(
                f"`{ctx.prefix}level [@user]` - Check level\n"
                f"`{ctx.prefix}leaderboard` - Server rankings\n"
                f"`{ctx.prefix}rank [@user]` - Check rank\n"
                f"`{ctx.prefix}togglenotifications` - Toggle level-up messages\n"
                f"`{ctx.prefix}levelsystem` - Level system info"
            ),
            inline=False
        )
        
        embed.add_field(
            name="😂 Fun Commands",
            value=(
                f"`{ctx.prefix}roast [@user]` - Roast someone\n"
                f"`{ctx.prefix}superroast [@user]` - Ultimate roast combo\n"
                f"`{ctx.prefix}compliment [@user]` - Backhanded compliment\n"
                f"`{ctx.prefix}rate <thing>` - Rate something 1-10\n"
                f"`{ctx.prefix}coinflip` - Flip a coin\n"
                f"`{ctx.prefix}dice [sides]` - Roll a dice\n"
                f"`{ctx.prefix}choose opt1|opt2|opt3` - Choose for you\n"
                f"`{ctx.prefix}joke` - Tell a joke\n"
                f"`{ctx.prefix}8ball <question>` - Magic 8-ball\n"
                f"`{ctx.prefix}mock <text>` - Mock text"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🔧 Utility Commands",
            value=(
                f"`{ctx.prefix}help` - This menu\n"
                f"`{ctx.prefix}ping` - Check bot latency\n"
                f"`{ctx.prefix}info` - Bot information\n"
                f"`{ctx.prefix}userinfo [@user]` - User information\n"
                f"`{ctx.prefix}invite` - Get bot invite link\n"
                f"`{ctx.prefix}servers` - Bot statistics"
            ),
            inline=False
        )
        
        embed.set_footer(text=f"Use {ctx.prefix} before each command • Total commands: 25+")
        await ctx.send(embed=embed)

    @commands.command()
    async def ping(self, ctx):
        """Check bot latency"""
        latency = round(self.bot.latency * 1000)
        await ctx.send(f"🏓 Pong! Latency: {latency}ms")

    @commands.command()
    async def invite(self, ctx):
        """Get bot invite link"""
        invite_url = f"https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot%20applications.commands"
        
        embed = discord.Embed(
            title="🎉 Invite Me to Your Server!",
            description=f"**[Click here to add me to your server!]({invite_url})**",
            color=discord.Color.green()
        )
        
        features = [
            "🔥 Advanced roasting system",
            "📊 Leveling with GIF rewards", 
            "🛡️ Moderation tools",
            "🎮 Fun games & commands",
            "🤖 Auto-responses",
            "🔇 Auto-reply mute controls",
            "💫 And much more!"
        ]
        
        embed.add_field(
            name="Features",
            value="\n".join([f"• {feature}" for feature in features]),
            inline=False
        )
        
        embed.add_field(
            name="Requirements", 
            value="• Manage Server permission\n• Bot must be online",
            inline=True
        )
        
        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else self.bot.user.default_avatar.url)
        embed.set_footer(text="Thank you for using me! 🚀")
        
        await ctx.send(embed=embed)

    @commands.command()
    async def servers(self, ctx):
        """Show how many servers the bot is in"""
        server_count = len(self.bot.guilds)
        member_count = sum(guild.member_count for guild in self.bot.guilds)
        
        embed = discord.Embed(
            title="📊 Bot Statistics",
            color=discord.Color.blue()
        )
        embed.add_field(name="Servers", value=server_count, inline=True)
        embed.add_field(name="Total Members", value=member_count, inline=True)
        embed.add_field(name="Ping", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        
        await ctx.send(embed=embed)

    @commands.command()
    async def info(self, ctx):
        """Get bot information"""
        embed = discord.Embed(
            title="🤖 Troll Moderator Bot",
            description="A moderation bot with fun auto-reply features",
            color=discord.Color.green(),
            timestamp=datetime.datetime.utcnow()
        )
        
        embed.add_field(name="Servers", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="Prefix", value="!", inline=True)
        
        embed.add_field(
            name="Features", 
            value="Moderation • Auto-Reply • Level System • Fun Commands • Troll Features",
            inline=False
        )
        
        embed.set_footer(text="Made with ❤️ and a bit of trolling")
        await ctx.send(embed=embed)

    @commands.command()
    async def userinfo(self, ctx, member: discord.Member = None):
        """Get information about a user"""
        target = member or ctx.author
        
        embed = discord.Embed(
            title=f"👤 User Info - {target.display_name}",
            color=target.color,
            timestamp=datetime.datetime.utcnow()
        )
        
        embed.set_thumbnail(url=target.avatar.url if target.avatar else target.default_avatar.url)
        
        embed.add_field(name="Username", value=f"{target.name}#{target.discriminator}", inline=True)
        embed.add_field(name="ID", value=target.id, inline=True)
        embed.add_field(name="Status", value=str(target.status).title(), inline=True)
        
        embed.add_field(name="Account Created", value=target.created_at.strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name="Joined Server", value=target.joined_at.strftime("%Y-%m-%d") if target.joined_at else "N/A", inline=True)
        embed.add_field(name="Top Role", value=target.top_role.mention, inline=True)
        
        roles = [role.mention for role in target.roles[1:][:5]]  # Skip @everyone and limit to 5
        embed.add_field(
            name="Roles", 
            value=", ".join(roles) if roles else "None",
            inline=False
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utilities(bot))