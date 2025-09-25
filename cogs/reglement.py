# cogs/reglement.py
import logging
import discord
from discord.ext import commands

log = logging.getLogger("choixpeau.reglement")

class Reglement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        cfg = getattr(bot, "config", {}) or {}

        # Valeurs par défaut (si config absente)
        channels = cfg.get("channel_ids", {}) if isinstance(cfg.get("channel_ids", {}), dict) else {}
        roles = cfg.get("roles", {}) if isinstance(cfg.get("roles", {}), dict) else {}

        self.reglement_name = channels.get("reglement", "règlement")
        self.halle_name = channels.get("halle", "halle-d-entrée")
        self.grande_salle_name = channels.get("grande_salle", "grande-salle")

        self.rolename_nouvel = roles.get("nouvel", "Nouvel arrivant")
        self.rolename_eleve = roles.get("eleve", "Élève")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # ignore bots and DMs
        if message.author.bot or not message.guild:
            return

        # Only react in the règlement channel
        if message.channel.name != self.reglement_name:
            # let commands run in other channels
            await self.bot.process_commands(message)
            return

        content = message.content.strip().lower()
        member = message.author
        guild = message.guild

        # correct keyword
        if content == "lumos":
            # delete the trigger message if possible
            try:
                await message.delete()
            except Exception:
                pass

            # remove "Nouvel arrivant" if present
            try:
                role_nouvel = discord.utils.get(guild.roles, name=self.rolename_nouvel)
                if role_nouvel and role_nouvel in member.roles:
                    await member.remove_roles(role_nouvel)
            except Exception:
                log.exception("Impossible de retirer 'Nouvel arrivant'")

            # add "Élève"
            try:
                role_eleve = discord.utils.get(guild.roles, name=self.rolename_eleve)
                if role_eleve and role_eleve not in member.roles:
                    await member.add_roles(role_eleve)
            except Exception:
                log.exception("Impossible d'ajouter le rôle 'Élève'")

            # feedback ephemeral-like (message supprimé au bout de 30s)
            try:
                await message.channel.send(f"✨ Bravo {member.mention}, tu as validé le règlement !", delete_after=30)
            except Exception:
                pass

            # send welcome message in the hall with the button view (if views available)
            try:
                hall = discord.utils.get(guild.text_channels, name=self.halle_name)
                if hall:
                    try:
                        # import the View class from cogs.views (sa présence est optionnelle)
                        from cogs.views import AccederGrandeSalle
                        view = AccederGrandeSalle(member)
                    except Exception:
                        view = None

                    sent = await hall.send(
                        content=(
                            f"👋 Bienvenue à Poudlard !\n"
                            f"{member.mention}, te voici dans le Hall d’entrée.\n\n"
                            f"Avance vers la Grande Salle pour participer à la cérémonie de répartition."
                        ),
                        view=view
                    )
                    # store message id so quiz can remove it later
                    self.bot.welcome_messages[member.id] = sent.id
            except Exception:
                log.exception("Impossible d'envoyer le message dans le hall")

        else:
            # delete any other message in the règlement channel
            try:
                await message.delete()
            except Exception:
                pass

        # ensure commands still work
        await self.bot.process_commands(message)

def setup(bot):
    bot.add_cog(Reglement(bot))
