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
        
        rarity_tier = random.choices(["Common", "Rare", "Legendary", "Mythic"], weights=[0.60, 0.28, 0.10, 0.02])[0]
        wild_pokemon = random.choice(POKEMON_POOL[rarity_tier])
        
        capture_rates = {"Common": 0.75, "Rare": 0.45, "Legendary": 0.15, "Mythic": 0.04}
        
        embed = discord.Embed(
            title="🌿 Tall Grass Exploration Encounter!",
            description=f"A wild **[{rarity_tier}] {wild_pokemon['name']}** appeared right in front of you!",
            color=discord.Color.green()
        )
        
        roll = random.random()
        if roll <= capture_rates[rarity_tier]:
            already_owned = any(p["name"] == wild_pokemon["name"] for p in prof["pokemon"])
            
            if already_owned:
                bounty = random.randint(5000, 15000)
                prof["sycoizz"] += bounty
                embed.description += f"\n\n✨ You caught it! Since you already owned this sticker, it converted into a duplication reward of `+{bounty:,}` sycoizz!"
            else:
                new_capture = {
                    "name": wild_pokemon["name"],
                    "emoji": wild_pokemon["emoji"],
                    "hp": wild_pokemon["hp"],
                    "attack": wild_pokemon["attack"],
                    "equipped_weapon": None
                }
                prof["pokemon"].append(new_capture)
                embed.description += f"\n\n🎉 **SUCCESSFUL CAPTURE!** Added {wild_pokemon['emoji']} **{wild_pokemon['name']}** to your profile inventory."
        else:
            embed.description += f"\n\n💨 *Oh no! The wild Pokémon broke out of the ball and fled!*"

        await ctx.send(embed=embed)

    @hunt_pokemon.error
    async def hunt_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏱️ You are moving too fast! Wait `{error.retry_after:.1f}` seconds before searching the grass.")

async def setup(bot):
    await bot.add_cog(HuntEngine(bot))
  
