import discord
from discord.ext import commands

# IDs des salons (à remplacer si nécessaire)
HALL_ID = 1420336349613002774
GRANDE_SALLE_ID = 1420514190631768254

# === Vue pour aller au Hall-d’Entrée ===
class ButtonHall(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🚪 Avancer vers le Hall-d’Entrée", style=discord.ButtonStyle.primary)
    async def go_hall(self, interaction: discord.Interaction, button: discord.ui.Button):
        hall_channel = interaction.guild.get_channel(HALL_ID)

        # Supprime le message dans règlement
        await interaction.message.delete()

        # Envoie le message RP dans Hall-d’Entrée
        embed = discord.Embed(
            title="🗝️ Le Hall-d’Entrée",
            description=(
                "Les lourdes portes grincent et tu pénètres dans le **Hall-d’Entrée**...\n\n"
                "Au centre, des torches flottent dans les airs et une atmosphère solennelle t’entoure.\n\n"
                "Il est temps de rejoindre la **Grande Salle** où t’attend la cérémonie de répartition.\n\n"
                "➡️ Clique sur le bouton ci-dessous pour t’y rendre."
            ),
            color=discord.Color.dark_gold()
        )
        embed.set_thumbnail(url="https://i.ibb.co/W3W3b8f/hogwarts-crest.png")

        view = ButtonGrandeSalle()
        await hall_channel.send(content=f"{interaction.user.mention}", embed=embed, view=view)
        await interaction.response.defer()  # empêche l’erreur d’interaction déjà répondue


# === Vue pour aller à la Grande Salle ===
class ButtonGrandeSalle(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🕯️ Entrer dans la Grande Salle", style=discord.ButtonStyle.success)
    async def go_grande_salle(self, interaction: discord.Interaction, button: discord.ui.Button):
        grande_salle_channel = interaction.guild.get_channel(GRANDE_SALLE_ID)

        # Supprime le message dans Hall-d’Entrée
        await interaction.message.delete()

        # Envoie le message RP dans Grande Salle
        embed = discord.Embed(
            title="🕯️ La Grande Salle",
            description=(
                "Tu franchis les hautes portes et découvres la majestueuse **Grande Salle**...\n\n"
                "Les quatre longues tables s’étendent devant toi, décorées des blasons de "
                "chaque maison : 🦁 Gryffondor, 🐍 Serpentard, 🦅 Serdaigle et 🦡 Poufsouffle.\n\n"
                "Avance jusqu’au tabouret au centre de la salle... le Choixpeau va être posé sur ta tête.\n\n"
                "➡️ Quand tu es prêt(e), invoque le Choixpeau avec la commande **`!quiz`**."
            ),
            color=discord.Color.purple()
        )
        embed.set_thumbnail(url="https://i.ibb.co/W3W3b8f/hogwarts-crest.png")

        await grande_salle_channel.send(content=f"{interaction.user.mention}", embed=embed)
        await interaction.response.defer()
