import os

class Config:
    # Bot Settings
    BOT_TOKEN = "MTMxNTY2NDcwMjMxOTM2MjA2OA.GyRvSY.wt9_HAcxdlF6gOejlNX5wN-UPUt38Q58WZNGwc"
    PREFIX = "!"
    
    # Data files
    DATA_FILE = "bot_data.json"
    LEVEL_DATA_FILE = "level_data.json"
    CIVILIZATION_DATA_FILE = "civilization_data.json"
    
    # Auto-Reply Settings
    AUTO_REPLY_CHANCE = 0.3  # 30% chance to auto-reply
    
    # Auto-Reply Triggers
    AUTO_REPLIES = {
        "hello": ["👋 Hey there!", "Hello human!", "Hi! Ready to get trolled?"],
        "hi": ["👋 Well hello!", "Hi there!", "Hey! Don't trigger me..."],
        "bot": ["🤖 Yes, I'm a bot. What about it?", "Beep boop! Bot here!"],
        "stupid": ["🤔 Look who's talking!", "Says the one who triggered me..."],
        "idiot": ["🎯 Projection much?", "I know you are but what am I?"],
        "shut up": ["🙊 Make me!", "No u!", "I don't think so..."],
        "fuck": ["🚨 Language!", "Whoa there, sailor!", "My circuits!"],
        "lol": ["😂 What's so funny?", "Glad I amuse you!"],
        "good bot": ["❤️ Thanks! You're not so bad yourself!", "Beep boop 💖"],
        "bad bot": ["😢 Why so mean?", "I have feelings too!"],
        "ping": ["🏓 Pong! Did you expect something else?"],
    }
    
    # Special Triggers
    SPECIAL_REPLIES = {
        "rick roll": "🎵 Never gonna give you up, never gonna let you down...",
        "amogus": "🔴 SUS! ඞ",
        "skill issue": "💀 Sounds like a skill issue to me!",
        "cope": "😎 Can't cope, won't cope!",
        "seethe": "😤 Keep seething!",
        "ratio": "📊 Ratio + L + Bozo + Didn't Ask",
    }
    
    # Roast Responses
    ROASTS = [
        "You're the reason the gene pool needs a lifeguard.",
        "If laughter is the best medicine, your face must be curing the world.",
        "You have two brain cells and they're both fighting for third place.",
        "I'd agree with you but then we'd both be wrong.",
        "You're like a cloud. When you disappear, it's a beautiful day.",
    ]
    
    # Compliments (Backhanded)
    COMPLIMENTS = [
        "You're smarter than you look!",
        "You're almost as awesome as me!",
        "Your face doesn't scare me... much.",
        "You're proof that evolution can go backwards!",
        "You have a face for radio!",
    ]
    
    # Level System Settings
    LEVEL_SETTINGS = {
        "base_xp": 100,
        "xp_multiplier": 1.5,
        "cooldown": 60,
        "max_level": 100
    }
    
    # Moderation Settings
    MODERATION = {
        "max_warnings": 3,
        "mute_role": "Muted",
        "log_channel": "mod-logs"
    }

    @classmethod
    def validate_config(cls):
        """Validate critical configuration"""
        if not cls.BOT_TOKEN or cls.BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
            raise ValueError("❌ BOT_TOKEN not set. Please set it in config.py")
        if not cls.PREFIX:
            raise ValueError("❌ PREFIX not set")

        return True

