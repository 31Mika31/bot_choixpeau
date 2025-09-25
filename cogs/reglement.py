import discord
from discord.ext import commands

class ReglementCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        # Vérifie le bon canal + le mot-clé "lumos"
        if message.channel.name == "règlement" and message.content.lower().strip() == "lumos":
            guild = message.guild
            member = message.author

            # Attribue le rôle Élève
            role = discord.utils.get(guild.roles, name="Élève")
            if role:
                try:
                    await member.add_roles(role, reason="Validation du règlement")
                except discord.Forbidden:
                    await message.channel.send(
                        f"⚠️ {member.mention}, je n’ai pas la permission de t’ajouter le rôle."
                    )
                    return

            # Cherche le salon textuel Hall-d-Entrée
            hall = discord.utils.get(guild.text_channels, name="hall-d-entrée")

            # Message de confirmation
            if hall:
                await message.channel.send(
                    f"✨ Bravo {member.mention}, tu as validé le règlement et reçu ton rôle d’Élève !\n"
                    f"👉 Rends-toi maintenant dans {hall.mention} pour continuer ton aventure."
                )
            else:
                await message.channel.send(
                    f"✨ Bravo {member.mention}, tu as validé le règlement et reçu ton rôle d’Élève !"
                )

async def setup(bot):
    await bot.add_cog(ReglementCog(bot))
