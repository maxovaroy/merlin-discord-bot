# app.py - Merlin Discord Bot
# Copyright (c) 2024 Merlin Discord Bot. All rights reserved.

import discord
from discord.ext import commands
import os
import sys
import asyncio

# Import config - FIXED for your config structure
try:
    import config
    print("✅ Config imported successfully!")
except ImportError as e:
    print(f"❌ Failed to import config: {e}")
    sys.exit(1)

class MerlinBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=config.PREFIX,
            intents=discord.Intents.all(),
            help_command=None,
            owner_ids=set(config.OWNER_IDS) if hasattr(config, 'OWNER_IDS') else set()
        )
    
    async def setup_hook(self):
        """Setup bot when starting"""
        print("🚀 Starting Merlin Discord Bot...")
        print("📦 Loading cogs...")
        
        # Load each cog from config
        loaded = 0
        for cog in config.COGS:
            try:
                await self.load_extension(cog)
                print(f"   ✅ {cog}")
                loaded += 1
            except Exception as e:
                print(f"   ❌ {cog}: {e}")
        
        print(f"📊 Loaded {loaded}/{len(config.COGS)} cogs")
    
    async def on_ready(self):
        """When bot is ready"""
        print(f"\n🎉 {self.user} is now online!")
        print(f"📊 Connected to {len(self.guilds)} server(s)")
        print(f"🏓 Latency: {round(self.latency * 1000)}ms")
        
        # Set bot status
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(self.guilds)} servers | {config.PREFIX}help"
        )
        await self.change_presence(activity=activity)
        
        print("🔧 Bot is fully operational!\n")

async def main():
    """Main function to start the bot"""
    print("=" * 50)
    print("🤖 Merlin Discord Bot - Starting Up...")
    print("=" * 50)
    
    # Validate config using the function from config
    if hasattr(config, 'validate_config'):
        if not config.validate_config():
            print("❌ Configuration validation failed!")
            return
    else:
        print("⚠️  No config validation function found, continuing...")
    
    # Validate token
    if not config.BOT_TOKEN or config.BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ ERROR: Bot token not configured!")
        print("\n🔧 For Zampto Deployment:")
        print("1. Edit config.py and set your actual token:")
        print('   BOT_TOKEN = "your_actual_token_here"')
        print("2. Save and the bot will auto-restart")
        return
    
    if len(config.BOT_TOKEN) < 50:
        print("❌ ERROR: Bot token appears invalid (too short)")
        return
    
    # Create and start bot
    bot = MerlinBot()
    
    try:
        await bot.start(config.BOT_TOKEN)
    except discord.LoginFailure:
        print("❌ INVALID BOT TOKEN! Please:")
        print("1. Go to https://discord.com/developers/applications")
        print("2. Reset your bot token")
        print("3. Update config.py with the new token")
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
