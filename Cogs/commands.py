import random

import discord
from discord.commands import slash_command
from discord.ext import commands
import pycordSuperUtils
import datetime
import asyncio
from pycordSuperUtils import MusicManager

class Commands(commands.Cog,pycordSuperUtils.CogManager.Cog, name="Music"):

    def __init__(self, client):
        self.client = client
        self.client_id = "ddf765a360274a02a3cc44e8982e78aa"
        self.client_secret = "ce864f1f031e434ca1c291442a189841"
        self.MusicManager = MusicManager(self.client,client_id=self.client_id,client_secret=self.client_secret,spotify_support=True)

    @pycordSuperUtils.CogManager.event(pycordSuperUtils.MusicManager)
    async def on_music_error(self, ctx, error):
        errors = {
            pycordSuperUtils.NotPlaying: "Not playing any music right now...",
            pycordSuperUtils.NotConnected: f"Bot not connected to a voice channel!",
            pycordSuperUtils.NotPaused: "Player is not paused!",
            pycordSuperUtils.QueueEmpty: "The queue is empty!",
            pycordSuperUtils.AlreadyConnected: "Already connected to voice channel!",
            pycordSuperUtils.QueueError: "There has been a queue error!",
            pycordSuperUtils.SkipError: "There is no song to skip to!",
            pycordSuperUtils.UserNotConnected: "User is not connected to a voice channel!",
            pycordSuperUtils.InvalidSkipIndex: "That skip index is invalid!",
        }

        for error_type, response in errors.items():
            if isinstance(error, error_type):
                await ctx.send(response)
                return

        print("unexpected error")
        raise error

    @pycordSuperUtils.CogManager.event(pycordSuperUtils.MusicManager)
    async def on_inactivity_disconnect(self,ctx):
        iembed = discord.Embed(description=f"I have left due to inactivity.",color = 0xb16ad4)
        await ctx.send(embed=iembed)


    @pycordSuperUtils.CogManager.event(pycordSuperUtils.MusicManager)
    async def on_play(self, ctx, player):
        thumbnail = player.data["videoDetails"]["thumbnail"]["thumbnails"][-1]["url"]
        uploader = player.data["videoDetails"]["author"]
        requester = player.requester.mention if player.requester else "Autoplay"

        embed = discord.Embed(
            title="Now Playing",
            color=0xb16ad4,
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            description=f"[**{player.title}**]({player.url}) by **{uploader}**",
        )
        embed.add_field(name="Requested by", value=requester)
        embed.set_thumbnail(url=thumbnail)

        await ctx.send(embed=embed)

    @slash_command(description="Disconnects from voice")
    async def leave(self, ctx):
        connected = ctx.author.voice
        amconnected = ctx.guild.me.voice
        if connected is None:
            nembed = discord.Embed(description=f"You're not in a voice channel [{ctx.author.mention}]",
                                   color=0xb16ad4)
            return await ctx.respond(embed=nembed)
        if amconnected is None:
            nembed = discord.Embed(description=f"I'm not in a voice channel [{ctx.author.mention}]",
                                   color=0xb16ad4)
            return await ctx.respond(embed=nembed)
        if await self.MusicManager.leave(ctx):
            dembed = discord.Embed(description=f"Disconnected from your channel [{ctx.author.mention}]",
                                   color=0xb16ad4)
            await ctx.respond(embed=dembed)

    @slash_command(description="Shows what is currently playing")
    async def nowplaying(self, ctx):
        if player := await self.MusicManager.now_playing(ctx):
            duration_playedex = await self.MusicManager.get_player_played_duration(ctx, player)
            duration_played = round(duration_playedex)
            npembed = discord.Embed(title=f"{player} is currently playing",
                                    description=f"Duration: {duration_played}s/{player.duration}s", color=0xb16ad4)
            await ctx.respond(embed=npembed)

    @slash_command(description="Connects to your voice channel")
    async def join(self, ctx):
        if await self.MusicManager.join(ctx):
            jembed = discord.Embed(description=f"Joined your Voice Channel [{ctx.author.mention}]",
                                   color=0xb16ad4)
            await ctx.respond(embed=jembed)

    @slash_command(description="Plays a song of your choice")
    async def play(self, ctx, *, query: str):
        if not ctx.voice_client or not ctx.voice_client.is_connected():
            await self.MusicManager.join(ctx)

        async with ctx.typing():
            players = await self.MusicManager.create_player(query, ctx.author)

        if players:
            if await self.MusicManager.queue_add(players=players, ctx=ctx) and not await self.MusicManager.play(ctx):
                if ctx_queue := await self.MusicManager.get_queue(ctx):
                    pos = ctx_queue.queue[ctx_queue.pos -1]
                    queembed = discord.Embed(description=f"Added {pos.title} to the queue", color=0xb16ad4)
                    await ctx.respond(embed=queembed)
            else:
                if player := await self.MusicManager.now_playing(ctx):
                    npembed = discord.Embed(description=f"Playing {player}", color=0xb16ad4)
                    await ctx.respond(embed=npembed)


        else:
            await ctx.respond("Query not found.")

    @slash_command(description="Pauses the song")
    async def pause(self, ctx):
        if await self.MusicManager.pause(ctx):
            if player := await self.MusicManager.now_playing(ctx):
                paembed = discord.Embed(description=f"Paused {player}", color=0xb16ad4)
                await ctx.respond(embed=paembed)

    @slash_command(description="Skips the currently playing song")
    async def skip(self, ctx, index: int = None):
        if player := await self.MusicManager.now_playing(ctx):
            sembed = discord.Embed(description=f"Skipped {player}", color=0xb16ad4)
            await ctx.respond(embed=sembed)
            if await self.MusicManager.skip(ctx, index) is None:
                await self.MusicManager.pause(ctx)
            else:
                await self.MusicManager.skip(ctx, index)

    @slash_command(description="poop")
    async def poop(self, ctx, index: int = None):
        rannum = random.randrange(1,20)
        await ctx.respond("💩" * rannum)

    @slash_command(description="Shows the lyrics of the currently playing song")
    async def lyrics(self, ctx):
        if response := await self.MusicManager.lyrics(ctx):
            # If lyrics are found
            title, author, query_lyrics = response
            # Formatting the lyrics
            splitted = query_lyrics.split("\n")
            res = []
            current = ""
            for i, split in enumerate(splitted):
                if len(splitted) <= i + 1 or len(current) + len(splitted[i + 1]) > 1024:
                    res.append(current)
                    current = ""
                    continue
                current += split + "\n"
            # Creating embeds list for PageManager
            embeds = [
                discord.Embed(
                    title=f"Lyrics for '{title}' by '{author}', (Page {i + 1}/{len(res)})",
                    description=x, color=0xb16ad4
                )
                for i, x in enumerate(res)
            ]
            # editing the embeds
            for embed in embeds:
                embed.timestamp = datetime.datetime.utcnow()

            page_manager = pycordSuperUtils.PageManager(
                ctx,
                embeds,
                public=True,
            )

            await page_manager.run()

        else:
            await ctx.respond("No lyrics were found for the song")

    @slash_command(description="Resumes the currently playing song")
    async def resume(self, ctx):
        if await self.MusicManager.resume(ctx):
            if player := await self.MusicManager.now_playing(ctx):
                rembed = discord.Embed(description=f"Resumed {player}", color=0xb16ad4)
                await ctx.respond(embed=rembed)

    @slash_command(description="Changes the volume of the bot")
    async def volume(self, ctx, volume: int):
        await self.MusicManager.volume(ctx, volume)
        vembed = discord.Embed(description=f"Changed the volume to {volume}%", color=0xb16ad4)
        await ctx.respond(embed=vembed)

    @slash_command(description="Loops the currently playing song")
    async def loop(self, ctx):
        is_loop = await self.MusicManager.loop(ctx)

        if is_loop is not None:
            await ctx.respond(f"Looping toggled to {is_loop}")

    @slash_command(description="Shuffles the current queue")
    async def shuffle(self, ctx):
        is_shuffle = await self.MusicManager.shuffle(ctx)

        if is_shuffle is not None:
            sembed = discord.Embed(description=f"Shuffle toggled to {is_shuffle}", color=0xb16ad4)
            await ctx.respond(embed=sembed)

    @slash_command(description="Auto plays based off the last song played")
    async def autoplay(self, ctx):
        is_autoplay = await self.MusicManager.autoplay(ctx)

        if is_autoplay is not None:
            aembed = discord.Embed(description=f"Autoplay toggled to {is_autoplay}", color=0xb16ad4)
            await ctx.respond(embed=aembed)

    @slash_command(description="Loops the queue")
    async def queueloop(self, ctx):
        is_loop = await self.MusicManager.queueloop(ctx)

        if is_loop is not None:
            await ctx.respond(f"Queue looping toggled to {is_loop}")

    @slash_command(description="Hello")
    async def hello(self, ctx):
        await ctx.respond("Hi!")

    @slash_command(description="Shows the previously played songs")
    async def history(self, ctx):
        if ctx_queue := await self.MusicManager.get_queue(ctx):
            formatted_history = [
                f"Title: '{x.title}'\nRequester: {x.requester and x.requester.mention}"
                for x in ctx_queue.history
            ]

            embeds = pycordSuperUtils.generate_embeds(
                formatted_history,
                "Song History",
                "Shows all played songs",
                25,
                string_format="{}",
            )

            page_manager = pycordSuperUtils.PageManager(ctx, embeds, public=True)
            await page_manager.run()

    @slash_command(description="Removes a song of your choice from the queue you must use it's queue idex eg 1")
    async def remove(self, ctx, index: int):
        await self.MusicManager.queue_remove(ctx, index)
        sembed = discord.Embed(description=f"Removed queue number {index} from the queue", color=0xb16ad4)
        await ctx.respond(embed=sembed)

    @slash_command(description="clears the queue")
    async def clear(self, ctx):
        rembed = discord.Embed(description=f"Clearing queue", color=0xb16ad4)
        await ctx.respond(embed=rembed)
        await self.MusicManager.leave(ctx)
        await asyncio.sleep(1)
        await self.MusicManager.join(ctx)

    @slash_command(description="Shows the queue")
    async def queue(self, ctx):
        process = await ctx.respond("processing")
        await ctx.channel.purge(limit=1)
        if ctx_queue := await self.MusicManager.get_queue(ctx):
            formatted_queue = [
                f"Title: '{x.title}\nRequester: {x.requester and x.requester.mention}"
                for x in ctx_queue.queue[ctx_queue.pos + 1:]
            ]

            embeds = pycordSuperUtils.generate_embeds(
                formatted_queue,
                "Queue",
                f"Now Playing: {await self.MusicManager.now_playing(ctx)}",
                25,
                string_format="{}",
            )

            page_manager = pycordSuperUtils.PageManager(ctx, embeds, public=True)
            await page_manager.run()

    @slash_command(description="Plays the previous song")
    async def rewind(self, ctx, index: int = None):
        rembed = discord.Embed(description=f"Skipping to previous song", color=0xb16ad4)
        await ctx.respond(embed=rembed)
        await self.MusicManager.previous(ctx, index, no_autoplay=True)

    @slash_command(description="Shows if anything is currently looping")
    async def loopstatus(self, ctx):
        if queue := await self.MusicManager.get_queue(ctx):
            loop = queue.loop
            loop_status = None

            if loop == pycordSuperUtils.Loops.LOOP:
                loop_status = "Looping enabled."

            elif loop == pycordSuperUtils.Loops.QUEUE_LOOP:
                loop_status = "Queue looping enabled."

            elif loop == pycordSuperUtils.Loops.NO_LOOP:
                loop_status = "No loop enabled."

            if loop_status:
                await ctx.respond(loop_status)

    @slash_command(description="Shows all the commands in the bot")
    async def help(self, ctx):
        hembed = discord.Embed(title="Groovier Help",
                               description=f"-play: plays the song(shortcut:-p) \n \n -disconnect: disconnects from your vc(shortcut:-dc,-leave) \n \n -queue: see what songs are in the queue(shortcut:-q) \n \n -stop: pauses your song(shortcut:-pause) \n \n -resume: resumes your song(shortcut:-r) \n \n -loop: loops your current song(shortcut:-l) \n \n -nowplaying: shows what is currently playing(shortcut -np) \n \n -skip: skips the currently playing song(shortcut:-s) \n \n -volume: changes the volume of the song(shortcut:-v) \n \n -lyrics: lists the lyrics of the song currently playing song. \n \n -ls: tells you your loop status. \n \n -rewind: Skips to previous song. \n \n -history: displays previously playing songs. \n \n -queueloop: loops the queue(shortcut: -ql) \n \n -autoplay: autoplays a song similar to the previous one(shortcut:-ap) \n \n -shuffle: shuffles songs in the queue(shortcut:-shfl) \n \n -remove:removes the queue number from the queue")
        hembed.set_thumbnail(
            url="https://cdn.discordapp.com/app-icons/880405301851996191/586027a98ef4abc647f41634baed3e02.png?size=256")
        await ctx.respond(embed=hembed)

    @commands.command(aliases=['leave', 'dc'])
    async def disconnect(self,ctx):
        connected = ctx.author.voice
        amconnected = ctx.guild.me.voice
        if connected is None:
            nembed = discord.Embed(description=f"You're not in a voice channel [{ctx.author.mention}]",color = 0xb16ad4)
            return await ctx.send(embed=nembed)
        if amconnected is None:
            nembed = discord.Embed(description=f"I'm not in a voice channel [{ctx.message.author.mention}]",color = 0xb16ad4)
            return await ctx.send(embed=nembed)
        if await self.MusicManager.leave(ctx):
            dembed = discord.Embed(description=f"Disconnected from your channel [{ctx.message.author.mention}]",color = 0xb16ad4)
            await ctx.send(embed=dembed)


    @commands.command(aliases=['nowplaying'])
    async def np(self,ctx):
      if player := await self.MusicManager.now_playing(ctx):
        duration_playedex = await self.MusicManager.get_player_played_duration(ctx, player)
        duration_played = round(duration_playedex)
        npembed = discord.Embed(title=f"{player} is currently playing",description=f"Duration: {duration_played}s/{player.duration}s",color = 0xb16ad4)
        await ctx.send(embed=npembed)


    @commands.command(aliases=['join'])
    async def connect(self,ctx):
      if await self.MusicManager.join(ctx):
          jembed= discord.Embed(description=f"Joined your Voice Channel [{ctx.message.author.mention}]",color = 0xb16ad4)
          await ctx.send(embed=jembed)

    @commands.command(aliases=['play'])
    async def p(self,ctx, *, query: str):
      if not ctx.voice_client or not ctx.voice_client.is_connected():
        await self.MusicManager.join(ctx)

      async with ctx.typing():
        players = await self.MusicManager.create_player(query, ctx.author)

      if players:
        if await self.MusicManager.queue_add(players=players, ctx=ctx) and not await self.MusicManager.play(ctx):
          await ctx.send(f"Added {query} to queue")
        else:
            if player := await self.MusicManager.now_playing(ctx):
                npembed = discord.Embed(description=f"Playing {player}",color = 0xb16ad4)
                await ctx.send(embed=npembed)

      else:
        await ctx.send("Query not found.")

    @commands.command(aliases=['pause'])
    async def stop(self,ctx):
      if await self.MusicManager.pause(ctx):
          if player := await self.MusicManager.now_playing(ctx):
            paembed = discord.Embed(description=f"Paused {player}",color = 0xb16ad4)
            await ctx.send(embed=paembed)

    @commands.command(aliases=['lyrics'])
    async def ly(self, ctx, *, query=None):
        if response := await self.MusicManager.lyrics(ctx, query):
            # If lyrics are found
            title, author, query_lyrics = response
            # Formatting the lyrics
            splitted = query_lyrics.split("\n")
            res = []
            current = ""
            for i, split in enumerate(splitted):
                if len(splitted) <= i + 1 or len(current) + len(splitted[i + 1]) > 1024:
                    res.append(current)
                    current = ""
                    continue
                current += split + "\n"
            # Creating embeds list for PageManager
            embeds = [
                discord.Embed(
                    title=f"Lyrics for '{title}' by '{author}', (Page {i + 1}/{len(res)})",
                    description=x,color=0xb16ad4
                )
                for i, x in enumerate(res)
            ]
            # editing the embeds
            for embed in embeds:
                embed.timestamp = datetime.datetime.utcnow()

            page_manager = pycordSuperUtils.PageManager(
                ctx,
                embeds,
                public=True,
            )

            await page_manager.run()

        else:
            await ctx.send("No lyrics were found for the song")


    @commands.command(aliases=['resume'])
    async def r(self,ctx):
      if await self.MusicManager.resume(ctx):
          if player := await self.MusicManager.now_playing(ctx):
            rembed = discord.Embed(description=f"Resumed {player}",color = 0xb16ad4)
            await ctx.send(embed=rembed)


    @commands.command(aliases=['volume'])
    async def v(self,ctx, volume: int):
      await self.MusicManager.volume(ctx, volume)
      vembed = discord.Embed(description=f"Changed the volume to {volume}%",color = 0xb16ad4)
      await ctx.send(embed=vembed)

    @commands.command(aliases=['loop'])
    async def l(self,ctx):
      is_loop = await self.MusicManager.loop(ctx)

      if is_loop is not None:
        await ctx.send(f"Looping toggled to {is_loop}")

    @commands.command(aliases=['shuffle'])
    async def shfl(self,ctx):
      is_shuffle = await self.MusicManager.shuffle(ctx)

      if is_shuffle is not None:
          sembed = discord.Embed(description=f"Shuffle toggled to {is_shuffle}",color = 0xb16ad4)
          await ctx.send(embed=sembed)


    @commands.command(aliases=['autoplay'])
    async def ap(self,ctx):
      is_autoplay = await self.MusicManager.autoplay(ctx)

      if is_autoplay is not None:
          aembed = discord.Embed(description=f"Autoplay toggled to {is_autoplay}",color = 0xb16ad4)
          await ctx.send(embed=aembed)

    @commands.command(aliases=['queueloop'])
    async def ql(self,ctx):
      is_loop = await self.MusicManager.queueloop(ctx)

      if is_loop is not None:
        await ctx.send(f"Queue looping toggled to {is_loop}")


    @commands.command(aliases=['history'])
    async def hi(self,ctx):
      if ctx_queue := await self.MusicManager.get_queue(ctx):
        formatted_history = [
            f"Title: '{x.title}'\nRequester: {x.requester and x.requester.mention}"
            for x in ctx_queue.history
        ]

        embeds = pycordSuperUtils.generate_embeds(
            formatted_history,
            "Song History",
            "Shows all played songs",
            25,
            string_format="{}",
        )

        page_manager = pycordSuperUtils.PageManager(ctx, embeds, public=True)
        await page_manager.run()


    @commands.command(aliases=['skip'])
    async def s(self,ctx, index: int = None):
        if player := await self.MusicManager.now_playing(ctx):
            sembed = discord.Embed(description=f"Skipped {player}",color = 0xb16ad4)
            await ctx.send(embed=sembed)
            if await self.MusicManager.skip(ctx, index) is None:
                await self.MusicManager.pause(ctx)
            else:
                await self.MusicManager.skip(ctx, index)

    @commands.command(aliases=['remove'])
    async def rm(self,ctx, index: int):
      await self.MusicManager.queue_remove(ctx,index)
      sembed = discord.Embed(description=f"Removed queue number {index} from the queue",color = 0xb16ad4)
      await ctx.send(embed=sembed)


    @commands.command(aliases=['clear'])
    async def cls(self,ctx):
      rembed = discord.Embed(description=f"Clearing queue",color = 0xb16ad4)
      await ctx.send(embed=rembed)
      await self.MusicManager.leave(ctx)
      await asyncio.sleep(1)
      await self.MusicManager.join(ctx)



    @commands.command(aliases=['queue'])
    async def q(self,ctx):
      if ctx_queue := await self.MusicManager.get_queue(ctx):
        formatted_queue = [
            f"Title: '{x.title}\nRequester: {x.requester and x.requester.mention}"
            for x in ctx_queue.queue[ctx_queue.pos + 1 :]
        ]

        embeds = pycordSuperUtils.generate_embeds(
            formatted_queue,
            "Queue",
            f"Now Playing: {await self.MusicManager.now_playing(ctx)}",
            25,
            string_format="{}",
        )

        page_manager = pycordSuperUtils.PageManager(ctx, embeds, public=True)
        await page_manager.run()


    @commands.command(aliases=["rewind"])
    async def re(self,ctx, index: int = None):
        rembed = discord.Embed(description=f"Skipping to previous song",color = 0xb16ad4)
        await ctx.send(embed=rembed)
        await self.MusicManager.previous(ctx, index, no_autoplay=True)

    @commands.command(aliases=["loopstatus"])
    async def ls(self,ctx):
      if queue := await self.MusicManager.get_queue(ctx):
        loop = queue.loop
        loop_status = None

        if loop == pycordSuperUtils.Loops.LOOP:
            loop_status = "Looping enabled."

        elif loop == pycordSuperUtils.Loops.QUEUE_LOOP:
            loop_status = "Queue looping enabled."

        elif loop == pycordSuperUtils.Loops.NO_LOOP:
            loop_status = "No loop enabled."

        if loop_status:
            await ctx.send(loop_status)

    @commands.command(aliases=['help'])
    async def he(self, ctx):
      hembed = discord.Embed(title="Groovier Help", description=f"-play: plays the song(shortcut:-p) \n \n -disconnect: disconnects from your vc(shortcut:-dc,-leave) \n \n -queue: see what songs are in the queue(shortcut:-q) \n \n -stop: pauses your song(shortcut:-pause) \n \n -resume: resumes your song(shortcut:-r) \n \n -loop: loops your current song(shortcut:-l) \n \n -nowplaying: shows what is currently playing(shortcut -np) \n \n -skip: skips the currently playing song(shortcut:-s) \n \n -volume: changes the volume of the song(shortcut:-v) \n \n -lyrics: lists the lyrics of the song currently playing song. \n \n -ls: tells you your loop status. \n \n -rewind: Skips to previous song. \n \n -history: displays previously playing songs. \n \n -queueloop: loops the queue(shortcut: -ql) \n \n -autoplay: autoplays a song similar to the previous one(shortcut:-ap) \n \n -shuffle: shuffles songs in the queue(shortcut:-shfl) \n \n -remove:removes the queue number from the queue")
      hembed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/880405301851996191/586027a98ef4abc647f41634baed3e02.png?size=256")
      await ctx.send(embed=hembed)

def setup(client):
    client.add_cog(Commands(client))
