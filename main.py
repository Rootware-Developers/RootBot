import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)


cogs_list = [
    "JoinRoles"
]
async def load_cogs():
    for cog in cogs_list:
        await bot.load_extension(f'cogs.{cog}')


@bot.event
async def on_ready():
    await load_cogs()
    print(f'Bot started succesfully!')
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} Slash-Commands synced: {[cmd.name for cmd in synced]}")
    except Exception as e:
        print(f"Error on Sync: {e}")

bot.run(os.getenv("TOKEN"))
