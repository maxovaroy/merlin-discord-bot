#!/usr/bin/env python3
"""
Test if the new approach works
"""
import discord
from discord.ext import commands

# Test creating a simple bot instance
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print("✅ Bot is ready!")
    
    try:
        # Try loading the new cog
        await bot.load_extension('cogs.new_moderations')
        print("🎉 SUCCESS: New moderations cog loaded!")
        
        # Test a command
        print("✅ All systems working!")
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
    
    await bot.close()

# Run the test
import asyncio
asyncio.run(bot.start('TEST_TOKEN'))