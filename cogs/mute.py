import discord
import json
import os
import re
from discord.ext import commands
from discord.ui import Container, View
from datetime import datetime
from datetime import timedelta
from .appeals import AppealButton, save_appeal_button

MUTE_PERMS = 1353126414869725456 # Role ID requiered to use /mute & /umnute
LOG_CHANNEL = 1387425316577869994 # Channel to log mutes / unmutes
CASES_FILE = "data/cases.json" # File to save current Case Number
MUTES_FILE = "data/mutes.json" # file to save mutes


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


def add_mute(case, user, moderator, reason, duration):
    # Adds a mute to the mutes-file
    if not os.path.exists(MUTES_FILE):
        with open (MUTES_FILE, "w") as f:
            json.dump([], f)

    with open(MUTES_FILE, "r") as f:
        MUTES = json.load(f)

    MUTES.append({
        "CASE": case,
        "USER_ID": user.id,
        "MODERATOR_ID": moderator.id,
        "REASON": reason,
        "DURATION": duration,
        "TIMESTAMP": datetime.now().isoformat()
    })

    with open(MUTES_FILE, "w") as f:
        json.dump(MUTES, f, indent=4)


def add_unmute(case, user, moderator, reason):
    # Adds a unmute to the mutes-file
    if not os.path.exists(MUTES_FILE):
        with open (MUTES_FILE, "w") as f:
            json.dump([], f)
    
    with open(MUTES_FILE, "r") as f:
        UNMUTES = json.load(f)

    UNMUTES.append({
        "CASE": case,
        "USER_ID": user.id,
        "MODERATOR_ID": moderator.id,
        "REASON": reason,
        "TIMESTAMP": datetime.now().isoformat()
    })

    with open(MUTES_FILE, "w") as f:
        json.dump(UNMUTES, f, indent=4)



class Mute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  
        

    @discord.slash_command(name="mute", description="Timeout a user")
    async def mute(self, ctx , user: discord.Member, reason: str, duration: str):
        LOGS_CONTAINER = Container() # create UI Container for logs
        USER_CONTAINER = Container() # create UI Container for user
        MODERATOR = ctx.author
        CASE = get_case()


        # Check if user has the required role to mute
        if not any(role.id == MUTE_PERMS for role in MODERATOR.roles):
            await ctx.respond("You don't have the permissions to use this command.", ephemeral=True)
            return
        

        # Fetch Duration of mute
        PATTERN = re.compile(r"(?:(\d+)d)?\s*(?:(\d+)h)?\s*(?:(\d+)m)?", re.IGNORECASE)
        MATCH = PATTERN.fullmatch(duration.strip())
        if not MATCH:
            await ctx.respond("**Please use a valid format:** m, h, d", ephemeral=True)
            return

        DAYS = int(MATCH.group(1)) if MATCH.group(1) else 0
        HOURS = int(MATCH.group(2)) if MATCH.group(2) else 0
        MINUTES = int(MATCH.group(3)) if MATCH.group(3) else 0
        DURATION = timedelta(days=DAYS, hours=HOURS, minutes=MINUTES)

        if DURATION.total_seconds() == 0:
            await ctx.respond("Duration must be higher than 0", ephemeral=True)
            return
        

        # Save mute to Json File
        add_mute(CASE, user, MODERATOR, reason, duration)
        # Create Appeal-Button & save to Json File
        APPEAL_BUTTON = AppealButton(CASE, user.id, "mute", self.bot)
        save_appeal_button(CASE, user.id, APPEAL_BUTTON.appealed, "mute")

        # Message for user
        USER_CONTAINER.add_text("# <:mute:1398921067762024449>  You got muted ")
        USER_CONTAINER.add_separator()
        USER_CONTAINER.add_text(
            f"> **<:paper:1397984129928265902>Reason:** `{reason}`\n"  
            f"> **<:moderator:1397981211640598719>Moderator: {MODERATOR.mention}** \n"
            f"> **<:timer:1398916124745142272>Duration:** `{duration}` \n"
            f"> **<:wallet:1397981208763433112>Case:** `#{CASE}`"
        )
        USER_CONTAINER.add_separator()
        USER_CONTAINER.add_item(APPEAL_BUTTON)
        USER_VIEW = View(USER_CONTAINER, timeout=None)
        
        # Message for log Channel
        LOGS_CONTAINER.add_text("# <:mute:1398921067762024449>  User got muted ")
        LOGS_CONTAINER.add_separator()
        LOGS_CONTAINER.add_text(
            f"> **<:person:1397981170431688844>User:** {user.mention}\n" 
            f"> **<:paper:1397984129928265902>Reason:** `{reason}`\n"  
            f"> **<:moderator:1397981211640598719>Moderator:** {MODERATOR.mention} \n"
            f"> **<:timer:1398916124745142272>Duration:** `{duration}` \n"
            f"> **<:wallet:1397981208763433112>Case:** `#{CASE}`"
        )
        LOGS_CONTAINER.add_separator()
        LOGS_CONTAINER.add_text(f"-# {datetime.now().strftime('%b %d, %Y %I:%M %p')}")
        LOG_VIEW = View(LOGS_CONTAINER, timeout=None)

        # mute suer
        await user.timeout_for(DURATION, reason=reason)

        # send messages
        CHANNEL = self.bot.get_channel(LOG_CHANNEL)
        await CHANNEL.send(view=LOG_VIEW) 
        await ctx.respond(view=LOG_VIEW, ephemeral=True) 
        await user.send(view=USER_VIEW) 


    @discord.slash_command(name="unmute", description="Remove a timeout from a user")
    async def unmute(self, ctx , user: discord.Member, reason: str):
        LOGS_CONTAINER = Container() # create UI Container for logs
        USER_CONTAINER = Container() # create UI Container for user
        MODERATOR = ctx.author
        CASE = get_case()


        # Check if user has the required role to mute
        if not any(role.id == MUTE_PERMS for role in MODERATOR.roles):
            await ctx.respond("You don't have the permissions to use this command.", ephemeral=True)
            return

        # save unmute to Json
        add_unmute(CASE, user, MODERATOR, reason)

        # message for user
        USER_CONTAINER.add_text("# <:circle_check_mark:1398677122091847731>  You got unmuted ")
        USER_CONTAINER.add_separator()
        USER_CONTAINER.add_text(
            f"> **<:paper:1397984129928265902>Reason:** `{reason}`\n"  
            f"> **<:moderator:1397981211640598719>Moderator: {MODERATOR.mention}** \n"
            f"> **<:wallet:1397981208763433112>Case:** `#{CASE}`"
        )
        USER_CONTAINER.add_separator()
        USER_CONTAINER.add_text(f"-# {datetime.now().strftime('%b %d, %Y %I:%M %p')}")
        USER_VIEW = View(USER_CONTAINER, timeout=None)
        
        # message for log Channel
        LOGS_CONTAINER.add_text("# <:circle_check_mark:1398677122091847731>  User got unmuted ")
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

        # unmute the user
        await user.timeout(None, reason=reason)

        # send messages
        CHANNEL = self.bot.get_channel(LOG_CHANNEL)
        await CHANNEL.send(view=LOG_VIEW) 
        await ctx.respond(view=LOG_VIEW, ephemeral=True) 
        await user.send(view=USER_VIEW) 



def setup(bot):
    bot.add_cog(Mute(bot))