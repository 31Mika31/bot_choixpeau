# cogs/quiz.py
import discord, json, random, asyncio, os
from discord.ext import commands

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
QUESTIONS_PATH = os.path.join(BASE_DIR, "data", "questions.json")

def load_questions():
    try:
        with open(QUESTIONS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("questions", [])
    except Exception:
        return []

class QuizCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_quizzes = {}  # {user_id: True}

        # Mapping maison -> rôle avec emoji
        self.roles_mapping = {
            "Gryffondor": "Gryffondor 🦁",
            "Poufsouffle": "Poufsouffle 🦡",
            "Serdaigle": "Serdaigle 🦅",
            "Serpentard": "Serpentard 🐍",
        }

    @commands.command(name="quiz")
    async def start_quiz(self, ctx):
        """Lancer le quiz de répartition"""
        if ctx.author.id in self.active_quizzes:
            await ctx.send("⚠️ Tu as déjà un quiz en cours.")
            return

        # Supprimer le message RP du Hall-d’Entrée si présent
        if ctx.author.id in getattr(self.bot, "welcome_messages", {}):
            try:
                msg = self.bot.welcome_messages.pop(ctx.author.id)
                await msg.delete()
            except Exception:
                pass

        questions = load_questions()
        if not questions:
            await ctx.send("❌ Aucune question disponible.")
            return

        selected = random.sample(questions, min(10, len(questions)))
        self.active_quizzes[ctx.author.id] = True
        scores = {}

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]

        for q in selected:
            if ctx.author.id not in self.active_quizzes:
                return

            embed = discord.Embed(title=q["question"], color=discord.Color.purple())
            for i, opt in enumerate(q["options"], 1):
                embed.add_field(name=f"{i}️⃣", value=opt["texte"], inline=False)

            msg = await ctx.send(embed=embed)
            for e in ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]:
                await msg.add_reaction(e)

            try:
                reaction, _ = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
                idx = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"].index(str(reaction.emoji))
                maison = q["options"][idx]["maison"]
                scores[maison] = scores.get(maison, 0) + 1
                await msg.delete()
            except asyncio.TimeoutError:
                await ctx.send("⏰ Temps écoulé.", delete_after=10)
                await msg.delete()

        if ctx.author.id not in self.active_quizzes:
            return

        if not scores:
            await ctx.send("❌ Aucune maison déterminée.")
            del self.active_quizzes[ctx.author.id]
            return

        maison_finale = max(scores, key=scores.get)

        # 🎨 Couleurs, emojis et blasons
        maisons_info = {
            "Gryffondor": {
                "couleur": discord.Color.red(),
                "emoji": "🦁",
                "image": "https://i.imgur.com/V0pXQBJ.png",
            },
            "Serdaigle": {
                "couleur": discord.Color.blue(),
                "emoji": "🦅",
                "image": "https://i.imgur.com/5D5H7ZT.png",
            },
            "Serpentard": {
                "couleur": discord.Color.green(),
                "emoji": "🐍",
                "image": "https://i.imgur.com/vp1ZTLh.png",
            },
            "Poufsouffle": {
                "couleur": discord.Color.gold(),
                "emoji": "🦡",
                "image": "https://i.imgur.com/Hq5p0Cg.png",
            },
        }

        info = maisons_info.get(maison_finale, {})
        couleur_embed = info.get("couleur", discord.Color.purple())
        emoji_maison = info.get("emoji", "👑")
        image_maison = info.get("image")

        # 1️⃣ Message suspense
        suspense_msg = await ctx.send(
            f"👑 *Le Choixpeau est posé sur la tête de {ctx.author.mention}...* 🤔\n"
            "« Hmm... voyons voir... »"
        )
        await asyncio.sleep(5)
        try:
            await suspense_msg.delete()
        except Exception:
            pass

        # 2️⃣ Révélation
        description = (
            f"👑 Le Choixpeau magique réfléchit un instant, puis s’exclame :\n\n"
            f"🎩 **« {maison_finale.upper()} ! »** {emoji_maison}\n\n"
            f"✨ {ctx.author.mention}, tu rejoins officiellement ta maison à Poudlard !"
        )

        embed = discord.Embed(
            title="🎩 Le Choixpeau a parlé !",
            description=description,
            color=couleur_embed,
        )

        if image_maison:
            embed.set_image(url=image_maison)

        await ctx.send(embed=embed, delete_after=60)

        # Attribution du rôle maison
        role_name = self.roles_mapping.get(maison_finale)
        role = discord.utils.get(ctx.guild.roles, name=role_name)

        if role:
            try:
                await ctx.author.add_roles(role)
                await ctx.send(f"✅ Rôle **{role.name}** attribué avec succès !", delete_after=10)
            except discord.Forbidden:
                await ctx.send("❌ Permissions insuffisantes pour attribuer le rôle.", delete_after=15)
            except Exception as e:
                await ctx.send(f"❌ Erreur lors de l’attribution du rôle : {e}", delete_after=15)
        else:
            await ctx.send(f"❌ Rôle introuvable pour la maison **{maison_finale}**.", delete_after=15)

        del self.active_quizzes[ctx.author.id]

    @commands.command(name="stopquiz")
    async def stop_quiz(self, ctx):
        """Arrêter un quiz en cours"""
        if ctx.author.id in self.active_quizzes:
            del self.active_quizzes[ctx.author.id]
            await ctx.send("🛑 Quiz interrompu.")
        else:
            await ctx.send("❌ Aucun quiz en cours.")

async def setup(bot):
    await bot.add_cog(QuizCog(bot))
