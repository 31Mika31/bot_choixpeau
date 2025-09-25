# cogs/reglement.py
import discord
from discord.ext import commands
from discord.ui import View, Button
import asyncio
import logging

log = logging.getLogger("choixpeau")

# IDs de salons (à adapter avec tes vrais IDs)
HALL_ID = 1420336349613002774         # 🗝️｜𝐇αᥣᥣ-ᑯ-𝐄𐓣𝗍𝗋é𝖾
GRANDE_SALLE_ID = 1420336349613002775 # 🏰｜Grande-Salle (remplace par ton vrai ID)

class EntryView(View):
    def __init__(self, guild_id: int, hall_id: int, grande_salle_id: int):
        super().__init__(timeout=None)
        self.add_item(Button(label="🔑 Hall-d'Entrée", url=f"https://discord.com/channels/{guild_id}/{hall_id}"))
        self.add_item(Button(label="🏰 Grande-Salle", url=f"https://discord.com/channels/{guild_id}/{grande_salle_id}"))

class Reglement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
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

            # Envoie le message RP dans le Hall-d’Entrée
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

                # Suppression automatique après 15 min si rien n’est lancé
                async def delete_later():
                    await asyncio.sleep(900)
                    if member.id in self.bot.welcome_messages:
                        try:
                            await msg.delete()
                            self.bot.welcome_messages.pop(member.id, None)
                        except Exception:
                            pass
                asyncio.create_task(delete_later())

        # 🎩 Quand l’élève arrive dans la Grande-Salle → message RP spécial
        if message.channel.id == GRANDE_SALLE_ID and not message.author.bot:
            guild = message.guild
            member = message.author

            # Vérifie si ce membre n’a pas déjà eu son message de répartition
            if member.id not in self.bot.welcome_messages:
                grande_salle_msg = (
                    f"🏰 {member.mention} pénètre dans la majestueuse **Grande-Salle**...\n\n"
                    "Les quatre longues tables brillent de mille chandelles flottantes, "
                    "et les blasons des Maisons décorent les murs ancestraux.\n\n"
                    "Une voix profonde s’élève du Choixpeau magique posé sur son tabouret :\n"
                    "« Approche, jeune sorcier... Il est temps de découvrir ta Maison. "
                    "Invoque-moi avec la commande `!quiz`. »"
                )
                msg = await message.channel.send(grande_salle_msg)
                self.bot.welcome_messages[member.id] = msg

                # Le message disparaît dès que l’élève lance !quiz
                async def wait_for_quiz():
                    try:
                        await self.bot.wait_for(
                            "message",
                            timeout=900,  # 15 minutes max
                            check=lambda m: m.author == member and m.content.strip().lower().startswith("!quiz")
                        )
                        await msg.delete()
                        self.bot.welcome_messages.pop(member.id, None)
                    except asyncio.TimeoutError:
                        try:
                            await msg.delete()
                            self.bot.welcome_messages.pop(member.id, None)
                        except Exception:
                            pass
                asyncio.create_task(wait_for_quiz())

async def setup(bot):
    await bot.add_cog(Reglement(bot))
