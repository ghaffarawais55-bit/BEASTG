# battles.py
import random
import asyncio
import discord
from discord.ext import commands
from config import get_profile, WEAPONS, POKEMON_POOL, WORLD_BOSS, edit_msg_safe

class BattleEngine(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- HIGH PHYSICS RAID BOSS ACTION SYSTEM ---
    @commands.command(name="boss")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def boss_raid_fight(self, ctx):
        prof = get_profile(ctx.author.id)
        if not prof: return await ctx.send("❌ Create a character entry log mapping via `s start` first.")
        
        player_pet = prof["pokemon"][0]
        bonus_dmg = WEAPONS[player_pet["equipped_weapon"]]["dmg"] if player_pet.get("equipped_weapon") else 0
        w_title = WEAPONS[player_pet["equipped_weapon"]]["name"] if player_pet.get("equipped_weapon") else "None"
        strike_action = WEAPONS[player_pet["equipped_weapon"]]["attack_name"] if player_pet.get("equipped_weapon") else player_pet["attack"]

        p_hp = player_pet["hp"] + 200  # Buff raid profile stats
        b_hp = WORLD_BOSS["hp"]
        b_name = WORLD_BOSS["name"]
        b_emoji = WORLD_BOSS["emoji"]

        template = (
            "👹 **[ ANIMATED ULTIMATE WORLD RAID BEAST ENCOUNTER ]** 👹\n"
            "```\n"
            "🚨 LEVEL OVERLOAD BOSS PROTOCOLS ENGAGED 🚨\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🔵 {p_emoji} {p_name:<12} HP: [{p_hp:<4}] | Armory Loadout: {w_name}\n"
            "💀 {b_emoji} {b_name:<12} HP: [{b_hp:<4}] | CLASS: SUPREME BEAST APEX\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "```\n"
            "⚡ **[Raid Combat Stream Logs]:** {logs}"
        )

        msg = await ctx.send(template.format(p_emoji=player_pet["emoji"], p_name=player_pet["name"], p_hp=p_hp, w_name=w_title, b_emoji=b_emoji, b_name=b_name, b_hp=b_hp, logs="Spawning grid arenas... Reality distortions occurring."))

        while p_hp > 0 and b_hp > 0:
            await asyncio.sleep(1.0)
            p_hit = random.randint(35, 75) + (bonus_dmg * 2)
            b_hp = max(0, b_hp - p_hit)
            await edit_msg_safe(msg, template.format(p_emoji=player_pet["emoji"], p_name=player_pet["name"], p_hp=p_hp, w_name=w_title, b_emoji=b_emoji, b_name=b_name, b_hp=b_hp, logs=f"⚔️ CRITICAL CRUSH! {player_pet['name']} channels {strike_action}! Pierced World Boss for **{p_hit}** damage!"))
            
            if b_hp <= 0: break
            await asyncio.sleep(1.0)
            
            b_hit = random.randint(40, 90)
            p_hp = max(0, p_hp - b_hit)
            await edit_msg_safe(msg, template.format(p_emoji=player_pet["emoji"], p_name=player_pet["name"], p_hp=p_hp, w_name=w_title, b_emoji=b_emoji, b_name=b_name, b_hp=b_hp, logs=f"🌌 HORRIFIC ROAR! {b_name} triggers {WORLD_BOSS['attack']}! Shockwaves flattened player for **{b_hit}** dmg!"))

        await asyncio.sleep(0.8)
        if p_hp > 0:
            bounty = random.randint(1500000, 3500000)
            prof["sycoizz"] += bounty
            final_log = f"🏆 MYTHIC DESTROYER EXTRACTION COMPLETE! Cleared {b_name}. Discovered legendary bounty payout cache drop of `+{bounty:,}` sycoizz!"
        else:
            final_log = f"💀 WIPEOUT COMPLETED! The Chaos Beast obliterated your stance vector. Recalibrating nodes."

        await edit_msg_safe(msg, template.format(p_emoji=player_pet["emoji"], p_name=player_pet["name"], p_hp=p_hp, w_name=w_title, b_emoji=b_emoji, b_name=b_name, b_hp=b_hp, logs=final_log))

    # --- STANDARD BATTLE INTERFACE STREAMS ---
    @commands.command(name="battle")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def battle(self, ctx):
        prof = get_profile(ctx.author.id)
        if not prof: return await ctx.send("❌ Open account first.")
        
        player_pet = prof["pokemon"][0]
        bonus_dmg = WEAPONS[player_pet["equipped_weapon"]]["dmg"] if player_pet.get("equipped_weapon") else 0
        w_title = WEAPONS[player_pet["equipped_weapon"]]["name"] if player_pet.get("equipped_weapon") else "None"
        strike_action = WEAPONS[player_pet["equipped_weapon"]]["attack_name"] if player_pet.get("equipped_weapon") else player_pet["attack"]

        tier = random.choices(["Common", "Rare", "Legendary", "Mythic"], weights=[0.55, 0.30, 0.10, 0.05])[0]
        enemy = random.choice(POKEMON_POOL[tier])
        
        p_hp, e_hp = player_pet["hp"], enemy["hp"]
        e_name, e_emoji = f"Wild {enemy['name']}", enemy["emoji"]

        status_template = (
            "⚔️ **STAGE ENCOUNTER: WILD STICKER DUEL** ⚔️\n"
            "```\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🔵 {p_emoji} {p_name:<12} HP: [{p_hp:<4}] | Loadout: {w_name}\n"
            "🔴 {e_emoji} {e_name:<12} HP: [{e_hp:<4}] | Tier: {e_tier}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "```\n"
            "**[Sticker Action Streams]:** {log}"
        )

        msg = await ctx.send(status_template.format(p_emoji=player_pet["emoji"], p_name=player_pet["name"], p_hp=p_hp, w_name=w_title, e_emoji=e_emoji, e_name=e_name, e_hp=e_hp, e_tier=tier, log="Loading timeline frame layers... Sync complete."))

        while p_hp > 0 and e_hp > 0:
            await asyncio.sleep(0.8)
            hit = random.randint(15, 30) + bonus_dmg
            e_hp = max(0, e_hp - hit)
            await edit_msg_safe(msg, status_template.format(p_emoji=player_pet["emoji"], p_name=player_pet["name"], p_hp=p_hp, w_name=w_title, e_emoji=e_emoji, e_name=e_name, e_hp=e_hp, e_tier=tier, log=f"💥 {player_pet['name']} struck with {strike_action}! Dealt {hit} damage!"))
            
            if e_hp <= 0: break
            await asyncio.sleep(0.8)
            
            e_hit = random.randint(12, 28) + (20 if tier == "Legendary" else 45 if tier == "Mythic" else 0)
            p_hp = max(0, p_hp - e_hit)
            await edit_msg_safe(msg, status_template.format(p_emoji=player_pet["emoji"], p_name=player_pet["name"], p_hp=p_hp, w_name=w_title, e_emoji=e_emoji, e_name=e_name, e_hp=e_hp, e_tier=tier, log=f"⚡ {e_name} unleashed {enemy['attack']}! Returned {e_hit} damage counter!"))

        if p_hp > 0:
            reward = tier == "Mythic" and random.randint(100000, 250000) or random.randint(2000, 6000)
            prof["sycoizz"] += reward
            final_log = f"🏆 VICTORY! Successfully knocked out {e_name}. Collected bounty payout of `+{reward:,}` sycoizz!"
        else:
            final_log = f"💀 ARENA RUN BUSTED! Your leading companion pet collapsed. Focus up."
            
        await edit_msg_safe(msg, status_template.format(p_emoji=player_pet["emoji"], p_name=player_pet["name"], p_hp=p_hp, w_name=w_title, e_emoji=e_emoji, e_name=e_name, e_hp=e_hp, e_tier=tier, log=final_log))

    @boss_raid_fight.error
    @battle.error
    async def battle_cooldowns(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏱️ **Combat Exhaustion!** Your squad requires recovery time. Try moving in `{error.retry_after:.1f}` seconds.")

async def setup(bot):
    await bot.add_cog(BattleEngine(bot))
          
