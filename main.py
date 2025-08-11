import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
from cogs.appeals import load_appeal_buttons, AppealPersistentView
load_dotenv() # loads the token from the .env file


intents = discord.Intents.default()
intents.message_content = True
intents.members = True # receive member events
bot = commands.Bot(command_prefix="!", intents=intents)


# list of Cogs to be loaded at startup
cogs_list = [
    "OnJoin",
    "rules",
    "warning",
    "mute",
    "ban"
]

@bot.event
async def on_ready():
    # load stored Appeal-Buttons on restart
    stored_buttons = load_appeal_buttons()
    if stored_buttons:
        view = AppealPersistentView(bot)
        # adds stored Appeal-Buttons to view
        for b in stored_buttons:
            view.add_button(b["case"], b["user_id"], b["case_type"])
        bot.add_view(view)
    print(f"Bot is now online!")


async def main():
    # loads all Cogs from the list
    async with bot:
        for cog in cogs_list:
            bot.load_extension(f"cogs.{cog}")
        await bot.start(os.getenv("TOKEN"))


asyncio.run(main())
