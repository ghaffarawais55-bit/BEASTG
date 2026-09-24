# hunt.py
import random
import discord
from discord.ext import commands
from config import get_profile, POKEMON_POOL

class HuntEngine(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="hunt", aliases=["catch"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def hunt_pokemon(self, ctx):
        prof = get_profile(ctx.author.id)
        if not prof: return await ctx.send("❌ Character profile uninitialized. Run `s start` first.")
        
        tier = random.choices(["Common", "Rare", "Legendary", "Mythic"], weights=[0.60, 0.28, 0.10, 0.02])[0]
        wild_p = random.choice(POKEMON_POOL[tier])
        rates = {"Common": 0.75, "Rare": 0.45, "Legendary": 0.15, "Mythic": 0.04}
        
        embed = discord.Embed(title="🌿 S HUNT: Tall Grass Exploration Scene!", description=f"You encountered a wild **[{tier}] {wild_p['name']}**!", color=discord.Color.green())
        
        if random.random() <= rates[tier]:
            owned = any(p["name"] == wild_p["name"] for p in prof["pokemon"])
            if owned:
                bounty = random.randint(5000, 15000)
                prof["sycoizz"] += bounty
                embed.description += f"\n\n✨ **Caught!** Duplication asset detected. Clean parsed conversion reward credit added: `+{bounty:,}` sycoizz!"
            else:
                prof["pokemon"].append({"name": wild_p["name"], "emoji": wild_p["emoji"], "hp": wild_p["hp"], "attack": wild_p["attack"], "equipped_weapon": None})
                embed.description += f"\n\n🎉 **SUCCESSFUL CAPTURE STAGE SECURED!** Transferred {wild_p['emoji']} **{wild_p['name']}** straight into your companion bag profile ledger data fields!"
        else:
            embed.description += f"\n\n💨 *Ball fragmented! The wild Pokémon escaped through the brush cover branches...*"

        await ctx.send(embed=embed)

    @hunt_pokemon.error
    async def hunt_errors(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏱️ **Tracking Exhaustion!** The tall grass fields are quiet. Ready again in `{error.retry_after:.1f}` seconds.")

async def setup(bot):
    await bot.add_cog(HuntEngine(bot))
  
