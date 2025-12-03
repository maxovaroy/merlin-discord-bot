import discord
from discord.ext import commands
import aiosqlite

DB_PATH = "database.db"
AUTHORIZED_ROLE = "SO2-Manager"

# Example skin metadata
SKINS = {
    "AK-47 | Dragonfire": "https://link.to/dragonfire_skin_image.png",
    "Desert Eagle | Golden Eagle": "https://link.to/goldeneagle_skin_image.png",
    # add more skins...
}

class SetPriceDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=skin, description=f"Set price for {skin}")
            for skin in SKINS.keys()
        ]
        super().__init__(placeholder="Select a skin…", max_values=1, min_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        skin = self.values[0]
        await interaction.response.send_modal(SetPriceModal(skin))

class SetPriceView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(SetPriceDropdown())

class SetPriceModal(discord.ui.Modal, title="Set Skin Price"):
    def __init__(self, skin_name):
        super().__init__()
        self.skin = skin_name
        self.price = discord.ui.TextInput(
            label="New price (integer)",
            placeholder="e.g. 450",
            required=True,
        )
        self.add_item(self.price)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            new_price = int(self.price.value)
        except ValueError:
            await interaction.response.send_message("❌ Invalid price value.", ephemeral=True)
            return

        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "REPLACE INTO standoff_prices (skin_name, price) VALUES (?, ?)",
                (self.skin, new_price)
            )
            await db.commit()

        img_url = SKINS.get(self.skin)
        embed = discord.Embed(
            title=f"Price updated — {self.skin}",
            description=f"New price: **{new_price}** coins",
            color=discord.Color.green()
        )
        if img_url:
            embed.set_image(url=img_url)

        await interaction.response.send_message(embed=embed)

class Standoff2Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="setprice")
    @commands.has_role(AUTHORIZED_ROLE)
    async def setprice_cmd(self, ctx):
        view = SetPriceView()
        await ctx.send("Select a skin to set price:", view=view)

    @setprice_cmd.error
    async def setprice_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            await ctx.send("❌ You don’t have permission to use this command.")

    @commands.command(name="price")
    async def price_cmd(self, ctx, *, skin_name: str):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(
                "SELECT price FROM standoff_prices WHERE skin_name = ?", (skin_name,)
            ) as cursor:
                row = await cursor.fetchone()
        if row is None:
            await ctx.send(f"❌ Skin **{skin_name}** not found.")
            return

        price = row[0]
        img_url = SKINS.get(skin_name)
        embed = discord.Embed(
            title=skin_name,
            description=f"Price: **{price}** coins",
            color=discord.Color.blue()
        )
        if img_url:
            embed.set_image(url=img_url)

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Standoff2Cog(bot))
