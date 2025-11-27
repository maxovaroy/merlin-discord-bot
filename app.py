# app.py - Merlin Discord Bot
# Copyright (c) 2024 Merlin Discord Bot. All rights reserved.

import discord
from discord.ext import commands
import os
import sys
import asyncio

# Try to import config
try:
    from config import BOT_TOKEN, PREFIX, COGS
except ImportError as e:
    print(f"❌ Failed to import config: {e}")
    sys.exit(1)

class MerlinBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=PREFIX,
            intents=discord.Intents.all(),
            help_command=None
        )
    
    async def setup_hook(self):
        """Setup bot when starting"""
        print("🚀 Starting Merlin Discord Bot...")
        print("📦 Loading cogs...")
        
        # Load each cog
        loaded = 0
        for cog in COGS:
            try:
                await self.load_extension(cog)
                print(f"   ✅ {cog}")
                loaded += 1
            except Exception as e:
                print(f"   ❌ {cog}: {e}")
        
        print(f"📊 Loaded {loaded}/{len(COGS)} cogs")
    
    async def on_ready(self):
        """When bot is ready"""
        print(f"\n🎉 {self.user} is now online!")
        print(f"📊 Connected to {len(self.guilds)} server(s)")
        print(f"🏓 Latency: {round(self.latency * 1000)}ms")
        
        # Set bot status
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(self.guilds)} servers | {PREFIX}help"
        )
        await self.change_presence(activity=activity)
        
        print("🔧 Bot is fully operational!\n")

async def main():
    """Main function to start the bot"""
    print("=" * 50)
    print("🤖 Merlin Discord Bot - Starting Up...")
    print("=" * 50)
    
    # Validate token
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ ERROR: Bot token not configured!")
        print("\n🔧 For Zampto Deployment:")
        print("1. Edit config.py and set your actual token:")
        print('   BOT_TOKEN = "your_actual_token_here"')
        print("2. Save and the bot will auto-restart")
        return
    
    if len(BOT_TOKEN) < 50:
        print("❌ ERROR: Bot token appears invalid (too short)")
        return
    
    # Create and start bot
    bot = MerlinBot()
    
    try:
        await bot.start(BOT_TOKEN)
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
