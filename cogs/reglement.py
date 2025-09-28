# cogs/reglement.py
import discord
from discord.ext import commands
import asyncio
import os


class EntryView(discord.ui.View):
    def __init__(self, guild_id: int, hall_id: int, grande_salle_id: int):
        super().__init__(timeout=None)
        self.guild_id = guild_id
        self.hall_id = hall_id
        self.grande_salle_id = grande_salle_id

    @discord.ui.button(
        label="🚪 Entrer dans le Hall-d’Entrée",
        style=discord.ButtonStyle.primary,
        custom_id="enter_hall"
    )
    async def enter_hall(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
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
                "✨ Tu as franchi les portes et pénétré dans le Hall-d’Entrée !",
                ephemeral=True,
            )
            interaction.client.welcome_messages[interaction.user.id] = msg

    @discord.ui.button(
        label="🏰 Se rendre à la Grande-Salle",
        style=discord.ButtonStyle.success,
        custom_id="go_grande_salle"
    )
    async def go_grande_salle(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        grande_salle_channel = interaction.guild.get_channel(self.grande_salle_id)
        if grande_salle_channel:
            await interaction.response.send_message(
                f"🏰 Tu te diriges vers la **Grande-Salle** : {grande_salle_channel.mention}\n\n"
                "Prépare-toi… le Choixpeau t’attend pour la Répartition !",
                ephemeral=True,
            )
            old_msg = interaction.client.welcome_messages.pop(
                interaction.user.id, None
            )
            if old_msg:
                try:
                    await old_msg.delete()
                except Exception:
                    pass


class Reglement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.welcome_messages = {}

        # Récupération des IDs depuis les variables d'environnement
        self.channel_ids = {
            "REGLEMENT": int(os.getenv("CHANNEL_REGLEMENT", 0)),
            "HALL": int(os.getenv("CHANNEL_HALL", 0)),
            "GRANDE_SALLE": int(os.getenv("CHANNEL_GRANDE_SALLE", 0)),
        }

        self.roles = {
            "ELEVE": os.getenv("ROLE_ELEVE", "Élève"),
            "NOUVEL": os.getenv("ROLE_NOUVEL", "Nouvel arrivant"),
        }

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        # Vérifie que le message est "lumos" dans le bon salon
        if (
            message.channel.id == self.channel_ids.get("REGLEMENT")
            and message.content.lower().strip() == "lumos"
        ):
            guild = message.guild
            member = message.author

            # Ajouter le rôle "Élève"
            role_eleve = discord.utils.get(guild.roles, name=self.roles.get("ELEVE"))
            if role_eleve and role_eleve not in member.roles:
                await member.add_roles(role_eleve)

            # Retirer le rôle "Nouvel arrivant"
            role_nouvel = discord.utils.get(guild.roles, name=self.roles.get("NOUVEL"))
            if role_nouvel and role_nouvel in member.roles:
                await member.remove_roles(role_nouvel)

            try:
                await message.delete()
            except discord.Forbidden:
                pass

            # 🎉 Message RP intermédiaire
            hall_channel = guild.get_channel(self.channel_ids.get("HALL"))
            if hall_channel:
                rp_message = (
                    f"🎉 Félicitations {member.mention} ! Tu vas pouvoir accéder à "
                    "l’école des sorciers **Poudlard**.\n\n"
                    f"➡️ Rends-toi dès maintenant au **Hall-d’Entrée** en cliquant sur le bouton ci-dessous."
                )

                view = EntryView(
                    guild.id,
                    self.channel_ids["HALL"],
                    self.channel_ids["GRANDE_SALLE"],
                )
                msg = await message.channel.send(rp_message, view=view)

                self.bot.welcome_messages[member.id] = msg

                async def delete_when_clicked():
                    # supprime après 15 min si non utilisé
                    await asyncio.sleep(900)
                    if member.id in self.bot.welcome_messages:
                        try:
                            old_msg = self.bot.welcome_messages.pop(member.id)
                            await old_msg.delete()
                        except Exception:
                            pass

                asyncio.create_task(delete_when_clicked())


async def setup(bot):
    await bot.add_cog(Reglement(bot))
