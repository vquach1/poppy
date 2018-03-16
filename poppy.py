import discord
from discord.ext import commands
from errors import *
from settings import Settings
from base64 import b64encode
import urllib
import requests
from bs4 import *
import html
import re
from message_easter_eggs import *


"""After more structure has been added, this will be refactored into a class definition"""

bot = commands.Bot(command_prefix='!',
                   description='Poppy is a personalized Discord chat bot for anime, manga, games, and more!')


@bot.event
async def on_ready():
    bot.msg_easter_eggs = MessageEasterEggs(bot)
    bot.load_extension("cogs.dev")
    bot.load_extension("cogs.management")
    bot.load_extension("cogs.misc")
    bot.load_extension("cogs.otaku")
    bot.load_extension("cogs.audio")
    print("Poppy is online!")

@bot.event
async def on_message(msg):
    await bot.msg_easter_eggs.process_eggs(msg)
    await bot.process_commands(msg)

"""
@bot.event
async def on_command_error(error, ctx):
    channel = ctx.message.channel

    if isinstance(error, NotOwner):
        await bot.send_message(channel, ":confounded: You are not an owner!")
    elif isinstance(error, NotInVoiceChannel):
        await bot.send_message(channel, ":confounded: I am not in a voice channel!")
    elif isinstance(error, UserNotInVoiceChannel):
        await bot.send_message(channel, ":confounded: You are not in a voice channel!")
    elif isinstance(error, NotPlayingSong):
        await bot.send_message(channel, ":confounded: I am not playing any song!")
    else:
        await bot.send_message(channel, ":confounded: Error unhandled")
"""

bot.settings = Settings()
bot.run(bot.settings.token)