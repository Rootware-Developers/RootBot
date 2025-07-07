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


async def setup_hook():
    for cog in cogs_list:
        await bot.load_extension(f"cogs.{cog}")
    synced = await bot.tree.sync()
    print(f"✅ {len(synced)} Slash-Commands synced")


@bot.event
async def on_ready():
    print(f'Bot started succesfully!')

bot.run(os.getenv("TOKEN"))
