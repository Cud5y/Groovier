import discord
from discord.ext import commands

class Events(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Bot is online')
        await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='-play'))

def setup(client):
    client.add_cog(Events(client))