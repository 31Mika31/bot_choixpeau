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
        log.info(f"[DEBUG] GrandeSalleView initialisée avec grande_salle_id={grande_salle_id}")

    @discord.ui.button(
        label="🍽️ Aller à la Grande-Salle",
        style=discord.ButtonStyle.success,
        custom_id="go_grande_salle"
    )
    async def go_grande_salle(self, interaction: discord.Interaction, button: discord.ui.Button):
        log.info(f"[DEBUG] Bouton vert cliqué par {interaction.user} (ID={interaction.user.id})")
        log.info(f"[DEBUG] ID Grande-Salle utilisé : {self.grande_salle_id}")

        grande_salle = interaction.guild.get_channel(self.grande_salle_id)
        log.info(f"[DEBUG] Résultat get_channel : {grande_salle}")

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
            interaction.client.welcome_messages[interaction.user.id] = grande_msg
        except Exception as e:
            log.exception(f"[DEBUG] Erreur lors de l'envoi du message dans Grande-Salle: {e}")
            await interaction.followup.send("❌ Impossible d'envoyer le message dans la Grande-Salle.", ephemeral=True)
            return

        try:
            if self.hall_message:
                await self.hall_message.delete()
        except Exception:
            pass

        try:
            await interaction.followup.send("✨ Tu es maintenant dans la Grande-Salle !", ephemeral=True)
        except Exception:
            pass
