import discord
from discord.ext import commands

PERMS_ROLES=[1323625301024047169] # Roles authorized to execute the !rules command


class Rules(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  

    @commands.command()
    async def rules(self, ctx):
        user = ctx.author
        # Check if user has at least one required Role
        if not any(role.id in PERMS_ROLES for role in user.roles):
            return
        
        # Embed with every rule
        rules = discord.Embed(
            title="Server rules",
            description="Please read and follow these rules to ensure a safe and welcoming community. Violations may result in warnings, timeouts, or bans.",
            color=discord.Color.green()
        )
        rules.add_field(name="**1️⃣  Be respectful and helpful:**", value="> Treat everyone respectfully and be helpful. Hate, harassment, or toxic behavior will not be tolerated.", inline=False)
        rules.add_field(name="**2️⃣  Only English:**", value="> Communicate in English only in all channels to ensure everyone can participate.", inline=False)
        rules.add_field(name="**3️⃣  Avoid politics or religious topics:**", value="> Avoid political or religious discussions. This server focuses on tech, coding, and development.", inline=False)
        rules.add_field(name="**4️⃣  No NSFW, extreme, or violent content:**", value="> No NSFW, extreme, or violent content. Memes are allowed but must remain appropriate.", inline=False)
        rules.add_field(name="**5️⃣  Self-promotion:**", value="> Self-promotion is only allowed in the designated projects channel. Advertising via DMs is prohibited.", inline=False)
        rules.add_field(name="**6️⃣  Stay on topic:**", value="> Keep discussions relevant. Use the appropriate channels for your topics.", inline=False)
        rules.add_field(name="**7️⃣  Voice-chat rules:**", value="> In voice channels, do not yell or use soundboards. Always remain respectful.")
        rules.add_field(name="**8️⃣  Chat behavior:**", value="> Avoid spamming, trolling, or low-effort messages. Contribute to meaningful discussions.", inline=False)
        rules.add_field(name="**9️⃣  Support is voluntary:**", value="> Support is voluntary. Be patient and polite if you don’t receive an immediate response.", inline=False)
        rules.add_field(name="**🔟  Code & questions:**", value="> Use code blocks (```) for longer snippets. Ask clear, well-formulated questions.", inline=False)
        rules.add_field(name="**📜  Discord-rules:**", value="> Always follow Discord's [Terms of Service](https://discord.com/terms) and [Community Guidelines](https://discord.com/guidelines).", inline=False)
        rules.set_footer(text="Last Update: September 6, 2025")

        # send Embed
        await ctx.send(embed=rules)


def setup(bot):
    bot.add_cog(Rules(bot))