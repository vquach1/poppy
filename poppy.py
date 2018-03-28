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
import itertools
import inspect

from message_easter_eggs import *


# List of all cogs to load
cogs = [
    "dev",
    "management",
    "misc",
    "anime",
    "audio",
    # "league"
]

# Path to the cogs folder
cogs_folder = "cogs"

_mentions_transforms = {
    '@everyone': '@\u200beveryone',
    '@here': '@\u200bhere'
}

_mention_pattern = re.compile('|'.join(_mentions_transforms.keys()))


class Formatter(commands.HelpFormatter):
    def __init__(self, show_hidden=False, show_check_failure=False, width=80):
        super().__init__(show_hidden, show_check_failure, width)
        self.context = None
        self.command = None

    def format_help(self, ctx):
        self.context = ctx
        self.command = ctx.bot

        bot = ctx.bot
        description = bot.description

        def category(tup):
            cog = tup[1].cog_name
            return cog if cog else ""

        icon_url = ctx.message.author.avatar_url

        em = discord.Embed(description=description, color=discord.Color.dark_green())
        em.set_author(name="Poppi's Command Guide", icon_url=icon_url)


        data = sorted(self.filter_command_list(), key=category)
        for category, commands in itertools.groupby(data, key=category):
            if category == "":
                continue

            commands = list(commands)
            print(category)

            names = ["`{0}`".format(tup[0]) for tup in commands if tup[0] not in tup[1].aliases]
            names_spaced = " ".join(names)

            em.add_field(name=category, value=names_spaced, inline=False)

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
        # self.command(**self.help_attrs)(_def_help_command)

    async def on_ready(self):
        print("Poppi is online!")

    async def on_message(self, msg):
        await self.msg_easter_eggs.process_eggs(msg)
        await self.process_commands(msg)

    """
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
    """

    async def _help_command(self, ctx, *commands: str):
        destination = ctx.message.author if self.pm_help else ctx.message.channel

        def repl(obj):
            return _mentions_transforms.get(obj.group(0), '')

        if len(commands) == 0:
            # If 'help' is called by itself, list all of the commands
            em = self.formatter.format_help(ctx)
        elif len(commands) == 1:
            # If 'help' is called with a role/command, list information for the role/command
            name = _mention_pattern.sub(repl, commands[0])
            command = self.commands.get(name)
            if command is None:
                await self.send_message(destination, self.command_not_found.format(name))
                return

            # TODO
            em = self.formatter.format_help_command(ctx, command)

        await self.send_message(destination, embed=em)

    def _load_cogs(self):
        for cog in cogs:
            try:
                cog_path = "{0}.{1}".format(cogs_folder, cog)
                self.load_extension(cog_path)
            except Exception as e:
                print("ERROR: " + str(e))  # TODO: Replace this with logging


des = "Poppi is a personalized Discord chat bot for anime, manga, games, and more! If you wish to learn more about a " \
      "commmand, type in **!help <command>**"

bot = Bot(command_prefix='!',
          description=des,
          formatter=Formatter())

bot.run(bot.settings.token)