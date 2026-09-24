# main.py
import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

# Core framework engine setup with lowercase 's' prefix mapping
bot = commands.Bot(command_prefix="s", intents=intents, case_insensitive=True)

@bot.event
async def on_ready():
    print(f"==================================================")
    print(f"🌟 Termux RPG System Online! Loaded as: {bot.user.name}")
    print(f"👉 Core Prefix Activated: 's' (e.g., scash, sdaily, scf, shunt)")
    print(f"==================================================")

async def main():
    async with bot:
        # --- MODULAR REFACTOR HOT-LOADING CHANNELS ---
        # Seamlessly injects each separate sub-script into the runtime memory field
        await bot.load_extension("economy")    # Handles balance checks, transfers & daily reward systems
        await bot.load_extension("gambling")   # Handles slots, blackjack, coinflip physics, & lottery
        await bot.load_extension("shop")       # Handles bazaar store embeds, purchases & weapon equipping
        await bot.load_extension("battles")    # Handles arena text physics fights & monster leveling
        await bot.load_extension("hunt")       # Handles exploration catch algorithms
        
        # Read tokens from system environments or localized .env configurations
        TOKEN = os.getenv("discord_token") or os.getenv("DISCORD_TOKEN")
        if TOKEN:
            await bot.start(TOKEN)
        else:
            print("❌ SYSTEM ERROR: Neither 'discord_token' nor 'DISCORD_TOKEN' found inside .env file.")

if __name__ == "__main__":
    asyncio.run(main())
  
