import discord
from discord.ext import commands
import asyncio

# IDs des salons
HALL_ID = 1420336349613002774  # Hall-d-Entrée
GRANDE_SALLE_ID = 1420336456842813480  # Grande-Salle


class EntryView(discord.ui.View):
    def __init__(self, guild_id: int, hall_id: int, grande_salle_id: int):
        super().__init__(timeout=None)
        self.guild_id = guild_id
        self.hall_id = hall_id
        self.grande_salle_id = grande_salle_id

    @discord.ui.button(label="🚪 Entrer dans le Hall-d’Entrée", style=discord.ButtonStyle.primary, custom_id="enter_hall")
    async def enter_hall(self, interaction: discord.Interaction, button: discord.ui.Button):
        hall_channel = interaction.guild.get_channel(self.hall_id)
        if hall_channel:
            msg = await hall_channel.send(
                f"🪄 Les lourdes portes grincent et {interaction.user.mention} franchit enfin le **Hall-d’Entrée**...\n\n"
                "De hautes torches magiques illuminent les pierres froides, projetant des ombres dansantes.\n\n"
                "Une voix solennelle résonne dans le silence :\n"
                "« Tu as prêté serment en validant le règlement… "
                "Tu peux désormais faire officiellement ton entrée à **Poudlard** ! »\n\n"
                "➡️ **Rends-toi maintenant dans la Grande-Salle** pour la Cérémonie de Répartition "
                "et invoque le Choixpeau magique en lançant la commande `!quiz`."
            )
            await interaction.response.send_message(
                "✨ Tu as franchi les portes et pénétré dans le Hall-d’Entrée !", ephemeral=True
            )
            # Sauvegarde le message pour suppression ultérieure
            interaction.client.welcome_messages[interaction.user.id] = msg

    @discord.ui.button(label="🏰 Se rendre à la Grande-Salle", style=discord.ButtonStyle.success, custom_id="go_grande_salle")
    async def go_grande_salle(self, interaction: discord.Interaction, button: discord.ui.Button):
        grande_salle_channel = interaction.guild.get_channel(self.grande_salle_id)
        if grande_salle_channel:
            await interaction.response.send_message(
                f"🏰 Tu te diriges vers la **Grande-Salle** : {grande_salle_channel.mention}\n\n"
                "Prépare-toi… le Choixpeau t’attend pour la Répartition !",
                ephemeral=True
            )
            # Supprime le message précédent si encore présent
            old_msg = interaction.client.welcome_messages.pop(interaction.user.id, None)
            if old_msg:
                try:
                    await old_msg.delete()
                except Exception:
                    pass


class Reglement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore si le message vient du bot
        if message.author.bot:
            return

        # Vérifie si on est dans le salon règlement et que l'élève tape "lumos"
        if message.channel.name == "règlement" and message.content.lower().strip() == "lumos":
            guild = message.guild
            member = message.author

            # Rôle Élève
            role = discord.utils.get(guild.roles, name="Élève")
            if role and role not in member.roles:
                await member.add_roles(role)

            # Supprime le message de l'élève pour garder le salon propre
            try:
                await message.delete()
            except discord.Forbidden:
                pass

            # Envoie uniquement dans Hall-d’Entrée (PAS dans règlement)
            hall_channel = guild.get_channel(HALL_ID)
            if hall_channel:
                rp_message = (
                    f"🪄 Les lourdes portes grincent et {member.mention} franchit enfin le **Hall-d’Entrée**...\n\n"
                    "De hautes torches magiques illuminent les pierres froides, projetant des ombres dansantes.\n\n"
                    "Une voix solennelle résonne dans le silence :\n"
                    "« Tu as prêté serment en validant le règlement… "
                    "Tu peux désormais faire officiellement ton entrée à **Poudlard** ! »\n\n"
                    "➡️ **Rends-toi maintenant dans la Grande-Salle** pour la Cérémonie de Répartition "
                    "et invoque le Choixpeau magique en lançant la commande `!quiz`."
                )

                view = EntryView(guild.id, HALL_ID, GRANDE_SALLE_ID)
                msg = await hall_channel.send(rp_message, view=view)

                # Sauvegarde pour suppression future
                self.bot.welcome_messages[member.id] = msg

                # Suppression automatique après 15 minutes si inactif
                async def delete_later():
                    await asyncio.sleep(900)
                    if member.id in self.bot.welcome_messages:
                        try:
                            old_msg = self.bot.welcome_messages.pop(member.id)
                            await old_msg.delete()
                        except Exception:
                            pass

                asyncio.create_task(delete_later())


async def setup(bot):
    await bot.add_cog(Reglement(bot))
