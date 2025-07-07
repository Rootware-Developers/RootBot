import discord
import json
import os
from discord.ext import commands
from discord.commands import SlashCommandGroup


class JoinRoles(commands.Cog):

    join_roles = SlashCommandGroup("join_roles", "Manage join roles")

    def __init__(self, bot):
        self.bot = bot
        self.join_roles = {}
        self.file = "join_roles.json"
        self.load_roles()
    
    async def setup(bot: commands.Bot):
        cog = JoinRoles(bot)
        await bot.add_cog(cog)
        # Slash-Group registrieren
        bot.tree.add_command(cog.join_roles)


    def load_roles(self):
        if os.path.isfile(self.file):
            with open(self.file, "r") as f:
                self.join_roles = json.load(f)
        else:
            self.join_roles = {}

    def save_roles(self):
        with open(self.file, "w") as f:
            json.dump(self.join_roles, f)



    join_roles = discord.SlashCommandGroup("join_roles", "Manage join roles")

    @join_roles.command(name="add", description="Add a role to be assigned to a user on join")
    @commands.has_permissions(administrator=True)
    async def add(self, ctx, role: discord.Role):
        guild_id = str(ctx.guild.id)
        if guild_id not in self.join_roles:
            self.join_roles[guild_id] = []

        if role.id in self.join_roles[guild_id]:
            await ctx.respond(f"{role.mention} has already been added.", ephemeral=True)
            return
        
        self.join_roles[guild_id].append(role.id)
        self.save_roles()
        await ctx.respond(f"{role.mention} is now awarded upon joining.", ephemeral=True)

    @join_roles.command(name="remove", description="Remove a role from the join roles")
    @commands.has_permissions(administrator=True)
    async def remove(self, ctx, role: discord.Role):
        guild_id = str(ctx.guild.id)
        if guild_id not in self.join_roles or role.id not in self.join_roles[guild_id]:
            await ctx.respond(f"{role.mention} is not saved as join role.", ephemeral=True)
            return
        
        self.join_roles[guild_id].remove(role.id)
        self.save_roles()
        await ctx.respond(f"{role.mention} is no longer awarded upon entry", ephemeral=True)

    @join_roles.command(name="list", description="List all roles assigned on join")
    async def list(self, ctx):
        guild_id = str(ctx.guild.id)
        if guild_id not in self.join_roles or len(self.join_roles[guild_id]) == 0:
            await ctx.respond("You have hot defined any join roles", ephemeral=True)
            return
        
        roles = []
        for role_id in self.join_roles[guild_id]:
            role = ctx.guild.get_role(role_id)
            if role:
                roles.append(role.mention)

        embed = discord.Embed(
            title="Join Roles",
            description="These roles are automatically assigned to new members:\n\n" + "\n".join(roles),
            color=discord.Color.blurple()
        )

        await ctx.respond(embed=embed, ephemeral=True)



    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = str(member.guild.id)
        if guild_id not in self.join_roles:
            return
        
        roles_ids = self.join_roles[guild_id]
        roles_to_add = []

        for role_id in roles_ids:
            role = member.guild.get_role(role_id)
            if role:
                roles_to_add.append(role)

        if roles_to_add:
            try:
                await member.add_roles(*roles_to_add, reason="Joined the Server")
            except Exception as e:
                print(f"Error adding roles: {e}")



def setup(bot):
    bot.add_cog(JoinRoles(bot))