import discord
import json
import os
from discord.ext import commands

class JoinRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.join_roles_data = {}
        self.file = "join_roles.json"
        self.load_roles()
    
    def load_roles(self):
        if os.path.isfile(self.file):
            with open(self.file, "r") as f:
                self.join_roles_data = json.load(f)
        else:
            self.join_roles_data = {}

    def save_roles(self):
        with open(self.file, "w") as f:
            json.dump(self.join_roles_data, f)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = str(member.guild.id)
        if guild_id not in self.join_roles_data:
            return
        
        roles_ids = self.join_roles_data[guild_id]
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
    # Slash-Commands werden separat registriert
    join_roles = discord.app_commands.Group(name="join_roles", description="Manage join roles")
    
    @join_roles.command(name="add", description="Add a role to be assigned on join")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def add(interaction: discord.Interaction, role: discord.Role):
        cog = interaction.client.get_cog("JoinRoles")
        guild_id = str(interaction.guild.id)
        
        if guild_id not in cog.join_roles_data:
            cog.join_roles_data[guild_id] = []
        
        if role.id in cog.join_roles_data[guild_id]:
            await interaction.response.send_message(f"{role.mention} has already been added.", ephemeral=True)
            return
        
        cog.join_roles_data[guild_id].append(role.id)
        cog.save_roles()
        await interaction.response.send_message(f"{role.mention} is now awarded upon joining.", ephemeral=True)

    @join_commands.command(name="remove", description="Remove a join role")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def remove(interaction: discord.Interaction, role: discord.Role):
        cog = interaction.client.get_cog("JoinRoles")
        guild_id = str(interaction.guild.id)
        
        if guild_id not in cog.join_roles_data or role.id not in cog.join_roles_data[guild_id]:
            await interaction.response.send_message(f"{role.mention} is not saved as join role.", ephemeral=True)
            return
        
        cog.join_roles_data[guild_id].remove(role.id)
        cog.save_roles()
        await interaction.response.send_message(f"{role.mention} is no longer awarded upon entry", ephemeral=True)

    @join_roles.command(name="list", description="List all join roles")
    async def list(interaction: discord.Interaction):
        cog = interaction.client.get_cog("JoinRoles")
        guild_id = str(interaction.guild.id)
        
        if not cog.join_roles_data.get(guild_id):
            await interaction.response.send_message("You have not defined any join roles", ephemeral=True)
            return
        
        roles = []
        for role_id in cog.join_roles_data[guild_id]:
            role = interaction.guild.get_role(role_id)
            if role:
                roles.append(role.mention)

        embed = discord.Embed(
            title="Join Roles",
            description="These roles are automatically assigned to new members:\n\n" + "\n".join(roles),
            color=discord.Color.blurple()
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    bot.tree.add_command(join_roles)