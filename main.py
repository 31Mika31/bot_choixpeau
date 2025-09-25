# main.py
import os
import json
import threading
import logging
from flask import Flask
import discord
from discord.ext import commands

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("choixpeau")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Charge config.json si présent (sinon on continue — utiliser ENV VARS)
config = {}
config_path = os.path.join(BASE_DIR, "config.json")
if os.path.exists(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

# Token : priorité à la variable d'environnement (Render)
TOKEN = os.getenv("DISCORD_TOKEN") or config.get("TOKEN")
PREFIX = os.getenv("BOT_PREFIX") or config.get("PREFIX", "!")

if not TOKEN:
    raise SystemExit("❌ DISCORD_TOKEN not found in environment or config.json")

# Simple Flask keep-alive (Render)
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot Choixpeau is running!"

def run_flask():
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_flask, daemon=True).start()

# Intents (message_content nécessaire pour lire "lumos")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)
# expose la config au reste du bot
bot.config = config
# dictionnaire partagé (welcome messages, etc.)
bot.welcome_messages = {}

@bot.event
async def on_ready():
    log.info(f"Bot connecté : {bot.user} (guilds: {len(bot.guilds)})")
    log.info("Cogs chargés : " + ", ".join(bot.extensions.keys()))

# Charge les cogs et logue proprement les erreurs
extensions = ["cogs.quiz", "cogs.reglement", "cogs.views"]
for ext in extensions:
    try:
        bot.load_extension(ext)
        log.info(f"✅ Extension chargée : {ext}")
    except Exception as e:
        log.exception(f"❌ Échec chargement extension {ext} : {e}")

bot.run(TOKEN)
