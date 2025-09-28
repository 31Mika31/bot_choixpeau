# cogs/reglement.py
import discord
from discord.ext import commands
import asyncio
import os


class GrandeSalleView(discord.ui.View):
    def __init__(self, hall_message: discord.Message, grande_salle_id: int):
        super().__init__(timeout=None)
        self.hall_message = hall_message
        self.grande_salle_id = grande_salle_id

    @discord.ui.button(
        label="🍽️ Aller à la Grande-Salle",
        style=discord.ButtonStyle.success,
        custom_id="go_grande_salle"
    )
    async def go_grande_salle(self, interaction: discord.Interaction, button: discord.ui.Button):
        grande_salle = interaction.guild.get_channel(self.grande_salle_id)
        if not grande_salle:
            await interaction.response.send_message("❌ Salon Grande-Salle introuvable.", ephemeral=True)
            return

        try:
            await interaction.response.defer(ephemeral=True)
        except Exception:
            pass

        # Message RP dans la Grande-Salle
        try:
            await grande_salle.send(
                f"🍽️ {interaction.user.mention} pousse les lourdes portes et entre dans la **Grande-Salle**.\n\n"
                "Les quatre longues tables s’illuminent de mille chandelles flottantes. "
                "Les regards des élèves se tournent vers toi tandis que le Choixpeau magique attend d’être invoqué...\n\n"
                "➡️ Lance la commande `!quiz` pour commencer la Cérémonie de Répartition."
            )
        except Exception:
            await interaction.followup.send("❌ Impossible d'envoyer le message dans la Grande-Salle.", ephemeral=True)
            return

        try:
            # Supprimer le message du Hall (celui avec le bouton)
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

        try:
            await interaction.response.defer(ephemeral=True)
        except Exception:
            pass

        try:
            hall_msg = await hall_channel.send(
                f"🪄 Les lourdes portes grincent et {interaction.user.mention} franchit enfin le **Hall-d’Entrée**...\n\n"
                "De hautes torches magiques illuminent les pierres froides, projetant des ombres dansantes.\n\n"
                "Une voix solennelle résonne dans le silence :\n"
                "« Tu as prêté serment en validant le règlement… "
                "Tu peux désormais faire officiellement ton entrée à **Poudlard** ! »\n\n"
                "➡️ **Rends-toi maintenant dans la Grande-Salle** pour la Cérémonie de Répartition "
                "et invoque le Choixpeau magique en lançant la commande `!quiz`.",
                view=GrandeSalleView(None, self.grande_salle_id)  # view corrigée après envoi
            )
            # Fixer la référence pour que la view sache supprimer ce message
            hall_msg.edit(view=GrandeSalleView(hall_msg, self.grande_salle_id))
        except Exception:
            await interaction.followup.send("❌ Impossible d'envoyer le message dans le Hall.", ephemeral=True)
            return

        try:
            await interaction.followup.send("✨ Tu as franchi les portes et pénétré dans le Hall-d’Entrée !", ephemeral=True)
        except Exception:
            pass

        interaction.client.welcome_messages[interaction.user.id] = hall_msg

        if self.origin_message:
            try:
                await self.origin_message.delete()
            except Exception:
                pass


class Reglement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.welcome_messages = getattr(self.bot, "welcome_messages", {})

        self.channel_ids = {
            "REGLEMENT": int(os.getenv("CHANNEL_REGLEMENT", 0)),
            "HALL": int(os.getenv("CHANNEL_HALL", 0)),
            "GRANDE_SALLE": int(os.getenv("CHANNEL_GRANDE_SALLE", 0)),  # ✅ corrigé ici
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

            if member.id in self.bot.welcome_messages:
                return
            self.bot.welcome_messages[member.id] = "pending"

            role_eleve = discord.utils.get(guild.roles, name=self.roles.get("ELEVE"))
            if role_eleve and role_eleve not in member.roles:
                try:
                    await member.add_roles(role_eleve)
                except Exception:
                    pass

            role_nouvel = discord.utils.get(guild.roles, name=self.roles.get("NOUVEL"))
            if role_nouvel and role_nouvel in member.roles:
                try:
                    await member.remove_roles(role_nouvel)
                except Exception:
                    pass

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
                view.origin_message = sent_msg
                await sent_msg.edit(view=view)
                self.bot.welcome_messages[member.id] = sent_msg
            except Exception:
                self.bot.welcome_messages.pop(member.id, None)
                return

            async def delete_when_expired():
                await asyncio.sleep(900)
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
