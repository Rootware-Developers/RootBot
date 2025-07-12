import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
import asyncio

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

cogs_list = [
    "JoinRoles",
    "container"
]

@bot.event
async def on_ready():
    print(f"Bot is now online!")

async def main():
    async with bot:
        for cog in cogs_list:
            bot.load_extension(f"cogs.{cog}")
        await bot.start(os.getenv("TOKEN"))

asyncio.run(main())