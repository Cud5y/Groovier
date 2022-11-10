import os
import discord
from discord.ext import commands
import pycordSuperUtils
from pycordSuperUtils import MusicManager

client_id = "id"
client_secret = "secret"

client = commands.Bot(command_prefix='-', case_insensitive=True)
client.remove_command('help')
MusicManager = MusicManager(client, client_id=client_id,client_secret=client_secret,spotify_support=True)
@client.command()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')

@client.command()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')

for filename in os.listdir('./Cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'Cogs.{filename[:-3]}')

client.run('token')