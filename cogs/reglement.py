import discord
from discord.ext import commands

HALL_CHANNEL_ID = 1420336349613002774  # 🗝️｜𝐇αᥣᥣ-ᑯ-𝐄𐓣𝗍𝗋é𝖾

class GoHallButton(discord.ui.View):
    def __init__(self, author: discord.Member):
        super().__init__(timeout=None)
        self.author = author

    @discord.ui.button(label="🚪 Pousser les portes de la Grande Salle", style=discord.ButtonStyle.primary, emoji="🕯️")
    async def go_hall(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Vérifie que seul l'élève concerné peut cliquer
        if interaction.user.id != self.author.id:
            await interaction.response.send_message(
                "❌ Ces portes ne s’ouvrent pas pour toi... Patience, jeune sorcier.",
                ephemeral=True
            )
            return

        hall = interaction.guild.get_channel(HALL_CHANNEL_ID)
        if hall:
            await interaction.response.send_message(
                f"🕯️ Tandis que les bougies flottantes s’élèvent au-dessus de toi, "
                f"les immenses portes de chêne s’ouvrent lentement...\n\n"
                f"➡️ Avance dans {hall.mention}, la **Grande Salle**, où le Choixpeau magique 🎩 "
                f"t’attend pour sceller ton destin.",
                ephemeral=True
            )

        # Efface le message public pour garder la magie intacte
        await interaction.message.delete()


class ReglementCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        # Si l'élève écrit "lumos" dans le salon règlement
        if message.channel.name == "règlement" and message.content.lower().strip() == "lumos":
            guild = message.guild
            member = message.author

            embed = discord.Embed(
                title="📜 Serment Solennel Accompli",
                description=(
                    f"✨ {member.mention}, les runes gravées sur le parchemin se sont illuminées d’une lueur dorée.\n\n"
                    "🕯️ Des centaines de bougies flottantes s’élèvent dans les airs, éclairant ton chemin vers l’inconnu...\n\n"
                    "🏰 Devant toi, le majestueux château de **Poudlard** t’accueille enfin.\n\n"
                    "🎩 Dans la **Grande Salle**, le Choixpeau magique t’attend pour révéler à quelle maison "
                    "tu appartiens.\n\n"
                    "➡️ Avance avec courage, jeune sorcier : pousse les portes et découvre ta destinée."
                ),
                color=discord.Color.gold()
            )

            if guild.icon:
                embed.set_thumbnail(url=guild.icon.url)

            await message.channel.send(embed=embed, view=GoHallButton(member))


async def setup(bot):
    await bot.add_cog(ReglementCog(bot))
