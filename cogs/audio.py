import discord
from queue import *
from discord.ext import commands
from checks import *
import asyncio

"Adapted from https://github.com/Rapptz/discord.py/blob/async/examples/playlist.py"

class AudioRequest:
    def __init__(self, requester, channel, player):
        self.requester = requester
        self.channel = channel
        self.player = player

    def __str__(self):
        return self.player.title

"""The playlist handler holds a queue of songs that it plays. When there are no songs in the queue, 
   the handler will wait for one to arrive"""

class PlaylistHandler:
    def __init__(self, bot, voice=None, vol=0.2):
        self.bot = bot
        self.next_flag = asyncio.Event()
        self.playlist = asyncio.Queue()
        self.voice = voice
        self.current = None
        self.vol = vol   # The default volume that is used in all songs
        self.playlist_task = self.bot.loop.create_task(self.process_playlist())

    async def pause(self):
        if self.not_playing():
            await self.bot.say("I am not currently playing any song!")
            return

        self.current.player.pause()
        await self.bot.say("Paused " + str(self.current))

    async def resume(self):
        if self.not_playing():
            await self.bot.say("I am not currently playing any song!")
            return

        self.current.player.resume()
        await self.bot.say("Resumed " + str(self.current))

    async def volume(self, vol):
        self.vol = vol
        if self.current is not None:
            self.current.player.volume = self.vol

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
            await self.next_flag.wait()


class AudioCog:
    def __init__(self, bot):
        self.bot = bot
        self.handlers = {}
        self.vols = {}

    """TODO"""
    async def _get_handler(self, server):
        pass

    async def _join_channel(self, channel=None):
        """Creates a PlaylistHandler for the channel"""
        id = channel.server.id
        vol = self.vols.get(id, 1.0)
        voice = await self.bot.join_voice_channel(channel)

        self.handlers[channel.server.id] = PlaylistHandler(self.bot, voice, vol)
        await self.bot.say("I am now in " + channel.name)

    @commands.command(pass_context=True)
    async def join(self, ctx, channel: discord.Channel=None):
        server = ctx.message.server

        if channel is None:
            channel = ctx.message.author.voice.voice_channel

        if server.id in self.handlers:
            voice = self.handlers[server.id].voice
            await voice.move_to(channel)
            await self.bot.say("I have moved to " + channel.name)
        else:
            await self._join_channel(channel)

    @is_in_voice_channel()
    @commands.command(aliases=["leave"], pass_context=True)
    async def stop(self, ctx):
        server = ctx.message.server
        handler = self.handlers.pop(server.id)
        channel = handler.voice.channel

        handler.playlist_task.cancel()
        await handler.voice.disconnect()
        await self.bot.say("I am no longer in " + channel.name)

    @commands.command(pass_context=True)
    async def play(self, ctx, url):
        server = ctx.message.server

        """If bot not in channel, add bot to user's voice channel"""
        """TODO: Refactor this later on to make the logic cleaner"""
        if server.id not in self.handlers or self.handlers[server.id].voice is None:
            channel = ctx.message.author.voice.voice_channel
            await self._join_channel(channel)

        handler = self.handlers[server.id]
        player = await handler.voice.create_ytdl_player(url, after=handler.play_next)
        req = AudioRequest(ctx.message.author, ctx.message.channel, player)

        await self.bot.say("Added " + str(req) + " to the queue")
        await handler.playlist.put(req)

    @is_in_voice_channel()
    @commands.command(pass_context=True)
    async def pause(self, ctx):
        handler = self.handlers[ctx.message.server.id]
        await handler.pause()

    @is_in_voice_channel()
    @commands.command(pass_context=True)
    async def resume(self, ctx):
        handler = self.handlers[ctx.message.server.id]
        await handler.resume()

    @commands.command(pass_context=True)
    async def volume(self, ctx, vol):
        id = ctx.message.server.id
        self.vols[id] = float(vol)/100

        if id in self.handlers:
            handler = self.handlers[id]
            await handler.volume(self.vols[id])

        await self.bot.say("Set the volume to {}%".format(vol))


def setup(bot):
    bot.add_cog(AudioCog(bot))
