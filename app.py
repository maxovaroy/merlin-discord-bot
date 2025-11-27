# app.py - Merlin Discord Bot
# Secure token handling for Zampto deployment
# Copyright (c) 2024 Merlin Discord Bot. All rights reserved.

import discord
from discord.ext import commands
import os
import sys
import asyncio

class MerlinBot(commands.Bot):
    def __init__(self):
        # Get token using secure method
        self.token = self.get_secure_token()
        
        if not self.token:
            print("❌ ERROR: Bot token not found!")
            print("\n🔧 For Zampto Deployment:")
            print("1. Temporarily add your token to config.py as:")
            print('   BOT_TOKEN = "your_token_here"')
            print("2. Deploy on Zampto")
            print("3. Immediately remove token and push again")
            print("\n🛡️ For Local Development:")
            print("Set BOT_TOKEN environment variable")
            sys.exit(1)
            
        super().__init__(
            command_prefix=self.get_prefix,
            intents=discord.Intents.all(),
            help_command=None,
            case_insensitive=True
        )
        
    def get_secure_token(self):
        """Secure method to get bot token from multiple sources"""
        
        # Method 1: Environment variable (most secure)
        env_token = os.getenv("BOT_TOKEN")
        if env_token:
            print("✅ Token loaded from environment variable")
            return env_token
            
        # Method 2: Config file (for Zampto deployment)
        try:
            from config import BOT_TOKEN
            if BOT_TOKEN and BOT_TOKEN != "YOUR_BOT_TOKEN_HERE":
                print("✅ Token loaded from config.py")
                return BOT_TOKEN
        except ImportError:
            pass
        except Exception as e:
            print(f"⚠️ Config import warning: {e}")
            
        # Method 3: Check for common token patterns in config
        try:
            import config
            if hasattr(config, 'BOT_TOKEN'):
                token = getattr(config, 'BOT_TOKEN')
                if token and isinstance(token, str) and len(token) > 50:
                    print("✅ Token loaded from config attribute")
                    return token
        except:
            pass
            
        return None
        
    def get_prefix(self, client, message):
        """Get command prefix"""
        prefixes = ['!', '?', '.']
        return commands.when_mentioned_or(*prefixes)(client, message)
    
    async def setup_hook(self):
        """Setup bot when starting"""
        print("🚀 Starting Merlin Discord Bot...")
        print("📦 Loading cogs...")
        
        # List of cogs to load
        cogs = [
            "cogs.profile_system",
            "cogs.social_system", 
            "cogs.advanced_moderations",
            "cogs.fun",
            "cogs.level_system",
            "cogs.utilities",
            "cogs.events",
            "cogs.auto_reply",
            "cogs.name_troll"
        ]
        
        # Load each cog
        loaded_cogs = 0
        for cog in cogs:
            try:
                await self.load_extension(cog)
                print(f"   ✅ {cog}")
                loaded_cogs += 1
            except Exception as e:
                print(f"   ❌ {cog}: {e}")
        
        print(f"📊 Loaded {loaded_cogs}/{len(cogs)} cogs")
        
        # Sync application commands
        print("🔄 Syncing slash commands...")
        try:
            synced = await self.tree.sync()
            print(f"   ✅ Synced {len(synced)} command(s)")
        except Exception as e:
            print(f"   ❌ Failed to sync commands: {e}")
    
    async def on_ready(self):
        """When bot is ready"""
        print(f"\n🎉 {self.user} is now online!")
        print(f"📊 Connected to {len(self.guilds)} server(s)")
        print(f"👥 Serving {sum(g.member_count for g in self.guilds)} users")
        print(f"🆔 Bot ID: {self.user.id}")
        print(f"🏓 Latency: {round(self.latency * 1000)}ms")
        
        # Set bot status
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(self.guilds)} servers | !help"
        )
        await self.change_presence(activity=activity)
        
        print("🔧 Bot is fully operational!\n")
    
    async def on_command_error(self, ctx, error):
        """Global error handler"""
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore unknown commands
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command.")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ I don't have permission to execute this command.")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏰ Command on cooldown. Try again in {error.retry_after:.1f}s.")
        else:
            print(f"❌ Command Error: {error}")
            await ctx.send("❌ An error occurred while executing the command.")

    async def on_guild_join(self, guild):
        """When bot joins a new server"""
        print(f"➕ Joined new guild: {guild.name} (ID: {guild.id})")
        
        # Find system channel or first text channel
        channel = guild.system_channel or next((ch for ch in guild.text_channels if ch.permissions_for(guild.me).send_messages), None)
        
        if channel:
            embed = discord.Embed(
                title="🎉 Thanks for adding Merlin!",
                description="I'm a multi-feature Discord bot with profiles, social systems, and more!",
                color=0x00ff00
            )
            embed.add_field(name="🔧 Setup", value="Use `!help` to see all commands", inline=False)
            embed.add_field(name="📊 Features", value="• Profile System\n• Social Features\n• Moderation Tools\n• Fun Commands", inline=False)
            embed.add_field(name="🔗 Support", value="[GitHub Repository](https://github.com/maxovaroy/merlin-discord-bot)", inline=False)
            embed.set_footer(text="Made with ❤️ by Max Ovaroy")
            
            try:
                await channel.send(embed=embed)
            except:
                pass  # Can't send message

    async def on_guild_remove(self, guild):
        """When bot is removed from a server"""
        print(f"➖ Left guild: {guild.name} (ID: {guild.id})")

def main():
    """Main function to start the bot"""
    print("=" * 50)
    print("🤖 Merlin Discord Bot - Starting Up...")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        sys.exit(1)
    
    # Create bot instance
    bot = MerlinBot()
    
    try:
        # Start the bot
        bot.run(bot.token)
    except discord.LoginFailure:
        print("❌ Invalid bot token! Please check your configuration.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
