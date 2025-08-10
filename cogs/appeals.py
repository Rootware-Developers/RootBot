import discord
from discord.ui import View, Button, Modal, InputText, Container
from datetime import datetime
import os
import json

APPEAL_CHANNEL = 1403335529633681418  
BUTTONS_FILE = "data/appeal_buttons.json"


class AppealReviewModal(Modal):
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
            if self.case_type ==  "warning":
                ctx = await self.bot.get_application_context(interaction)
                cog = self.bot.get_cog("Warning")
                if cog:
                    await cog.unwarn(ctx, case=self.case_id, reason=f"{REASON}")

            if self.case_type == "mute":
                ctx = await self.bot.get_application_context(interaction)
                cog = self.bot.get_cog("Mute")
                if cog:
                    guild = interaction.guild
                    member = guild.get_member(self.user.id) or await guild.fetch_member(self.user.id)
                    await cog.unmute(ctx, user=member, reason=f"{REASON}")

            self.view.embed.color = discord.Color.green()
            self.view.embed.set_footer(text="Status: Accepted")
            self.view.embed.description += f"\n > **<:moderator:1397981211640598719>Claimed by: {MODERATOR.mention}**\n> `{REASON}`"
            await self.view.message.edit(embed=self.view.embed, view=None)
            await interaction.response.send_message(f"Appeal #{self.case_id} has been accepted.", ephemeral=True)

        else:
            embed = discord.Embed(
                title=f"Your appeal for Case #{self.case_id} has been denied",
                description=f"`{REASON}`",
                color=discord.Colour.red()
            )
            await self.user.send(embed=embed)

            self.view.embed.color = discord.Color.red()
            self.view.embed.set_footer(text="Status: Denied")
            self.view.embed.description += f"\n > **<:moderator:1397981211640598719>Claimed by: {MODERATOR.mention}**\n> `{REASON}`"
            await self.view.message.edit(embed=self.view.embed, view=None)
            await interaction.response.send_message(f"Appeal #{self.case_id} has been denied.", ephemeral=True)



class AppealReviewView(View):
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
        self.appeal_button.appealed = True
        save_appeal_button(self.case_id, self.user.id, True, case_type=self.case_type)

        await interaction.response.send_message(
            f"Your appeal for Case #{self.case_id} has been submitted.",
            ephemeral=True
        )

        embed = discord.Embed(
            title=f"Appeal Submitted - Case #{self.case_id}",
            description=f"> **<:person:1397981170431688844>User:** {self.user.mention}\n> **<:paper:1397984129928265902>Reason:** `{APPEAL_TEXT}`",
            color=discord.Colour.light_grey()
        )
        embed.set_footer(text="Status: Pending")

        view = AppealReviewView(case_id=self.case_id, user=self.user, embed=embed, case_type=self.case_type, bot=self.bot)
        CHANNEL = self.bot.get_channel(APPEAL_CHANNEL)
        view.message = await CHANNEL.send(embed=embed, view=view)



class AppealButton(Button):
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
            await interaction.response.send_message("You have already appealed for this case.", ephemeral=True)
            return
            
        modal = AppealModal(case=self.case, user=user, case_type=self.case_type, bot=self.bot, appeal_button=self)
        await interaction.response.send_modal(modal)



def save_appeal_button(case: int, user_id: int, appealed: bool, case_type: str):
    if not os.path.exists(BUTTONS_FILE):
        with open(BUTTONS_FILE, "w") as f:
            json.dump([], f)
    
    with open(BUTTONS_FILE, "r") as f:
        data = json.load(f)

    data.append({"case": case, "user_id": user_id, "case_type": case_type, "appealed": appealed})
    with open(BUTTONS_FILE, "w") as f:
        json.dump(data, f, indent=4)


def load_appeal_buttons():
    if not os.path.exists(BUTTONS_FILE):
        return []
    
    with open(BUTTONS_FILE, "r") as f:
        return json.load(f)
    


class AppealPersistentView(View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    def add_button(self, case, user_id, case_type):
        saved_buttons = load_appeal_buttons()
        appealed = any(entry["case"] == case and entry["user_id"] == user_id and entry["case_type"] == case_type and entry.get("appealed", False) for entry in saved_buttons)

        btn = AppealButton(case=case, user_id=user_id, case_type=case_type, bot=self.bot)
        btn.appealed = appealed
        self.add_item(btn)