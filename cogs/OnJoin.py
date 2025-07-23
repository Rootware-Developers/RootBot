import discord
from discord.ext import commands
from discord.ui import Container, View, MediaGallery, TextDisplay, Thumbnail

AUTOROLE_IDS = [1388242446076477530, 1323949668199305236]
JOIN_CHANNEL = 1386305196279205908



class JoinRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.bot:
            return
        
        container = Container()
        member_count = sum(1 for m in member.guild.members if not m.bot)
        thumbnail = Thumbnail(member.avatar.url)
        roles = [member.guild.get_role(role) for role in AUTOROLE_IDS]

        container.add_section(TextDisplay(
            f"# Welcome {member.mention} \n"
            f"Welcome to **Rootware Developers**, you are our **#{member_count}** member. We are glad to have you here!"
        ), accessory=thumbnail)
        container.add_separator()
        WelcomeBanner = MediaGallery()
        WelcomeBanner.add_item("https://cdn.discordapp.com/attachments/1387428754871156808/1395769977054957698/WLC3_Banner.png?ex=687ba796&is=687a5616&hm=f81d2f977fcf411af4807ad67ab3ef3294be35b439b43638b93da9a6ae685205&")
        container.add_item(WelcomeBanner)


        view = View(container, timeout=None)
        channel = self.bot.get_channel(JOIN_CHANNEL)
        await channel.send(view=view)
        await member.add_roles(*roles, reason="Autorole")
        


def setup(bot):
    bot.add_cog(JoinRoles(bot))

   