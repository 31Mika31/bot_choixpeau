# main.py
import os
import threading
import logging
from flask import Flask
import discord
from discord.ext import commands

# -----------------------------------------------------------
# Logs
# -----------------------------------------------------------
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("choixpeau")

# -----------------------------------------------------------
# Token et préfixe
# -----------------------------------------------------------
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("BOT_PREFIX", "!")

if not TOKEN:
    raise SystemExit("❌ DISCORD_TOKEN non trouvé dans les variables d'environnement")

# -----------------------------------------------------------
# Flask keep-alive (Render)
# -----------------------------------------------------------
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Bot Choixpeau is running on Render!"

def run_flask():
    port = int(os.getenv("PORT", 8080))
    log.info(f"🌍 Flask serveur lancé sur le port {port}")
    app.run(host="0.0.0.0", port=port)

# Lancer Flask en thread parallèle
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

@bot.command()
async def ping(ctx):
    await ctx.send("pong 🏓")

# -----------------------------------------------------------
# Chargement des cogs
# -----------------------------------------------------------
async def load_extensions():
    extensions = ["cogs.quiz", "cogs.reglement"]
    for ext in extensions:
        try:
            await bot.load_extension(ext)
            log.info(f"✅ Extension chargée : {ext}")
        except Exception as e:
            log.exception(f"❌ Échec chargement extension {ext} : {e}")

@bot.event
async def on_ready():
    log.info(f"🤖 Bot connecté : {bot.user} (guilds: {len(bot.guilds)})")
    await load_extensions()
    log.info("📦 Cogs chargés : " + ", ".join(bot.extensions.keys()))

# -----------------------------------------------------------
# Lancer le bot
# -----------------------------------------------------------
if __name__ == "__main__":
    log.info("🚀 Lancement du bot Choixpeau...")
    bot.run(TOKEN)
