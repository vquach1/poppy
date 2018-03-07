import discord
from queue import *
from discord.ext import commands
from checks import *
import asyncio

"Adapted from https://github.com/Rapptz/discord.py/blob/async/examples/playlist.py"

class AudioRequest:
    def __init__(self, ctx, url, player):
        self.requester = ctx.message.author
        self.channel = ctx.message.channel
        self.url = url
        self.player = player

    def __str__(self):
        return self.player.title

"""The playlist handler holds a queue of songs that it plays. When there are no songs in the queue, 
   the handler will wait for one to arrive"""

class PlaylistHandler:
    def __init__(self, bot):
        self.bot = bot
        self.voice = None
        self.current = None
        self.next_flag = asyncio.Event()
        self.playlist = asyncio.Queue() # Use this queue to process songs with nonblocking gets
        self.playlist_printable = []    # Use this list to examine/mix queue contents with min disruption
        self.vol = 0.2   # The default volume that is used in all songs
        self.playlist_task = self.bot.loop.create_task(self.process_playlist())

    async def join(self, ctx, channel=None):
        if channel is None:
            channel = ctx.message.author.voice.voice_channel

        if self.voice is None:
            self.voice = await self.bot.join_voice_channel(channel)
        else:
            await self.voice.move_to(channel)

        await self.bot.say("I am now in " + channel.name)

    async def play(self, ctx, url):
        """If bot not in channel, add bot to user's voice channel"""
        if self.voice is None:
            await self.join(ctx)

        player = await self.voice.create_ytdl_player(url, after=self.play_next)
        req = AudioRequest(ctx, url, player)
        await self.playlist.put(req)
        self.playlist_printable.append(req)

        await self.bot.say("Added " + str(req) + " to the queue")

    async def stop(self, ctx):
        channel = self.voice.channel

        """Cancel playlist processing and disconnect the voice client"""
        self.playlist_task.cancel()
        await self.voice.disconnect()
        self.voice = None

        """Reset the playlist"""
        del self.playlist
        self.playlist = asyncio.Queue()

        await self.bot.say("I am no longer in " + channel.name)

    async def pause(self, ctx):
        if self.not_playing():
            await self.bot.say("I am not currently playing any song!")
            return

        self.current.player.pause()
        await self.bot.say("Paused " + str(self.current))

    async def resume(self, ctx):
        if self.not_playing():
            await self.bot.say("I am not currently playing any song!")
            return

        self.current.player.resume()
        await self.bot.say("Resumed " + str(self.current))

    async def volume(self, ctx, vol):
        self.vol = float(vol) / 100
        if self.current is not None:
            self.current.player.volume = self.vol

        await self.bot.say("Set the volume to {}%".format(vol))

    async def queue(self, ctx):
        queue_str = ""
        num_iter = min(10, len(self.playlist_printable))
        for i in range(num_iter):
            queue_str += "**{}. {}**\n".format(i + 1, self.playlist_printable[i])

        em = discord.Embed(title="Poppy's Playlist", description=queue_str, color=discord.Color.dark_purple())
        await self.bot.say(embed=em)

    def not_playing(self):
        return self.voice is None or \
               self.current is None or \
               self.current.player.is_done()

    def play_next(self):
        self.bot.loop.call_soon_threadsafe(self.next_flag.set)

    async def process_playlist(self):
        while True:
            self.next_flag.clear()
            self.current = await self.playlist.get()
            self.current.player.volume = self.vol
            await self.bot.send_message(self.current.channel, "Now playing " + str(self.current))
            self.current.player.start()
            del self.playlist_printable[0]
            await self.next_flag.wait()


class AudioCog:
    def __init__(self, bot):
        self.bot = bot
        self.handlers = {}

    """TODO"""
    def _get_handler(self, server):
        if server.id in self.handlers:
            return self.handlers[server.id]
        else:
            handler = PlaylistHandler(self.bot)
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
    async def play(self, ctx, url):
        handler = self._get_handler(ctx.message.server)
        await handler.play(ctx, url)

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

    @commands.command(pass_context=True)
    async def volume(self, ctx, vol):
        handler = self._get_handler(ctx.message.server)
        await handler.volume(ctx, vol)

    @commands.command(pass_context=True)
    async def queue(self, ctx):
        handler = self._get_handler(ctx.message.server)
        await handler.queue(ctx)


def setup(bot):
    bot.add_cog(AudioCog(bot))
