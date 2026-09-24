# shop.py
import discord
from discord.ext import commands
from config import get_profile, GEMS, WEAPONS

class ShopEngine(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="shop")
    async def show_rpg_shop(self, ctx):
        embed = discord.Embed(
            title="🏪 THE GRAND SYCOIZZ CONTINENTAL BAZAAR",
            description="*Equip your monsters, claim legendary tools, and augment your fortunes.*",
            color=discord.Color.purple()
        )
        
        weapon_list = []
        for wid, w in WEAPONS.items():
            weapon_list.append(f"▫️ `{wid}` **{w['name']}**\n   **Tier:** [{w['tier']}] | 💥 Dmg: `{w['dmg']}`\n   💰 Cost: `{w['price']:,} sycoizz`\n")
        embed.add_field(name="⚔️ ARMORY STALL", value="".join(weapon_list), inline=False)
        
        gem_list = []
        for gid, g in GEMS.items():
            gem_list.append(f"▫️ `{gid}` **{g['name']}**\n   *Effect:* `{g['desc']}`\n   💰 Cost: `{g['price']:,} sycoizz`\n")
        embed.add_field(name="💎 MYSTIC JEWELERS", value="".join(gem_list), inline=False)
        
        embed.set_footer(text="🛒 Use Commands: sbuy_weapon [id]  |  sbuy_gem [id]  |  sequip [id]")
        await ctx.send(embed=embed)

    @commands.command(name="buy_weapon")
    async def buy_weapon(self, ctx, weapon_id: str):
        if weapon_id not in WEAPONS:
            return await ctx.send("❌ Weapon code variant not found in store logs.")
        prof = get_profile(ctx.author.id)
        item = WEAPONS[weapon_id]
        if prof["sycoizz"] < item["price"]:
            return await ctx.send(f"❌ You need `{item['price']:,}` sycoizz.")
        if weapon_id in prof["weapons"]:
            return await ctx.send("⚠️ You already own this tool blueprint.")
        prof["sycoizz"] -= item["price"]
        prof["weapons"].append(weapon_id)
        await ctx.send(f"✅ Purchased **{item['name']}** for `{item['price']:,}` sycoizz.")

    @commands.command(name="buy_gem")
    async def buy_gem(self, ctx, gem_id: str):
        if gem_id not in GEMS:
            return await ctx.send("❌ Gem identifier entry matches no store inventory.")
        prof = get_profile(ctx.author.id)
        item = GEMS[gem_id]
        if prof["sycoizz"] < item["price"]:
            return await ctx.send("❌ Insufficient funds.")
        if gem_id in prof["gems"]:
            return await ctx.send("⚠️ You are already buffed by this active slot gemstone.")
        prof["sycoizz"] -= item["price"]
        prof["gems"].append(gem_id)
        await ctx.send(f"✅ Socketed **{item['name']}**! Gambling luck factors have advanced.")

    @commands.command(name="equip")
    async def equip(self, ctx, weapon_id: str):
        prof = get_profile(ctx.author.id)
        if weapon_id not in prof["weapons"]:
            return await ctx.send("❌ You do not own this weapon asset. Buy it first!")
        if not prof["pokemon"]:
            return await ctx.send("❌ No active battle companions available.")
            
        # Target the leading pokemon slot
        prof["pokemon"][0]["equipped_weapon"] = weapon_id
        prof["equipped_weapon"] = weapon_id
        w_info = WEAPONS[weapon_id]
        await ctx.send(f"⚔️ **LOADOUT MODIFIED:** {prof['pokemon'][0]['emoji']} **{prof['pokemon'][0]['name']}** has equipped the **{w_info['name']}**!")

async def setup(bot):
    await bot.add_cog(ShopEngine(bot))
      
