import discord
from discord.ext import commands
from discord.ui import Container, View, MediaGallery, TextDisplay, Thumbnail

AUTOROLE_IDS = [1388242446076477530, 1323949668199305236] # IDs for Roles that users get after join
JOIN_CHANNEL = 1386305196279205908 # Channel to show Welcome-Message



class OnJoin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        # Ignore Bots
        if member.bot:
            return
        
        container = Container() # Create a UI Container
        member_count = sum(1 for m in member.guild.members if not m.bot) # Counts current members, excluding bots
        thumbnail = Thumbnail(member.avatar.url) # User's Avatar
        roles = [member.guild.get_role(role) for role in AUTOROLE_IDS] # Get roles by their IDs

        #Create Buttons (Introduce yourself, Show Your Projects, Informations)
        Introduce_Yourself_Button = discord.ui.Button(
            label="Introduce Yourself",
            style=discord.ButtonStyle.link,
            url="https://discord.com/channels/1321476283632189481/1386305307017347122"
        )

        Project_Button = discord.ui.Button(
            label="Show Your Projects",
            style=discord.ButtonStyle.link,
            url="https://discord.com/channels/1321476283632189481/1424068050654855229"
        )

        Informations_Button = discord.ui.Button(
            label="Informations",
            style=discord.ButtonStyle.link,
            url="https://discord.com/channels/1321476283632189481/1368520205428330566"
        )


        # Build UI-Container
        container.add_section(TextDisplay(
            f"# Welcome {member.mention} \n"
            f"Welcome to **Rootware Developers**, you are our **#{member_count}** member. We are glad to have you here!"
        ), accessory=thumbnail)
        container.add_separator()
        container.add_item(Introduce_Yourself_Button)
        container.add_item(Project_Button)
        container.add_item(Informations_Button)
        WelcomeBanner = MediaGallery()
        WelcomeBanner.add_item("https://cdn.discordapp.com/attachments/1387428754871156808/1395769977054957698/WLC3_Banner.png?ex=687ba796&is=687a5616&hm=f81d2f977fcf411af4807ad67ab3ef3294be35b439b43638b93da9a6ae685205&") # URL to Welcome-Banner-Image
        container.add_item(WelcomeBanner)

        # Send message in join channel
        view = View(container, timeout=None)
        channel = self.bot.get_channel(JOIN_CHANNEL)
        await channel.send(view=view)
        # Assign autoroles to the new member
        await member.add_roles(*roles, reason="Autorole")
        


def setup(bot):
    bot.add_cog(OnJoin(bot))

   