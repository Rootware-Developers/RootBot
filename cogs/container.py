import discord
import json
import os
from discord.ext import commands
from discord.commands import SlashCommandGroup 
from discord.ui import View, Container

class Container(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.containers_data = {}
        self.file = "containers"
        self.load_containers()

    
    # ────────── persistence helpers ──────────
    def save_containers(self):
        with open(self.file, "w") as f:
            json.dump(self.containers_data, f)

    
    def load_containers(self):
        if os.path.isfile(self.file):
            with open(self.file, "r") as f:
                self.containers_data = json.load(f)
        else:
            self.containers_data = {}



    # ──────────────────── slash‑command group ────────────────────
    container = SlashCommandGroup("container", "Manage your containers")

    @container.command(name="create", description="Create a Container")
    @commands.has_permissions(administrator=True)
    async def create(self, ctx: discord.ApplicationContext, name: str):
        guild_id = str(ctx.guild.id)

        if any(container["name"] == name for container in self.containers_data.get(guild_id, [])):
            await ctx.response.send_message(f'The container "{name}" already exists.', ephemeral=True)
            return
            

        new_container = {"name": name, "content": {}}
        self.containers_data.setdefault(guild_id, []).append(new_container)
        self.save_containers()
        await ctx.response.send_message(f'The container "{name}" was created succesfully', ephemeral=True)


    @container.command(name="remove", description="Remove a Container from your Guild")
    @commands.has_permissions(administrator=True)
    async def remove(self, ctx: discord.ApplicationContext, name: str):
        guild_id = str(ctx.guild.id)
        containers = self.containers_data.get(guild_id, [])

        target = next((c for c in containers if c["name"] == name), None)
        if target is None:
            await ctx.response.send_message(f'There is no container called "{name}".', ephemeral=True)
            return
        
        containers.remove(target)
        self.save_containers()
        await ctx.response.send_message(f'The container "{name}" was removed successfully.', ephemeral=True)


    @container.command(name="list", description="List your Containers")
    @commands.has_permissions(administrator=True)
    async def list (self, ctx: discord.ApplicationContext):
        guild_id = str(ctx.guild.id)

        if guild_id not in self.containers_data or not self.containers_data[guild_id]:
            await ctx.response.send_message("You don't have any containers.", ephemeral=True)
            return
        
        container_names = [c["name"] for c in self.containers_data[guild_id]]

        embed = discord.Embed(
            title="Containers",
            description="\n".join(container_names),
            color=discord.Color.blurple()
        )
        await ctx.response.send_message(embed=embed, ephemeral=True)



def setup(bot):
    bot.add_cog(Container(bot))


#TODO: contianer: show, add_element, remove_element, move_element, clear 
# Maybe /container edit: name, colro, etc. etc. 