import discord
from discord.ext import commands
from discord.ui import View, Button
import asyncio

HALL_ENTREE_ID = 1420336349613002774  # ID du salon Hall-d-Entrée

class Reglement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        # Vérifie que l’on est bien dans le salon règlement
        if message.channel.name.lower() != "règlement":
            return

        if message.content.lower() == "lumos":
            role = discord.utils.get(message.guild.roles, name="Élève")
            if role:
                await message.author.add_roles(role)

            # On construit un message RP immersif
            embed = discord.Embed(
                title="📜 Bienvenue à Poudlard !",
                description=(
                    f"✨ {message.author.mention}, tu as récité la formule magique et validé le règlement.\n\n"
                    "Les lourdes portes du château s’ouvrent devant toi... "
                    "Tu peux désormais **faire officiellement ton entrée à Poudlard**.\n\n"
                    "➡️ Avance jusqu’au **Hall-d-Entrée** pour te préparer à la Cérémonie de Répartition."
                ),
                color=discord.Color.gold()
            )

            view = View(timeout=None)

            button = Button(
                style=discord.ButtonStyle.primary,
                label="🚪 Avancer jusqu’au Hall-d-Entrée",
                custom_id=f"hall_entree_{message.author.id}"
            )

            async def button_callback(interaction: discord.Interaction):
                if interaction.user.id != message.author.id:
                    await interaction.response.send_message(
                        "❌ Seul l’élève concerné peut utiliser ce bouton.", ephemeral=True
                    )
                    return

                hall = message.guild.get_channel(HALL_ENTREE_ID)
                if hall:
                    await interaction.response.send_message(
                        f"🚪 Les lourdes portes grincent et tu pénètres dans le **Hall-d-Entrée**...\n\n"
                        "Au centre, des torches flottent dans les airs et une lueur mystérieuse t’invite à "
                        "attendre patiemment la Cérémonie de Répartition.\n\n"
                        "Quand tu es prêt, invoque le Choixpeau en lançant `!quiz` 🎩",
                        ephemeral=True
                    )

                    # On supprime le message RP initial pour tout le monde
                    try:
                        await self.bot.welcome_messages[message.author.id].delete()
                    except Exception:
                        pass

            button.callback = button_callback
            view.add_item(button)

            sent = await message.channel.send(
                embed=embed,
                view=view
            )

            # On garde une trace du message pour pouvoir le supprimer plus tard
            self.bot.welcome_messages[message.author.id] = sent

            # Suppression automatique au bout de 15 min si rien n’est fait
            async def delete_later():
                await asyncio.sleep(900)  # 15 minutes
                if message.author.id in self.bot.welcome_messages:
                    try:
                        msg = self.bot.welcome_messages.pop(message.author.id)
                        await msg.delete()
                        await message.author.send(
                            "🌫️ Les bougies du règlement vacillent et s’éteignent... "
                            "Ton opportunité de rejoindre Poudlard s’est dissipée. "
                            "Tu devras à nouveau réciter la formule **Lumos** pour entrer."
                        )
                    except Exception:
                        pass

            asyncio.create_task(delete_later())

async def setup(bot):
    await bot.add_cog(Reglement(bot))
