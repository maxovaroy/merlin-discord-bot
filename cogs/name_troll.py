import discord
from discord.ext import commands
import random
import config

class NameTroll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.name_responses = self.load_name_responses()

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
            "-2 bump": [
                "go away",
                "you gay go away",
                "i will call diddy so you better go away",
                "+1 bump",
                "+10000 bump, you gay",
                "shush! gay"
            ],
            # Add more names here following the same format
        }

    @commands.Cog.listener()
    async def on_message(self, message):
        """Check for names in messages and troll accordingly"""
        if message.author.bot:
            return
        
        content = message.content.lower()
        
        # Debug: Print the message to see what's being received
        print(f"📨 Message received: {content}")
        
        # Check for names in the message (more flexible matching)
        for name, responses in self.name_responses.items():
            # Check if name appears as a separate word in the message
            if f" {name} " in f" {content} " or content.startswith(name) or content.endswith(name):
                # 80% chance to reply when a name is mentioned (increased for testing)
                if random.random() < 0.99:  # Increased chance for testing
                    response = random.choice(responses)
                    print(f"🎯 Name '{name}' detected! Replying: {response}")
                    await message.reply(response)
                    break  # Only reply to one name per message

    @commands.group(name="nametroll", invoke_without_command=True)
    async def nametroll(self, ctx):
        """Manage name-based trolling"""
        embed = discord.Embed(
            title="🎭 Name Troll System",
            description="Automatically troll when specific names are mentioned!",
            color=discord.Color.purple()
        )
        
        embed.add_field(
            name="Current Tracked Names",
            value="\n".join([f"• **{name.capitalize()}**" for name in self.name_responses.keys()]),
            inline=False
        )
        
        embed.add_field(
            name="Commands",
            value=(
                "`!nametroll list` - Show all names and responses\n"
                "`!nametroll add <name> <response>` - Add new name response\n"
                "`!nametroll remove <name>` - Remove a name\n"
                "`!nametroll responses <name>` - See responses for a name\n"
                "`!nametroll test <name>` - Test if name detection works\n"
            ),
            inline=False
        )
        
        await ctx.send(embed=embed)

    @nametroll.command(name="list")
    async def nametroll_list(self, ctx):
        """List all tracked names"""
        if not self.name_responses:
            await ctx.send("❌ No names are being tracked yet!")
            return
        
        embed = discord.Embed(
            title="📋 Tracked Names",
            color=discord.Color.blue()
        )
        
        for name, responses in self.name_responses.items():
            embed.add_field(
                name=f"🎯 {name.capitalize()}",
                value=f"{len(responses)} responses\n`!nametroll responses {name}` to view",
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
        """Add a new name response (Admin only)"""
        name = name.lower()
        
        if name not in self.name_responses:
            self.name_responses[name] = []
        
        self.name_responses[name].append(response)
        await ctx.send(f"✅ Added response for **{name}**: \"{response}\"")

    @nametroll.command(name="remove")
    @commands.has_permissions(administrator=True)
    async def nametroll_remove(self, ctx, name: str):
        """Remove a name from tracking (Admin only)"""
        name = name.lower()
        
        if name in self.name_responses:
            del self.name_responses[name]
            await ctx.send(f"✅ Removed **{name}** from tracking")
        else:
            await ctx.send(f"❌ **{name}** is not being tracked")

    @nametroll.command(name="responses")
    async def nametroll_responses(self, ctx, name: str):
        """View all responses for a specific name"""
        name = name.lower()
        
        if name not in self.name_responses:
            await ctx.send(f"❌ **{name}** is not being tracked")
            return
        
        responses = self.name_responses[name]
        embed = discord.Embed(
            title=f"🎭 Responses for {name.capitalize()}",
            color=discord.Color.green()
        )
        
        for i, response in enumerate(responses, 1):
            embed.add_field(
                name=f"Response #{i}",
                value=response,
                inline=False
            )
        
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

