import discord, asyncio

class AccederGrandeSalle(discord.ui.View):
    def __init__(self, member, welcome_dict):
        super().__init__(timeout=None)
        self.member = member
        self.welcome_dict = welcome_dict

    @discord.ui.button(label="Accéder à la Grande Salle", style=discord.ButtonStyle.primary, emoji="✨")
    async def acceder(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.member.id:
            await interaction.response.send_message("⚠️ Tu ne peux pas utiliser ce bouton.", ephemeral=True)
            return

        grande_salle = discord.utils.get(interaction.guild.text_channels, name="grande-salle")
        if grande_salle:
            embed = discord.Embed(
                title="⚜️ Les portes de la Grande Salle s’ouvrent ⚜️",
                description=(
                    f"✨ {self.member.mention}, tu fais ton entrée sous les chandelles flottantes "
                    f"et les bannières des quatre maisons.\n\n"
                    f"🎩 Avance vers l’estrade et invoque le Choixpeau avec la commande `!quiz` "
                    f"pour commencer ta cérémonie de répartition."
                ),
                color=discord.Color.purple()
            )
            embed.set_footer(text="Poudlard • La magie opère... ✨")

            rp_msg = await grande_salle.send(embed=embed)
            self.welcome_dict[self.member.id] = rp_msg.id

            try:
                await interaction.message.delete()
            except Exception:
                pass

            await interaction.response.send_message("✅ Tu es entré dans la Grande Salle !", ephemeral=True)

            await asyncio.sleep(60)
            try:
                msg_check = await grande_salle.fetch_message(rp_msg.id)
                await msg_check.delete()
            except Exception:
                pass

def setup(bot):
    pass
