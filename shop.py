# shop.py
import discord
from discord.ext import commands
from config import get_profile, GEMS, WEAPONS, POKEMON_POOL

class ShopEngine(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="shop")
    async def show_rpg_shop(self, ctx):
        prof = get_profile(ctx.author.id)
        if not prof: return await ctx.send("❌ Run `s start` first.")
        
        embed = discord.Embed(title="🏪 THE GRAND SYCOIZZ CONTINENTAL BAZAAR", description="*Equip your monsters, claim legendary tools, and augment your fortunes.*", color=discord.Color.purple())
        
        w_list = [f"▫️ `{wid}` **{w['name']}**\n   **Tier:** [{w['tier']}] | 💥 Dmg: `{w['dmg']}`\n   💰 Cost: `{w['price']:,} sycoizz`\n" for wid, w in WEAPONS.items()]
        embed.add_field(name="⚔️ ARMORY STALL", value="".join(w_list), inline=False)
        
        g_list = [f"▫️ `{gid}` **{g['name']}**\n   *Effect:* `{g['desc']}`\n   💰 Cost: `{gid == 'ruby_gem' and 50000 or gid == 'sapphire_gem' and 150000 or gid == 'emerald_gem' and 500000 or 2500000:,} sycoizz`\n" for gid, g in GEMS.items()]
        embed.add_field(name="💎 MYSTIC JEWELERS", value="".join(g_list), inline=False)
        
        embed.add_field(
            name="🍂 PAWNSHOP LIQUIDATION DISPOSAL CHANNELS",
            value="👉 **Bulk Sell Pokémon:** `s sell all` *(Preserves equipped assets!)*\n"
                  "👉 **Sell Single Pokémon:** `s sell [pokemon_name]`\n"
                  "👉 **Sell Blueprints:** `s sell weapon [weapon_id]` *(Yields 50% refund)*\n\n"
                  "▫️ **Common:** `+1,500` | **Rare:** `+8,000` | **Legendary:** `+25,000` | **Mythic:** `+100,000` sycoizz",
            inline=False
        )
        embed.set_footer(text="🛒 Use Matrix: s buy_weapon [id] | s buy_gem [id] | s equip [id]")
        await ctx.send(embed=embed)

    # --- MASS ALL & SINGLE REFUND VECTOR HOOKS ---
    @commands.command(name="sell")
    async def sell_pokemon(self, ctx, *, argument: str = None):
        prof = get_profile(ctx.author.id)
        if not prof: return await ctx.send("❌ Profile ledger mapping empty. Use `s start`.")
        if not argument: return await ctx.send("❌ Missing target item tag parameters. Run `s sell all` or `s sell Pikachu`.")

        user_pokemon_list = prof["pokemon"]
        
        # --- SUB-ROUTINE: MASS ALL REFUNDS ---
        if argument.lower() == "all":
            keep_list, sell_list = [], []
            for pet in user_pokemon_list:
                if pet.get("equipped_weapon") is not None: keep_list.append(pet)
                else: sell_list.append(pet)
            
            if not sell_list: return await ctx.send("⚠️ **Bulk Sell Terminated:** No unequipped stickers detected inside your collection bags!")
            if not keep_list:
                keep_list.append(sell_list.pop(0))
                if not sell_list: return await ctx.send("⚠️ **Safety Interlock:** Your last structural starter monster cannot be liquidated under any condition loops.")

            total_payout = 0
            breakdown = {"Common": 0, "Rare": 0, "Legendary": 0, "Mythic": 0}

            for pet in sell_list:
                found_tier = "Common"
                for tier_name, species_list in POKEMON_POOL.items():
                    if any(s["name"].lower() == pet["name"].lower() for s in species_list):
                        found_tier = tier_name
                        break
                p = found_tier == "Rare" and 8000 or found_tier == "Legendary" and 25000 or found_tier == "Mythic" and 100000 or 1500
                total_payout += p
                breakdown[found_tier] += 1

            prof["pokemon"] = keep_list
            prof["sycoizz"] += total_payout
            sum_str = ", ".join([f"{count}x {t}" for t, count in breakdown.items() if count > 0])
            return await ctx.send(f"🍂 💰 **MASS REFUND LIQUIDATION COMPLETE:**\nTraded away: **{sum_str}**.\n🪙 Capital Received: `+{total_payout:,}` sycoizz.\n🔒 *Note: All weapon-bearing team units were fully preserved safely.*")

        # --- SUB-ROUTINE: INDIVIDUAL TRANSFERS ---
        if len(user_pokemon_list) <= 1: return await ctx.send("⚠️ You only hold 1 active companion asset left. Transaction aborted.")
        
        target_index = -1
        for idx, pet in enumerate(user_pokemon_list):
            if pet["name"].lower() == argument.lower():
                target_index = idx
                break

        if target_index == -1: return await ctx.send(f"❌ Target entity asset **{argument}** matches no entries in your roster logs.")
        matched_pokemon = user_pokemon_list[target_index]
        if matched_pokemon.get("equipped_weapon") is not None: return await ctx.send("🔒 **Sticker Locked:** This Pokémon has a weapon loadout bound to it! Unbind or run `s sell all`.")

        found_tier = "Common"
        for tier_name, species_list in POKEMON_POOL.items():
            if any(s["name"].lower() == matched_pokemon["name"].lower() for s in species_list):
                found_tier = tier_name
                break
        p = found_tier == "Rare" and 8000 or found_tier == "Legendary" and 25000 or found_tier == "Mythic" and 100000 or 1500

        removed_pet = user_pokemon_list.pop(target_index)
        prof["sycoizz"] += p
        await ctx.send(f"🍂 💰 **PAWNSHOP DISPOSAL SECURED:** Traded **[{found_tier}] {removed_pet['name']}** for `+{p:,}` sycoizz.")

    # --- INDEPENDENT WEAPON BLUEPRINT REFUNDS ---
    @commands.command(name="sell_weapon", aliases=["sellweapon"])
    async def sell_weapon_blueprint(self, ctx, weapon_id: str = None):
        prof = get_profile(ctx.author.id)
        if not prof: return await ctx.send("❌ Run `s start` first.")
        if not weapon_id: return await ctx.send("❌ State the item key blueprint to pawn. (e.g. `s sell_weapon iron_blade`)")

        if weapon_id not in WEAPONS or weapon_id not in prof["weapons"]:
            return await ctx.send("❌ Item index mismatch: Blueprint entry not matched or unowned inside inventory profiles.")

        if any(p.get("equipped_weapon") == weapon_id for p in prof["pokemon"]):
            return await ctx.send("🔒 **Blueprint Locked:** This item asset tool is currently actively equipped onto your combat lineup team! Change gears first.")

        w_data = WEAPONS[weapon_id]
        refund = int(w_data["price"] * 0.50)
        prof["weapons"].remove(weapon_id)
        prof["sycoizz"] += refund
        await ctx.send(f"⚔️ 🍂 **ARMORY RECYCLER ACCEPTANCE:** Returned your **{w_data['name']}** to the forge masters! Refund value: `+{refund:,}` sycoizz.")

    @commands.command(name="buy_weapon")
    async def buy_weapon(self, ctx, weapon_id: str):
        prof = get_profile(ctx.author.id)
        if not prof or weapon_id not in WEAPONS: return await ctx.send("❌ Invalid item index identifier.")
        item = WEAPONS[weapon_id]
        if prof["sycoizz"] < item["price"] or weapon_id in prof["weapons"]: return await ctx.send("❌ Transaction rejected: Funds check failure or duplication limit reached.")
        
        prof["sycoizz"] -= item["price"]
        prof["weapons"].append(weapon_id)
        await ctx.send(f"✅ Purchased **{item['name']}** tier blueprint successfully.")

    @commands.command(name="buy_gem")
    async def buy_gem(self, ctx, gem_id: str):
        prof = get_profile(ctx.author.id)
        if not prof or gem_id not in GEMS: return await ctx.send("❌ Gem structural index invalid.")
        item = GEMS[gem_id]
        if prof["sycoizz"] < item["price"] or gem_id in prof["gems"]: return await ctx.send("❌ Gem purchase declined: Insufficient capital or asset owned.")
        
        prof["sycoizz"] -= item["price"]
        prof["gems"].append(gem_id)
        await ctx.send(f"✅ Socketed **{item['name']}** luck talisman field.")

    @commands.command(name="equip")
    async def equip(self, ctx, weapon_id: str):
        prof = get_profile(ctx.author.id)
        if not prof or weapon_id not in prof["weapons"]: return await ctx.send("❌ Target tool unowned inside inventory logs.")
        
        prof["pokemon"][0]["equipped_weapon"] = weapon_id
        await ctx.send(f"⚔️ **LOADOUT MODIFIED:** Your primary lead companion successfully bound **{WEAPONS[weapon_id]['name']}** into active equipment slots!")

async def setup(bot):
    await bot.add_cog(ShopEngine(bot))
              
