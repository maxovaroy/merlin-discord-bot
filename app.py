# app.py - Merlin Discord Bot

import discord
from discord.ext import commands
import logging
import asyncio
import sys

# ---------------------------
# Logging setup
# ---------------------------
logger = logging.getLogger("MerlinBot")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Reduce noisy discord logs
logging.getLogger("discord").setLevel(logging.WARNING)

# -----------------------------
# IMPORT CONFIG
# -----------------------------
try:
    import config
    PREFIX = getattr(config, "PREFIX", "!")
    OWNER_IDS = set(getattr(config, "OWNER_IDS", []))
    COGS = getattr(config, "COGS", [])
    BOT_TOKEN = getattr(config, "BOT_TOKEN", None)
    logger.info("✅ Config imported successfully!")
except ImportError as e:
    logger.error(f"❌ Failed to import config: {e}")
    sys.exit(1)

# -----------------------------
# IMPORT STORAGE
# -----------------------------
try:
    from storage import DataStorage
    STORAGE = DataStorage()
    logger.info("✅ Storage instance created")
except ImportError as e:
    STORAGE = None
    logger.error(f"❌ Storage module not found: {e}")
    sys.exit(1)

# -----------------------------
# IMPORT LEVELING SYSTEM
# -----------------------------
try:
    from discordLevelingSystem import DiscordLevelingSystem, errors as leveling_errors
    LEVEL_SYSTEM = DiscordLevelingSystem(rate=1, per=60.0)
except ImportError as e:
    logger.error(f"❌ Failed to import leveling system: {e}")
    LEVEL_SYSTEM = None
    leveling_errors = None

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
        self.levelsystem = LEVEL_SYSTEM
        self.user_data = {}

    async def setup_hook(self):
        # -----------------------------
        # Connect leveling DB
        # -----------------------------
        if self.levelsystem:
            loop = asyncio.get_running_loop()
            try:
                await loop.run_in_executor(None, self.levelsystem.connect_to_database_file, "./leveling.db")
                logger.info("✅ Leveling system database connected")
            except leveling_errors.ConnectionFailure:
                logger.error("❌ Failed to connect to leveling database")
            except Exception as e:
                logger.error(f"❌ Leveling DB error: {e}")

        # -----------------------------
        # Load storage data
        # -----------------------------
        if self.storage:
            try:
                await self.storage.load_data_async()
                logger.info("✅ Storage data loaded successfully")
            except Exception as e:
                logger.error(f"❌ Failed to load storage data: {e}")

        # -----------------------------
        # Load cogs
        # -----------------------------
        logger.info("🚀 Loading cogs...")
        loaded = 0
        for cog in COGS:
            try:
                # Pass storage to all cogs that accept it
                await self.load_extension(cog)
                logger.info(f"   ✅ {cog}")
                loaded += 1
            except Exception as e:
                logger.error(f"   ❌ {cog}: {e}")
        logger.info(f"📊 Loaded {loaded}/{len(COGS)} cogs")

    async def on_ready(self):
        logger.info(f"🎉 {self.user} is online!")
        logger.info(f"📊 Connected to {len(self.guilds)} server(s)")
        logger.info(f"🏓 Latency: {round(self.latency * 1000)}ms")

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
            try:
                await self.levelsystem.award_xp(amount=[15, 25], message=message)
            except leveling_errors.TableNotFound:
                await self.levelsystem.create_database_file()
                await self.levelsystem.award_xp(amount=[15, 25], message=message)
            except Exception as e:
                logger.error(f"❌ Failed to award XP: {e}")

        # -----------------------------
        # Track messages
        # -----------------------------
        if message.guild:
            user_id = message.author.id
            if user_id not in self.user_data:
                joined_date = message.author.joined_at.isoformat() if message.author.joined_at else "Unknown"
                self.user_data[user_id] = {
                    "username": str(message.author),
                    "joined_at": joined_date,
                    "messages": 0
                }
            self.user_data[user_id]["messages"] += 1

        await self.process_commands(message)

# -----------------------------
# MAIN FUNCTION
# -----------------------------
async def main():
    logger.info("="*50)
    logger.info("🤖 Merlin Discord Bot - Starting Up")
    logger.info("="*50)

    if not BOT_TOKEN or BOT_TOKEN == "YOUR_ACTUAL_BOT_TOKEN_HERE":
        logger.error("❌ Bot token not configured")
        return

    bot = MerlinBot()

    # Inject storage and leveling system into cogs
    bot.storage = STORAGE
    bot.levelsystem = LEVEL_SYSTEM

    try:
        await bot.start(BOT_TOKEN)
    except discord.LoginFailure:
        logger.error("❌ INVALID BOT TOKEN")
    except KeyboardInterrupt:
        logger.error("\n🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")

# -----------------------------
# ENTRY POINT
# -----------------------------
if __name__ == "__main__":
    asyncio.run(main())
