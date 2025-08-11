import discord
import json
import os
import re
from discord.ext import commands
from discord.ui import Container, View
from datetime import datetime
from datetime import timedelta
from .appeals import AppealButton, save_appeal_button

BAN_PERMS = 1388449595436044318 # Role ID requiered to use /mute & /umnute
LOG_CHANNEL = 1387425316577869994 # Channel to log bans / unbans
CASES_FILE = "data/cases.json" # File to save current Case Number
BANS_FILE = "data/bans.json" # file to save mutes


def get_case():
    # Increments and returns the current case number
    if not os.path.exists(CASES_FILE):
        with open (CASES_FILE, "w") as f:
            json.dump({"CASE": 0}, f)
            
    with open(CASES_FILE, "r") as f:
        data = json.load(f)

    data["CASE"] += 1
    NEXT_CASE = data["CASE"]

    with open(CASES_FILE, "w") as f:
        json.dump(data, f, indent=4)

    return NEXT_CASE


def add_ban(case, user, moderator, reason):
    # Adds a ban to the bans-file
    if not os.path.exists(BANS_FILE):
        with open (BANS_FILE, "w") as f:
            json.dump([], f)

    with open(BANS_FILE, "r") as f:
        BANS = json.load(f)

    BANS.append({
        "CASE": case,
        "USER_ID": user.id,
        "MODERATOR_ID": moderator.id,
        "REASON": reason,
        "TIMESTAMP": datetime.now().isoformat()
    })

    with open(BANS_FILE, "w") as f:
        json.dump(BANS, f, indent=4)


def add_unmute(case, user_id, moderator, reason):
    # Adds a unban to the bans-file
    if not os.path.exists(BANS_FILE):
        with open(BANS_FILE, "w") as f:
            json.dump([], f)
    
    with open(BANS_FILE, "r") as f:
        UNBANS = json.load(f)

    UNBANS.append({
        "CASE": case,
        "USER_ID": user_id,
        "MODERATOR_ID": moderator.id,
        "REASON": reason,
        "TIMESTAMP": datetime.now().isoformat()
    })

    with open(BANS_FILE, "w") as f:
        json.dump(UNBANS, f, indent=4)



class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  
        

    @discord.slash_command(name="ban", description="Ban a user from the Server")
    async def mute(self, ctx , user: discord.Member, reason: str):
        LOGS_CONTAINER = Container() # create UI Container for logs
        USER_CONTAINER = Container() # create UI Container for user
        MODERATOR = ctx.author
        CASE = get_case()


        # Check if user has the required role to ban
        if not any(role.id == BAN_PERMS for role in MODERATOR.roles):
            await ctx.respond("You don't have the permissions to use this command.", ephemeral=True)
            return

        # save ban to JSON file
        add_ban(CASE, user, MODERATOR, reason)
        # Create Appeal-Button & save to Json File
        APPEAL_BUTTON = AppealButton(CASE, user.id, "ban", self.bot)
        save_appeal_button(CASE, user.id, APPEAL_BUTTON.appealed, "ban")

        # message for user
        USER_CONTAINER.add_text("# <:banhammer:1404129307219066970>  You got banned ")
        USER_CONTAINER.add_separator()
        USER_CONTAINER.add_text(
            f"> **<:paper:1397984129928265902>Reason:** `{reason}`\n"  
            f"> **<:moderator:1397981211640598719>Moderator: {MODERATOR.mention}** \n"
            f"> **<:wallet:1397981208763433112>Case:** `#{CASE}`"
        )
        USER_CONTAINER.add_separator()
        USER_CONTAINER.add_item(APPEAL_BUTTON)
        USER_VIEW = View(USER_CONTAINER, timeout=None)
        
        # message for log channel
        LOGS_CONTAINER.add_text("# <:banhammer:1404129307219066970>  User got banned ")
        LOGS_CONTAINER.add_separator()
        LOGS_CONTAINER.add_text(
            f"> **<:person:1397981170431688844>User:** {user.mention}\n" 
            f"> **<:paper:1397984129928265902>Reason:** `{reason}`\n"  
            f"> **<:moderator:1397981211640598719>Moderator:** {MODERATOR.mention} \n"
            f"> **<:wallet:1397981208763433112>Case:** `#{CASE}`"
        )
        LOGS_CONTAINER.add_separator()
        LOGS_CONTAINER.add_text(f"-# {datetime.now().strftime('%b %d, %Y %I:%M %p')}")
        LOG_VIEW = View(LOGS_CONTAINER, timeout=None)

        # ban the user
        await user.ban(reason=reason)

        # send messages
        CHANNEL = self.bot.get_channel(LOG_CHANNEL)
        await CHANNEL.send(view=LOG_VIEW) 
        await ctx.respond(view=LOG_VIEW, ephemeral=True) 
        await user.send(view=USER_VIEW) 



    # --- UNBAN COMMAND (/unban) ---
    @discord.slash_command(name="unban", description="Unban a user from the Server")
    async def unban(self, ctx , user_id: str, reason: str):
        LOGS_CONTAINER = Container() # create UI Container for logs
        USER_CONTAINER = Container() # create UI Container for user
        user = await self.bot.fetch_user(user_id) # fetch user with entered User-ID
        MODERATOR = ctx.author
        CASE = get_case()


        # Check if user has the required role to ban
        if not any(role.id == BAN_PERMS for role in MODERATOR.roles):
            await ctx.respond("You don't have the permissions to use this command.", ephemeral=True)
            return

        # save unban to json
        add_unmute(CASE, user_id, MODERATOR, reason)

        # message for user
        USER_CONTAINER.add_text("# <:circle_check_mark:1398677122091847731>  You got unbanned ")
        USER_CONTAINER.add_separator()
        USER_CONTAINER.add_text(
            f"> **<:paper:1397984129928265902>Reason:** `{reason}`\n"  
            f"> **<:moderator:1397981211640598719>Moderator: {MODERATOR.mention}** \n"
            f"> **<:wallet:1397981208763433112>Case:** `#{CASE}`"
        )
        USER_CONTAINER.add_separator()
        USER_CONTAINER.add_text(f"-# **Rejoin:** https://discord.gg/dSeAXPPBBD")
        USER_VIEW = View(USER_CONTAINER, timeout=None)
        
        # message for log channel
        LOGS_CONTAINER.add_text("# <:circle_check_mark:1398677122091847731>  User got unbanned ")
        LOGS_CONTAINER.add_separator()
        LOGS_CONTAINER.add_text(
            f"> **<:person:1397981170431688844>User:** {user.mention}\n" 
            f"> **<:paper:1397984129928265902>Reason:** `{reason}`\n"  
            f"> **<:moderator:1397981211640598719>Moderator:** {MODERATOR.mention} \n"
            f"> **<:wallet:1397981208763433112>Case:** `#{CASE}`"
        )
        LOGS_CONTAINER.add_separator()
        LOGS_CONTAINER.add_text(f"-# {datetime.now().strftime('%b %d, %Y %I:%M %p')}")
        LOG_VIEW = View(LOGS_CONTAINER, timeout=None)

        # unban the user
        await ctx.guild.unban(user)

        # send messages
        CHANNEL = self.bot.get_channel(LOG_CHANNEL)
        await CHANNEL.send(view=LOG_VIEW) 
        await ctx.respond(view=LOG_VIEW, ephemeral=True) 
        await user.send(view=USER_VIEW) 



def setup(bot):
    bot.add_cog(Ban(bot))