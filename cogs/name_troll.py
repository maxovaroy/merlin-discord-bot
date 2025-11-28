import discord
from discord.ext import commands
import random
import config

class NameTroll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.name_responses = self.load_name_responses()

        # Map a tracked name to a Discord user ID manually
        self.name_mentions = {
            "max": 717689371293384766,
            "alex": 1209165207784525837,
            "alyssa": 1326313175930634250,
            "flip": 1004839468865433601,
            "ava": 1206101095667998751,
            "una": 574005462534586379,
            "shad": 1237355589701472279,
            "intre": 1312424830213165086,
            "kartik": 1377607512081170502,
            "iron": 1351252842366763029,
            "blaze": 1226831809866891345,
            "xil": 989850262120325150,
            "bun": 1235188867997634645,
            "laspard": 1379043538955927685,
            "candy": 1128157772492574822,
        }

        # Create variants for each name
        self.name_variants = self.create_name_variants(self.name_responses)


    def load_name_responses(self):
        """Load name-based troll responses"""
        return {
            # Format: "name": ["response1", "response2", "response3"]
            "max": [
                "broke ass nagoor",
                "he's black",
                "dont call my master",
                "got no rizz",
                "got no bitches",
                "got no gold"
            ],
            "alex": [
                "alex the minor who identify as a gay jew",
                "dont call that gay please",
                "check your coins because jews are on the run",
                "he's probably A MINORRRRRRRRRR",
                "dont call him, he takes screenshots and evidences to sue in court"
            ],
            "alyssa": [
                "keep your dicks in pants she can cut it in half",
                "penguin are not allowed here",
                "your iq is worse than a donkey",
                "be careful she fucks a lot",
                "keep her name out your fucking mouth"
            ],
            "flip": [
                "he cant do a flip",
                "oh shit who called final boss?",
                "he wants to flirt",
                "sigma boi coming",
                "rizzler?? Run girls!!!!!!!!!!!!"
                "he got fliped over by alyssa"
            ],
            "ava": [
                "mommy is coming hide!!!!",
                "she can hack you so dont call her",
                "she's getting your ip address",
                "max dont pay her",
                "bad mommy"
            ],
            "una": [
                "omg are you talking about real UNAXD??",
                "UNA goat, just dont tag him please, or i will ban you",
                "UNA LEGEND!!!!!!!!",
                "you better not stalk our UNA, or i will come for you",
                "UNA UNA UNA UNA UNA UNA"
            ],
            "shad": [
                "oh hell no, why you calling him?",
                "shad goat",
                "he will mute you",
                "he's a good boy",
                "damn!!! bro is moderator"
            ],
            "intre": [
                "intre paglu",
                "goat is busy, he's getting milked :)",
                "daddy will give you better advices than your actual dad",
                "he will steal your girl!",
                "bomboclat intre nigggggaaaaaaaa"
            ],
            "kartik": [
                "fighter will fight everything",
                "he dont ask for gold anymore",
                "you better not troll him, im watching you",
                "he will get better at standoff 2",
                "bomboclat Kart1k nigggggaaaaaaaa"
            ],
            "iron": [
                "ironsour?????????? who tasted it anyway?",
                "he gay like alex",
                "he like minors, such a pedo",
                "oh nooooooooo dont call him!!!!!!!!",
                "bomboclat ironsour nigggggaaaaaaaa"
            ],
            "blaze": [
                "broke ass nigga",
                "he's black mongolian",
                "annoying ass gay boy",
                "cant keep his mouth shut",
                "got bigger dick than alyssa",
                "he's pro in front of bots"
            ],
            "xil": [
                "he's busy",
                "he's making something insane",
                "bro is making doublebind ui famous ",
                "goat coder",
                "he's a silent mod here, do not mess with him",
                "russian legend"
            ],
            "bun": [
                "tasty bun, oh waittttttttt noooooooooo",
                "bun with skills is not bun anymore, its burn",
                "she can eat you alive",
                "you cant win against her",
                "easy kid, she's vip here",
                "jigga figga gold digga bun is not a nigga"
            ],
            "laspard": [
                "someone need nitro??",
                "legend is busy",
                "roblox legend",
                "bro can do anything except for rizzing a girl",
                "if you touch him then this bot will fuck you with his metal dick!!!!!! dont tell alyssa that i have a metal dick",
                "need something??"
            ],
            "ᴄᴀɴᴅʏ": [
                "oh nooooo he's pedo brooooooooo",
                "does he have drugs??",
                "chilling with his candy",
                "got a big basement............. im not talking about his ass!!!",
                "he aint from turkey",
                "he dont have crypto!"
            ],
        }

    def create_name_variants(self, names_dict):
        """Create simple variants for each name"""
        variants = {}
        for name in names_dict:
            lower = name.lower()
            variants[name] = {
                lower,                   # lowercase
                lower[:3],               # first 3 letters
                lower[:4],               # first 4 letters
                lower.replace(" ", ""),  # no spaces
                lower + "y",             # adding 'y'
                lower + "ie",            # adding 'ie'
                lower.capitalize(),      # capitalized
            }
        return variants

    def get_manual_mentions(self, message):
        """Return set of names that were manually mentioned via mapping"""
        mentioned_names = set()
        for name, user_id in self.name_mentions.items():
            for mention in message.mentions:
                if mention.id == user_id:
                    mentioned_names.add(name)
        return mentioned_names

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        content = message.content.lower()
        manually_mentioned_names = self.get_manual_mentions(message)
        detected_name = None

        # Check text variants first
        for name, variants in self.name_variants.items():
            for variant in variants:
                if re.search(rf"\b{re.escape(variant)}\b", content):
                    detected_name = name
                    print(f"🎯 DEBUG - Name variant '{variant}' detected in message: {content}")
                    break
            if detected_name:
                break

        # If no variant detected, check manual mentions
        if not detected_name:
            for name in manually_mentioned_names:
                detected_name = name
                print(f"📌 DEBUG - @{name} manually mentioned in message: {content}")
                break

        # Send response if detected
        if detected_name:
            response = random.choice(self.name_responses[detected_name])
            await message.reply(response)
            print(f"✅ DEBUG - Replied to {message.author} for name '{detected_name}'")

    # Command group for management
    @commands.group(name="nametroll", invoke_without_command=True)
    async def nametroll(self, ctx):
        embed = discord.Embed(
            title="🎭 Name Troll System",
            description="Automatically troll when specific names are mentioned!",
            color=discord.Color.purple()
        )
        embed.add_field(
            name="Tracked Names",
            value="\n".join([f"• **{name.capitalize()}**" for name in self.name_responses.keys()]),
            inline=False
        )
        await ctx.send(embed=embed)

    @nametroll.command(name="list")
    async def nametroll_list(self, ctx):
        embed = discord.Embed(title="📋 Tracked Names", color=discord.Color.blue())
        for name, responses in self.name_responses.items():
            embed.add_field(
                name=f"🎯 {name.capitalize()}",
                value=f"{len(responses)} responses",
                inline=True
            )
        await ctx.send(embed=embed)

    @nametroll.command(name="test")
    async def nametroll_test(self, ctx, name: str):
        """Test if a name is being detected properly"""
        name = name.lower()
        
        if name in self.name_responses:
            # Simulate message detection
            test_message = f"test message with {name} in it"
            print(f"🧪 Testing name: '{name}' in message: '{test_message}'")
            
            # Check if it would trigger
            if f" {name} " in f" {test_message} " or test_message.startswith(name) or test_message.endswith(name):
                responses = self.name_responses[name]
                await ctx.send(f"✅ **{name}** is properly configured! Would reply with one of {len(responses)} responses.")
            else:
                await ctx.send(f"❌ **{name}** detection failed in test.")
        else:
            await ctx.send(f"❌ **{name}** is not being tracked")

    @nametroll.command(name="add")
    @commands.has_permissions(administrator=True)
    async def nametroll_add(self, ctx, name: str, *, response: str):
        name = name.lower()
        if name not in self.name_responses:
            self.name_responses[name] = []
        self.name_responses[name].append(response)
        # Update variants dynamically
        self.name_variants[name] = {name, name + "y", name + "ie", name.capitalize()}
        await ctx.send(f"✅ Added response for **{name}**: \"{response}\"")

    @nametroll.command(name="remove")
    @commands.has_permissions(administrator=True)
    async def nametroll_remove(self, ctx, name: str):
        name = name.lower()
        if name in self.name_responses:
            del self.name_responses[name]
            self.name_variants.pop(name, None)
            await ctx.send(f"✅ Removed **{name}** from tracking")
        else:
            await ctx.send(f"❌ **{name}** is not being tracked")

    @nametroll.command(name="responses")
    async def nametroll_responses(self, ctx, name: str):
        name = name.lower()
        if name not in self.name_responses:
            await ctx.send(f"❌ **{name}** is not being tracked")
            return
        embed = discord.Embed(title=f"🎭 Responses for {name.capitalize()}", color=discord.Color.green())
        for i, response in enumerate(self.name_responses[name], 1):
            embed.add_field(name=f"Response #{i}", value=response, inline=False)
        await ctx.send(embed=embed)

    @nametroll.command(name="edit")
    @commands.has_permissions(administrator=True)
    async def nametroll_edit(self, ctx, name: str, index: int, *, new_response: str):
        """Edit a specific response for a name (Admin only)"""
        name = name.lower()
        
        if name not in self.name_responses:
            await ctx.send(f"❌ **{name}** is not being tracked")
            return
        
        if index < 1 or index > len(self.name_responses[name]):
            await ctx.send(f"❌ Invalid response number. Use 1-{len(self.name_responses[name])}")
            return
        
        old_response = self.name_responses[name][index-1]
        self.name_responses[name][index-1] = new_response
        
        embed = discord.Embed(
            title="✅ Response Updated",
            color=discord.Color.gold()
        )
        embed.add_field(name="Old Response", value=old_response, inline=False)
        embed.add_field(name="New Response", value=new_response, inline=False)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(NameTroll(bot))
