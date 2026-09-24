# battles.py
import random
import asyncio
import discord
from discord.ext import commands
from config import get_profile, WEAPONS, POKEMON_POOL, WORLD_BOSS, edit_msg_safe

class BattleEngine(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def draw_health_bar(self, current_hp, max_hp):
        if max_hp <= 0: return "░░░░░░░░░░"
        percentage = max(0, min(current_hp / max_hp, 1.0))
        filled_blocks = int(percentage * 10)
        return "█" * filled_blocks + "░" * (10 - filled_blocks)

    # ========================================================
    # ⚔️ CHOICE-BASED ARENA COMBAT ENGINE
    # ========================================================
    @commands.command(name="battle")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def battle(self, ctx):
        prof = get_profile(ctx.author.id)
        if not prof: 
            return await ctx.send("❌ Run `s start` first to establish your account profile.")
        
        player_pet = prof["pokemon"][0] if isinstance(prof["pokemon"], list) else prof["pokemon"]
        bonus_dmg = WEAPONS[player_pet["equipped_weapon"]]["dmg"] if player_pet.get("equipped_weapon") else 0
        w_title = WEAPONS[player_pet["equipped_weapon"]]["name"] if player_pet.get("equipped_weapon") else "None"

        # Roll Wild Opponent
        tier = random.choices(["Common", "Rare", "Legendary", "Mythic"], weights=[0.55, 0.30, 0.10, 0.05])[0]
        enemy = random.choice(POKEMON_POOL[tier])
        
        max_p_hp, max_e_hp = player_pet["hp"], enemy["hp"]
        p_hp, e_hp = max_p_hp, max_e_hp
        e_name = f"Wild {enemy['name']}"

        # 📋 MOVES LIST FOR THE PLAYER
        # Standard structural attacks + dynamic weapon moves if an item is equipped
        moves = {
            "1": {"name": player_pet["attack"], "min": 15, "max": 25, "type": "STAB"},
            "2": {"name": "Tackle", "min": 10, "max": 18, "type": "Normal"}
        }
        if player_pet.get("equipped_weapon"):
            w_meta = WEAPONS[player_pet["equipped_weapon"]]
            moves["3"] = {"name": w_meta["attack_name"], "min": w_meta["dmg"] - 5, "max": w_meta["dmg"] + 15, "type": "Weapon"}

        status_template = (
            "⚔️ **[ POKÉMON INTERACTIVE COMBAT FIELD ]** ⚔️\n"
            "```\n"
            "🔵 {p_name}\n"
            "   HP: [{p_hp}/{max_p_hp}] \n"
            "   [{p_bar}] ⚔️ Loadout: {w_name}\n\n"
            "🔴 {e_name}\n"
            "   HP: [{e_hp}/{max_e_hp}] \n"
            "   [{e_bar}] 📋 Rarity: {e_tier}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "```\n"
            "👉 **CHOOSE YOUR ATTACK MOVE NOW!**\n"
            "{move_options}\n"
            "*(Type the move number inside this chat channel)*\n\n"
            "💥 **[VFX Animations]:** {log}"
        )

        p_emoji_prefix = f"{player_pet['emoji']} " if "emoji" in player_pet else "🔵 "
        e_emoji_prefix = f"{enemy['emoji']} " if "emoji" in enemy else "🔴 "

        # Format the interactive choice panel string text
        opt_str = "\n".join([f"🔹 Type **`{k}`** to use **{v['name']}**" for k, v in moves.items()])

        msg = await ctx.send(f"{p_emoji_prefix}**{player_pet['name']}** encounters {e_emoji_prefix}**{e_name}**!\n" + status_template.format(
            p_name=player_pet["name"], p_hp=p_hp, max_p_hp=max_p_hp, p_bar=self.draw_health_bar(p_hp, max_p_hp), w_name=w_title,
            e_name=e_name, e_hp=e_hp, max_e_hp=max_e_hp, e_bar=self.draw_health_bar(e_hp, max_e_hp), e_tier=tier,
            move_options=opt_str, log="Waiting for player commands..."
        ))

        def input_check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content in moves.keys()

        # --- COMBAT ROUND TURNS PROCESSOR ---
        while p_hp > 0 and e_hp > 0:
            try:
                # Bot pauses and waits 30 seconds for the user to pick an attack item
                player_selection = await self.bot.wait_for("message", check=input_check, timeout=30.0)
                selected_move = moves[player_selection.content]
                
                # Delete user choice command text to keep chat screens clean
                try: await player_selection.delete()
                except Exception: pass
                
            except asyncio.TimeoutError:
                await ctx.send("⏱️ **Match Terminated:** You took too long to pick an attack move!")
                return

            # --- 1. PLAYER ATTACK TURN PHASE ---
            hit = random.randint(selected_move["min"], selected_move["max"])
            # Apply passive loadout damage buff if using native companion strikes
            if selected_move["type"] != "Weapon":
                hit += bonus_dmg
                
            e_hp = max(0, e_hp - hit)
            
            await edit_msg_safe(msg, f"{p_emoji_prefix}**{player_pet['name']}** encounters {e_emoji_prefix}**{e_name}**!\n" + status_template.format(
                p_name=player_pet["name"], p_hp=p_hp, max_p_hp=max_p_hp, p_bar=self.draw_health_bar(p_hp, max_p_hp), w_name=w_title,
                e_name=e_name, e_hp=e_hp, max_e_hp=max_e_hp, e_bar=self.draw_health_bar(e_hp, max_e_hp), e_tier=tier,
                move_options=opt_str, log=f"💥 {player_pet['name']} used {selected_move['name']}! ✨──► 💥 Dealt **{hit}** damage!"
            ))
            
            if e_hp <= 0: break
            await asyncio.sleep(1.5)
            
            # --- 2. WILD OPPONENT ATTACK TURN PHASE ---
            e_hit = random.randint(12, 28)
            if tier == "Legendary": e_hit += 20
            elif tier == "Mythic": e_hit += 45
            
            p_hp = max(0, p_hp - e_hit)
            
            await edit_msg_safe(msg, f"{p_emoji_prefix}**{player_pet['name']}** encounters {e_emoji_prefix}**{e_name}**!\n" + status_template.format(
                p_name=player_pet["name"], p_hp=p_hp, max_p_hp=max_p_hp, p_bar=self.draw_health_bar(p_hp, max_p_hp), w_name=w_title,
                e_name=e_name, e_hp=e_hp, max_e_hp=max_e_hp, e_bar=self.draw_health_bar(e_hp, max_e_hp), e_tier=tier,
                move_options=opt_str, log=f"⚡ {e_name} counters with {enemy['attack']}! 💥──► 🩸 Dealt **{e_hit}** damage!"
            ))

        # --- 3. POST MATCH WINNER RESOLUTION & ECONOMY CASH REWARD ---
        await asyncio.sleep(1.0)
        if p_hp > 0:
            reward = random.randint(100000, 250000) if tier == "Mythic" else random.randint(2500, 7500)
            prof["sycoizz"] += reward
            final_log = f"🏆 **MATCH OVER:** {player_pet['name']} wins the match!\n💰 **BOUNTY REWARD:** Earned `+{reward:,}` sycoizz payout added directly to bank wallet accounts!"
        else:
            final_log = f"💀 **MATCH OVER:** {e_name} wins the match!\n❌ **BOUNTY REWARD:** 0 sycoizz loot generated. Your team fainted."

        # Final panel print rendering out victory blocks and prices clean
        await edit_msg_safe(msg, f"{p_emoji_prefix}**{player_pet['name']}** encounters {e_emoji_prefix}**{e_name}**!\n" + status_template.format(
            p_name=player_pet["name"], p_hp=p_hp, max_p_hp=max_p_hp, p_bar=self.draw_health_bar(p_hp, max_p_hp), w_name=w_title,
            e_name=e_name, e_hp=e_hp, max_e_hp=max_e_hp, e_bar=self.draw_health_bar(e_hp, max_e_hp), e_tier=tier,
            move_options="🏁 Battle concluded.", log=final_log
        ))

    @battle.error
    async def battle_cooldowns(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏱️ **Combat Exhaustion!** Your team needs rest. Ready again in `{error.retry_after:.1f}` seconds.")

async def setup(bot):
    await bot.add_cog(BattleEngine(bot))
      
