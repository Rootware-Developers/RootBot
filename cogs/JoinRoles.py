import discord
import json
import os
from discord.ext import commands
from discord.commands import SlashCommandGroup 


class JoinRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.join_roles = {}
        self.file = "join_roles.json"
        self.load_roles()


    # ────────── persistence helpers ──────────
    def load_roles(self):
        if os.path.isfile(self.file):
            with open(self.file, "r") as f:
                self.join_roles = json.load(f)
        else:
            self.join_roles = {}

    def save_roles(self):
        with open(self.file, "w") as f:
            json.dump(self.join_roles, f)


    # ────────── listeners ──────────
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




    # ──────────────────── slash‑command group ────────────────────
    joinroles = SlashCommandGroup("joinroles", "Manage joinroles")

    @joinroles.command(name="add", description="Add a role to assign when a user joins")
    @commands.has_permissions(administrator=True)
    async def add(self, ctx: discord.ApplicationContext, role: discord.Role):
            guild_id = str(ctx.guild.id)
            if guild_id not in self.join_roles:
                self.join_roles[guild_id] = []

            if role.id in self.join_roles[guild_id]:
                await ctx.respond(f"{role.mention} is already added.", ephemeral=True)
                return

            self.join_roles[guild_id].append(role.id)
            self.save_roles()
            await ctx.response.send_message(f"{role.mention} will be given to new members.", ephemeral=True)

    @joinroles.command(name="remove", description="Remove a role from the join list")
    @commands.has_permissions(administrator=True)
    async def remove(self, ctx: discord.ApplicationContext, role: discord.Role):
        
        guild_id = str(ctx.guild.id)
        if guild_id not in self.join_roles or role.id not in self.join_roles[guild_id]:
            await ctx.response.send_message(f"{role.mention} is not a join role.", ephemeral=True)
            return

        self.join_roles[guild_id].remove(role.id)
        self.save_roles()
        await ctx.response.send_message(f"{role.mention} removed from join roles.", ephemeral=True)



    @joinroles.command(name="list", description="List all join roles")
    async def list(self, ctx: discord.ApplicationContext):
        guild_id = str(ctx.guild.id)
        if guild_id not in self.join_roles or not self.join_roles[guild_id]:
            await ctx.response.send_message("No join roles are set.", ephemeral=True)
            return

        roles = []
        for role_id in self.join_roles[guild_id]:
            role = ctx.guild.get_role(role_id)
            if role:
                roles.append(role.mention)

        embed = discord.Embed(
            title="Join Roles",
            description="\n".join(roles),
            color=discord.Color.blurple()
        )
        await ctx.response.send_message(embed=embed, ephemeral=True)



# ────────── setup function ──────────
def setup(bot):
    bot.add_cog(JoinRoles(bot))

   