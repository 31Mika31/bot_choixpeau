# main.py
import os
import threading
import logging
from flask import Flask
import discord
from discord.ext import commands

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("choixpeau")

# -----------------------------------------------------------
# Token et préfixe via variables d'environnement
# -----------------------------------------------------------
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("BOT_PREFIX", "!")

if not TOKEN:
    raise SystemExit("❌ DISCORD_TOKEN non trouvé dans les variables d'environnement")

# -----------------------------------------------------------
# Flask Keep-Alive (Render)
# -----------------------------------------------------------
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot Choixpeau is running!"

def run_flask():
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_flask, daemon=True).start()

# -----------------------------------------------------------
# Discord Bot
# -----------------------------------------------------------
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)
bot.welcome_messages = {}

# -----------------------------------------------------------
# Suppression automatique des commandes utilisateur
# -----------------------------------------------------------
@bot.listen("on_message")
async def delete_command_messages(message: discord.Message):
    """Supprime les messages des commandes (préfixées) après traitement."""
    if message.author.bot:
        return
    if not message.content.startswith(PREFIX):
        return

    try:
        await message.delete()
        log.debug(f"Message de commande supprimé : {message.content}")
    except Exception:
        pass

# -----------------------------------------------------------
# Commande simple de test
# -----------------------------------------------------------
@bot.command()
async def ping(ctx):
    await ctx.send("pong 🏓", delete_after=10)

# -----------------------------------------------------------
# Chargement asynchrone des cogs
# -----------------------------------------------------------
async def load_extensions():
    extensions = ["cogs.quiz", "cogs.reglement"]
    for ext in extensions:
        if ext in bot.extensions:
            log.warning(f"⚠️ Extension déjà chargée ignorée : {ext}")
            continue
        try:
            await bot.load_extension(ext)
            log.info(f"✅ Extension chargée : {ext}")
        except Exception as e:
            log.exception(f"❌ Échec chargement extension {ext} : {e}")

@bot.event
async def on_ready():
    log.info(f"Bot connecté : {bot.user} (guilds: {len(bot.guilds)})")
    await load_extensions()
    log.info("Cogs actifs : " + ", ".join(bot.cogs.keys()))
    log.info("Extensions actives : " + ", ".join(bot.extensions.keys()))

# -----------------------------------------------------------
# Lancer le bot
# -----------------------------------------------------------
bot.run(TOKEN)
