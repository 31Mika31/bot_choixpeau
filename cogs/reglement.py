# cogs/reglement.py
import discord
from discord.ext import commands
import asyncio
import os
import logging

log = logging.getLogger("choixpeau")


class GrandeSalleView(discord.ui.View):
    def __init__(self, hall_message: discord.Message, grande_salle_id: int):
        super().__init__(timeout=None)
        self.hall_message = hall_message
        self.grande_salle_id = grande_salle_id
        log.info(f"[Reglement] GrandeSalleView initialisée avec grande_salle_id={grande_salle_id}")

    @discord.ui.button(
        label="🍽️ Aller à la Grande-Salle",
        style=discord.ButtonStyle.success,
        custom_id="go_grande_salle"
    )
    async def go_grande_salle(self, interaction: discord.Interaction, button: discord.ui.Button):
        log.info(f"[Reglement] go_grande_salle cliqué par {interaction.user} (id={interaction.user.id})")
        log.info(f"[Reglement] Cherche channel id={self.grande_salle_id} dans guild {interaction.guild.id}")

        grande_salle = interaction.guild.get_channel(self.grande_salle_id)
        log.info(f"[Reglement] get_channel -> {grande_salle}")

        if not grande_salle:
            await interaction.response.send_message("❌ Salon Grande-Salle introuvable.", ephemeral=True)
            return

        try:
            await interaction.response.defer(ephemeral=True)
        except Exception:
            pass

        try:
            grande_msg = await grande_salle.send(
                f"🍽️ {interaction.user.mention} pousse les lourdes portes et entre dans la **Grande-Salle**.\n\n"
                "Les quatre longues tables s’illuminent de mille chandelles flottantes. "
                "Les regards des élèves se tournent vers toi tandis que le Choixpeau magique attend d’être invoqué...\n\n"
                "➡️ Lance la commande `!quiz` pour commencer la Cérémonie de Répartition."
            )
            # Sauvegarder le message pour le supprimer plus tard quand le quiz commence
            interaction.client.welcome_messages[interaction.user.id] = grande_msg
        except Exception as e:
            log.exception(f"[Reglement] Erreur en envoyant le message dans la Grande-Salle: {e}")
            await interaction.followup.send("❌ Impossible d'envoyer le message dans la Grande-Salle.", ephemeral=True)
            return

        # Supprimer le message du Hall s'il existe
        try:
            if self.hall_message:
                await self.hall_message.delete()
        except Exception:
            pass

        try:
            await interaction.followup.send("✨ Tu es maintenant dans la Grande-Salle !", ephemeral=True)
        except Exception:
            pass


class EntryView(discord.ui.View):
    def __init__(self, guild_id: int, hall_id: int, grande_salle_id: int, origin_message=None):
        super().__init__(timeout=None)
        self.guild_id = guild_id
        self.hall_id = hall_id
        self.grande_salle_id = grande_salle_id
        self.origin_message = origin_message
        log.info(f"[Reglement] EntryView ready (hall={hall_id}, grande_salle={grande_salle_id})")

    @discord.ui.button(
        label="🚪 Entrer dans le Hall-d’Entrée",
        style=discord.ButtonStyle.primary,
        custom_id="enter_hall"
    )
    async def enter_hall(self, interaction: discord.Interaction, button: discord.ui.Button):
        log.info(f"[Reglement] enter_hall cliqué par {interaction.user} (id={interaction.user.id})")
        hall_channel = interaction.guild.get_channel(self.hall_id)
        log.info(f"[Reglement] get_channel(hall) -> {hall_channel}")

        if not hall_channel:
            await interaction.response.send_message("❌ Salon Hall introuvable.", ephemeral=True)
            return

        try:
            await interaction.response.defer(ephemeral=True)
        except Exception:
            pass

        try:
            # On envoie d'abord le message dans le Hall
            hall_msg = await hall_channel.send(
                f"🪄 Les lourdes portes grincent et {interaction.user.mention} franchit enfin le **Hall-d’Entrée**...\n\n"
                "De hautes torches magiques illuminent les pierres froides, projetant des ombres dansantes.\n\n"
                "Une voix solennelle résonne dans le silence :\n"
                "« Tu as prêté serment en validant le règlement… "
                "Tu peux désormais faire officiellement ton entrée à **Poudlard** ! »\n\n"
                "➡️ **Rends-toi maintenant dans la Grande-Salle** pour la Cérémonie de Répartition "
                "et invoque le Choixpeau magique en lançant la commande `!quiz`."
            )

            # Puis on attache la view qui contient le bouton pour aller à la Grande-Salle
            view = GrandeSalleView(hall_msg, self.grande_salle_id)
            await hall_msg.edit(view=view)
            log.info("[Reglement] hall_msg envoyé et view attachée")
        except Exception as e:
            log.exception(f"[Reglement] Impossible d'envoyer/éditer le message du Hall: {e}")
            await interaction.followup.send("❌ Impossible d'envoyer le message dans le Hall.", ephemeral=True)
            return

        try:
            await interaction.followup.send("✨ Tu as franchi les portes et pénétré dans le Hall-d’Entrée !", ephemeral=True)
        except Exception:
            pass

        # On sauvegarde pour pouvoir supprimer le message lié à l'utilisateur plus tard
        interaction.client.welcome_messages[interaction.user.id] = hall_msg

        # Supprimer le message d'origine (celui qui a félicité dans le salon règlement)
        if self.origin_message:
            try:
                await self.origin_message.delete()
            except Exception:
                pass


class Reglement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # map user_id -> discord.Message (ou "pending")
        self.bot.welcome_messages = getattr(self.bot, "welcome_messages", {})

        # Lecture robuste des IDs depuis l'environnement
        def load_env_int(name):
            raw = os.getenv(name)
            if not raw:
                return 0
            try:
                return int(raw.strip())
            except Exception:
                log.warning(f"[Reglement] Variable d'environnement {name} invalide: {raw!r}")
                return 0

        self.channel_ids = {
            "REGLEMENT": load_env_int("CHANNEL_REGLEMENT"),
            "HALL": load_env_int("CHANNEL_HALL"),
            "GRANDE_SALLE": load_env_int("CHANNEL_GRANDE_SALLE"),
        }

        log.info(f"[Reglement] channel_ids chargés: {self.channel_ids}")

        self.roles = {
            "ELEVE": os.getenv("ROLE_ELEVE", "Élève"),
            "NOUVEL": os.getenv("ROLE_NOUVEL", "Nouvel arrivant"),
        }

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # protège contre doublons: ne traiter que les messages textuels des utilisateurs
        if message.author.bot:
            return

        reg_id = self.channel_ids.get("REGLEMENT", 0)
        if not reg_id:
            return  # pas configuré

        if message.channel.id == reg_id and message.content.lower().strip() == "lumos":
            guild = message.guild
            member = message.author

            # Si on est déjà en cours pour cet utilisateur, on ne relance pas
            if member.id in self.bot.welcome_messages:
                log.info(f"[Reglement] Ignored lumos: already processing for user {member.id}")
                return
            self.bot.welcome_messages[member.id] = "pending"

            # Ajouter le rôle "Élève"
            role_eleve = discord.utils.get(guild.roles, name=self.roles.get("ELEVE"))
            if role_eleve and role_eleve not in member.roles:
                try:
                    await member.add_roles(role_eleve)
                except Exception:
                    log.exception("[Reglement] Impossible d'ajouter le rôle Élève")

            # Retirer le rôle "Nouvel arrivant"
            role_nouvel = discord.utils.get(guild.roles, name=self.roles.get("NOUVEL"))
            if role_nouvel and role_nouvel in member.roles:
                try:
                    await member.remove_roles(role_nouvel)
                except Exception:
                    log.exception("[Reglement] Impossible de retirer le rôle Nouvel arrivant")

            try:
                await message.delete()
            except Exception:
                pass

            rp_message = (
                f"🎉 Félicitations {member.mention} ! Tu vas pouvoir accéder à "
                "l’école des sorciers **Poudlard**.\n\n"
                "➡️ Rends-toi dès maintenant au **Hall-d’Entrée** en cliquant sur le bouton ci-dessous."
            )

            view = EntryView(
                guild.id,
                self.channel_ids["HALL"],
                self.channel_ids["GRANDE_SALLE"],
                origin_message=None
            )

            try:
                sent_msg = await message.channel.send(rp_message, view=view)
                # l'origine est le message de félicitations (pour pouvoir le supprimer après)
                view.origin_message = sent_msg
                await sent_msg.edit(view=view)
                self.bot.welcome_messages[member.id] = sent_msg
                log.info(f"[Reglement] message de bienvenue envoyé pour user {member.id}")
            except Exception as e:
                log.exception(f"[Reglement] Impossible d'envoyer le message de félicitations: {e}")
                self.bot.welcome_messages.pop(member.id, None)
                return

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


# Fonction setup obligatoire pour charger le cog
async def setup(bot: commands.Bot):
    await bot.add_cog(Reglement(bot))
