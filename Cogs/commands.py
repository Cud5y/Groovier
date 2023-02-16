import discord
from discord.commands import slash_command
from discord.ext import commands
import pycordSuperUtils
import datetime
import asyncio
from pycordSuperUtils import LavalinkMusicManager

# Define a class for the search buttons
class SearchButtons(discord.ui.View):
    # Initialize the class with client and context (ctx) and options
    def __init__(self, client, ctx, options):
        self.options = options
        self.client = client
        self.ctx = ctx
        super().__init__(timeout=120)

    # Create a button for option 1
    @discord.ui.button(
        emoji="1️⃣",
        style=discord.ButtonStyle.blurple,
    )
    async def one(self, button: discord.ui.Button, interaction: discord.Interaction):
        # Call the play method in the Commands class with the context and the first option
        await Commands.play(self.ctx, query=self.options[0])
        # Send a confirmation message to the user
        await interaction.response.send_message("👍", ephemeral=True)

    # Create a button for option 2
    @discord.ui.button(
        emoji="2️⃣",
        style=discord.ButtonStyle.blurple,
    )
    async def two(self, button: discord.ui.Button, interaction: discord.Interaction):
        # Call the play method in the Commands class with the context and the second option
        await Commands.play(self.ctx, query=self.options[1])
        # Send a confirmation message to the user
        await interaction.response.send_message("👍", ephemeral=True)

    # Create a button for option 3
    @discord.ui.button(
        emoji="3️⃣",
        style=discord.ButtonStyle.blurple,
    )
    async def three(self, button: discord.ui.Button, interaction: discord.Interaction):
        # Call the play method in the Commands class with the context and the third option
        await Commands.play(self.ctx, query=self.options[2])
        # Send a confirmation message to the user
        await interaction.response.send_message("👍", ephemeral=True)

    # Create a button for option 4
    @discord.ui.button(
        emoji="4⃣",
        style=discord.ButtonStyle.blurple,
    )
    async def four(self, button: discord.ui.Button, interaction: discord.Interaction):
        # Call the play method in the Commands class with the context and the fourth option
        await Commands.play(self.ctx, query=self.options[3])
        # Send a confirmation message to the user
        await interaction.response.send_message("👍", ephemeral=True)

    # Create a button for option 5
    @discord.ui.button(
        emoji="5⃣",
        style=discord.ButtonStyle.blurple,
    )
    async def five(self, button: discord.ui.Button, interaction: discord.Interaction):
        # Call the play method in the Commands class with the context and the fifth option
        await Commands.play(self.ctx, query=self.options[4])
        # Send a confirmation message to the user
        await interaction.response.send_message("👍", ephemeral=True)

# Define a class for button controls
class PlayerButtons(discord.ui.View):
    # Initialize the class with client and context (ctx)
    def __init__(self, client, ctx):
        self.ctx = ctx
        self.client = client
        self.MusicManager = LavalinkMusicManager(client, client_id="ddf765a360274a02a3cc44e8982e78aa",
                                                 client_secret="ce864f1f031e434ca1c291442a189841", spotify_support=True)
        # Call the superclass constructor to set the timeout
        super().__init__(timeout=None)

    # Button for rewind
    @discord.ui.button(
        emoji="⏮",
        style=discord.ButtonStyle.blurple,
    )
    async def rewind(self, button: discord.ui.Button, interaction: discord.Interaction,index: int = None):
        # Call the rewind command from the Commands class with the provided context and index
        await Commands.rewind(self.ctx,index=None)
        # Send a message to confirm the operation with a thumbs-up emoji, and set the message to be ephemeral (only visible to the user who triggered the button)
        await interaction.response.send_message("👍",ephemeral=True)

    # Button for playing and pausing
    @discord.ui.button(
        emoji="⏯",
        style=discord.ButtonStyle.blurple,
    )
    async def pause(self, button: discord.ui.Button, interaction: discord.Interaction):
        # Check if the music is playing, if it is then pause it, otherwise resume it
        if await self.MusicManager.pause(self.ctx):
            await interaction.response.send_message("Paused", ephemeral=True)
        else:
            await self.MusicManager.resume(self.ctx)
            await interaction.response.send_message("Resumed",ephemeral=True)

    # Button for skip
    @discord.ui.button(
        emoji="⏭",
        style=discord.ButtonStyle.blurple,
    )
    async def skip(self, button: discord.ui.Button, interaction: discord.Interaction):
        # Call the skip command from the Commands class with the provided context and index
        await Commands.skip(self.ctx,index=None)
        # Send a message to confirm the operation with a thumbs-up emoji, and set the message to be ephemeral (only visible to the user who triggered the button)
        await interaction.response.send_message("👍",ephemeral=True)

    # Button for shuffle
    @discord.ui.button(
        emoji="🔀",
        style=discord.ButtonStyle.blurple,
    )
    async def shuffle(self, button: discord.ui.Button, interaction: discord.Interaction):
        # Call the shuffle command from the Commands class with the provided context
        await Commands.shuffle(self.ctx)
        # Send a message to confirm the operation with a thumbs-up emoji, and set the message to be ephemeral (only visible to the user who triggered the button)
        await interaction.response.send_message("👍",ephemeral=True)

    # Button for loop
    @discord.ui.button(
        emoji="🔁",
        style=discord.ButtonStyle.blurple,
    )
    async def loop(self, button: discord.ui.Button, interaction: discord.Interaction):
        # Call the loop command from the Commands class with the provided context
        await Commands.loop(self.ctx)
        # Send a message to confirm the operation with a thumbs-up emoji, and set the message to be ephemeral (only visible to the user


# Define a new class called Commands that extends from multiple classes
class Commands(commands.Cog, pycordSuperUtils.CogManager.Cog, name="Music"):

    # Constructor function that gets called when an object of this class is created
    def __init__(self, client):
        self.boost = False  # Initialize the boost attribute to False
        self.client = client  # Save the client object as an attribute
        self.client_id = "CLIENT ID"
        self.client_secret = "CLIENT SECRET"
        self.MusicManager = LavalinkMusicManager(self.client, client_id=self.client_id,
                                                 client_secret=self.client_secret, spotify_support=True)

    # Decorator that registers a function as an event listener for the on_music_error event
    @pycordSuperUtils.CogManager.event(pycordSuperUtils.LavalinkMusicManager)
    async def on_music_error(self, ctx, error):
        # Define a dictionary that maps error types to error responses
        errors = {
            pycordSuperUtils.NotPlaying: "Not playing any music right now...",
            pycordSuperUtils.NotConnected: f"Bot not connected to a voice channel!",
            pycordSuperUtils.NotPaused: "Player is not paused!",
            pycordSuperUtils.QueueEmpty: "The queue is empty!",
            pycordSuperUtils.AlreadyConnected: "Already connected to voice channel!",
            pycordSuperUtils.SkipError: "There is no song to skip to!",
            pycordSuperUtils.UserNotConnected: "User is not connected to a voice channel!",
            pycordSuperUtils.InvalidSkipIndex: "That skip index is invalid!",
        }

        # Loop through the error types and their corresponding responses
        for error_type, response in errors.items():
            if isinstance(error, error_type):  # If the error matches the current type
                await ctx.send(response)  # Send the response
                return

        print("unexpected error")  # If no error type matches, print an error message
        raise error

    # Decorator that registers a function as an event listener for the on_queue_end event
    @pycordSuperUtils.CogManager.event(pycordSuperUtils.LavalinkMusicManager)
    async def on_queue_end(self, ctx):
        print(f"The queue has ended in {ctx}")  # Print a message indicating that the queue has ended

    # Decorator that registers a function as an event listener for the on_inactivity_disconnect event
    @pycordSuperUtils.CogManager.event(pycordSuperUtils.LavalinkMusicManager)
    async def on_inactivity_disconnect(self, ctx):
        iembed = discord.Embed(description=f"I have left due to inactivity.",
                               color=0xb16ad4)  # Create an embed with a message
        await ctx.send(embed=iembed)  # Send the embed to the channel

    @pycordSuperUtils.CogManager.event(pycordSuperUtils.LavalinkMusicManager)
    async def on_play(self, ctx, player):
        # Get the thumbnail and uploader of the currently playing song
        thumbnail = player.data["videoDetails"]["thumbnail"]["thumbnails"][-1]["url"]
        uploader = player.data["videoDetails"]["author"]
        # Get the mention of the user who requested the song or "Autoplay" if it was an auto-played song
        requester = player.requester.mention if player.requester else "Autoplay"

        # Create an embed with information about the currently playing song
        embed = discord.Embed(
            title="Now Playing",
            color=0xb16ad4,
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            description=f"[**{player.title}**]({player.url}) by **{uploader}**",
        )
        embed.add_field(name="Requested by", value=requester)
        embed.set_thumbnail(url=thumbnail)

        # Send the embed to the channel where the song is playing
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        # Connect to the Lavalink node
        await self.MusicManager.connect_node(
            host="127.0.0.1", port=2333, password="youshallnotpass"
        )

    @slash_command(description="Disconnects from voice")
    async def leave(self, ctx):
        # Check if the user and the bot are connected to a voice channel
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
        # Disconnect from the voice channel
        if await self.MusicManager.leave(ctx):
            dembed = discord.Embed(description=f"Disconnected from your channel [{ctx.author.mention}]",
                                   color=0xb16ad4)
            await ctx.respond(embed=dembed)

    @slash_command(description="Shows what is currently playing")
    async def nowplaying(self, ctx):
        # Get the currently playing song
        if player := await self.MusicManager.now_playing(ctx):
            # Get the duration of the song that has been played so far
            duration_playedex = await self.MusicManager.get_player_played_duration(ctx, player)
            duration_played = round(duration_playedex)
            # Create an embed with information about the currently playing song and the duration played
            npembed = discord.Embed(title=f"{player} is currently playing",
                                    description=f"Duration: {duration_played}s/{player.duration}s", color=0xb16ad4)
            # Add a button to the embed to show the player's queue
            await ctx.respond(embed=npembed, view=PlayerButtons(self.client, ctx))

    # Command to toggle bass boost for the currently playing song
    @slash_command(description="Bass boosts the currently playing song")
    async def bassboost(self, ctx):
        if not self.boost:
            await self.MusicManager.set_equalizer(ctx, pycordSuperUtils.Equalizer.boost())
            self.boost = True
            boostembed = discord.Embed(title=f"Bass boosting toggled", color=0xb16ad4)
            await ctx.respond(embed=boostembed)
        else:
            await self.MusicManager.set_equalizer(ctx, pycordSuperUtils.Equalizer.flat())
            self.boost = False
            boostembed = discord.Embed(title=f"Bass boosting toggled", color=0xb16ad4)
            await ctx.respond(embed=boostembed)

    # Command to join the user's voice channel
    @slash_command(description="Connects to your voice channel")
    async def join(self, ctx):
        if await self.MusicManager.join(ctx):
            jembed = discord.Embed(description=f"Joined your Voice Channel [{ctx.author.mention}]", color=0xb16ad4)
            await ctx.respond(embed=jembed)

    # Command to play a song
    async def play(self, ctx, *, query: str):
        if not ctx.voice_client or not ctx.voice_client.is_connected():  # If the bot is not already in a voice channel
            await self.MusicManager.join(ctx)  # Join the voice channel

        async with ctx.typing():
            players = await self.MusicManager.create_player(query, ctx.author)  # Create a player for the query

        if players:  # If the player was successfully created
            if await self.MusicManager.queue_add(players=players, ctx=ctx) and not await self.MusicManager.play(
                    ctx):  # Add the player to the queue and start playing it
                # If the player was added to the queue but not played yet (i.e., it's not the first player in the queue)
                if ctx_queue := await self.MusicManager.get_queue(ctx):  # Get the current queue
                    x = ctx_queue.queue
                    thumbnail = x[-1].data["videoDetails"]["thumbnail"]["thumbnails"][-1]["url"]
                    uploader = x[-1].data["videoDetails"]["author"]
                    requester = x[-1].requester.mention if x[-1].requester else "Autoplay"

                    # Create an embed to show that the player was added to the queue
                    embed = discord.Embed(
                        title="Added to Queue",
                        color=0xb16ad4,
                        timestamp=datetime.datetime.now(datetime.timezone.utc),
                        description=f"[**{x[-1].title}**]({x[-1].url}) by **{uploader}**",
                    )
                    embed.add_field(name="Requested by", value=requester)
                    embed.set_thumbnail(url=thumbnail)

                    await ctx.respond(embed=embed, view=PlayerButtons(self.client,
                                                                      ctx))  # Respond with the embed and the PlayerButtons view
            else:  # If the player was either played or not added to the queue
                if player := await self.MusicManager.now_playing(ctx):  # Get the currently playing player
                    thumbnail = player.data["videoDetails"]["thumbnail"]["thumbnails"][-1]["url"]
                    uploader = player.data["videoDetails"]["author"]
                    requester = player.requester.mention if player.requester else "Autoplay"

                    # Create an embed to show the currently playing player
                    embed = discord.Embed(
                        title="Now Playing",
                        timestamp=datetime.datetime.now(datetime.timezone.utc),
                        description=f"[**{player.title}**]({player.url}) by **{uploader}**",
                        color=0xb16ad4
                    )
                    embed.add_field(name="Requested by", value=requester)
                    embed.set_thumbnail(url=thumbnail)

                    await ctx.respond(embed=embed, view=PlayerButtons(self.client,
                                                                      ctx))  # Respond with the embed and the PlayerButtons view

        else:  # If the player could not be created
            notfoundembed = discord.Embed(description="Query not found.", color=0xb16ad4)
            await ctx.respond(embed=notfoundembed)

    @slash_command(description="Pauses the song")
    async def pause(self, ctx):
        if await self.MusicManager.pause(ctx):  # Pause the current player
            if player := await self.MusicManager.now_playing(ctx):  # Get the currently playing player
                paembed = discord.Embed(description=f"Paused {player}", color=0xb16ad4)
                await ctx.respond(embed=paembed)

    @slash_command(description="Skips the currently playing song")
    async def skip(self, ctx, index: int = None):
        # Check if there's a song currently playing
        if player := await self.MusicManager.now_playing(ctx):
            # If there is a song playing, create an embed to indicate that it's been skipped
            sembed = discord.Embed(description=f"Skipped {player}", color=0xb16ad4)
            # Respond with the embed
            await ctx.respond(embed=sembed)
            # Skip the song
            if await self.MusicManager.skip(ctx, index) is None:
                # If there are no more songs in the queue, pause the music
                await self.MusicManager.pause(ctx)
            else:
                # If there are more songs in the queue, skip to the next one
                await self.MusicManager.skip(ctx, index)
        else:
            # If there's no song playing, create an embed to indicate that there's nothing to skip
            nfembed = discord.Embed(description="No song is playing to skip", color=0xb16ad4)
            # Respond with the embed
            await ctx.respond(embed=nfembed)

    @slash_command(description="Shows the lyrics of the currently playing song")
    async def lyrics(self, ctx):
        await ctx.respond("processing")
        await ctx.channel.purge(limit=1)  # remove the "processing" message from the chat
        if response := await self.MusicManager.lyrics(ctx):
            # If lyrics are found
            title, author, query_lyrics = response
            # Formatting the lyrics
            splitted = query_lyrics.split("\n")
            res = []
            current = ""
            for i, split in enumerate(splitted):
                if len(splitted) <= i + 1 or len(current) + len(splitted[i + 1]) > 1024:
                    # Each embed can only contain up to 1024 characters, so we split the lyrics
                    # into multiple pages if they exceed the limit
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
                timeout=300,
                public=True,
            )

            await page_manager.run()

        else:
            await ctx.respond("No lyrics were found for the song")

    @slash_command(description="Resumes the currently playing song")
    async def resume(self, ctx):
        if await self.MusicManager.resume(ctx):
            # Finds what song is currently playing
            if player := await self.MusicManager.now_playing(ctx):
                rembed = discord.Embed(description=f"Resumed {player}", color=0xb16ad4)
                await ctx.respond(embed=rembed)

    @slash_command(description="Changes the volume of the bot")
    async def volume(self, ctx, volume: int):
        # Changes the volume to the specified amount in the command
        await self.MusicManager.volume(ctx, volume)
        vembed = discord.Embed(description=f"Changed the volume to {volume}%", color=0xb16ad4)
        await ctx.respond(embed=vembed)

    @slash_command(description="Loops the currently playing song")
    async def loop(self, ctx):
        # toggles loop and gets the current loop status
        is_loop = await self.MusicManager.loop(ctx)

        if is_loop is not None:
            # sends a message indicating the new loop status
            await ctx.respond(f"Looping toggled to {is_loop}")

    @slash_command(description="Shuffles the current queue")
    async def shuffle(self, ctx):
        # toggles shuffle and gets the current shuffle status
        is_shuffle = await self.MusicManager.shuffle(ctx)

        if is_shuffle is not None:
            # sends a message indicating the new shuffle status
            sembed = discord.Embed(description=f"Shuffle toggled to {is_shuffle}", color=0xb16ad4)
            await ctx.respond(embed=sembed)

    @slash_command(description="Auto plays based off the last song played")
    async def autoplay(self, ctx):
        # toggles autoplay and gets the current autoplay status
        is_autoplay = await self.MusicManager.autoplay(ctx)

        if is_autoplay is not None:
            # sends a message indicating the new autoplay status
            aembed = discord.Embed(description=f"Autoplay toggled to {is_autoplay}", color=0xb16ad4)
            await ctx.respond(embed=aembed)

    @slash_command(description="Loops the queue")
    async def queueloop(self, ctx):
        # toggles queue loop and gets the current queue loop status
        is_loop = await self.MusicManager.queueloop(ctx)

        if is_loop is not None:
            # sends a message indicating the new queue loop status
            await ctx.respond(f"Queue looping toggled to {is_loop}")

    @slash_command(description="Seeks to specific position in song format is min:seconds")
    async def seek(self, ctx, time):
        if ":" in time:
            # converts seek time from minutes:seconds to milliseconds
            timesplit = time.split(":")
            totaltime = int(timesplit[0]) * 60000
            totaltime = totaltime + (int(timesplit[1]) * 1000)
            # seeks to the specified time and sends a message indicating the new position
            await self.MusicManager.seek(ctx, totaltime)
            seekembed = discord.Embed(description=f"Seeked to {time}", color=0xb16ad4)
            await ctx.respond(embed=seekembed)
        else:
            # sends an error message if the seek time is not in the correct format
            seekembed = discord.Embed(
                description=f"That is not a valid time please put time in this format min:seconds")
            await ctx.respond(embed=seekembed, color=0xb16ad4)

    @slash_command(description="Shows the previously played songs")
    async def history(self, ctx):
        # Get the queue for the current context
        if ctx_queue := await self.MusicManager.get_queue(ctx):
            # Create a formatted string for each song in the history
            formatted_history = [
                f"Title: '{x.title}'\nRequester: {x.requester and x.requester.mention}"
                for x in ctx_queue.history
            ]

            # Generate a list of embeds with the formatted history
            embeds = pycordSuperUtils.generate_embeds(
                formatted_history,
                "Song History",
                "Shows all played songs",
                25,
                string_format="{}",
            )

            # Create a PageManager with the generated embeds and run it
            page_manager = pycordSuperUtils.PageManager(ctx, embeds, public=True)
            await page_manager.run()

    @slash_command(description="Removes a song of your choice from the queue you must use it's queue index eg. 1")
    async def remove(self, ctx, index: int):
        # Remove the song with the specified index from the queue
        await self.MusicManager.queue_remove(ctx, index)
        sembed = discord.Embed(description=f"Removed queue number {index} from the queue", color=0xb16ad4)
        await ctx.respond(embed=sembed)

    @slash_command(description="Clears the queue")
    async def clear(self, ctx):
        # Send an embed indicating that the queue is being cleared
        rembed = discord.Embed(description=f"Clearing queue", color=0xb16ad4)
        await ctx.respond(embed=rembed)

        # Leave the voice channel, wait for 1 second, and then join again to clear the queue
        await self.MusicManager.leave(ctx)
        await asyncio.sleep(1)
        await self.MusicManager.join(ctx)

    @slash_command(description="Shows the queue")
    async def queue(self, ctx):
        # Send a "processing" message to the channel
        await ctx.respond("processing")
        # Delete the previous message to remove the "processing" message
        await ctx.channel.purge(limit=1)
        # Get the queue from the music manager
        if ctx_queue := await self.MusicManager.get_queue(ctx):
            # Format the queue to display title and requester
            formatted_queue = [
                f"Title: '{x.title}\nRequester: {x.requester and x.requester.mention}"
                for x in ctx_queue.queue[ctx_queue.pos + 1:]
            ]
            # Generate embeds to display the queue in a paginated format
            embeds = pycordSuperUtils.generate_embeds(
                formatted_queue,
                "Queue",
                f"Now Playing: {await self.MusicManager.now_playing(ctx)}",
                25,
                string_format="{}",
            )
            # Create a page manager to handle the paginated queue
            page_manager = pycordSuperUtils.PageManager(ctx, embeds, public=True)
            # Display the paginated queue
            await page_manager.run()

    @slash_command(description="Plays the previous song")
    async def rewind(self, ctx, index: int = None):
        # Create an embed to indicate that the bot is going back to the previous song
        rembed = discord.Embed(description=f"Going back to previous song", color=0xb16ad4)
        # Respond to the command with the embed
        await ctx.respond(embed=rembed)
        # Go back to the previous song and disable autoplay
        await self.MusicManager.previous(ctx, index, no_autoplay=True)

    @slash_command(description="Shows if anything is currently looping")
    async def loopstatus(self, ctx):
        # Get the queue from the music manager
        if queue := await self.MusicManager.get_queue(ctx):
            # Check if the queue is currently looping and generate a message indicating the loop status
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

    @slash_command(description="Search for a song of your choice")
    async def search(self, ctx, query):
        await ctx.respond("processing")
        await ctx.channel.purge(limit=1)

        # Type a message while the bot is processing
        async with ctx.typing():
            # Initialize variables to store the search results
            one = "Not Found"
            two = "Not Found"
            three = "Not Found"
            four = "Not Found"
            five = "Not Found"

            # Search for the query with different suffixes to get more results
            if query1 := await self.MusicManager.create_player(query, ctx.author):
                if query1array := str(query1).split(','):
                    one = query1array[1].replace('title=', '')

            if query2 := await self.MusicManager.create_player(query + " music video", ctx.author):
                if query2array := str(query2).split(','):
                    two = query2array[1].replace('title=', '')

            if query3 := await self.MusicManager.create_player(query + " song", ctx.author):
                if query3array := str(query3).split(','):
                    three = query3array[1].replace('title=', '')

            if query4 := await self.MusicManager.create_player(query + " lyrics", ctx.author):
                if query4array := str(query4).split(','):
                    four = query4array[1].replace('title=', '')

            if query5 := await self.MusicManager.create_player(query + "Offical Video", ctx.author):
                if query5array := str(query5).split(','):
                    five = query5array[1].replace('title=', '')

            # Create an embed with the search results and options for the user to choose from
            embed = discord.Embed(
                description=f" **1.** {one} \n **2.** {two} \n **3.** {three} \n **4.** {four} \n **5.** {five}",
                color=0xb16ad4)
            options = [one, two, three, four, five]
            # Add a view that allows the user to choose from the search results
            await ctx.respond(embed=embed, view=SearchButtons(self.client, ctx, options))

# Add the commands to the client
def setup(client):
    client.add_cog(Commands(client))