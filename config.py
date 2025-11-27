# config.py - Merlin Bot Configuration
# Copyright (c) 2024 Merlin Discord Bot. All rights reserved.

import os

# ===== BOT CORE SETTINGS =====
# Bot Token - USE ONE OF THESE METHODS:
BOT_TOKEN = os.getenv("BOT_TOKEN")  # For environment variables
# BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # TEMPORARY for Zampto deployment

PREFIX = "!"
DATABASE_URL = "sqlite:///merlin_data.db"

# ===== BANNER SYSTEM =====
AVAILABLE_BANNERS = {
    "default": {"name": "Default", "rarity": "common", "url": ""},
    "blue_sky": {"name": "Blue Sky", "rarity": "common", "url": ""},
    "forest": {"name": "Forest", "rarity": "common", "url": ""},
    "ocean": {"name": "Ocean", "rarity": "uncommon", "url": ""},
    "sunset": {"name": "Sunset", "rarity": "uncommon", "url": ""},
    "galaxy": {"name": "Galaxy", "rarity": "rare", "url": ""},
    "nebula": {"name": "Nebula", "rarity": "rare", "url": ""},
    "fire": {"name": "Fire", "rarity": "epic", "url": ""},
    "ice": {"name": "Ice", "rarity": "epic", "url": ""},
    "golden": {"name": "Golden", "rarity": "legendary", "url": ""}
}

# ===== SOCIAL SYSTEM SETTINGS =====
MARRIAGE_SETTINGS = {
    "cooldown_days": 7,
    "max_marriages": 1
}

REPUTATION_SETTINGS = {
    "cooldown_hours": 24,
    "daily_limit": 5
}

FRIEND_SETTINGS = {
    "max_friends": 50
}

# ===== LEVEL SYSTEM =====
LEVEL_SETTINGS = {
    "base_xp": 100,
    "xp_multiplier": 1.5,
    "message_xp_range": (15, 25),
    "cooldown_seconds": 60,
    "max_level": 100
}

# ===== AUTO-REPLY SYSTEM =====
AUTO_REPLY_SETTINGS = {
    "chance": 0.3,  # 30% chance to auto-reply
    "cooldown_seconds": 300  # 5 minutes between auto-replies per user
}

AUTO_REPLIES = {
    "hello": ["👋 Hey there!", "Hello!", "Hi there!"],
    "hi": ["👋 Hello!", "Hi!", "Hey!"],
    "bot": ["🤖 Yes, I'm a bot!", "Beep boop!"],
    "merlin": ["🧙 That's me!", "Merlin at your service!"],
    "thanks": ["You're welcome!", "No problem! 😊"],
    "good bot": ["❤️ Thanks!", "Beep boop 💖"]
}

# ===== COG CONFIGURATION =====
COGS = [
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

# ===== BOT METADATA =====
OWNER_IDS = []  # Add your Discord ID for owner commands
DEBUG_MODE = False
VERSION = "1.0.0"

# ===== FEATURE TOGGLES =====
PROFILES_ENABLED = True
SOCIAL_SYSTEM_ENABLED = True
LEVELING_ENABLED = True
MODERATION_ENABLED = True
AUTO_REPLY_ENABLED = True

# ===== VALIDATION =====
def validate_config():
    """Validate critical configuration"""
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ WARNING: BOT_TOKEN not set properly")
        print("   For local dev: Set BOT_TOKEN environment variable")
        print("   For Zampto: Temporarily add token to config.py")
        return False
    
    required_files = ["storage.py", "app.py"]
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ MISSING: {file}")
            return False
    
    print("✅ Configuration validated successfully!")
    return True

# Validate on import
if __name__ == "__main__":
    validate_config()
