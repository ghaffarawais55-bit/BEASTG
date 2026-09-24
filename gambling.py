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

    # --- ANIME HIGH-DETAIL FLICK COINFLIP ---
    @commands.command(name="cf", aliases=["flip"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def coin_flip_gamble(self, ctx, bet: str):
        prof = get_profile(ctx.author.id)
        if not prof: return await ctx.send("❌ Run `s start` first to establish your profile.")
        bal = prof["sycoizz"]
        
        amt = bal if bet.lower() == "all" else int(bet) if bet.isdigit() else 0
        if amt <= 0 or bal < amt: return await ctx.send("❌ Input parsed error: Set a positive amount or type `all`.")

        luck = max([GEMS[g]["boost"] for g in prof["gems"]] + [1.0])

        frames = [
            "💨 **[ S FLICK! ]**  `🪙` 🚀  ⚡ *[Flicking coin upward into air]*",
            "📈 **[ S RISING ]** `🟡` ▲  💥 *[Spinning at hyper speeds]*",
            "✨ **[ S APEX ]**   `⚪⟲ SPINNING ⟳` 🔥 *[Apex deceleration state]*",
            "📉 **[ S FALLING ]** `🟡` ▼  💤 *[Dropping downward fast]*",
            "🖐️ **[ S CATCH! ]**  `🪙🫲` 🎰  ⚔️ *[Caught on hand back]*"
        ]
        msg = await ctx.send(frames)
        for f in frames[1:]:
            await asyncio.sleep(0.35)
            await edit_msg_safe(msg, f)

        await asyncio.sleep(0.4)
        if random.random() <= (0.50 * luck):
            prof["sycoizz"] += amt
            await edit_msg_safe(msg, f"🎉 **S COIN RESULT: HEADS! WINNER!**\nGained `+{amt:,}` sycoizz! Wallet Total: `{prof['sycoizz']:,}`")
        else:
            prof["sycoizz"] -= amt
            await edit_msg_safe(msg, f"💀 **S COIN RESULT: TAILS! BUSTED!**\nLost `-{amt:,}` sycoizz. Wallet Total: `{prof['sycoizz']:,}`")

    @commands.command(name="slots", aliases=["s", "slot"])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def slots_gamble(self, ctx, bet: int):
        prof = get_profile(ctx.author.id)
        if not prof or bet <= 0 or prof["sycoizz"] < bet: return await ctx.send("❌ Invalid slot bet limit metrics.")
        
        items = ["🍒", "🍇", "🍊", "💎", "👑", "❌"]
        msg = await ctx.send("🎰 **[ SLOTS REELS SPINNING ]**\n`[ 🔄 | 🔄 | 🔄 ]` 🌀 *[Reels churning]*")
        await asyncio.sleep(0.6)
        
        r1, r2, r3 = random.choice(items), random.choice(items), random.choice(items)
        res = f"🎰 **[ SLOTS RESULTS ]**\n`[ {r1} | {r2} | {r3} ]`"
        if r1 == r2 == r3:
            p = bet * 5 if r1 != "👑" else bet * 10
            prof["sycoizz"] += p
            await edit_msg_safe(msg, f"{res}\n🎉 **JACKPOT ROWS MATCHED!** Gained `+{p:,}` sycoizz!")
        elif r1 == r2 or r2 == r3 or r1 == r3:
            p = int(bet * 1.5)
            prof["sycoizz"] += p
            await edit_msg_safe(msg, f"{res}\n✨ **Double Row!** Gained `+{p:,}` sycoizz.")
        else:
            prof["sycoizz"] -= bet
            await edit_msg_safe(msg, f"{res}\n💀 **Bust!** The slot machine swallowed your `{bet:,}` sycoizz.")

    @commands.command(name="blackjack", aliases=["bj"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def blackjack_gamble(self, ctx, bet: int):
        prof = get_profile(ctx.author.id)
        if not prof or bet <= 0 or prof["sycoizz"] < bet: return await ctx.send("❌ Financial ledger tracking failure.")
        draw = lambda: random.randint(1, 11)
        p, d = [draw(), draw()], [draw(), draw()]
        p_sc, d_sc = sum(p), sum(d)
        
        tpl = "🃏 **S BLACKJACK TABLES**\n```\n👤 Player Hand: {p_h:<10} Score: [{p_s}]\n🤖 Dealer Hand: {d_h:<10} Score: [{d_s}]\n```\n👉 Reply **`hit`** to draw a card, or **`stand`** to hold positions."
        msg = await ctx.send(tpl.format(p_h=", ".join(map(str, p)), p_s=p_sc, d_h=f"{d}, ?", d_s="?"))

        def chk(m): return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ["hit", "stand"]
        while p_sc < 21:
            try: r = await self.bot.wait_for("message", check=chk, timeout=20.0)
            except asyncio.TimeoutError: return await ctx.send("⏱️ Blackjack match abandoned due to game timeout.")
            if r.content.lower() == "hit":
                p.append(draw()); p_sc = sum(p)
                await edit_msg_safe(msg, tpl.format(p_h=", ".join(map(str, p)), p_s=p_sc, d_h=f"{d}, ?", d_s="?"))
            else: break

        if p_sc > 21:
            prof["sycoizz"] -= bet
            return await ctx.send(f"💀 **Bust over 21 limits!** Score hit [{p_sc}]. Lost your bet of `{bet:,}` sycoizz.")

        while d_sc < 17: d.append(draw()); d_sc = sum(d)
        fin = "🃏 **BLACKJACK FINAL SHOWDOWN**\n```\n👤 Player Hand: {p_h:<10} Score: [{p_s}]\n🤖 Dealer Hand: {d_h:<10} Score: [{d_s}]\n```\n**Resulting Output:** {out}"
        if d_sc > 21 or p_sc > d_sc:
            prof["sycoizz"] += bet
            await edit_msg_safe(msg, fin.format(p_h=", ".join(map(str, p)), p_s=p_sc, d_h=", ".join(map(str, d)), d_s=d_sc, out=f"🏆 **WINNER WINNER!** +`{bet:,}` sycoizz!"))
        elif p_sc == d_sc:
            await edit_msg_safe(msg, fin.format(p_h=", ".join(map(str, p)), p_s=p_sc, d_h=", ".join(map(str, d)), d_s=d_sc, out="🤝 **Push.** All bets split safely."))
        else:
            prof["sycoizz"] -= bet
            await edit_msg_safe(msg, fin.format(p_h=", ".join(map(str, p)), p_s=p_sc, d_h=", ".join(map(str, d)), d_s=d_sc, out=f"💀 **Dealer wins.** Lost `{bet:,}` sycoizz."))

    @commands.command(name="lottery", aliases=["lot"])
    async def lottery_pool_sys(self, ctx, buy_tickets: int = None):
        prof = get_profile(ctx.author.id)
        if not prof: return await ctx.send("❌ Profile required.")
        cost = 5000
        if buy_tickets is None:
            tot = sum(self.lottery_tickets.values())
            emb = discord.Embed(title="🎟️ GLOBAL JACKPOT LOTTERY HUB", color=discord.Color.gold())
            emb.description = f"💰 Active Jackpot Vault: **`{self.lottery_pool:,}` sycoizz**\n🎫 Ticket Rate: `{cost:,}` sycoizz"
            emb.add_field(name="Pool Stats", value=f"▫ Lives Sold: `{tot}`\n▫ Your Owned Shares: `{self.lottery_tickets.get(ctx.author.id, 0)}`")
            return await ctx.send(embed=emb)
        if buy_tickets <= 0: return await ctx.send("❌ Selection count must exceed zero value limits.")
        tot_c = buy_tickets * cost
        if prof["sycoizz"] < tot_c: return await ctx.send("❌ Insufficient bank currency reserves.")
        
        prof["sycoizz"] -= tot_c
        self.lottery_pool += int(tot_c * 0.85)
        self.lottery_tickets[ctx.author.id] = self.lottery_tickets.get(ctx.author.id, 0) + buy_tickets
        await ctx.send(f"🎟️ Successfully logged `{buy_tickets}` lottery entries into the master ticket drum!")

    @coin_flip_gamble.error
    @slots_gamble.error
    @blackjack_gamble.error
    async def gambling_cooldown_errors(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏱️ **OwO Table Cooldown!** Shuffling decks... Wait `{error.retry_after:.1f}` seconds.")

async def setup(bot):
    await bot.add_cog(GamblingEngine(bot))
  
