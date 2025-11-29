# config.py - Merlin Bot Configuration
# Copyright (c) 2024 Merlin Discord Bot. All rights reserved.

import os  # ADD THIS IMPORT AT THE TOP

# ===== BOT CORE SETTINGS =====
# Replace with your actual bot token
BOT_TOKEN = "BOT.TOKEN"

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
    "max_marriages": 4
}

REPUTATION_SETTINGS = {
    "cooldown_hours": 1,
    "daily_limit": 10
}

FRIEND_SETTINGS = {
    "max_friends": 500
}

# ===== LEVEL SYSTEM =====
LEVEL_SETTINGS = {
    "base_xp": 100,
    "xp_multiplier": 1.5,
    "message_xp_range": (15, 25),
    "cooldown_seconds": 3,
    "max_level": 1000
}

# ===== AUTO-REPLY SYSTEM =====
AUTO_REPLY_SETTINGS = {
    "chance": 0.5,  # 30% chance to auto-reply
    "cooldown_seconds": 60  # 5 minutes between auto-replies per user
}

AUTO_REPLIES = {

    "merlin": ["That's me!", "Merlin at your service!"],
    "thanks merlin": ["You're welcome!", "No problem!"],
    "good bot": ["Thanks! bro"],
    "fuck": ["language!"],
    "fuk": ["language!"],
    "fucking": ["language!"],
    "fcuk": ["language!"],
    "fak": ["language!"],
    "fucker": ["language!"],
    "fuker": ["language!"],
    "nigga": ["you racist bitch!"],
    "niga": ["you racist bitch!"],
    "nigger": ["you racist bitch!"],
    "niggas": ["you racist bitch!"],
    "nig": ["you racist bitch!"],
    "-3 bump": ["go away gay"],
    "-1 bump": ["go away gay"],
    "-4 bump": ["go away gay"],
    "-5 bump": ["go away gay"],
    "alex": ["gay jew"],
    "flip": ["rizzler"],
    "jew": ["did anyone called alex?? <@1209165207784525837>"],
    "alyssa": ["will cut your dick"],
    "shut up": ["https://cdn.discordapp.com/attachments/874749642523435020/1440751429085298688/G5-6JLnakAAevdJ.gif"],
    "<@574005462534586379>": ["dont tag him"],
    "<@717689371293384766>": ["dont tag my master"],
    "<@1209165207784525837>": ["he gay!"],
    "<@1326313175930634250>": ["nooooooo brooooooo! she cuts dick"],
    "help merlin": ["show can i help?"],
    "gold": ["begger"],
    "wtf": ["https://tenor.com/view/wtf-joe-pesci-pesci-what-gif-10718026964868693743"],
    "sad": ["https://tenor.com/view/dave-chapelle-the-show-rick-gif-24862254"]
    
}

# ===== COG CONFIGURATION =====
COGS = [
    # EXISTING COGS
    "cogs.profile_system",
    "cogs.social_system", 
    "cogs.advanced_moderations",
    "cogs.fun",
    "cogs.level_system",
    "cogs.utilities",
    "cogs.events",
    "cogs.auto_reply",
    "cogs.name_troll",
    
    # NEW PROFILE SYSTEM COGS
    "cogs.banner_system",      # Banner management commands
    "cogs.achievement_system"  # Achievements & badges system
]

# ===== BOT METADATA =====
OWNER_IDS = [717689371293384766]  # Your Discord ID for owner commands
DEBUG_MODE = False
VERSION = "1.0.0"

# ===== FEATURE TOGGLES =====
PROFILES_ENABLED = True
SOCIAL_SYSTEM_ENABLED = True
LEVELING_ENABLED = True
MODERATION_ENABLED = True
AUTO_REPLY_ENABLED = True
BANNER_SYSTEM_ENABLED = True
ACHIEVEMENT_SYSTEM_ENABLED = True

# ===== VALIDATION =====
def validate_config():
    """Validate critical configuration"""
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_ACTUAL_BOT_TOKEN_HERE":
        print("❌ WARNING: BOT_TOKEN not set properly")
        print("   Please replace 'YOUR_ACTUAL_BOT_TOKEN_HERE' with your real bot token")
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
