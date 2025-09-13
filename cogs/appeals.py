import discord
from discord.ui import View, Button, Modal, InputText, Container
from datetime import datetime
import os
import json

APPEAL_CHANNEL = 1403335529633681418 # ID of the channel to which incoming appeals are sent
BUTTONS_FILE = "data/appeal_buttons.json" # File to save Appeal-Buttons persistent



class AppealReviewModal(Modal):
    # Modal for Moderators to accept / deny Appeals
    # Will be shown if a Moderator clicks on "Accept" / "Deny"
    def __init__(self, case: int, user: discord.User, accepted: bool, case_type: str, bot, view: 'AppealReviewView'):
        super().__init__(title=f"Response to Appeal for Case #{case}")
        self.case_id = case
        self.user = user
        self.accepted = accepted
        self.bot = bot
        self.case_type = case_type
        self.view = view

        self.add_item(InputText(
            label="Reason",
            placeholder="Enter reason...",
            style=discord.InputTextStyle.long,
            max_length=500
        ))    


    async def callback(self, interaction: discord.Interaction):
        REASON = self.children[0].value
        MODERATOR = interaction.user

        if self.accepted == True:
            # Depending on the case type, execute the appropriate “un” function
            if self.case_type ==  "warning":
                ctx = await self.bot.get_application_context(interaction)
                cog = self.bot.get_cog("Moderation")
                if cog:
                    guild = interaction.guild
                    member = guild.get_member(self.user.id) or await guild.fetch_member(self.user.id)
                    await cog.unwarn(ctx, user=member, case=self.case_id, reason=f"{REASON}")

            if self.case_type == "mute":
                ctx = await self.bot.get_application_context(interaction)
                cog = self.bot.get_cog("Moderation")
                if cog:
                    guild = interaction.guild
                    member = guild.get_member(self.user.id) or await guild.fetch_member(self.user.id) # to unmute a User, needed from Discord
                    await cog.unmute(ctx, user=member, reason=f"{REASON}")

            if self.case_type == "ban":
                ctx = await self.bot.get_application_context(interaction)
                cog = self.bot.get_cog("Moderation")
                if cog:
                    await cog.unban(ctx, user_id=self.user.id, reason=f"{REASON}")

            # Set embed visually to "accepted"
            self.view.embed.color = discord.Color.green()
            self.view.embed.set_footer(text="Status: Accepted")
            self.view.embed.description += f"\n **<:moderator:1397981211640598719>Claimed by: {MODERATOR.mention}**\n ```{REASON}```"
            await self.view.message.edit(embed=self.view.embed, view=None)

        else:
            # Inform users about denied appeal
            embed = discord.Embed(
                title=f"Your appeal for Case `#{self.case_id}` has been denied",
                description=f"```{REASON}```",
                color=discord.Colour.red()
            )
            await self.user.send(embed=embed)

            # Set embed visually to "denied"
            self.view.embed.color = discord.Color.red()
            self.view.embed.set_footer(text="Status: Denied")
            self.view.embed.description += f"\n **<:moderator:1397981211640598719>Claimed by: {MODERATOR.mention}**\n ```{REASON}```"
            await interaction.response.send_message(f"Denied appeal for Case #{self.case_id}.", ephemeral=True )
            await self.view.message.edit(embed=self.view.embed, view=None)



class AppealReviewView(View):
   # View with buttons for moderators to accept / deny appeal
   # Will be shown in Embed (AppealModal class) 
    def __init__(self, case_id: int, user: discord.User, embed: discord.Embed, case_type: str, bot):
        super().__init__(timeout=None)
        self.case_id = case_id
        self.user = user
        self.embed = embed
        self.bot = bot
        self.case_type = case_type
        self.message = None

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success, custom_id="appeal:accept")
    async def accept(self, button: Button, interaction: discord.Interaction):
        modal = AppealReviewModal(case=self.case_id, accepted=True, case_type=self.case_type, user=self.user, bot=self.bot, view=self)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.danger, custom_id="appeal:deny")
    async def deny(self, button: Button, interaction: discord.Interaction):
        modal = AppealReviewModal(case=self.case_id, accepted=False, case_type=self.case_type, user=self.user, bot=self.bot, view=self)
        await interaction.response.send_modal(modal)



class AppealModal(Modal):
    # Modal for users to submit an appeal to a case.
    def __init__(self, case: int, user: discord.User, bot, case_type: str, appeal_button: 'AppealButton'):
        super().__init__(title=f"Appeal for Case #{case}")
        self.case_id = case
        self.user = user
        self.bot = bot
        self.case_type = case_type
        self.appeal_button = appeal_button

        self.add_item(InputText(
            label="Why do you want to appeal this Case?",
            placeholder="Please explain...",
            style=discord.InputTextStyle.long,
            max_length=500
        ))

    async def callback(self, interaction: discord.Interaction):
        APPEAL_TEXT = self.children[0].value
        self.appeal_button.appealed = True # set Appealed to True, so the user can't appeal a second time
        save_appeal_button(self.case_id, self.user.id, True, case_type=self.case_type)

        await interaction.response.send_message(
            f"Your appeal for Case #{self.case_id} was successfully submitted.",
            ephemeral=True
        )
        # Embed is shown to Moderators with needed Appeal Informations
        embed = discord.Embed(
            title=f"Appeal Submitted - Case #{self.case_id}",
            description=f"**<:person:1397981170431688844>User: {self.user.mention}**\n ```{APPEAL_TEXT}```",
            color=discord.Colour.light_grey()
        )
        embed.set_footer(text="Status: Pending")

        # Add Buttons & send in Appeal Channel
        view = AppealReviewView(case_id=self.case_id, user=self.user, embed=embed, case_type=self.case_type, bot=self.bot)
        CHANNEL = self.bot.get_channel(APPEAL_CHANNEL)
        view.message = await CHANNEL.send(embed=embed, view=view)



class AppealButton(Button):
    # Button to submit an Appeal 
    # shown in Warning / Mute / Ban Container
    def __init__(self, case: int, user_id: int, case_type: str, bot):
        super().__init__(label="Appeal Case", style=discord.ButtonStyle.secondary, custom_id=f"appeal_button:{case}:{user_id}")
        self.case = case
        self.user_id = user_id
        self.bot = bot
        self.case_type = case_type
        self.appealed = False

    async def callback(self, interaction: discord.Interaction):
        user = await self.bot.fetch_user(self.user_id)

        if self.appealed:
            await interaction.response.send_message("You have already submitted an appeal for this case", ephemeral=True)
            return
            
        modal = AppealModal(case=self.case, user=user, case_type=self.case_type, bot=self.bot, appeal_button=self)
        await interaction.response.send_modal(modal)



def save_appeal_button(case: int, user_id: int, appealed: bool, case_type: str):
    # Saves the Appeal Button persistently in a Json File
    if not os.path.exists(BUTTONS_FILE):
        with open(BUTTONS_FILE, "w") as f:
            json.dump([], f)
    
    with open(BUTTONS_FILE, "r") as f:
        data = json.load(f)

    data.append({"case": case, "user_id": user_id, "case_type": case_type, "appealed": appealed})
    with open(BUTTONS_FILE, "w") as f:
        json.dump(data, f, indent=4)


def load_appeal_buttons():
    # Loads the appeal button from JSON File
    if not os.path.exists(BUTTONS_FILE):
        return []
    
    with open(BUTTONS_FILE, "r") as f:
        return json.load(f)
    


class AppealPersistentView(View):
    # View to add appeal buttons after restart
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    def add_button(self, case, user_id, case_type):
        # Check if user has just appealed for Case
        saved_buttons = load_appeal_buttons()
        appealed = any(entry["case"] == case and entry["user_id"] == user_id and entry["case_type"] == case_type and entry.get("appealed", False) for entry in saved_buttons)
        # generate Button
        btn = AppealButton(case=case, user_id=user_id, case_type=case_type, bot=self.bot)
        btn.appealed = appealed
        self.add_item(btn)