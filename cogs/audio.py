import discord
from queue import *
from discord.ext import commands
from checks import *
import asyncio


class AudioRequest:
    def __init__(self, requester, channel, player):
        self.requester = requester
        self.channel =channel
        self.player = player

    def __str__(self):
        return self.player.title

class AudioPlaylist:
    def __init__(self, bot, voice):
        self.bot = bot
        self.next_flag = asyncio.Event()
        self.playlist = asyncio.Queue()
        self.voice = voice
        self.current = None
        self.playlist_task = self.bot.loop.create_task(self.process_playlist())

    def play_next(self):
        self.bot.loop.call_soon_threadsafe(self.next_flag.set)

    async def process_playlist(self):
        while True:
            self.next_flag.clear()
            print("I am in process_playlist")
            self.current = await self.playlist.get()
            print("Got song")
            await self.bot.send_message(self.current.channel, "Now playing " + str(self.current))
            self.current.player.start()
            await self.next_flag.wait()


class AudioCog:
    def __init__(self, bot):
        self.bot = bot
        self.audio_playlists = {}

    @commands.command(pass_context=True)
    async def join(self, ctx, channel: discord.Channel=None):
        server = ctx.message.server

        voice = await self.bot.join_voice_channel(channel)
        self.audio_playlists[server.id] = AudioPlaylist(self.bot, voice)

    @commands.command(pass_context=True)
    async def play(self, ctx, url):
        server = ctx.message.server

        ap = self.audio_playlists[server.id]
        player = await ap.voice.create_ytdl_player(url, after=ap.play_next)
        req = AudioRequest(ctx.message.author, ctx.message.channel, player)

        await self.bot.say("Added " + str(req) + " to the queue")
        await ap.playlist.put(req)


def setup(bot):
    bot.add_cog(AudioCog(bot))
