# main.py
import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

# 🌟 ENHANCED PREFIX SPACE: Evaluates exact "s " command chains (with a required space)
bot = commands.Bot(command_prefix="s ", intents=intents, case_insensitive=True)

@bot.event
async def on_ready():
    print(f"==================================================")
    print(f"🌟 Termux RPG System Online! Loaded as: {bot.user.name}")
    print(f"👉 Core Prefix Space Activated: 's ' (e.g., s start, s cash, s boss)")
    print(f"==================================================")

async def main():
    async with bot:
        # Load up each individual feature slice from separate script assets
        await bot.load_extension("economy")
        await bot.load_extension("gambling")
        await bot.load_extension("shop")
        await bot.load_extension("battles")
        await bot.load_extension("hunt")
        
        TOKEN = os.getenv("discord_token") or os.getenv("DISCORD_TOKEN")
        if TOKEN:
            await bot.start(TOKEN)
        else:
            print("❌ SYSTEM ERROR: Neither 'discord_token' nor 'DISCORD_TOKEN' found inside .env file.")

if __name__ == "__main__":
    asyncio.run(main())
  
