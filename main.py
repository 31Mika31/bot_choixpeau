import os, json, threading, logging
from flask import Flask
import discord
from discord.ext import commands

logging.basicConfig(level=logging.INFO)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load config.json si dispo, sinon vide
config_path = os.path.join(BASE_DIR, "config.json")
config = {}
if os.path.exists(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

# Token en priorité depuis Render (variable d'environnement)
TOKEN = os.getenv("DISCORD_TOKEN") or config.get("TOKEN")
PREFIX = config.get("PREFIX", "!")

if not TOKEN:
    raise SystemExit("❌ DISCORD TOKEN not found in config.json or environment.")


# Flask app for keep-alive
app = Flask(__name__)
@app.route("/")
def home():
    return "Bot Choixpeau is alive!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run_flask, daemon=True).start()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Load cogs dynamically
for ext in ["cogs.quiz", "cogs.reglement", "cogs.views"]:
    try:
        bot.load_extension(ext)
        logging.info(f"✅ Cog loaded: {ext}")
    except Exception as e:
        logging.exception(f"❌ Failed to load {ext}: {e}")

bot.run(TOKEN)
