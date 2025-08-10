import discord
import json
import os
import re
from discord.ext import commands
from discord.ui import Container, View
from datetime import datetime
from datetime import timedelta


# ---------- VARIABLES ----------
BAN_PERMS = 1388449595436044318 # Required role to Ban (ID)
LOG_CHANNEL = 1387425316577869994 # Channel to log bans
CASES_FILE = "data/cases.json" # JSON file to save cases
BANS_FILE = "data/bans.json" # JSON file to save bans


# ---------- GET NUMBER OF CASE ----------
def get_case():
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


# ---------- ADD BAN TO JSON ----------
def add_ban(case, user, moderator, reason):
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


# ---------- ADD UNBAN TO JSON ----------
def add_unmute(case, user_id, moderator, reason):
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



# ---------- COG ----------
class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  
        

    # --- BAN COMMAND (/ban) ---
    @discord.slash_command(name="ban", description="Ban a user from the Server")
    async def mute(self, ctx , user: discord.Member, reason: str):
        # > VARIABLES <
        LOGS_CONTAINER = Container()
        USER_CONTAINER = Container()
        MODERATOR = ctx.author
        CASE = get_case()


        # > CHECK IF USER HAS BAN PERMISSIONS <
        if not any(role.id == BAN_PERMS for role in MODERATOR.roles):
            await ctx.respond("You don't have the permissions to use this command.", ephemeral=True)
            return

        # > SAVE BAN <
        add_ban(CASE, user, MODERATOR, reason)


        # > USER CONTAINER <
        USER_CONTAINER.add_text("# <:banhammer:1400854673724018769> 〢 You got banned ")
        USER_CONTAINER.add_separator()
        USER_CONTAINER.add_text(
            f"> **<:paper:1397984129928265902>Reason:** `{reason}`\n"  
            f"> **<:moderator:1397981211640598719>Moderator: {MODERATOR.mention}** \n"
            f"> **<:wallet:1397981208763433112>Case:** `#{CASE}`"
        )
        USER_CONTAINER.add_separator()
        USER_CONTAINER.add_text("-# if you want to appeal your Ban, you need to contact devmatrix0815 (Better System is coming soon)")
        USER_VIEW = View(USER_CONTAINER, timeout=None)
        

        # > LOG CONTAINER <
        LOGS_CONTAINER.add_text("# <:banhammer:1400854673724018769> 〢 User got banned ")
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

        # > BAN THE USER <
        await user.ban(reason=reason)

        # > SENT THE CONTAINERS <
        CHANNEL = self.bot.get_channel(LOG_CHANNEL)
        await CHANNEL.send(view=LOG_VIEW) 
        await ctx.respond(view=LOG_VIEW, ephemeral=True) 
        await user.send(view=USER_VIEW) 



    # --- UNBAN COMMAND (/unban) ---
    @discord.slash_command(name="unban", description="Unban a user from the Server")
    async def unban(self, ctx , user_id: str, reason: str):
        # > VARIABLES <
        LOGS_CONTAINER = Container()
        USER_CONTAINER = Container()
        user = await self.bot.fetch_user(user_id)
        MODERATOR = ctx.author
        CASE = get_case()


        # > CHECK IF USER HAS UNBAN PERMISSIONS <
        if not any(role.id == BAN_PERMS for role in MODERATOR.roles):
            await ctx.respond("You don't have the permissions to use this command.", ephemeral=True)
            return

        # > SAVE BAN <
        add_unmute(CASE, user_id, MODERATOR, reason)


        # > USER CONTAINER <
        USER_CONTAINER.add_text("# <:circle_check_mark:1398677122091847731> 〢 You got unbanned ")
        USER_CONTAINER.add_separator()
        USER_CONTAINER.add_text(
            f"> **<:paper:1397984129928265902>Reason:** `{reason}`\n"  
            f"> **<:moderator:1397981211640598719>Moderator: {MODERATOR.mention}** \n"
            f"> **<:wallet:1397981208763433112>Case:** `#{CASE}`"
        )
        USER_CONTAINER.add_separator()
        USER_CONTAINER.add_text(f"-# {datetime.now().strftime('%b %d, %Y %I:%M %p')}")
        USER_VIEW = View(USER_CONTAINER, timeout=None)
        

        # > LOG CONTAINER <
        LOGS_CONTAINER.add_text("# <:circle_check_mark:1398677122091847731> 〢 User got unbanned ")
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

        # > UNBAN THE USER <
        await ctx.guild.unban(user)

        # > SENT THE CONTAINERS <
        CHANNEL = self.bot.get_channel(LOG_CHANNEL)
        await CHANNEL.send(view=LOG_VIEW) 
        await ctx.respond(view=LOG_VIEW, ephemeral=True) 
        await user.send(view=USER_VIEW) 



def setup(bot):
    bot.add_cog(Ban(bot))