import discord
import json
import os
import logging
from discord.ext import commands
from discord.commands import SlashCommandGroup 
from discord.ui import View, Container

class ContainerManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.containers_data = {}
        self.file = "containers.json"
        self.load_containers()

    
    # ────────── persistence helpers ──────────
    def save_containers(self):
        with open(self.file, "w") as f:
            json.dump(self.containers_data, f)

    
    def load_containers(self):
        if not os.path.isfile(self.file) or os.path.getsize(self.file) == 0:
            self.containers_data = {}
            return
        
        try:
            with open(self.file, "r") as f:
                self.containers_data = json.load(f)
        except json.JSONDecodeError as e:
            logging.warning("containers.json was corrupt or empty: %s", e)
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
            

        new_container = {"name": name, "content": []}
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

    @container.command(name="show", description="Show your Container")
    @commands.has_permissions(administrator=True)
    async def show(self, ctx: discord.ApplicationContext, name: str, channel: discord.TextChannel, mode: discord.Option(str, choices=['public', 'private'])):  # type: ignore
        guild_id = str(ctx.guild.id)
        containers = self.containers_data.get(guild_id, [])

        target = next((c for c in containers if c["name"] == name), None)
        if target is None:
            await ctx.response.send_message(f'There is no container called "{name}".', ephemeral=True)
            return
        
        container = Container()
        content = target.get("content", {})
        for item in content:
            item_type = item.get("type")
            if item_type == "title":
                container.add_text(f"# {item.get('text', '')}")
            elif item_type == "text":
                container.add_text(item.get("text", ""))
            elif item_type == "separator":
                container.add_separator()
            elif item_type == "button":
                print("TODO")
            elif item_type == "dropdown":
                print("TODO")
            elif item_type == "image":
                print("TODO")
            
        view = View(container, timeout=None)

        if mode == "private":
            await ctx.respond(view=view, ephemeral=True)
        else:
            await channel.send(view=view)
            await ctx.respond(f"Container **{name}** was successfully sent in {channel.mention}.", ephemeral=True)


    @container.command(name="remove_element", description="Remove a element from your container.")
    @commands.has_permissions(administrator=True)
    async def remove_element(self, ctx: discord.ApplicationContext, name: str, id: str):
        guild_id = str(ctx.guild.id)
        containers = self.containers_data.get(guild_id, [])

        target = next((c for c in containers if c["name"] == name), None)
        if target is None:
            await ctx.response.send_message(f'There is no container called "{name}".', ephemeral=True)
            return
        
        element = next((e for e in target["content"] if e.get("id") == id), None)

        if element is None:
            await ctx.response.send_message(f'There is no container with Id **{id}** in **{name}**.', ephemeral=True)
            return

        target["content"].remove(element)
        self.save_containers()
        await ctx.response.send_message(f"Succesfully deleted Element with id **{id}** from **{name}**", ephemeral=True)




    # ──────────────────── slash‑command subgroup create_elemeent ────────────────────
    add_element = container.create_subgroup("add_element", "Add a element to your container.")

    @add_element.command(name="title", description="Add a title to your container")
    @commands.has_permissions(administrator=True)
    async def title(self, ctx: discord.ApplicationContext, name: str, title: str, id: str):
        guild_id = str(ctx.guild.id)
        containers = self.containers_data.get(guild_id, [])

        target = next((c for c in containers if c["name"] == name), None)
        if target is None:
            await ctx.response.send_message(f'There is no container called "{name}".', ephemeral=True)
            return
        
        if any(element.get("id") == id for element in target["content"]):
            await ctx.response.send_message(f'The id "{id}" already exists in the container. Please choose another id.', ephemeral=True)
            return

        new_title = {
            "type": "title",
            "text": title,
            "id": id
        }
        
        target["content"].append(new_title)
        self.save_containers()
        await ctx.response.send_message(f'Successfully added new title with id **{id}** to **{name}**', ephemeral=True)

    
    @add_element.command(name="text", description="Add a text to your container")
    @commands.has_permissions(administrator=True)
    async def text(self, ctx: discord.ApplicationContext, name: str, text: str, id: str):
        guild_id = str(ctx.guild.id)
        containers = self.containers_data.get(guild_id, [])

        target = next((c for c in containers if c["name"] == name), None)
        if target is None:
            await ctx.response.send_message(f'There is no container called "{name}".', ephemeral=True)
            return
        
        if any(element.get("id") == id for element in target["content"]):
            await ctx.response.send_message(f'The id "{id}" already exists in the container. Please choose another id.', ephemeral=True)
            return

        new_text = {
            "type": "text",
            "text": text,
            "id": id
        }
        
        target["content"].append(new_text)
        self.save_containers()
        await ctx.response.send_message(f'Successfully added new text with id **{id}** to **{name}**', ephemeral=True)


    @add_element.command(name="separator", description="Add a separator to your container")
    @commands.has_permissions(administrator=True)
    async def separator(self, ctx: discord.ApplicationContext, name: str, id: str):
        guild_id = str(ctx.guild.id)
        containers = self.containers_data.get(guild_id, [])

        target = next((c for c in containers if c["name"] == name), None)
        if target is None:
            await ctx.response.send_message(f'There is no container called "{name}".', ephemeral=True)
            return
        
        if any(element.get("id") == id for element in target["content"]):
            await ctx.response.send_message(f'The id "{id}" already exists in the container. Please choose another id.', ephemeral=True)
            return

        new_text = {
            "type": "separator",
            "id": id
        }
        
        target["content"].append(new_text)
        self.save_containers()
        await ctx.response.send_message(f'Successfully added new separator with id **{id}** to **{name}**', ephemeral=True)





def setup(bot):
    bot.add_cog(ContainerManager(bot))


#TODO: contianer: add_element(image / Btn  / dropdown), show(Image/ Btn / dropdown) remove_element, show_ids, move_element, clear 
# Maybe edit_name

# TODO: Make better textes, command parameters, descriptions!