import discord
from discord.ext import commands
import random
from config import Config
import asyncio
from datetime import datetime

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.roast_cooldowns = {}
        self.mock_cooldowns = {}

    # 🔥 EXPANDED ROAST DATABASE - 50+ ROASTS!
    ADVANCED_ROASTS = [
        # Intelligence roasts
        "You have two brain cells and they're both fighting for third place.",
        "If ignorance is bliss, you must be the happiest person alive.",
        "You're not stupid; you just have bad luck thinking.",
        "I'd agree with you but then we'd both be wrong.",
        "Your IQ is lower than your shoe size.",
        "You're proof that evolution can go backwards.",
        "You have a face for radio and a voice for silent film.",
        
        # Appearance roasts
        "You're so ugly, when you were born the doctor slapped your mother.",
        "Your face makes onions cry.",
        "You're like a cloud. When you disappear, it's a beautiful day.",
        "I've seen better faces on a pirate's treasure map.",
        "You look like what happens when you press 'randomize' in character creation.",
        "Mirrors don't lie, and lucky for you, they also can't laugh.",
        
        # Personality roasts
        "Your personality is as dry as unbuttered toast.",
        "You have the charm of a wet paper bag.",
        "If personality was currency, you'd be bankrupt.",
        "You're the human equivalent of a participation trophy.",
        "You bring everyone so much joy... when you leave the room.",
        "You have the social skills of a doorstop.",
        
        # Skill roasts
        "You couldn't pour water out of a boot with instructions on the heel.",
        "The only thing you're good at is being a bad example.",
        "You have the coordination of a newborn giraffe on ice skates.",
        "If failure was an Olympic sport, you'd be a gold medalist.",
        "You're about as useful as a screen door on a submarine.",
        
        # Family roasts
        "Your family tree must be a cactus because everybody on it is a prick.",
        "You're the reason they put instructions on shampoo bottles.",
        "Your parents are so disappointed, they use your baby pictures as warning signs.",
        "You were so ugly as a kid, your parents fed you with a slingshot.",
        
        # Animal comparison roasts
        "You have the grace of a reversing dump truck without any tires on.",
        "You're as sharp as a marble.",
        "You're about as bright as a black hole.",
        "You have the memory of a goldfish with Alzheimer's.",
        
        # Food roasts
        "You're as useful as a chocolate teapot.",
        "You have the warmth of a dead fish.",
        "You're about as exciting as plain toast.",
        "You're the human equivalent of decaf coffee.",
        
        # Tech roasts
        "You're glitchier than a Bethesda game on launch day.",
        "Your brain has a 404 error: Intelligence not found.",
        "You buffer more than a bad internet connection.",
        "You're about as stable as Windows 95.",
        
        # Creative roasts
        "You're like a Monday morning - nobody wants you.",
        "You have the appeal of a root canal.",
        "You're the reason the gene pool needs a lifeguard.",
        "You're not the sharpest tool in the shed, but you are a tool.",
        "If laughter is the best medicine, your face must be curing the world.",
        "You're proof that God has a sense of humor.",
    ]

    # ✨ EXPANDED COMPLIMENTS
    ADVANCED_COMPLIMENTS = [
        "You're smarter than you look! And you don't look that smart!",
        "You're almost as awesome as me! Key word: almost.",
        "Your face doesn't scare me... much.",
        "You have a face for radio! And a voice for mime!",
        "You're proof that miracles happen! How else did you survive this long?",
        "You're not as bad as people say! They say you're terrible!",
        "You have a great personality! If you consider 'annoying' great!",
        "You're one of a kind! Thank God for that!",
        "You're very photogenic! From certain angles! In dim lighting!",
        "You have a great future behind you!",
    ]

    def is_on_cooldown(self, user_id, cooldown_dict, seconds=10):
        """Check if a user is on cooldown"""
        if user_id in cooldown_dict:
            time_diff = datetime.now() - cooldown_dict[user_id]
            if time_diff.total_seconds() < seconds:
                return True
        cooldown_dict[user_id] = datetime.now()
        return False

    @commands.command()
    async def roast(self, ctx, member: discord.Member = None):
        """Roast someone (or get roasted yourself)"""
        # Cooldown check
        if self.is_on_cooldown(ctx.author.id, self.roast_cooldowns, 10):
            await ctx.send("🔥 Calm down! Wait 10 seconds before roasting again.")
            return
        
        target = member or ctx.author
        
        if target == self.bot.user:
            await ctx.send("🤖 Nice try, but I'm fireproof!")
            return
        
        if target == ctx.author:
            await ctx.send("🎯 Bold move roasting yourself! Let's see how this goes...")
            await asyncio.sleep(1)
        
        roast = random.choice(self.ADVANCED_ROASTS)
        
        # Create embed for better presentation
        embed = discord.Embed(
            title="🔥 ROASTED!",
            description=f"{target.mention}, {roast}",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url="https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif")
        embed.set_footer(text=f"Roasted by {ctx.author.display_name}")
        
        await ctx.send(embed=embed)

    @commands.command()
    async def compliment(self, ctx, member: discord.Member = None):
        """Give someone a backhanded compliment"""
        target = member or ctx.author
        
        if target == self.bot.user:
            await ctx.send("❤️ Aww, thanks! You're not so bad yourself... for a human.")
            return
        
        compliment = random.choice(self.ADVANCED_COMPLIMENTS)
        
        embed = discord.Embed(
            title="✨ COMPLIMENT!",
            description=f"{target.mention}, {compliment}",
            color=discord.Color.gold()
        )
        embed.set_footer(text=f"Complimented by {ctx.author.display_name}")
        
        await ctx.send(embed=embed)

    @commands.command()
    async def superroast(self, ctx, member: discord.Member = None):
        """ULTIMATE ROAST - Use with caution!"""
        # Longer cooldown for super roast
        if self.is_on_cooldown(ctx.author.id, self.roast_cooldowns, 30):
            await ctx.send("🔥 That was too hot! Wait 30 seconds before another super roast.")
            return
        
        target = member or ctx.author
        
        if target == self.bot.user:
            await ctx.send("🤖 I'm immune to your puny human roasts!")
            return
        
        # Select 3 roasts for maximum damage
        roasts = random.sample(self.ADVANCED_ROASTS, 3)
        roast_text = "\n\n".join([f"🔥 {roast}" for roast in roasts])
        
        embed = discord.Embed(
            title="💀 ULTIMATE ROAST COMBO!",
            description=f"{target.mention}\n\n{roast_text}",
            color=discord.Color.dark_red()
        )
        embed.set_thumbnail(url="https://media.giphy.com/media/l0MYJnJQ4EiYLxvQ4/giphy.gif")
        embed.set_footer(text=f"Annihilated by {ctx.author.display_name}")
        
        await ctx.send(embed=embed)

    @commands.command()
    async def roastbattle(self, ctx, member: discord.Member):
        """Challenge someone to a roast battle"""
        if member == ctx.author:
            await ctx.send("❌ You can't battle yourself! That's just sad.")
            return
        
        if member.bot:
            await ctx.send("❌ Bots don't have feelings to roast!")
            return
        
        embed = discord.Embed(
            title="⚔️ ROAST BATTLE!",
            description=f"{ctx.author.mention} has challenged {member.mention} to a roast battle!\n\nReact with 🔥 to accept!",
            color=discord.Color.orange()
        )
        
        battle_msg = await ctx.send(embed=embed)
        await battle_msg.add_reaction("🔥")
        
        def check(reaction, user):
            return user == member and str(reaction.emoji) == "🔥" and reaction.message.id == battle_msg.id
        
        try:
            await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
            
            # Battle accepted!
            await ctx.send(f"🎯 Battle accepted! {ctx.author.mention} vs {member.mention}")
            await asyncio.sleep(2)
            
            # Each person gets 3 roasts
            for round_num in range(1, 4):
                await ctx.send(f"**Round {round_num}!**")
                
                # Player 1's roast
                roast1 = random.choice(self.ADVANCED_ROASTS)
                await ctx.send(f"🔥 {ctx.author.mention}: {roast1}")
                await asyncio.sleep(3)
                
                # Player 2's roast
                roast2 = random.choice(self.ADVANCED_ROASTS)
                await ctx.send(f"🔥 {member.mention}: {roast2}")
                await asyncio.sleep(3)
            
            # Determine winner randomly for fun
            winner = random.choice([ctx.author, member])
            await ctx.send(f"🏆 **AND THE WINNER IS... {winner.mention}!** 🏆")
            
        except asyncio.TimeoutError:
            await ctx.send(f"⏰ {member.mention} was too scared to accept the challenge!")

    @commands.command()
    async def rate(self, ctx, *, thing: str = None):
        """Rate something on a scale of 1-10"""
        if not thing:
            await ctx.send("❌ Please provide something to rate!")
            return
        
        rating = random.randint(1, 10)
        emoji = "⭐" * rating
        
        # Funny rating comments
        comments = {
            1: "Absolutely terrible!",
            2: "Pretty bad...",
            3: "Not great!",
            4: "Meh...",
            5: "Average at best!",
            6: "Not bad!",
            7: "Pretty good!",
            8: "Great!",
            9: "Amazing!",
            10: "PERFECT! Absolutely incredible!"
        }
        
        embed = discord.Embed(
            title="📊 RATING",
            description=f"**{thing}**\n\nRating: **{rating}/10** {emoji}\n\n{comments[rating]}",
            color=discord.Color.blue()
        )
        
        await ctx.send(embed=embed)

    @commands.command()
    async def coinflip(self, ctx):
        """Flip a coin"""
        result = random.choice(["Heads", "Tails"])
        
        embed = discord.Embed(
            title="🪙 COIN FLIP",
            description=f"The coin landed on... **{result}**!",
            color=discord.Color.gold()
        )
        
        await ctx.send(embed=embed)

    @commands.command()
    async def dice(self, ctx, sides: int = 6):
        """Roll a dice (default 6 sides)"""
        if sides < 2 or sides > 100:
            await ctx.send("❌ Please choose between 2-100 sides.")
            return
        
        result = random.randint(1, sides)
        
        embed = discord.Embed(
            title="🎲 DICE ROLL",
            description=f"You rolled a **{result}** (1-{sides})",
            color=discord.Color.green()
        )
        
        await ctx.send(embed=embed)

    @commands.command()
    async def choose(self, ctx, *, options: str):
        """Let the bot choose for you (separate options with |)"""
        if "|" not in options:
            await ctx.send("❌ Please separate options with | (e.g., `!choose pizza|burger|tacos`)")
            return
        
        choices = [opt.strip() for opt in options.split("|") if opt.strip()]
        if len(choices) < 2:
            await ctx.send("❌ Please provide at least 2 options.")
            return
        
        chosen = random.choice(choices)
        
        embed = discord.Embed(
            title="🤔 CHOICE MAKER",
            description=f"Options: **{', '.join(choices)}**\n\nI choose... **{chosen}**!",
            color=discord.Color.purple()
        )
        
        await ctx.send(embed=embed)

    @commands.command()
    async def joke(self, ctx):
        """Tell a random joke"""
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the scarecrow win an award? He was outstanding in his field!",
            "Why don't eggs tell jokes? They'd crack each other up!",
            "What do you call a fake noodle? An impasta!",
            "Why did the math book look so sad? Because it had too many problems!",
            "What do you call a bear with no teeth? A gummy bear!",
            "Why don't skeletons fight each other? They don't have the guts!",
            "What do you call a sleeping bull? A bulldozer!",
            "Why did the coffee file a police report? It got mugged!",
            "What do you call a fish wearing a crown? King of the sea!",
        ]
        
        joke = random.choice(jokes)
        
        embed = discord.Embed(
            title="🎭 RANDOM JOKE",
            description=joke,
            color=discord.Color.blurple()
        )
        
        await ctx.send(embed=embed)

    @commands.command()
    async def eightball(self, ctx, *, question: str = None):
        """Ask the magic 8-ball a question"""
        if not question:
            await ctx.send("❌ Please ask a question!")
            return
        
        responses = [
            "It is certain.", "It is decidedly so.", "Without a doubt.",
            "Yes - definitely.", "You may rely on it.", "As I see it, yes.",
            "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.",
            "Reply hazy, try again.", "Ask again later.", "Better not tell you now.",
            "Cannot predict now.", "Concentrate and ask again.", "Don't count on it.",
            "My reply is no.", "My sources say no.", "Outlook not so good.", "Very doubtful."
        ]
        
        answer = random.choice(responses)
        
        embed = discord.Embed(
            title="🎱 MAGIC 8-BALL",
            description=f"**Question:** {question}\n\n**Answer:** {answer}",
            color=discord.Color.dark_gray()
        )
        
        await ctx.send(embed=embed)

    @commands.command()
    async def mock(self, ctx, *, text: str = None):
        """Mock someone's text (sPoNgEbOb CaSe)"""
        if self.is_on_cooldown(ctx.author.id, self.mock_cooldowns, 5):
            await ctx.send("🤪 Calm down! Wait 5 seconds before mocking again.")
            return
            
        if not text:
            await ctx.send("❌ Please provide text to mock!")
            return
        
        mocked = ''.join(
            char.upper() if i % 2 == 0 else char.lower() 
            for i, char in enumerate(text)
        )
        
        embed = discord.Embed(
            title="🤪 MOCKED TEXT",
            description=mocked,
            color=discord.Color.light_grey()
        )
        
        await ctx.send(embed=embed)

    @commands.command()
    async def funhelp(self, ctx):
        """Show all fun commands"""
        embed = discord.Embed(
            title="🎮 FUN COMMANDS HELP",
            description="Here are all the fun commands you can use:",
            color=discord.Color.purple()
        )
        
        commands_list = [
            "`!roast [@user]` - Roast someone (or yourself)",
            "`!superroast [@user]` - Ultimate roast combo",
            "`!roastbattle @user` - Challenge someone to a roast battle",
            "`!compliment [@user]` - Give a backhanded compliment",
            "`!rate [thing]` - Rate something 1-10",
            "`!coinflip` - Flip a coin",
            "`!dice [sides]` - Roll a dice",
            "`!choose option1|option2` - Choose between options",
            "`!joke` - Tell a random joke",
            "`!eightball [question]` - Ask magic 8-ball",
            "`!mock [text]` - Mock text (SpOnGeBoB case)",
            "`!funhelp` - Show this help message"
        ]
        
        embed.add_field(name="Commands", value="\n".join(commands_list), inline=False)
        embed.set_footer(text="Have fun! 🔥")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Fun(bot))
