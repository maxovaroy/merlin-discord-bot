# app.py - Merlin Discord Bot
# Copyright (c) 2024 Merlin Discord Bot. All rights reserved.

import discord
from discord.ext import commands
import os
import sys
import asyncio
from datetime import datetime

from discordLevelingSystem import DiscordLevelingSystem   # <-- added

# Import config
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

        self.user_data = {}

        # -----------------------------
        # ADD LEVELING SYSTEM HERE
        # -----------------------------
        self.levelsystem = DiscordLevelingSystem(rate=1, per=60.0)
        self.levelsystem.connect_to_database_file("./leveling.db")

    async def setup_hook(self):
        print("🚀 Starting Merlin Discord Bot...")
        print("📦 Loading cogs...")

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
        print(f"\n🎉 {self.user} is now online!")
        print(f"📊 Connected to {len(self.guilds)} server(s)")
        print(f"🏓 Latency: {round(self.latency * 1000)}ms")

        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(self.guilds)} servers | {config.PREFIX}help"
        )
        await self.change_presence(activity=activity)

        print("🔧 Bot is fully operational!\n")

    async def on_message(self, message):
        if message.author.bot:
            return await self.process_commands(message)

        # -----------------------------
        # GIVE XP USING SQLITE
        # -----------------------------
        await self.levelsystem.award_xp(amount=[15, 25], message=message)

        # -----------------------------
        # KEEP YOUR MESSAGE COUNTER
        # -----------------------------
        user_id = message.author.id

        if user_id not in self.user_data:
            joined_date = message.author.joined_at.isoformat() if message.author.joined_at else datetime.now().isoformat()
            self.user_data[user_id] = {
                "username": str(message.author),
                "joined_at": joined_date,
                "messages": 0
            }
            print(f"📝 Created new user record for {message.author}")

        self.user_data[user_id]["messages"] += 1

        await self.process_commands(message)

async def main():
    print("=" * 50)
    print("🤖 Merlin Discord Bot - Starting Up...")
    print("=" * 50)

    if hasattr(config, 'validate_config'):
        if not config.validate_config():
            print("❌ Configuration validation failed!")
            return
    else:
        print("⚠️  No config validation function found, continuing...")

    if not config.BOT_TOKEN or config.BOT_TOKEN == "YOUR_ACTUAL_BOT_TOKEN_HERE":
        print("❌ ERROR: Bot token not configured!")
        return

    if len(config.BOT_TOKEN) < 50:
        print("❌ ERROR: Bot token appears invalid (too short)")
        return

    bot = MerlinBot()

    try:
        await bot.start(config.BOT_TOKEN)
    except discord.LoginFailure:
        print("❌ INVALID BOT TOKEN!")
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
