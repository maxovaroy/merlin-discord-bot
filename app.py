# app.py - Merlin Discord Bot

import discord
from discord.ext import commands
import asyncio
from datetime import datetime
import sys

# -----------------------------
# IMPORT CONFIG
# -----------------------------
try:
    import config
    PREFIX = getattr(config, 'PREFIX', '!')
    OWNER_IDS = set(getattr(config, 'OWNER_IDS', []))
    COGS = getattr(config, 'COGS', [])
    BOT_TOKEN = getattr(config, 'BOT_TOKEN', None)
    print("✅ Config imported successfully!")
except ImportError as e:
    print(f"❌ Failed to import config: {e}")
    sys.exit(1)

# -----------------------------
# IMPORT STORAGE
# -----------------------------
try:
    from storage import DataStorage
    STORAGE = DataStorage()
    print("✅ Storage instance created")
except ImportError as e:
    STORAGE = None
    print(f"❌ Storage module not found: {e}")
    sys.exit(1)

# -----------------------------
# IMPORT LEVELING SYSTEM
# -----------------------------
try:
    from discordLevelingSystem import DiscordLevelingSystem, errors as leveling_errors
except ImportError as e:
    print(f"❌ Failed to import leveling system: {e}")
    leveling_errors = None
    DiscordLevelingSystem = None

# -----------------------------
# MERLIN BOT CLASS
# -----------------------------
class MerlinBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=PREFIX,
            intents=discord.Intents.all(),
            help_command=None,
            owner_ids=OWNER_IDS
        )

        self.storage = STORAGE
        self.user_data = {}
        self.levelsystem = DiscordLevelingSystem(rate=1, per=60.0) if DiscordLevelingSystem else None

    async def setup_hook(self):
        # -----------------------------
        # Connect leveling DB
        # -----------------------------
        if self.levelsystem:
            loop = asyncio.get_running_loop()
            try:
                await loop.run_in_executor(None, self.levelsystem.connect_to_database_file, "./leveling.db")
                print("✅ Leveling system database connected")
            except leveling_errors.ConnectionFailure:
                print("❌ Failed to connect to leveling database")

        # -----------------------------
        # Load storage
        # -----------------------------
        if self.storage:
            try:
                await self.storage.load_data_async()
                print("✅ Storage data loaded successfully")
            except Exception as e:
                print(f"❌ Failed to load storage data: {e}")

        # -----------------------------
        # Load cogs
        # -----------------------------
        print("🚀 Loading cogs...")
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
        print(f"\n🎉 {self.user} is online!")
        print(f"📊 Connected to {len(self.guilds)} server(s)")
        print(f"🏓 Latency: {round(self.latency * 1000)}ms")
        print("🔧 Bot fully operational\n")

        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(self.guilds)} servers | {PREFIX}help"
        )
        await self.change_presence(activity=activity)

    async def on_message(self, message):
        if message.author.bot:
            return

        # -----------------------------
        # Ensure storage profile exists
        # -----------------------------
        if self.storage and message.guild:
            self.storage.get_user_profile(message.author.id, message.guild.id)

        # -----------------------------
        # Award leveling XP
        # -----------------------------
        if self.levelsystem:
            await self.levelsystem.award_xp(amount=[15, 25], message=message)

        # -----------------------------
        # Track messages
        # -----------------------------
        if message.guild:
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

# -----------------------------
# MAIN FUNCTION
# -----------------------------
async def main():
    print("="*50)
    print("🤖 Merlin Discord Bot - Starting Up")
    print("="*50)

    if not BOT_TOKEN or BOT_TOKEN == "YOUR_ACTUAL_BOT_TOKEN_HERE":
        print("❌ Bot token not configured")
        return

    bot = MerlinBot()
    try:
        await bot.start(BOT_TOKEN)
    except discord.LoginFailure:
        print("❌ INVALID BOT TOKEN")
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

# -----------------------------
# ENTRY POINT
# -----------------------------
if __name__ == "__main__":
    asyncio.run(main())
