#events.py
import discord
from discord.ext import commands
import datetime

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """When bot is ready"""
        print(f'✅ {self.bot.user} is online!')
        print(f'📊 Connected to {len(self.bot.guilds)} servers')
        
        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="for trouble | !help"
            )
        )

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore unknown commands
        
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command.")
        
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument. Usage: `!{ctx.command.name} {ctx.command.signature}`")
        
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Invalid argument provided.")
        
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("❌ Member not found.")
        
        else:
            print(f"Error: {error}")
            await ctx.send("❌ An unexpected error occurred.")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """When a member joins the server"""
        # You can add welcome message logic here
        pass

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """When a member leaves the server"""
        # You can add goodbye message logic here
        pass

async def setup(bot):
    await bot.add_cog(Events(bot))

