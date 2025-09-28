# cogs/reglement.py
import discord
from discord.ext import commands
import asyncio
import os


class EntryView(discord.ui.View):
    def __init__(self, guild_id: int, hall_id: int, origin_message=None):
        super().__init__(timeout=None)
        self.guild_id = guild_id
        self.hall_id = hall_id
        self.origin_message = origin_message  # message "Félicitations..."

    @discord.ui.button(
        label="🚪 Entrer dans le Hall-d’Entrée",
        style=discord.ButtonStyle.primary,
        custom_id="enter_hall"
    )
    async def enter_hall(self, interaction: discord.Interaction, button: discord.ui.Button):
        hall_channel = interaction.guild.get_channel(self.hall_id)
        if not hall_channel:
            await interaction.response.send_message("❌ Salon Hall introuvable.", ephemeral=True)
            return

        # Répond vite pour éviter "Échec de l'interaction"
        try:
            await interaction.response.defer(ephemeral=True)
        except Exception:
            # si déjà répondu, ignore
            pass

        # Message RP dans le Hall
        try:
            msg = await hall_channel.send(
                f"🪄 Les lourdes portes grincent et {interaction.user.mention} franchit enfin le **Hall-d’Entrée**...\n\n"
                "De hautes torches magiques illuminent les pierres froides, projetant des ombres dansantes.\n\n"
                "Une voix solennelle résonne dans le silence :\n"
                "« Tu as prêté serment en validant le règlement… "
                "Tu peux désormais faire officiellement ton entrée à **Poudlard** ! »\n\n"
                "➡️ **Rends-toi maintenant dans la Grande-Salle** pour la Cérémonie de Répartition "
                "et invoque le Choixpeau magique en lançant la commande `!quiz`."
            )
        except Exception:
            await interaction.followup.send("❌ Impossible d'envoyer le message dans le Hall.", ephemeral=True)
            return

        # confirmation éphémère à l'utilisateur
        try:
            await interaction.followup.send(
                "✨ Tu as franchi les portes et pénétré dans le Hall-d’Entrée !",
                ephemeral=True,
            )
        except Exception:
            pass

        # Stocker la référence pour suppression ultérieure par le quiz
        interaction.client.welcome_messages[interaction.user.id] = msg

        # Supprimer le message "Félicitations..." (si présent)
        if self.origin_message:
            try:
                await self.origin_message.delete()
            except Exception:
                pass


class Reglement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # dictionnaire member_id -> Message ou "pending"
        # stocke le message "Félicitations..." envoyé dans le salon règlement
        self.bot.welcome_messages = getattr(self.bot, "welcome_messages", {})

        # Récupération des IDs depuis les variables d'environnement
        self.channel_ids = {
            "REGLEMENT": int(os.getenv("CHANNEL_REGLEMENT", 0)),
            "HALL": int(os.getenv("CHANNEL_HALL", 0)),
        }

        self.roles = {
            "ELEVE": os.getenv("ROLE_ELEVE", "Élève"),
            "NOUVEL": os.getenv("ROLE_NOUVEL", "Nouvel arrivant"),
        }

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if (
            message.channel.id == self.channel_ids.get("REGLEMENT")
            and message.content.lower().strip() == "lumos"
        ):
            guild = message.guild
            member = message.author

            # si un message "Félicitations..." est en attente ou déjà envoyé, on ignore la seconde exécution
            if member.id in self.bot.welcome_messages:
                # déjà en cours / envoyé => éviter doublon
                return

            # marquer comme pending pour éviter race condition
            self.bot.welcome_messages[member.id] = "pending"

            # Ajouter le rôle "Élève"
            role_eleve = discord.utils.get(guild.roles, name=self.roles.get("ELEVE"))
            if role_eleve and role_eleve not in member.roles:
                try:
                    await member.add_roles(role_eleve)
                except Exception:
                    pass

            # Retirer le rôle "Nouvel arrivant"
            role_nouvel = discord.utils.get(guild.roles, name=self.roles.get("NOUVEL"))
            if role_nouvel and role_nouvel in member.roles:
                try:
                    await member.remove_roles(role_nouvel)
                except Exception:
                    pass

            try:
                await message.delete()
            except discord.Forbidden:
                pass
            except Exception:
                pass

            # 🎉 Message RP intermédiaire avec SEUL bouton Hall
            rp_message = (
                f"🎉 Félicitations {member.mention} ! Tu vas pouvoir accéder à "
                "l’école des sorciers **Poudlard**.\n\n"
                "➡️ Rends-toi dès maintenant au **Hall-d’Entrée** en cliquant sur le bouton ci-dessous."
            )

            # Créer la view sans origin_message, on met placeholder "pending" avant d'envoyer
            view = EntryView(guild.id, self.channel_ids["HALL"], origin_message=None)

            try:
                sent_msg = await message.channel.send(rp_message, view=view)
            except Exception:
                # échec d'envoi : nettoyer le marqueur pending
                self.bot.welcome_messages.pop(member.id, None)
                return

            # attacher l'objet message à la view (pour que le clic puisse supprimer ce message)
            view.origin_message = sent_msg
            try:
                await sent_msg.edit(view=view)
            except Exception:
                pass

            # remplacer le marqueur "pending" par le Message réel
            self.bot.welcome_messages[member.id] = sent_msg

            # suppression automatique si non cliqué au bout de 15 min
            async def delete_when_expired():
                await asyncio.sleep(900)  # 15 minutes
                cur = self.bot.welcome_messages.get(member.id)
                if cur and cur != "pending":
                    try:
                        self.bot.welcome_messages.pop(member.id, None)
                        await cur.delete()
                    except Exception:
                        self.bot.welcome_messages.pop(member.id, None)

            asyncio.create_task(delete_when_expired())


async def setup(bot):
    await bot.add_cog(Reglement(bot))
