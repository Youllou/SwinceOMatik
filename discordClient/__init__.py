# discord imports
import asyncio
import os

import discord
from discord.ext.commands import Bot
from discord import app_commands




# local import
from commands import Swince
from events import *


SWINCE_O_MATIK_TOKEN = os.getenv("SWINCE_O_MATIK_TOKEN")

if not SWINCE_O_MATIK_TOKEN:
    raise ValueError("SWINCE_O_MATIK_TOKEN is not set")




intents = discord.Intents.default()
intents.members = True
intents.reactions = True
MY_GUILD = 779434195784564787


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        # A CommandTree is a special type that holds all the application command
        # state required to make it work. This is a separate class because it
        # allows all the extra state to be opt-in.
        # Whenever you want to work with application commands, your tree is used
        # to store and work with them.
        # Note: When using commands.Bot instead of discord.Client, the bot will
        # maintain its own tree instead.
        self.tree = app_commands.CommandTree(self)

    # In this basic example, we just synchronize the app commands to one guild.
    # Instead of specifying a guild to every command, we copy over our global commands instead.
    # By doing so, we don't have to wait up to an hour until they are shown to the end-user.
    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


client = MyClient(intents=intents)
SwinceOMatik = Bot(command_prefix='stp ', intents=intents)
SwinceOMatik.client = client
SwinceOMatik.remove_command('help')


@SwinceOMatik.event
async def on_ready():
    for guild in SwinceOMatik.guilds:
        try:
            SwinceOMatik.tree.copy_global_to(guild=guild)
            await SwinceOMatik.tree.sync(guild=discord.Object(id=guild.id))
            print(f"Synced commands for guild: {guild.name} (ID: {guild.id})")
        except discord.HTTPException:
            print(f"Failed to sync commands for guild: {guild.name} (ID: {guild.id})")

    myCommands = await SwinceOMatik.tree.sync(guild=guild)
    for cmd in myCommands:
        if cmd.guild_id is None:  # it's a global slash command
            SwinceOMatik.tree._global_commands[cmd.name].id = cmd.id
        else:  # it's a guild specific command
            SwinceOMatik.tree._guild_commands[cmd.guild_id][cmd.name].id = cmd.id

# adding events_listener
event_listener = []

# adding commands_listener
command_listener = [
    Swince(SwinceOMatik),
]

if __name__ == '__main__':
    SwinceOMatik.me = 280464892258025473
    for event in event_listener:
        asyncio.run(SwinceOMatik.add_cog(event))

    for command in command_listener:
        asyncio.run(SwinceOMatik.add_cog(command))
    
    SwinceOMatik.run(SWINCE_O_MATIK_TOKEN)