import discord
from discord.ext import commands

PERMS_ROLES=[1323620437262991410, 1323619918771388506]



class Rules(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  

    @commands.command()
    async def rules(self, ctx):
        user = ctx.author
        
        if not any(role.id in PERMS_ROLES for role in user.roles):
            return
        
        rules = discord.Embed(
            title="Server rules",
            description="Please read and follow these rules to keep our community safe and enjoyable. Breaking the rules may result in warnings, timeouts or bans.",
            color=discord.Color.green()
        )
        rules.add_field(name="**1. Be respectful and helpful:**", value="Hate, harassment, or toxic behavior will not be tolerated.", inline=False)
        rules.add_field(name="**2. Only English:**", value="Only English is allowed in all channels.", inline=False)
        rules.add_field(name="**3.  Avoid politics or religious topics:**", value="This server is only for tech, coding, and development!", inline=False)
        rules.add_field(name="**4. No NSFW, extreme, or violent content:**", value="Memes are allowed, but use common sense and keep it appropriate.", inline=False)
        rules.add_field(name="**5. Self-promotion:**", value="Self-promotion is allowed only in the designated projects channel. No advertising via DMs.", inline=False)
        rules.add_field(name="**6. bots & tools:**", value="No custom bots or automated tools without permission.", inline=False)
        rules.add_field(name="**7. Stay on topic:**", value="Use the correct channels for your topics.", inline=False)
        rules.add_field(name="**8. Voice-chat rules:**", value="No yelling, no soundboards, and always stay respectful.")
        rules.add_field(name="**9. Chat behavior:**", value="No spam, trolling, or low-effort messages. Focus on valuable discussions.", inline=False)
        rules.add_field(name="**10. Support is voluntary:**", value="Don’t spam if you don’t get an answer right away. Be patient and polite.", inline=False)
        rules.add_field(name="**11. Code & questions:**", value="Use code blocks (```) for longer code. Ask clear and well-formulated questions.", inline=False)
        rules.add_field(name="**12. Discord-rules:**", value="Always follow the Discord [Terms of Service](https://discord.com/terms) and [Community Guidelines](https://discord.com/guidelines).", inline=False)

        rules.set_footer(text="Last Update: July 15, 2025")
        await ctx.send(embed=rules)
    


def setup(bot):
    bot.add_cog(Rules(bot))