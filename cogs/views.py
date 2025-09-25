import discord
from discord.ext import commands

class Views(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # tu peux initialiser tes views ici si besoin

    # Exemple d’événement
    @commands.Cog.listener()
    async def on_ready(self):
        print("✅ Cog Views chargé et prêt !")

    # Exemple de commande pour tester
    @commands.command(name="testview")
    async def test_view(self, ctx):
        await ctx.send("La commande `!testview` fonctionne ✅")

# Nouvelle syntaxe obligatoire avec discord.py 2.0+
async def setup(bot: commands.Bot):
    await bot.add_cog(Views(bot))
