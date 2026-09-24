# economy.py
import random
import asyncio
import discord
from discord.ext import commands
from config import get_profile, GEMS, WEAPONS, OWNER_ID, edit_msg_safe

class EconomyEngine(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lottery_pool = 1000000  # Baseline seeded jackpot pool
        self.lottery_tickets = {}    # Keeps track of player purchases: {user_id: ticket_count}

    # --- OWNER-ONLY ADMIN COMMAND ---
    @commands.command(name="givecash")
    async def give_cash(self, ctx, target: discord.Member, amount: int):
        if ctx.author.id != OWNER_ID:
            return await ctx.send("❌ Access Denied: This command is restricted to the bot owner only.")
        if amount <= 0:
            return await ctx.send("❌ Amount must be positive.")
        prof = get_profile(target.id)
        prof["sycoizz"] += amount
        await ctx.send(f"👑 **[OWNER ADMIN]** Transferred `{amount:,}` sycoizz into {target.mention}'s account.")

    # --- OWO ECONOMY INTERFACES ---
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
            return await ctx.send("❌ Minimum transaction value must clear above 0.")
            
        sender_prof = get_profile(ctx.author.id)
        if sender_prof["sycoizz"] < amount:
            return await ctx.send("❌ Transaction aborted: Insufficient treasury balance.")
            
        receiver_prof = get_profile(target.id)
        sender_prof["sycoizz"] -= amount
        receiver_prof["sycoizz"] += amount
        await ctx.send(f"✅ Successfully transferred `{amount:,}` sycoizz to {target.mention}.")

    @commands.command(name="see", aliases=["profile", "inv", "bag"])
    async def see_cmd(self, ctx, target: discord.Member = None):
        user = target or ctx.author
        prof = get_profile(user.id)
        
        embed = discord.Embed(title=f"🎒 {user.name}'s Adventure Profile Ledger", color=discord.Color.blue())
        embed.add_field(name="💰 Cash Reserves", value=f"`{prof['sycoizz']:,}` sycoizz", inline=True)
        
        gem_display = [GEMS[gid]["name"] for gid in prof["gems"]] if prof["gems"] else ["No gems socketed"]
        embed.add_field(name="💎 Lucky Talismans", value=", ".join(gem_display), inline=True)
        
        pet_lines = []
        for pet in prof["pokemon"]:
            w_eq = f" (⚔️ Equipped: {WEAPONS[pet['equipped_weapon']]['name']})" if pet.get("equipped_weapon") else ""
            pet_lines.append(f"{pet['emoji']} **{pet['name']}** | HP: `{pet['hp']}`{w_eq}")
        
        embed.add_field(name="🐾 Roster Companion Lineup", value="\n".join(pet_lines) if pet_lines else "None", inline=False)
        await ctx.send(embed=embed)

    # ========================================================
    # 🎰 OWO GAMBLING MODULES
    # ========================================================

    # 1. COINFLIP (cf) - High-Fidelity Physics Flick Animation Sequence & All Bets
    @commands.command(name="cf", aliases=["flip"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def coin_flip_gamble(self, ctx, bet: str):
        prof = get_profile(ctx.author.id)
        current_balance = prof["sycoizz"]

        if bet.lower() == "all":
            bet_amount = current_balance
        else:
            try:
                bet_amount = int(bet)
            except ValueError:
                return await ctx.send("❌ Invalid input! Please enter a number or type `all` (e.g., `scf all` or `scf 5000`).")

        if bet_amount <= 0:
            return await ctx.send("❌ Minimum transaction value threshold must clear above 0.")
        if current_balance < bet_amount:
            return await ctx.send(f"❌ Transaction aborted: Insufficient treasury balance. Your current balance is `{current_balance:,}` sycoizz.")
            
        luck_modifier = 1.0
        for gid in prof["gems"]:
            if GEMS[gid]["boost"] > luck_modifier:
                luck_modifier = GEMS[gid]["boost"]

        # Immersive step-by-step frame animation sequence
        flick_frames = [
            "💨 **[  FLICK!  ]**   `  🪙  ` 🚀 *[Thumb snaps upward!]*",
            "📈 **[  RISING  ]**   `  🟡  `  ▲  *[Ascending into mid-air]*",
            "📈 **[  RISING  ]**   `  ⚪  `  ▲",
            "✨ **[   APEX   ]**   ` 🟡⟲ SPINNING ⟳ `  ⚡ *[Slowing down at highest peak]*",
            "✨ **[   APEX   ]**   ` ⚪⟲ SPINNING ⟳ `  ⚡",
            "📉 **[ FALLING ]**   `  🟡  `  ▼  *[Gravitational pull taking over]*",
            "📉 **[ FALLING ]**   `  ⚪  `  ▼",
            "🖐️ **[  CATCH!  ]**   ` 🪙🫲 ` 💥 *[Slapped firmly onto back of hand]*"
        ]
        
        msg = await ctx.send(flick_frames[0])
        for frame in flick_frames[1:]:
            await asyncio.sleep(0.35)
            await edit_msg_safe(msg, frame)
            
        base_chance = 0.50
        final_chance = base_chance * luck_modifier
        
        await asyncio.sleep(0.5)
        if random.random() <= final_chance:
            prof["sycoizz"] += bet_amount
            await edit_msg_safe(msg, f"🎉 **🎉 HEADS! YOU WIN! 🎉**\n🔥 Luck Factor Activated! Gained `+{bet_amount:,}` sycoizz!\n💳 Wallet Total: `{prof['sycoizz']:,}`")
        else:
            prof["sycoizz"] -= bet_amount
            await edit_msg_safe(msg, f"💀 **💀 TAILS! HOUSE WINS! 💀**\nLost your wager of `-{bet_amount:,}` sycoizz.\n💳 Wallet Total: `{prof['sycoizz']:,}`")

    # 2. SLOTS (s, slots)
    @commands.command(name="slots", aliases=["s", "slot"])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def slots_gamble(self, ctx, bet: int):
        prof = get_profile(ctx.author.id)
        if bet <= 0 or prof["sycoizz"] < bet:
            return await ctx.send("❌ Invalid bet amount or insufficient funds.")

        emojis = ["🍒", "🍇", "🍊", "💎", "👑", "❌"]
        msg = await ctx.send("🎰 **[ SLOTS SPINNING ]**\n`[ 🔄 | 🔄 | 🔄 ]`")
        await asyncio.sleep(0.6)
        
        r1, r2, r3 = random.choice(emojis), random.choice(emojis), random.choice(emojis)
        slot_view = f"🎰 **[ SLOTS RESULTS ]**\n`[ {r1} | {r2} | {r3} ]`"

        if r1 == r2 == r3:
            payout = bet * 5 if r1 != "👑" else bet * 10
            prof["sycoizz"] += payout
            await edit_msg_safe(msg, f"{slot_view}\n🎉 **JACKPOT MATRICES ALIGNED!** Earned: `+{payout:,}` sycoizz!")
        elif r1 == r2 or r2 == r3 or r1 == r3:
            payout = int(bet * 1.5)
            prof["sycoizz"] += payout
            await edit_msg_safe(msg, f"{slot_view}\n✨ **Double Match!** Payout returned: `+{payout:,}` sycoizz.")
        else:
            prof["sycoizz"] -= bet
            await edit_msg_safe(msg, f"{slot_view}\n💀 **Bust!** The machine ate your `{bet:,}` sycoizz entry fee.")

    # 3. BLACKJACK (bj, blackjack)
    @commands.command(name="blackjack", aliases=["bj"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def blackjack_gamble(self, ctx, bet: int):
        prof = get_profile(ctx.author.id)
        if bet <= 0 or prof["sycoizz"] < bet:
            return await ctx.send("❌ Verification failed: Insufficient funds.")

        def draw_card():
            return random.randint(1, 11)

        p_cards = [draw_card(), draw_card()]
        d_cards = [draw_card(), draw_card()]
        p_score = sum(p_cards)
        d_score = sum(d_cards)

        bj_template = (
            "🃏 **OwO BLACKJACK STAGE**\n"
            "```\n"
            "👤 Player Hand: {p_hand:<12} Score: [{p_score}]\n"
            "🤖 Dealer Hand: {d_hand:<12} Score: [{d_score}]\n"
            "```\n"
            "👉 Type **`hit`** for another card, or **`stand`** to hold your positions."
        )

        msg = await ctx.send(bj_template.format(p_hand=", ".join(map(str, p_cards)), p_score=p_score, d_hand=f"{d_cards[0]}, ?", d_score="?"))

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ["hit", "stand"]

        while p_score < 21:
            try:
                user_msg = await self.bot.wait_for("message", check=check, timeout=30.0)
            except asyncio.TimeoutError:
                await ctx.send("⏱️ Match abandoned due to player inactivity.")
                return

            if user_msg.content.lower() == "hit":
                p_cards.append(draw_card())
                p_score = sum(p_cards)
                await edit_msg_safe(msg, bj_template.format(p_hand=", ".join(map(str, p_cards)), p_score=p_score, d_hand=f"{d_cards[0]}, ?", d_score="?"))
            else:
                break

        if p_score > 21:
            prof["sycoizz"] -= bet
            return await ctx.send(f"💀 **Bust!** Your score hit `{p_score}` and went over 21. Lost `{bet:,}` sycoizz.")

        while d_score < 17:
            d_cards.append(draw_card())
            d_score = sum(d_cards)

        final_layout = (
            "🃏 **OwO BLACKJACK FINAL SHOWN STAGE**\n"
            "```\n"
            "👤 Player Hand: {p_hand:<12} Score: [{p_score}]\n"
            "🤖 Dealer Hand: {d_hand:<12} Score: [{d_score}]\n"
            "```\n"
            "**[System Result]:** {outcome_text}"
        )

        if d_score > 21 or p_score > d_score:
            prof["sycoizz"] += bet
            await edit_msg_safe(msg, final_layout.format(p_hand=", ".join(map(str, p_cards)), p_score=p_score, d_hand=", ".join(map(str, d_cards)), d_score=d_score, outcome_text=f"🏆 **VICTORY!** Gained `+{bet:,}` sycoizz!"))
                                           
