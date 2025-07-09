import discord
import json
import os
from discord.ext import commands
from discord import app_commands

class JoinRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.join_roles = {}
        self.file = "join_roles.json"
        self.load_roles()

    def load_roles(self):
        if os.path.isfile(self.file):
            with open(self.file, "r") as f:
                self.join_roles = json.load(f)
        else:
            self.join_roles = {}

    def save_roles(self):
        with open(self.file, "w") as f:
            json.dump(self.join_roles, f)


    @commands.Cog.listener()
    async def on_ready(self):
        try:
            await self.bot.tree.sync()
            print("Slash-Commands synced in JoinRoles Cog")
        except Exception as e:
            print(f"Error syncing JoinRoles commands: {e}")


    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild_id = str(member.guild.id)
        if guild_id not in self.join_roles:
            return

        role_ids = self.join_roles[guild_id]
        roles = [member.guild.get_role(rid) for rid in role_ids if member.guild.get_role(rid)]
        if roles:
            try:
                await member.add_roles(*roles, reason="Join roles assignment")
            except Exception as e:
                print(f"Error assigning join roles: {e}")



   
    @app_commands.command(name="add_join_role", description="Add a role to assign when a user joins")
    @app_commands.checks.has_permissions(administrator=True)
    async def add_join_role(self, interaction: discord.Interaction, role: discord.Role):
            guild_id = str(interaction.guild.id)
            if guild_id not in self.join_roles:
                self.join_roles[guild_id] = []

            if role.id in self.join_roles[guild_id]:
                await interaction.response.send_message(f"{role.mention} is already added.", ephemeral=True)
                return

            self.join_roles[guild_id].append(role.id)
            self.save_roles()
            await interaction.response.send_message(f"{role.mention} will be given to new members.", ephemeral=True)

    @app_commands.command(name="remove_join_role", description="Remove a role from the join list")
    @app_commands.checks.has_permissions(administrator=True)
    async def remove_join_role(self, interaction: discord.Interaction, role: discord.Role):
        guild_id = str(interaction.guild.id)
        if guild_id not in self.join_roles or role.id not in self.join_roles[guild_id]:
            await interaction.response.send_message(f"{role.mention} is not a join role.", ephemeral=True)
            return

        self.join_roles[guild_id].remove(role.id)
        self.save_roles()
        await interaction.response.send_message(f"{role.mention} removed from join roles.", ephemeral=True)



    @app_commands.command(name="list_join_roles", description="List all join roles")
    async def list_join_roles(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        if guild_id not in self.join_roles or not self.join_roles[guild_id]:
            await interaction.response.send_message("No join roles are set.", ephemeral=True)
            return

        roles = []
        for role_id in self.join_roles[guild_id]:
            role = interaction.guild.get_role(role_id)
            if role:
                roles.append(role.mention)

        embed = discord.Embed(
            title="Join Roles",
            description="\n".join(roles),
            color=discord.Color.blurple()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(JoinRoles(bot))

   