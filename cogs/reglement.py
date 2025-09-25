import discord
from discord.ext import commands

CHANNEL_REGLEMENT = "règlement"
CHANNEL_HALLE = "halle-d-entrée"

class Reglement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore les messages du bot lui-même
        if message.author.bot:
            return

        # Log debug pour Render
        print(f"[DEBUG] Salon: {message.channel.name} | Auteur: {message.author} | Message: {message.content}")

        # Vérifie uniquement dans #règlement
        if message.channel.name == CHANNEL_REGLEMENT:
            content = message.content.strip().lower()
            guild = message.guild
            member = message.author

            if content == "lumos":
                try:
                    await message.delete()
                except:
                    pass

                # Retirer rôle "Nouvel arrivant"
                new_role = discord.utils.get(guild.roles, name="Nouvel arrivant")
                if new_role in member.roles:
                    await member.remove_roles(new_role)

                # Ajouter rôle "Élève"
                eleve_role = discord.utils.get(guild.roles, name="Élève")
                if eleve_role and eleve_role not in member.roles:
                    await member.add_roles(eleve_role)

                # Message de confirmation auto-supprimé
                await message.channel.send(
                    f"✨ Bravo {member.mention}, tu as validé le règlement !",
                    delete_after=30
                )

                # Message RP dans le hall
                hall_channel = discord.utils.get(guild.text_channels, name=CHANNEL_HALLE)
                if hall_channel:
                    await hall_channel.send(
                        content=(
                            f"👋 Bienvenue à Poudlard !\n"
                            f"{member.mention}, te voici dans le Hall d’entrée.\n\n"
                            f"Avance vers la Grande Salle pour participer à la cérémonie de répartition."
                        )
                    )
            else:
                try:
                    await message.delete()
                except:
                    pass

async def setup(bot):
    await bot.add_cog(Reglement(bot))
