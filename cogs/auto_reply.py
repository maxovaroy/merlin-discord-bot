import discord
from discord.ext import commands
import random
import config

class AutoReply(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        """Handle auto-reply to messages"""
        if message.author.bot:
            return
        
        # Don't reply to commands
        if message.content.startswith(config.PREFIX):
            return
        
        content = message.content.lower()
        
        # Check special replies first (if you add SPECIAL_REPLIES in config)
        if hasattr(config, "SPECIAL_REPLIES"):
            for trigger, reply in config.SPECIAL_REPLIES.items():
                if trigger in content:
                    await message.reply(reply)
                    return
        
        # Check regular auto-replies
        for trigger, replies in config.AUTO_REPLIES.items():
            if trigger in content:
                if random.random() < config.AUTO_REPLY_SETTINGS["chance"]:
                    response = random.choice(replies)
                    await message.reply(response)
                    return

async def setup(bot):
    await bot.add_cog(AutoReply(bot))
