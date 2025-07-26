import discord
import json
import os
from discord.ext import commands
from discord.ui import Container, View, Button
from datetime import datetime


# ---------- VARIABLES ----------
WARN_PERMS = 1353126414869725456 # Required role to warn (ID)
UNWARN_PERMS = [1388241809767006460, 1388449595436044318] # Required role to unwarn (ID)
LOG_CHANNEL = 1387425316577869994 # Channel to log warnings
CASES_FILE = "data/cases.json" # JSON file to save cases
WARNINGS_FILE = "data/warnings.json" # JSON file to save warnings


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


# ---------- ADD WARNING TO JSON ----------
def add_warning(case, user, moderator, reason):
    if not os.path.exists(WARNINGS_FILE):
        with open (WARNINGS_FILE, "w") as f:
            json.dump([], f)

    with open(WARNINGS_FILE, "r") as f:
        WARNINGS = json.load(f)

    WARNINGS.append({
        "CASE": case,
        "USER_ID": user.id,
        "MODERATOR_ID": moderator.id,
        "REASON": reason,
        "TIMESTAMP": datetime.now().isoformat()
    })

    with open(WARNINGS_FILE, "w") as f:
        json.dump(WARNINGS, f, indent=4)


# ---------- REMOVE WARNING TO JSON ----------
def remove_warning(CASE):
    if not os.path.exists(WARNINGS_FILE):
        return None
    
    with open(WARNINGS_FILE, "r") as f:
        WARNINGS = json.load(f)

    USER_ID = None
    UPDATED_WARNINGS = []

    for w in WARNINGS:
        if w.get("CASE") == CASE:
            USER_ID = w.get("USER_ID")
        else:
            UPDATED_WARNINGS.append(w)

    with open(WARNINGS_FILE, "w") as f:
        json.dump(UPDATED_WARNINGS, f, indent=4)

    return USER_ID



# ---------- COG ----------
class Warning(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  
        

    # --- WARN COMMAND (/warn) ---
    @discord.slash_command(name="warn", description="Warn a user")
    async def warn(self, ctx , user: discord.Member, reason: str):
        # > VARIABLES <
        LOGS_CONTAINER = Container()
        USER_CONTAINER = Container()
        MODERATOR = ctx.author
        CASE = get_case()

        # > CHECK IF USER HAS WARN PERMISSIONS <
        if not any(role.id == WARN_PERMS for role in MODERATOR.roles):
            await ctx.respond("You don't have the permissions to use this command.", ephemeral=True)
            return
        
        # > SAVE WARNING <
        add_warning(CASE, user, MODERATOR, reason)


        # > USER CONTAINER <
        USER_CONTAINER.add_text("# <:warning:1397873177283264594> 〢 You got warned ")
        USER_CONTAINER.add_separator()
        USER_CONTAINER.add_text(
            f"> **<:paper:1397984129928265902>Reason:** `{reason}`\n"  
            f"> **<:moderator:1397981211640598719>Moderator: {MODERATOR.mention}** \n"
            f"> **<:wallet:1397981208763433112>Case:** `#{CASE}`"
        )
        USER_CONTAINER.add_separator()
        APPEAL_BUTTON = Button(
            label="Appeal Warning",
            style=discord.ButtonStyle.link,
            url="https://discord.com/channels/1321476283632189481/1387329237215875193"
        )
        USER_CONTAINER.add_item(APPEAL_BUTTON)
        USER_VIEW = View(USER_CONTAINER, timeout=None)
        

        # > LOG CONTAINER <
        LOGS_CONTAINER.add_text("# <:warning:1397873177283264594> 〢 User got warned ")
        LOGS_CONTAINER.add_separator()
        LOGS_CONTAINER.add_text(
            f"> **<:person:1397981170431688844>User:** {user.mention}\n" 
            f"> **<:paper:1397984129928265902>Reason:** `{reason}`\n"  
            f"> **<:moderator:1397981211640598719>Moderator: {MODERATOR.mention}** \n"
            f"> **<:wallet:1397981208763433112>Case:** `#{CASE}`"
        )
        LOGS_CONTAINER.add_separator()
        LOGS_CONTAINER.add_text(f"-# {datetime.now().strftime('%b %d, %Y %I:%M %p')}")
        LOG_VIEW = View(LOGS_CONTAINER, timeout=None)


        # > SENT THE CONTAINERS <
        CHANNEL = self.bot.get_channel(LOG_CHANNEL)
        await CHANNEL.send(view=LOG_VIEW) 
        await ctx.respond(view=LOG_VIEW, ephemeral=True) 
        await user.send(view=USER_VIEW) 



    # --- UNWARN COMMAND (/unwarn) ---
    @discord.slash_command(name="unwarn", description="Remove a warn from a user")
    async def unwarn(self, ctx, case: int, reason: str):
        LOGS_CONTAINER = Container()
        USER_CONTAINER = Container()
        MODERATOR = ctx.author

        # > CHECK IF USER HAS UNWARN PERMISSIONS <
        if not any (role.id in UNWARN_PERMS for role in MODERATOR.roles):
            await ctx.respond("You don't have the permissions to use this command.", ephemeral=True)
            return
        
        # > REMOVE WARNING <
        USER_ID = remove_warning(case)

        if not USER_ID:
            await ctx.respond("No entry with this case found.", ephemeral=True)
            return
        

        # > USER CONTAINER <
        USER_CONTAINER.add_text("# <:circle_check_mark:1398677122091847731> 〢 You got unwarned ")
        USER_CONTAINER.add_separator()
        USER_CONTAINER.add_text(
            f"> **<:paper:1397984129928265902>Reason:** `{reason}`\n"  
            f"> **<:moderator:1397981211640598719>Moderator: {MODERATOR.mention}**"
        )
        USER_CONTAINER.add_separator()
        USER_CONTAINER.add_text(f"-# {datetime.now().strftime('%b %d, %Y %I:%M %p')}")
        USER_VIEW = View(USER_CONTAINER, timeout=None)


        # > LOG CONTAINER <
        LOGS_CONTAINER.add_text("# <:circle_check_mark:1398677122091847731> 〢 User got unwarned ")
        LOGS_CONTAINER.add_separator()
        LOGS_CONTAINER.add_text(
            f"> **<:person:1397981170431688844>User:** <@{USER_ID}>\n" 
            f"> **<:paper:1397984129928265902>Reason:** `{reason}`\n"  
            f"> **<:moderator:1397981211640598719>Moderator: {MODERATOR.mention}**"
        )
        LOGS_CONTAINER.add_separator()
        LOGS_CONTAINER.add_text(f"-# {datetime.now().strftime('%b %d, %Y %I:%M %p')}")
        LOG_VIEW = View(LOGS_CONTAINER, timeout=None)


        # > SENT THE CONTAINERS <
        CHANNEL = self.bot.get_channel(LOG_CHANNEL)
        USER = await self.bot.fetch_user(USER_ID)
        await CHANNEL.send(view=LOG_VIEW) 
        await ctx.respond(view=LOG_VIEW, ephemeral=True) 
        await USER.send(view=USER_VIEW) 



def setup(bot):
    bot.add_cog(Warning(bot))


# EMOJI CHANGES: user -> person, reason -> paper, warn -> warning, case -> wallet