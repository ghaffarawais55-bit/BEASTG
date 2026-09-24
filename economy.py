# economy.py
import datetime
import discord
from discord.ext import commands
from config import get_profile, create_starter_account, GEMS, WEAPONS, OWNER_ID, USER_DATA

class EconomyEngine(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.daily_cooldowns = {}

    # --- S TOP LEADERBOARD MODULE ---
    @commands.command(name="top", aliases=["leaderboard", "lb"])
    async def global_leaderboard(self, ctx):
        """Displays the richest players on the server. Usage: s top"""
        if not USER_DATA:
            return await ctx.send("❌ No active database accounts found. Type `s start` to break the ice!")

        # Sort all memory profiles dynamically descending by balance size
        sorted_profiles = sorted(USER_DATA.items(), key=lambda item: item[1]["sycoizz"], reverse=True)
        
        embed = discord.Embed(
            title="🏆 GLOBAL RICHEST PLAYER LEADERBOARD Scoreboard",
            description="*The wealthiest players tracking across the server network.*",
            color=discord.Color.gold()
        )

        leaderboard_lines = []
        for rank, (user_id, data) in enumerate(sorted_profiles[:10], start=1):
            # Fetch user account nickname tags securely from cache lines
            member = ctx.guild.get_member(user_id)
            name = member.name if member else f"User ID: {user_id}"
            
            # Format decorative medals for high tiers
            medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"`#{rank}`"
            leaderboard_lines.append(f"{medal} **{name}** — `{data['sycoizz']:,}` sycoizz")

        embed.add_field(name="Top 10 Global Capital Balances", value="\n".join(leaderboard_lines), inline=False)
        embed.set_footer(text=f"Queried by {ctx.author.name}")
        await ctx.send(embed=embed)

    # --- S START PROFILE REQUISITIONING ---
    @commands.command(name="start")
    async def start_cmd(self, ctx, choice: str = None):
        if get_profile(ctx.author.id) is not None:
            return await ctx.send(f"⚠️ {ctx.author.mention}, your adventure matrix log has already been generated! Run `s see`.")

        starters = {
            "charmander": {"name": "Charmander", "emoji": "<a:scharmander:10000002>", "hp": 95, "attack": "Ember", "equipped_weapon": None},
            "bulbasaur": {"name": "Bulbasaur", "emoji": "<a:sbulbasaur:10000001>", "hp": 100, "attack": "Vine Whip", "equipped_weapon": None},
            "squirtle": {"name": "Squirtle", "emoji": "<a:ssquirtle:10000003>", "hp": 105, "attack": "Water Gun", "equipped_weapon": None}
        }

        if not choice or choice.lower() not in starters:
            embed = discord.Embed(title="🎒 SYCOIZZ RPG PROFILE INDUCTION SECTOR", description="Choose a primary Gen 1 starter pet blueprint to structure your profile bank ledger records!", color=discord.Color.gold())
            embed.add_field(name="Available Choices", value="👉 `s start bulbasaur` 🍃\n👉 `s start charmander` 🔥\n👉 `s start squirtle` 💧", inline=False)
            return await ctx.send(embed=embed)

        chosen = starters[choice.lower()]
        create_starter_account(ctx.author.id, chosen)
        await ctx.send(f"🎉 **ACCOUNT OPENED!** {ctx.author.mention}, you selected {chosen['emoji']} **{chosen['name']}**! Allocated `+50,000` starting sycoizz cash rewards to your balance ledger! Run `s see` to check your bag.")

    # --- DAILY COOLDOWN REWARDS ---
    @commands.command(name="daily")
    async def daily_claim(self, ctx):
        prof = get_profile(ctx.author.id)
        if not prof: return await ctx.send("❌ Profile log blank. Run `s start` first.")
        
        user_id = ctx.author.id
        now = datetime.datetime.utcnow()
        if user_id in self.daily_cooldowns and now - self.daily_cooldowns[user_id] < datetime.timedelta(hours=24):
            time_left = datetime.timedelta(hours=24) - (now - self.daily_cooldowns[user_id])
            hours, rem = divmod(int(time_left.total_seconds()), 3600)
            minutes, _ = divmod(rem, 60)
            return await ctx.send(f"⏱️ **Daily Cooldown Active!** Re-opens in `{hours}h {minutes}m`.")

        prof["sycoizz"] += 25000
        self.daily_cooldowns[user_id] = now
        await ctx.send(f"📆 🎉 **DAILY INJECTION SUCCESSFUL!** Gained `+25,000` sycoizz for {ctx.author.mention}!")

    @commands.command(name="cash", aliases=["money", "bal"])
    async def cash_cmd(self, ctx, target: discord.Member = None):
        user = target or ctx.author
        prof = get_profile(user.id)
        if not prof: return await ctx.send("❌ Profile uninitialized. Run `s start`.")
        await ctx.send(f"💳 {user.mention}'s Balance: `{prof['sycoizz']:,}` sycoizz.")

    @commands.command(name="give", aliases=["send", "pay"])
    async def give_cmd(self, ctx, target: discord.Member, amount: int):
        s_prof = get_profile(ctx.author.id)
        r_prof = get_profile(target.id)
        if not s_prof or not r_prof: return await ctx.send("❌ Both participants must maintain active accounts via `s start`.")
        if amount <= 0 or s_prof["sycoizz"] < amount: return await ctx.send("❌ Remittance authorization threshold failed.")
        
        s_prof["sycoizz"] -= amount
        r_prof["sycoizz"] += amount
        await ctx.send(f"✅ Secure wire completed! Sent `{amount:,}` sycoizz to {target.mention}.")

    @commands.command(name="see", aliases=["profile", "inv", "bag"])
    async def see_cmd(self, ctx, target: discord.Member = None):
        user = target or ctx.author
        prof = get_profile(user.id)
        if not prof: return await ctx.send("❌ Profile ledger entry missing. Use `s start`.")
        
        embed = discord.Embed(title=f"🎒 {user.name}'s Adventure Profile Ledger", color=discord.Color.blue())
        embed.add_field(name="💰 Cash Reserves", value=f"`{prof['sycoizz']:,}` sycoizz", inline=True)
        gems = [GEMS[g]["name"] for g in prof["gems"]] if prof["gems"] else ["None"]
        embed.add_field(name="💎 Talismans", value=", ".join(gems), inline=True)
        
        pets = []
        for p in prof["pokemon"]:
            w = f" (⚔️ {WEAPONS[p['equipped_weapon']]['name']})" if p.get("equipped_weapon") else ""
            pets.append(f"{p['emoji']} **{p['name']}** | HP: `{p['hp']}`{w}")
        embed.add_field(name="🐾 Pokémon Companion Lineup", value="\n".join(pets), inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="givecash")
    async def give_cash(self, ctx, target: discord.Member, amount: int):
        if ctx.author.id != OWNER_ID: return await ctx.send("❌ Security clearance verification failure.")
        prof = get_profile(target.id)
        if not prof: return await ctx.send("❌ Target account unregistered inside profile storage tracks.")
        prof["sycoizz"] += amount
        await ctx.send(f"👑 **[OWNER ADMIN EXCLUSIVE]** Infused `+{amount:,}` sycoizz capital assets directly into {target.mention}'s account.")

async def setup(bot):
    await bot.add_cog(EconomyEngine(bot))
      
