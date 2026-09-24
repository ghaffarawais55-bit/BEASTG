# economy.py
import datetime
import discord
from discord.ext import commands
from config import get_profile, GEMS, WEAPONS, OWNER_ID

class EconomyEngine(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.daily_cooldowns = {}  # Tracks daily check-ins: {user_id: datetime}

    # --- DAILY CHECK-IN REWARDS ---
    @commands.command(name="daily")
    async def daily_claim(self, ctx):
        """Claims 25,000 sycoizz every 24 hours."""
        user_id = ctx.author.id
        now = datetime.datetime.utcnow()
        reward = 25000

        if user_id in self.daily_cooldowns:
            last_claim = self.daily_cooldowns[user_id]
            if now - last_claim < datetime.timedelta(hours=24):
                time_left = datetime.timedelta(hours=24) - (now - last_claim)
                hours, remainder = divmod(int(time_left.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                return await ctx.send(f"⏱️ **OwO Daily Cooldown!** You can claim again in `{hours}h {minutes}m {seconds}s`.")

        prof = get_profile(user_id)
        prof["sycoizz"] += reward
        self.daily_cooldowns[user_id] = now
        await ctx.send(f"📆 🎉 **DAILY REWARD CLAIMED!** {ctx.author.mention}, you received `+{reward:,}` sycoizz!\n💳 Wallet Total: `{prof['sycoizz']:,}`")

    # --- OWNER-ONLY ADMIN CONSOLE ---
    @commands.command(name="givecash")
    async def give_cash(self, ctx, target: discord.Member, amount: int):
        if ctx.author.id != OWNER_ID:
            return await ctx.send("❌ Access Denied: Restricted to bot owner.")
        if amount <= 0:
            return await ctx.send("❌ Amount value must be positive.")
        prof = get_profile(target.id)
        prof["sycoizz"] += amount
        await ctx.send(f"👑 **[ADMIN]** Added `{amount:,}` sycoizz into {target.mention}'s account ledger.")

    # --- STANDARD BALANCES & WIRE TRANSFERS ---
    @commands.command(name="cash", aliases=["money", "bal"])
    async def cash_cmd(self, ctx, target: discord.Member = None):
        user = target or ctx.author
        prof = get_profile(user.id)
        await ctx.send(f"💳 {user.mention}'s Balance: `{prof['sycoizz']:,}` sycoizz.")

    @commands.command(name="give", aliases=["send", "pay"])
    async def give_cmd(self, ctx, target: discord.Member, amount: int):
        if ctx.author.id == target.id:
            return await ctx.send("❌ You cannot send currency to yourself.")
        if amount <= 0:
            return await ctx.send("❌ Value must be above 0.")
        s_prof = get_profile(ctx.author.id)
        if s_prof["sycoizz"] < amount:
            return await ctx.send("❌ Transaction declined: Insufficient funds.")
        r_prof = get_profile(target.id)
        s_prof["sycoizz"] -= amount
        r_prof["sycoizz"] += amount
        await ctx.send(f"✅ Securely sent `{amount:,}` sycoizz to {target.mention}.")

    # --- ADVENTURE SUMMARY DISPLAY ---
    @commands.command(name="see", aliases=["profile", "inv", "bag"])
    async def see_cmd(self, ctx, target: discord.Member = None):
        user = target or ctx.author
        prof = get_profile(user.id)
        embed = discord.Embed(title=f"🎒 {user.name}'s Profile Ledger", color=discord.Color.blue())
        embed.add_field(name="💰 Cash Reserves", value=f"`{prof['sycoizz']:,}` sycoizz", inline=True)
        gems = [GEMS[gid]["name"] for gid in prof["gems"]] if prof["gems"] else ["None"]
        embed.add_field(name="💎 Socketed Talismans", value=", ".join(gems), inline=True)
        pets = []
        for p in prof["pokemon"]:
            w = f" (⚔️ {WEAPONS[p['equipped_weapon']]['name']})" if p.get("equipped_weapon") else ""
            pets.append(f"{p['emoji']} **{p['name']}** | HP: `{p['hp']}`{w}")
        embed.add_field(name="🐾 Pokémon", value="\n".join(pets) if pets else "None", inline=False)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(EconomyEngine(bot))
  
