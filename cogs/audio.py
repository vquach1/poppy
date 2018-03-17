import discord
from discord.ext import commands
from checks import *
from pprint import pprint
from random import shuffle
import asyncio
import datetime
import json
import os

"Adapted from https://github.com/Rapptz/discord.py/blob/async/examples/playlist.py"

TRUNCATED_REQ_MIN_LEN = 50
TRUNCATED_REQ_MAX_LEN = 60
dir = os.path.dirname(__file__)

def format_time(sec):
    min_sec = divmod(sec, 60)
    return "{0[0]}:{0[1]:02d}".format(min_sec)


class AudioRequest:
    def __init__(self, requester, channel, song, player):
        self.requester = requester
        self.channel = channel
        self.song = song
        self.player = player
        self.start_time = None

    def start_song(self, vol):
        self.player.volume = vol
        self.player.start()
        self.start_time = datetime.datetime.now()

    def progress(self):
        """Returns seconds elapsed since the song started playing"""
        if self.start_time is None:
            return 0

        curr_time = datetime.datetime.now()
        elapsed = (curr_time - self.start_time).seconds
        return elapsed

    def pretty_print(self, max_len=None, show_progress=False):
        if max_len is not None and max_len < TRUNCATED_REQ_MIN_LEN:
            raise ValueError("audio.py: Max length of pretty print must be at least 50")

        name = self.requester.display_name

        """Display either Duration or Progress/Duration"""
        time = format_time(self.player.duration)
        if show_progress:
            progress = format_time(self.progress())
            time = "{0}/{1}".format(progress, time)

        """Truncate title if necessary"""
        if max_len is None:
            title = self.player.title
        else:
            curr_len = len(name) + len(time) + 6 # 6 is num of other non-title related chars in string
            rem_len = max_len - curr_len
            if rem_len > len(self.player.title):
                title = self.player.title
            else:
                title = self.player.title[0:(rem_len - 4)] + "..."

        pretty = "**{0}** ({1}) - {2}".format(title, time, name)
        return pretty

    def __str__(self):
        return self.pretty_print()

"""The playlist handler holds a queue of songs that it plays. When there are no songs in the queue, 
   the handler will wait for one to arrive"""

class PlaylistHandler:
    def __init__(self, bot, ytdl_opts):
        self.bot = bot
        self.ytdl_opts = ytdl_opts
        self.voice = None
        self.current = None
        self.looping = False
        self.playlist_lock = asyncio.Lock()
        self.next_flag = asyncio.Event()
        self.playlist = asyncio.Queue() # Use this queue to process songs with nonblocking gets
        self.playlist_printable = []    # Use this list to examine/mix queue contents with min disruption
        self.vol = 0.2   # The default volume that is used in all songs
        self.queue_duration = 0
        self.playlist_task = self.bot.loop.create_task(self.process_playlist())

    async def join(self, ctx, channel=None):
        if channel is None:
            channel = ctx.message.author.voice.voice_channel

        if self.voice is None:
            self.voice = await self.bot.join_voice_channel(channel)
        else:
            await self.voice.move_to(channel)

        await self.bot.say("I am now in " + channel.name)

    async def play(self, ctx, song):
        """If bot not in channel, add bot to user's voice channel"""
        if self.voice is None:
            await self.join(ctx)

        player = await self.voice.create_ytdl_player(song, ytdl_options=self.ytdl_opts, after=self.play_next)
        req = AudioRequest(ctx.message.author, ctx.message.channel, song, player)

        await self.playlist_lock.acquire()
        await self.playlist.put(req)
        self.queue_duration += player.duration
        self.playlist_printable.append(req)

        await self.bot.say("Added to queue: " + str(req))
        self.playlist_lock.release()

    async def stop(self, ctx):
        channel = self.voice.channel

        await self.playlist_lock.acquire()

        """Cancel playlist processing and disconnect the voice client"""
        self.playlist_task.cancel()
        await self.voice.disconnect()
        self.voice = None

        """Reset the playlist"""
        del self.playlist
        del self.playlist_printable
        self.playlist = asyncio.Queue()
        self.playlist_printable = []

        await self.bot.say("I am no longer in " + channel.name)
        self.playlist_lock.release()

    async def pause(self, ctx):
        if self.not_playing():
            raise NotPlayingSong()

        self.current.player.pause()
        await self.bot.say("Paused: " + str(self.current))

    async def resume(self, ctx):
        if self.not_playing():
            raise NotPlayingSong()

        self.current.player.resume()
        await self.bot.say("Resumed: " + str(self.current))

    async def skip(self, ctx):
        if self.not_playing():
            raise NotPlayingSong()

        await self.playlist_lock.acquire()
        self.current.player.stop()

        # If this isn't here, skipping will not pull up the next song if player is paused
        self.current.player.resume()
        await self.bot.say("Skipped: " + str(self.current))

        self.playlist_lock.release()

    async def loop(self, ctx, mode):
        if mode == "" or mode == "on":
            self.looping = True
            await self.bot.say("Looping enabled!")
        elif mode == "off":
            self.looping = False
            await self.bot.say("Looping disabled!")

    async def volume(self, ctx, vol=None):
        if vol is None:
            await self.bot.say("The curent volume is {}%".format(int(self.vol * 100)))
        else:
            self.vol = float(vol) / 100
            if self.current is not None:
                self.current.player.volume = self.vol

            await self.bot.say("Set the volume to {}%".format(vol))

    async def playing(self, ctx):
        if self.not_playing():
            raise NotPlayingSong()

        req_pretty = self.current.pretty_print(max_len=None, show_progress=True)
        await self.bot.say("Currently playing: " + req_pretty)

    async def queue(self, ctx):
        queue_str = ""

        """Add queue songs"""
        if len(self.playlist_printable) > 0:
            num_iter = min(10, len(self.playlist_printable))
            for i in range(num_iter):
                req_pretty = self.playlist_printable[i].pretty_print(max_len=TRUNCATED_REQ_MAX_LEN)
                queue_str += "**{}.** {}\n".format(i + 1, req_pretty)
        else:
            queue_str += "There are no pending songs in the playlist. Try adding songs with **!play <url/song>**"

        em = discord.Embed(description=queue_str,
                           color=discord.Color.dark_purple())
        em.set_thumbnail(url="https://d30y9cdsu7xlg0.cloudfront.net/png/9538-200.png")
        em.set_author(name="Poppi's Playlist", icon_url=ctx.message.author.avatar_url)
        em.add_field(name="Playlist Duration", value=format_time(self.queue_duration), inline=True)
        em.add_field(name="Playlist Size", value=len(self.playlist_printable), inline=True)

        """Display current song, if one exists"""
        if self.not_playing():
            curr_req_pretty = "Nothing"
        else:
            curr_req_pretty = self.current.pretty_print(max_len=TRUNCATED_REQ_MAX_LEN, show_progress=True)
        em.add_field(name="Currently Playing", value=curr_req_pretty, inline=False)

        await self.bot.say(embed=em)

    async def shuffle(self, ctx):
        await self.playlist_lock.acquire()

        shuffle(self.playlist_printable)

        del self.playlist
        self.playlist = asyncio.Queue()

        for req in self.playlist_printable:
            await self.playlist.put(req)

        await self.bot.say("Shuffled the queue!")
        self.playlist_lock.release()

    def not_playing(self):
        return self.voice is None or \
               self.current is None or \
               self.current.player.is_done()

    def play_next(self):
        self.bot.loop.call_soon_threadsafe(self.next_flag.set)

    async def process_playlist(self):
        while True:
            self.next_flag.clear()

            # Pull out next song from playlist, and start playing it
            print("Retrieving next song")
            if self.looping and self.current is not None:
                print("In looping mode")
                player = await self.voice.create_ytdl_player(self.current.song,
                                                             ytdl_options=self.ytdl_opts,
                                                             after=self.play_next)
                self.current = AudioRequest(self.current.requester,
                                            self.current.channel,
                                            self.current.song,
                                            player)
            else:
                print("In next get mode")
                self.current = await self.playlist.get()
                await self.playlist_lock.acquire()
                self.queue_duration -= self.current.player.duration
                del self.playlist_printable[0]
                self.playlist_lock.release()

            print("Got a song")

            self.current.start_song(self.vol)
            await self.bot.send_message(self.current.channel, "Now playing: " + str(self.current))
            await self.next_flag.wait()
            print("Got past the wait")

class AudioCog:
    def __init__(self, bot):
        self.bot = bot
        self.handlers = {}
        self.ytdl_opts = {
            'default_search': 'auto',   # When user provides song title, will search title on youtube
        }

    def _get_handler(self, server):
        if server.id in self.handlers:
            return self.handlers[server.id]
        else:
            handler = PlaylistHandler(self.bot, self.ytdl_opts)
            self.handlers[server.id] = handler
            return handler

    @commands.command(pass_context=True)
    async def join(self, ctx, channel: discord.Channel=None):
        handler = self._get_handler(ctx.message.server)
        await handler.join(ctx, channel)

    @is_in_voice_channel()
    @commands.command(aliases=["leave"], pass_context=True)
    async def stop(self, ctx):
        handler = self._get_handler(ctx.message.server)
        await handler.stop(ctx)

    @commands.command(pass_context=True)
    async def play(self, ctx, *, song):
        handler = self._get_handler(ctx.message.server)

        await handler.play(ctx, song)
        """
        await handler.play(ctx, "https://www.youtube.com/watch?v=CjIkPZiqiUQ")
        await handler.play(ctx, "https://www.youtube.com/watch?v=CaksNlNniis")
        await handler.play(ctx, "https://www.youtube.com/watch?v=3SDBTVcBUVs")
        await handler.play(ctx, "https://www.youtube.com/watch?v=zyk-Q7gzGqs")
        await handler.play(ctx, "https://www.youtube.com/watch?v=iWO4ff1HXYY")
        await handler.play(ctx, "https://www.youtube.com/watch?v=CKOEvNOM4DI")
        await handler.play(ctx, "https://www.youtube.com/watch?v=CV_2u6EDx6c")
        """

    @is_in_voice_channel()
    @commands.command(pass_context=True)
    async def pause(self, ctx):
        handler = self._get_handler(ctx.message.server)
        await handler.pause(ctx)

    @is_in_voice_channel()
    @commands.command(pass_context=True)
    async def resume(self, ctx):
        handler = self._get_handler(ctx.message.server)
        await handler.resume(ctx)

    @is_in_voice_channel()
    @commands.command(pass_context=True)
    async def skip(self, ctx):
        handler = self._get_handler(ctx.message.server)
        await handler.skip(ctx)

    @commands.command(pass_context=True)
    async def loop(self, ctx, mode=""):
        handler = self._get_handler(ctx.message.server)
        await handler.loop(ctx, mode)

    @commands.command(pass_context=True)
    async def volume(self, ctx, vol=None):
        handler = self._get_handler(ctx.message.server)
        await handler.volume(ctx, vol)

    @commands.command(aliases=["current", "song"], pass_context=True)
    async def playing(self, ctx):
        handler = self._get_handler(ctx.message.server)
        await handler.playing(ctx)

    @commands.command(aliases=["playlist"], pass_context=True)
    async def queue(self, ctx):
        handler = self._get_handler(ctx.message.server)
        await handler.queue(ctx)

    @commands.command(pass_context=True)
    async def shuffle(self, ctx):
        handler = self._get_handler(ctx.message.server)
        await handler.shuffle(ctx)


def setup(bot):
    bot.add_cog(AudioCog(bot))
