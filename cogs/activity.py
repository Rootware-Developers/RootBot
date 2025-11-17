import discord
from discord.ext import commands, tasks
from discord.commands import slash_command
from datetime import datetime, timedelta
import aiosqlite

REPORT_CHANNEL_ID = 1436830059746037866
ABSENCE_CHANNEL_ID = 1436830059746037866
APPROVED_ABSENCE_LOG_ID = 1387427212642484275
WARNING_CHANNEL_ID = 1403335929330008206

TRACKED_USERS = {
    718410140637986889: "Kittys",
    1024386008416006215: "Filzstift",
    1076385334159482952: "Load",
    1241822963909787699: "Luca",
}

MIN_MESSAGES = 3
WEEKLY_GOAL = 100


class ActivityDB:
    def __init__(self):
        self.db_path = "activity.db"

    async def setup(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    user_id INTEGER,
                    date TEXT,
                    count INTEGER,
                    PRIMARY KEY (user_id, date)
                )
            """)
            await db.commit()

    async def exec(self, query, params=()):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(query, params)
            await db.commit()

    async def one(self, query, params=()):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(query, params) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {"count": row[0]}  # Return as dict to match original usage
                return None


class AbsenceModal(discord.ui.Modal):
    def __init__(self, bot, user_id: int):
        self.bot = bot
        self.user_id = user_id
        super().__init__(
            discord.ui.InputText(label="Away From (DD/MM/YYYY)", placeholder="e.g. 13/10/2025", required=True),
            discord.ui.InputText(label="Until (DD/MM/YYYY)", placeholder="e.g. 22/10/2025", required=True),
            discord.ui.InputText(label="Reason", placeholder="Birthday week, don’t have time", required=True),
            discord.ui.InputText(label="Notes (optional)", style=discord.InputTextStyle.long, required=False),
            title="Submit Absence",
            timeout=None
        )

    async def callback(self, interaction: discord.Interaction):
        away_from = self.children[0].value
        until = self.children[1].value
        reason = self.children[2].value
        notes = self.children[3].value

        embed = discord.Embed(title="Absence Request", color=discord.Color.yellow(), timestamp=datetime.utcnow())
        embed.add_field(name="User", value=f"<@{self.user_id}>", inline=False)
        embed.add_field(name="Away From", value=away_from, inline=True)
        embed.add_field(name="Until", value=until, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        if notes:
            embed.add_field(name="Notes", value=notes, inline=False)

        view = AbsenceActionView(self.user_id)
        channel = self.bot.get_channel(ABSENCE_CHANNEL_ID)
        await channel.send(embed=embed, view=view)
        await interaction.response.send_message("✅ Your absence request was submitted.", ephemeral=True)


class AbsenceActionView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green, custom_id="absence_accept_button")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.client.get_user(self.user_id)
        if user:
            await user.send("✅ Your absence request has been **approved**.")
        log_channel = interaction.client.get_channel(APPROVED_ABSENCE_LOG_ID)
        await log_channel.send(f"✅ Absence approved for {user.mention if user else self.user_id}.")
        await interaction.response.send_message("Absence approved.", ephemeral=True)

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red, custom_id="absence_decline_button")
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.client.get_user(self.user_id)
        modal = DeclineReasonModal(user)
        await interaction.response.send_modal(modal)


class DeclineReasonModal(discord.ui.Modal):
    def __init__(self, user):
        self.user = user
        super().__init__(
            discord.ui.InputText(label="Reason for Decline", placeholder="Explain why it was declined", required=True),
            title="Decline Absence",
            timeout=None
        )

    async def callback(self, interaction: discord.Interaction):
        reason = self.children[0].value
        if self.user:
            await self.user.send(f"❌ Your absence request was **declined**.\nReason: {reason}")
        await interaction.response.send_message("Declined and user notified.", ephemeral=True)


class activity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = ActivityDB()
        self.weekly_report.start()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"✅ Cog Loaded: {self.__class__.__name__}")
        self.bot.add_view(AbsenceActionView(user_id=0))
        await self.db.setup()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.author.id in TRACKED_USERS:
            date_str = datetime.utcnow().strftime("%Y-%m-%d")
            await self.db.exec(
                "INSERT INTO messages(user_id, date, count) VALUES(?, ?, 1) "
                "ON CONFLICT(user_id, date) DO UPDATE SET count = count + 1;",
                (message.author.id, date_str),
            )

    @slash_command(name="absence", description="Submit an absence request.")
    async def absence(self, ctx):
        await ctx.send_modal(AbsenceModal(self.bot, ctx.author.id))

    @tasks.loop(hours=24)
    async def weekly_report(self):
        now = datetime.utcnow()
        if now.weekday() == 0 and now.hour == 0:
            report_channel = self.bot.get_channel(REPORT_CHANNEL_ID)
            warning_channel = self.bot.get_channel(WARNING_CHANNEL_ID)
            start_date = (now - timedelta(days=7)).strftime("%d/%m/%Y")
            end_date = now.strftime("%d/%m/%Y")

            msg = f"**{start_date} - {end_date}**\n\n"
            msg += "-# 🟢 = Did reach daily minimum activity\n"
            msg += "-# 🟠 = In Absence\n"
            msg += "-# 🔴 = Didn't reach daily minimum activity\n\n"

            for uid, name in TRACKED_USERS.items():
                msg += f"**{name}:**\n"
                total_messages = 0
                red_days = 0

                for i in range(7):
                    day = (now - timedelta(days=7 - i)).strftime("%Y-%m-%d")
                    result = await self.db.one("SELECT count FROM messages WHERE user_id = ? AND date = ?", (uid, day))
                    count = result["count"] if result else 0
                    total_messages += count
                    if count < MIN_MESSAGES:
                        red_days += 1

                    emoji = "🟢" if count >= MIN_MESSAGES else "🔴"
                    msg += f"> **{(now - timedelta(days=7 - i)).strftime('%A')}:** {emoji}"
                    if count < MIN_MESSAGES:
                        msg += f" ({count})"
                    msg += "\n"

                goal_status = "✅ Weekly goal reached!" if total_messages >= WEEKLY_GOAL else f"❌ {total_messages}/{WEEKLY_GOAL}"
                msg += f"> **Total:** {goal_status}\n\n"

                if red_days >= 2:
                    user = self.bot.get_user(uid)
                    date_str = now.strftime("%d/%m/%Y")
                    warn_message = (
                        f"# **Warn(2)**\n\n"
                        f"**User**\n"
                        f"`{user.mention if user else name}`\n\n"
                        f"**Date:**\n"
                        f"`{date_str}`\n\n"
                        f"**Reason:**\n"
                        f"`Minimum activity not reached`"
                    )
                    await warning_channel.send(warn_message)

            await report_channel.send(msg)
            await self.db.exec("DELETE FROM messages")

    @weekly_report.before_loop
    async def before_weekly_report(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(activity(bot))
