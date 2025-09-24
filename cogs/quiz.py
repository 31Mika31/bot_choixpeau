import discord, json, random, asyncio, os
from discord.ext import commands

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
QUESTIONS_PATH = os.path.join(BASE_DIR, "data", "questions.json")

def load_questions():
    try:
        with open(QUESTIONS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

class QuizCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_quizzes = {}

    @commands.command(name="quiz")
    async def start_quiz(self, ctx):
        if ctx.author.id in self.active_quizzes:
            await ctx.send("⚠️ Tu as déjà un quiz en cours.")
            return

        questions = load_questions()
        if not questions:
            await ctx.send("❌ Aucune question disponible.")
            return

        selected = random.sample(questions, min(10, len(questions)))
        self.active_quizzes[ctx.author.id] = selected

        scores = {}

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["1️⃣","2️⃣","3️⃣","4️⃣"]

        for q in selected:
            embed = discord.Embed(title=q["question"], color=discord.Color.purple())
            for i,opt in enumerate(q["options"],1):
                embed.add_field(name=f"{i}️⃣", value=opt["texte"], inline=False)
            msg = await ctx.send(embed=embed)
            for e in ["1️⃣","2️⃣","3️⃣","4️⃣"]:
                await msg.add_reaction(e)

            try:
                reaction, _ = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
                idx = ["1️⃣","2️⃣","3️⃣","4️⃣"].index(str(reaction.emoji))
                maison = q["options"][idx]["maison"]
                scores[maison] = scores.get(maison,0)+1
            except asyncio.TimeoutError:
                await ctx.send("⏰ Temps écoulé.")

        if not scores:
            await ctx.send("❌ Aucune maison déterminée.")
            return

        maison_finale = max(scores, key=scores.get)
        embed = discord.Embed(
            title="🎩 Le Choixpeau a parlé !",
            description=f"✨ {ctx.author.mention}, tu rejoins **{maison_finale}** !",
            color=discord.Color.purple()
        )
        await ctx.send(embed=embed, delete_after=30)

        role = discord.utils.get(ctx.guild.roles, name=maison_finale)
        if role:
            try:
                await ctx.author.add_roles(role)
            except Exception:
                pass

        del self.active_quizzes[ctx.author.id]

    @commands.command(name="stopquiz")
    async def stop_quiz(self, ctx):
        if ctx.author.id in self.active_quizzes:
            del self.active_quizzes[ctx.author.id]
            await ctx.send("🛑 Quiz interrompu.")
        else:
            await ctx.send("❌ Aucun quiz en cours.")

def setup(bot):
    bot.add_cog(QuizCog(bot))
