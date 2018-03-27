import discord
from discord.ext import commands
from discord.object import Object
from discord.errors import InvalidArgument, ClientException
from discord.enums import ChannelType
from errors import *
from settings import Settings
from base64 import b64encode
import urllib
import requests
from bs4 import *
import html
import re
import asyncio
from message_easter_eggs import *


# List of all cogs to load
cogs = [
    "dev",
    "management",
    "misc",
    "otaku",
    "audio",
    # "league"
]

# Path to the cogs folder
cogs_folder = "cogs"


class Formatter(commands.HelpFormatter):
    def format(self):
        """TODO: Make it return an embed"""
        em = discord.Embed(description="TODO: Format", color=discord.Color.dark_green())
        return em


class Bot(commands.Bot):
    def __init__(self, command_prefix, formatter=None, description=None, pm_help=False, **options):
        super().__init__(command_prefix, formatter, description, pm_help, **options)

        self.settings = Settings()
        self.msg_easter_eggs = MessageEasterEggs(self)
        self._load_cogs()

        # Replace the default help command with our custom help command
        self.remove_command("help")
        self.command(**self.help_attrs)(self._help_command)

    async def on_ready(self):
        print("Poppi is online!")

    async def on_message(self, msg):
        await self.msg_easter_eggs.process_eggs(msg)
        await self.process_commands(msg)

    async def on_command_error(self, error, ctx):
        channel = ctx.message.channel

        print(error.__class__.__name__)
        print(error)

        if isinstance(error, commands.MissingRequiredArgument) or \
                isinstance(error, commands.BadArgument):
            await self.send_message(channel, "Error: MissingRequiredArgument or BadArgument")
        elif isinstance(error, NotOwner):
            await self.send_message(channel, ":confounded: You are not an owner!")
        elif isinstance(error, NotInVoiceChannel):
            await self.send_message(channel, ":confounded: I am not in a voice channel!")
        elif isinstance(error, UserNotInVoiceChannel):
            await self.send_message(channel, ":confounded: You are not in a voice channel!")
        elif isinstance(error, NotPlayingSong):
            await self.send_message(channel, ":confounded: I am not playing any song!")
        else:
            await self.send_message(channel, ":confounded: Error unhandled")

    async def _help_command(self, ctx, *commands: str):
        """TODO: Make it call our formatter based on the structure of the command passed"""
        pass

    def _load_cogs(self):
        for cog in cogs:
            try:
                cog_path = "{0}.{1}".format(cogs_folder, cog)
                self.load_extension(cog_path)
            except Exception as e:
                print("ERROR: " + str(e))  # TODO: Replace this with logging


bot = Bot(command_prefix='!',
          description='Poppy is a personalized Discord chat bot for anime, manga, games, and more!',
          formatter=Formatter())

bot.run(bot.settings.token)