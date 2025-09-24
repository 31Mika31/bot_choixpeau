import discord
from discord.ext import commands
from .views import AccederGrandeSalle

class ReglementCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.welcome_messages = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.channel.name == "règlement":
            content = message.content.strip().lower()
            member = message.author
            guild = message.guild

            if content == "lumos":
                try:
                    await message.delete()
                except:
                    pass

                role_new = discord.utils.get(guild.roles, name="Nouvel arrivant")
                if role_new in member.roles:
                    try:
                        await member.remove_roles(role_new)
                    except:
                        pass

                role_eleve = discord.utils.get(guild.roles, name="Élève")
                if role_eleve and role_eleve not in member.roles:
                    try:
                        await member.add_roles(role_eleve)
                    except:
                        pass

                try:
                    await message.channel.send(f"✨ Bravo {member.mention}, tu as validé le règlement !", delete_after=30)
                except:
                    pass

                hall = discord.utils.get(guild.text_channels, name="halle-d-entrée")
                if hall:
                    try:
                        await hall.send(
                            content=f"👋 Bienvenue {member.mention} ! Avance vers la Grande Salle.",
                            view=AccederGrandeSalle(member, self.welcome_messages)
                        )
                    except:
                        pass
            else:
                try:
                    await message.delete()
                except:
                    pass

def setup(bot):
    bot.add_cog(ReglementCog(bot))
