# app.py - Merlin Discord Bot

import discord
from discord.ext import commands
import os
import sys
import asyncio
from datetime import datetime

from discordLevelingSystem import DiscordLevelingSystem, errors as leveling_errors

# Import config
try:
    import config
    print("✅ Config imported successfully!")
except ImportError as e:
    print(f"❌ Failed to import config: {e}")
    sys.exit(1)

# Import your storage module (do not run async yet)
try:
    from storage import DataStorage
    STORAGE = DataStorage()  # just create instance, do NOT call async here
    print("✅ Storage instance created (async loading deferred)")
except ImportError as e:
    STORAGE = None
    print(f"❌ Storage module not found: {e}")


class MerlinBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=config.PREFIX,
            intents=discord.Intents.all(),
            help_command=None,
            owner_ids=set(config.OWNER_IDS) if hasattr(config, 'OWNER_IDS') else set()
        )

        self.user_data = {}
        self.levelsystem = DiscordLevelingSystem(rate=1, per=60.0)

    async def setup_hook(self):
        # -----------------------------
        # Connect Leveling DB
        # -----------------------------
        loop = asyncio.get_running_loop()
        try:
            await loop.run_in_executor(None, self.levelsystem.connect_to_database_file, "./leveling.db")
            print("✅ Leveling system database connected!")
        except leveling_errors.ConnectionFailure:
            print("❌ Failed to connect to leveling database!")

        # -----------------------------
        # Load Storage (async)
        # -----------------------------
        if STORAGE:
            try:
                await STORAGE.load_data_async()  # proper async load
                print("✅ Storage data loaded successfully!")
            except Exception as e:
                print(f"❌ Failed to load storage data: {e}")

        # -----------------------------
        # Load cogs
        # -----------------------------
        print("🚀 Loading cogs...")
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
        print(f"✅ Bot ready, data loaded for {self.user}")

        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(self.guilds)} servers | {config.PREFIX}help"
        )
        await self.change_presence(activity=activity)
        print("🔧 Bot is fully operational!\n")

    async def on_message(self, message):
        if message.author.bot:
            return await self.process_commands(message)

        # Auto-create profile in storage
        if STORAGE:
            STORAGE.get_user_profile(message.author.id, message.guild.id)

        # Award XP
        await self.levelsystem.award_xp(amount=[15, 25], message=message)

        # Keep message counter
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

    if not config.BOT_TOKEN or config.BOT_TOKEN == "YOUR_ACTUAL_BOT_TOKEN_HERE":
        print("❌ ERROR: Bot token not configured!")
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
