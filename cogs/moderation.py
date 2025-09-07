import re
import discord
from discord.ext import commands
from .get_case import get_case
from datetime import timedelta
from .manage_moderation_json import save_moderation_json
from .appeals import AppealButton, save_appeal_button
from .container import create_logs_container, create_user_container

WARN_PERMISSIONS = [1353126414869725456]
MUTE_PERMISSIONS = [1353126414869725456]
BAN_PERMISSIONS = [1323625301024047169]
LOG_CHANNEL = 1387425316577869994

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    # ---------- WARNINGS ----------
    @discord.slash_command(name="warn", description="Warn a user") # Add warning Command
    async def warn(self, ctx, user: discord.Member, reason: str):
        # Variables
        MODERATOR = ctx.author
        CASE = get_case()

        # Check if user has the required role to use this command
        if not any(role.id in WARN_PERMISSIONS for role in MODERATOR.roles):
            await ctx.respond("You don't have permissions to use this command.", ephemeral=True)
            return
        
        # Create & save appeal Button for USER Container
        APPEAL_BUTTON = AppealButton(CASE, user.id, "warning", self.bot)
        save_appeal_button(CASE, user.id, APPEAL_BUTTON.appealed, "warning")

        # Save case to JSON & create LOGS -and USER Containers
        save_moderation_json("ADD", "WARNING", CASE, user, MODERATOR, reason, None)
        LOGS_CONTAINER = create_logs_container("WARNING", "add", user, reason, MODERATOR, CASE, None)
        USER_CONTAINER = create_user_container("WARNING", "add", reason, MODERATOR, CASE, None, APPEAL_BUTTON)

        # Send Messages
        CHANNEL = self.bot.get_channel(LOG_CHANNEL)
        await CHANNEL.send(view=LOGS_CONTAINER)
        await ctx.respond(view=LOGS_CONTAINER, ephemeral=True)
        await user.send(view=USER_CONTAINER)


    @discord.slash_command(name="unwarn", description="Remove a warn from a user") # Remove warning Command
    async def unwarn(self, ctx, user: discord.Member, case: int, reason: str):
        # Variables
        MODERATOR = ctx.author

        # Check if user has the required role to use this command
        if not any(role.id in WARN_PERMISSIONS for role in MODERATOR.roles):
            await ctx.respond("You don't have permissions to use this command.", ephemeral=True)
            return

        # Save case to JSON & create LOGS -and USER Containers 
        save_moderation_json("REMOVE", "WARNING", case, user, MODERATOR, reason, None)
        LOGS_CONTAINER = create_logs_container("WARNING", "remove", user, reason, MODERATOR, case, None)
        USER_CONTAINER = create_user_container("WARNING", "remove", reason, MODERATOR, case, None)

        # Send Messages
        CHANNEL = self.bot.get_channel(LOG_CHANNEL)
        await CHANNEL.send(view=LOGS_CONTAINER)
        await ctx.respond(view=LOGS_CONTAINER, ephemeral=True)
        await user.send(view=USER_CONTAINER)


    # ---------- MUTES ----------
    @discord.slash_command(name="mute", description="Timeout a user") # Mute User Command
    async def mute(self, ctx , user: discord.Member, reason: str, duration: str):
        # Variables
        MODERATOR = ctx.author
        CASE = get_case()

        # Check if user has the required role to use this command
        if not any(role.id in MUTE_PERMISSIONS for role in MODERATOR.roles):
            await ctx.respond("You don't have permissions to use this command.", ephemeral=True)
            return
        

        # Fetch Duration of mute
        PATTERN = re.compile(r"(?:(\d+)d)?\s*(?:(\d+)h)?\s*(?:(\d+)m)?", re.IGNORECASE)
        MATCH = PATTERN.fullmatch(duration.strip())
        # If the duration format is invalid (expected m/h/d)
        if not MATCH:
            await ctx.respond("**Please use a valid duration format:** m, h, d", ephemeral=True)
            return

        # Separate duration in Days, Hours & Minutes
        DAYS = int(MATCH.group(1)) if MATCH.group(1) else 0
        HOURS = int(MATCH.group(2)) if MATCH.group(2) else 0
        MINUTES = int(MATCH.group(3)) if MATCH.group(3) else 0
        DURATION = timedelta(days=DAYS, hours=HOURS, minutes=MINUTES)
        # Check that durations isn't 0
        if DURATION.total_seconds() == 0:
            await ctx.respond("Duration must be greater than 0", ephemeral=True)
            return

        # Create & save appeal Button for USER Container
        APPEAL_BUTTON = AppealButton(CASE, user.id, "mute", self.bot)
        save_appeal_button(CASE, user.id, APPEAL_BUTTON.appealed, "mute")

        # Save case to JSON & create LOGS -and USER Containers
        save_moderation_json("ADD", "MUTE", CASE, user, MODERATOR, reason, DURATION)
        LOGS_CONTAINER = create_logs_container("MUTE", "add", user, reason, MODERATOR, CASE, DURATION)
        USER_CONTAINER = create_user_container("MUTE", "add", reason, MODERATOR, CASE, DURATION, APPEAL_BUTTON)

        # Mute the user
        await user.timeout_for(DURATION, reason=reason)

        # Send messages
        CHANNEL = self.bot.get_channel(LOG_CHANNEL)
        await CHANNEL.send(view=LOGS_CONTAINER) 
        await ctx.respond(view=LOGS_CONTAINER, ephemeral=True) 
        await user.send(view=USER_CONTAINER)


    @discord.slash_command(name="unmute", description="Remove a timeout from a user") # Unmute User Command
    async def unmute(self, ctx , user: discord.Member, reason: str):
        # Variables
        MODERATOR = ctx.author
        CASE = get_case()

        # Check if user has the required role to use this command
        if not any(role.id in MUTE_PERMISSIONS for role in MODERATOR.roles):
            await ctx.respond("You don't have permissions to use this command.", ephemeral=True)
            return

        # Save case to JSON & create LOGS -and USER Containers 
        save_moderation_json("REMOVE", "MUTE", CASE, user, MODERATOR, reason, None)
        LOGS_CONTAINER = create_logs_container("MUTE", "remove", user, reason, MODERATOR, CASE, None)
        USER_CONTAINER = create_user_container("MUTE", "remove", reason, MODERATOR, CASE, None)

        # Unmute the user
        await user.timeout(None, reason=reason)

        # Send messages
        CHANNEL = self.bot.get_channel(LOG_CHANNEL)
        await CHANNEL.send(view=LOGS_CONTAINER) 
        await ctx.respond(view=LOGS_CONTAINER, ephemeral=True) 
        await user.send(view=USER_CONTAINER)  


    # ---------- BANS ----------
    @discord.slash_command(name="ban", description="Ban a user from the Server") # Ban User Command
    async def ban(self, ctx , user: discord.Member, reason: str):
        # Variables
        MODERATOR = ctx.author
        CASE = get_case()

        # Check if user has the required role to use this command
        if not any(role.id in BAN_PERMISSIONS for role in MODERATOR.roles):
            await ctx.respond("You don't have permissions to use this command.", ephemeral=True)
            return

        # Create & save appeal Button for USER Container
        APPEAL_BUTTON = AppealButton(CASE, user.id, "ban", self.bot)
        save_appeal_button(CASE, user.id, APPEAL_BUTTON.appealed, "ban")

        # Save case to JSON & create LOGS -and USER Containers
        save_moderation_json("ADD", "BAN", CASE, user, MODERATOR, reason, None)
        LOGS_CONTAINER = create_logs_container("BAN", "add", user, reason, MODERATOR, CASE, None)
        USER_CONTAINER = create_user_container("BAN", "add", reason, MODERATOR, CASE, None, APPEAL_BUTTON)

        # Ban the user
        await user.ban(reason=reason)

        # Send messages
        CHANNEL = self.bot.get_channel(LOG_CHANNEL)
        await CHANNEL.send(view=LOGS_CONTAINER) 
        await ctx.respond(view=LOGS_CONTAINER, ephemeral=True) 
        await user.send(view=USER_CONTAINER) 


    @discord.slash_command(name="unban", description="Unban a user from the Server") # Unban User Command
    async def unban(self, ctx , user_id: str, reason: str):
        # Variables
        MODERATOR = ctx.author
        CASE = get_case()
        user = await self.bot.fetch_user(user_id) # fetch user with entered User-ID

        # Check if user has the required role to use this command
        if not any(role.id in BAN_PERMISSIONS for role in MODERATOR.roles):
            await ctx.respond("You don't have permissions to use this command.", ephemeral=True)
            return

        # Save case to JSON & create LOGS -and USER Containers 
        save_moderation_json("REMOVE", "BAN", CASE, user, MODERATOR, reason, None)
        LOGS_CONTAINER = create_logs_container("BAN", "remove", user, reason, MODERATOR, CASE, None)
        USER_CONTAINER = create_user_container("BAN", "remove", reason, MODERATOR, CASE, None)

        # Unban the user
        await ctx.guild.unban(user)

        # Send messages
        CHANNEL = self.bot.get_channel(LOG_CHANNEL)
        await CHANNEL.send(view=LOGS_CONTAINER) 
        await ctx.respond(view=LOGS_CONTAINER, ephemeral=True) 
        await user.send(view=USER_CONTAINER) 

    # ---------- VIEW_USER (TODO) ----------


def setup(bot):
    bot.add_cog(Moderation(bot))