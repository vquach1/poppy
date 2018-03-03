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


"""After more structure has been added, this will be refactored into a class definition"""

bot = commands.Bot(command_prefix='!',
                   description='Poppy is a personalized Discord chat bot for anime, manga, games, and more!')


@bot.event
async def on_ready():
    bot.load_extension("cogs.dev")
    bot.load_extension("cogs.management")
    bot.load_extension("cogs.misc")
    bot.load_extension("cogs.otaku")
    print("Poppy is online!")

"""
@bot.event
async def on_command_error(error, ctx):
    channel = ctx.message.channel

    if isinstance(error, NotOwner):
        await bot.send_message(channel, "You are not an owner!")
    else:
        await bot.send_message(channel, "Error unhandled")
"""

bot.settings = Settings()
bot.run(bot.settings.token)