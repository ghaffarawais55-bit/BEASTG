# gambling.py
import random
import asyncio
import discord
from discord.ext import commands
from config import get_profile, GEMS, edit_msg_safe

class GamblingEngine(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lottery_pool = 1000000
        self.lottery_tickets = {}

    # --- ANIME COINFLIP ---
    @commands.command(name="cf", aliases=["flip"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def coin_flip_gamble(self, ctx, bet: str):
        prof = get_profile(ctx.author.id)
        bal = prof["sycoizz"]
        if bet.lower() == "all":
            amt = bal
        else:
            try: amt = int(bet)
            except ValueError: return await ctx.send("❌ Enter a specific number or type `all`.")
        if amt <= 0: return await ctx.send("❌ Must be greater than 0.")
        if bal < amt: return await ctx.send(f"❌ Insufficient funds. Balance: `{bal:,}`.")
        
        luck = 1.0
        for gid in prof["gems"]:
            if GEMS[gid]["boost"] > luck: luck = GEMS[gid]["boost"]

        frames = [
            "💨 **[ FLICK! ]** `🪙` 🚀 *[Thumb snaps!]*",
            "📈 **[ RISING ]** `🟡` ▲ *[Ascending]*",
            "✨ **[ APEX ]** `⚪⟲ SPINNING ⟳` ⚡",
            "📉 **[ FALLING ]** `🟡` ▼ *[Falling]*",
            "🖐️ **[ CATCH! ]** `🪙🫲` 💥 *[Caught!]*"
        ]
        msg = await ctx.send(frames)
        for f in frames[1:]:
            await asyncio.sleep(0.35)
            await edit_msg_safe(msg, f)
            
        await asyncio.sleep(0.4)
        if random.random() <= (0.50 * luck):
            prof["sycoizz"] += amt
            await edit_msg_safe(msg, f"🎉 **HEADS! YOU WIN!** Gained `+{amt:,}` sycoizz!\n💳 Total: `{prof['sycoizz']:,}`")
        else:
            prof["sycoizz"] -= amt
            await edit_msg_safe(msg, f"💀 **TAILS! HOUSE WINS!** Lost `-{amt:,}` sycoizz.\n💳 Total: `{prof['sycoizz']:,}`")

    # --- MATCHING SLOTS ---
    @commands.command(name="slots", aliases=["s", "slot"])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def slots_gamble(self, ctx, bet: int):
        prof = get_profile(ctx.author.id)
        if bet <= 0 or prof["sycoizz"] < bet: return await ctx.send("❌ Invalid bet configurations.")
        items = ["🍒", "🍇", "🍊", "💎", "👑", "❌"]
        msg = await ctx.send("🎰 **[ SPINNING ]**\n`[ 🔄 | 🔄 | 🔄 ]`")
        await asyncio.sleep(0.6)
        r1, r2, r3 = random.choice(items), random.choice(items), random.choice(items)
        res = f"🎰 **[ SLOTS ]**\n`[ {r1} | {r2} | {r3} ]`"
        if r1 == r2 == r3:
            payout = bet * 5 if r1 != "👑" else bet * 10
            prof["sycoizz"] += payout
            await edit_msg_safe(msg, f"{res}\n🎉 **JACKPOT!** Gained `+{payout:,}` sycoizz!")
        elif r1 == r2 or r2 == r3 or r1 == r3:
            payout = int(bet * 1.5)
            prof["sycoizz"] += payout
            await edit_msg_safe(msg, f"{res}\n✨ **Double!** Gained `+{payout:,}` sycoizz.")
        else:
            prof["sycoizz"] -= bet
            await edit_msg_safe(msg, f"{res}\n💀 **Bust!** Lost `{bet:,}` sycoizz.")

    # --- DEALER BLACKJACK ---
    @commands.command(name="blackjack", aliases=["bj"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def blackjack_gamble(self, ctx, bet: int):
        prof = get_profile(ctx.author.id)
        if bet <= 0 or prof["sycoizz"] < bet: return await ctx.send("❌ Insufficient vault funds.")
        draw = lambda: random.randint(1, 11)
        p, d = [draw(), draw()], [draw(), draw()]
        p_sc, d_sc = sum(p), sum(d)
        
        tpl = "🃏 **BLACKJACK**\n```\n👤 Player: {p_h:<10} Score: [{p_s}]\n🤖 Dealer: {d_h:<10} Score: [{d_s}]\n```\n👉 Type **`hit`** or **`stand`**."
        msg = await ctx.send(tpl.format(p_h=", ".join(map(str, p)), p_s=p_sc, d_h=f"{d}, ?", d_s="?"))

        def chk(m): return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ["hit", "stand"]
        while p_sc < 21:
            try: r = await self.bot.wait_for("message", check=chk, timeout=20.0)
            except asyncio.TimeoutError: return await ctx.send("⏱️ Match timed out.")
            if r.content.lower() == "hit":
                p.append(draw()); p_sc = sum(p)
                await edit_msg_safe(msg, tpl.format(p_h=", ".join(map(str, p)), p_s=p_sc, d_h=f"{d}, ?", d_s="?"))
            else: break

        if p_sc > 21:
            prof["sycoizz"] -= bet
            return await ctx.send(f"💀 **Bust!** Hit `{p_sc}`. Lost `{bet:,}` sycoizz.")

        while d_sc < 17: d.append(draw()); d_sc = sum(d)
        fin = "🃏 **BLACKJACK FINAL**\n```\n👤 Player: {p_h:<10} Score: [{p_s}]\n🤖 Dealer: {d_h:<10} Score: [{d_s}]\n```\n**Result:** {out}"
        if d_sc > 21 or p_sc > d_sc:
            prof["sycoizz"] += bet
            await edit_msg_safe(msg, fin.format(p_h=", ".join(map(str, p)), p_s=p_sc, d_h=", ".join(map(str, d)), d_s=d_sc, out=f"🏆 **WIN!** +`{bet:,}` sycoizz!"))
        elif p_sc == d_sc:
            await edit_msg_safe(msg, fin.format(p_h=", ".join(map(str, p)), p_s=p_sc, d_h=", ".join(map(str, d)), d_s=d_sc, out="🤝 **Push.** Bets returned."))
        else:
            prof["sycoizz"] -= bet
            await edit_msg_safe(msg, fin.format(p_h=", ".join(map(str, p)), p_s=p_sc, d_h=", ".join(map(str, d)), d_s=d_sc, out=f"💀 **Dealer wins.** Lost `{bet:,}` sycoizz."))

    # --- JACKPOT LOTTERY ---
    @commands.command(name="lottery", aliases=["lot"])
    async def lottery_pool_sys(self, ctx, buy_tickets: int = None):
        prof = get_profile(ctx.author.id)
        cost = 5000
        if buy_tickets is None:
            tot = sum(self.lottery_tickets.values())
            mine = self.lottery_tickets.get(ctx.author.id, 0)
            emb = discord.Embed(title="🎟️ GLOBAL LOTTERY POOL", color=discord.Color.gold())
            emb.description = f"💰 Jackpot Vault: **`{self.lottery_pool:,}` sycoizz**\n🎫 Ticket Rate: `{cost:,}`"
            emb.add_field(name="Stats", value=f"▫️ Total Tickets: `{tot}`\n▫️ Your Tickets: `{mine}`")
            return await ctx.send(embed=emb)
        if buy_tickets <= 0: return await ctx.send("❌ Must exceed zero.")
        tot_c = buy_tickets * cost
        if prof["sycoizz"] < tot_c: return await ctx.send(f"❌ Cost is `{tot_c:,}` sycoizz.")
        prof["sycoizz"] -= tot_c
        self.lottery_pool += int(tot_c * 0.85)
        self.lottery_tickets[ctx.author.id] = self.lottery_tickets.get(ctx.author.id, 0) + buy_tickets
        await ctx.send(f"🎟️ Purchased `{buy_tickets}` lottery tickets!")

    @coin_flip_gamble.error
    @slots_gamble.error
    @blackjack_gamble.error
    async def gambling_cooldown_errors(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏱️ **Cooldown!** Wait `{error.retry_after:.1f}` seconds.")

async def setup(bot):
    await bot.add_cog(GamblingEngine(bot))
      
