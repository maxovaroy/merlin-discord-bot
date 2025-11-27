import discord
from discord.ext import commands
import asyncio
import logging
import traceback
import sys
import os

# 🚀 CRITICAL: Add current directory to path BEFORE any imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Fix the config import for your structure
try:
    import config
    print("✅ Config imported successfully!")
    
    # Create a Config class for compatibility with existing code
    class Config:
        BOT_TOKEN = config.BOT_TOKEN
        PREFIX = config.PREFIX
        DATA_FILE = getattr(config, 'DATA_FILE', 'bot_data.json')
        LEVEL_DATA_FILE = getattr(config, 'LEVEL_DATA_FILE', 'level_data.json')
        
        @classmethod
        def validate_config(cls):
            return getattr(config, 'validate_config', lambda: True)()
            
except ImportError as e:
    print(f"❌ Failed to import config: {e}")
    sys.exit(1)

from storage import DataStorage  # 🚀 ADDED for migration

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('bot')

# Bot setup
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True
intents.reactions = True

bot = commands.Bot(
    command_prefix=Config.PREFIX,
    intents=intents,
    help_command=None
)

# 🚀 BANNER MIGRATION SYSTEM
async def migrate_to_banner_system():
    """Migrate from background system to banner system"""
    try:
        storage = DataStorage()
        await storage.load_data_async()  # Ensure data is loaded
        
        migrated_users = 0
        
        # Migrate user profiles from background to banner
        for server_key, server_data in storage.user_profiles.items():
            for user_key, user_data in server_data.items():
                # Check if user has old background field
                if 'background' in user_data:
                    old_background = user_data['background']
                    
                    # Map old background to new banner
                    if old_background == 'default':
                        new_banner = 'assassin'
                    else:
                        new_banner = old_background  # Keep same ID if it exists
                    
                    # Update to banner field
                    user_data['banner'] = new_banner
                    migrated_users += 1
        
        # Save migrated data
        await storage.save_data_async()
        
        logger.info(f"🚀 Banner Migration Complete: {migrated_users} user profiles migrated")
        
        if migrated_users > 0:
            logger.info("✅ Successfully migrated from background system to banner system!")
        else:
            logger.info("ℹ️ No migration needed - already using banner system")
            
    except Exception as e:
        logger.error(f"❌ Banner migration failed: {e}")
        traceback.print_exc()

async def load_cogs():
    """Load all cogs"""
    # Use the COGS list from your config
    cogs = config.COGS  # This uses the COGS list from your config.py
    
    loaded, failed = 0, 0

    for cog in cogs:
        try:
            await bot.load_extension(cog)
            logger.info(f"✅ Loaded cog: {cog}")
            loaded += 1
        except Exception as e:
            logger.error(f"❌ Failed to load cog {cog}: {e}")
            traceback.print_exc()
            failed += 1
    
    logger.info(f"📊 Cogs loaded: {loaded}/{len(cogs)} | Failed: {failed}")

@bot.event
async def on_ready():
    """Bot is ready"""
    logger.info(f"🚀 {bot.user} is online!")
    logger.info(f"📊 Connected to {len(bot.guilds)} guilds")
    
    # 🚀 RUN BANNER MIGRATION ON STARTUP
    try:
        await migrate_to_banner_system()  # ✅ ADDED AWAIT
    except Exception as e:
        logger.error(f"Migration error on startup: {e}")
    
    activity = discord.Activity(
        type=discord.ActivityType.watching,
        name=f"{Config.PREFIX}help | {len(bot.guilds)} servers"
    )
    await bot.change_presence(activity=activity)

@bot.event
async def on_command_error(ctx, error):
    """Global error handler"""
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command.")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("❌ I don't have the required permissions to execute this command.")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏰ Command on cooldown. Try again in {error.retry_after:.1f}s.")
    else:
        logger.error(f"Unhandled error in command {ctx.command}: {error}")
        await ctx.send("❌ An unexpected error occurred. Please try again later.")

# 🚀 ADD MIGRATION COMMAND FOR MANUAL CONTROL
@bot.command()
@commands.is_owner()
async def migratebanners(ctx):
    """Manually trigger banner migration (Owner only)"""
    await ctx.send("🔄 Starting banner migration...")
    
    try:
        await migrate_to_banner_system()
        await ctx.send("✅ Banner migration completed successfully!")
    except Exception as e:
        await ctx.send(f"❌ Migration failed: {e}")
        logger.error(f"Manual migration failed: {e}")

async def main():
    """Main function to start the bot"""
    logger.info("Starting bot...")
    
    try:
        await load_cogs()
        logger.info("All cogs loaded successfully")
        await bot.start(Config.BOT_TOKEN)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except discord.errors.LoginError:
        logger.error("Invalid bot token provided")
    except Exception as e:
        logger.critical(f"Failed to start bot: {e}")
        traceback.print_exc()
    finally:
        if not bot.is_closed():
            await bot.close()

if __name__ == "__main__":
    try:
        Config.validate_config()
    except ValueError as e:
        print(e)
        exit(1)
    
    asyncio.run(main())
