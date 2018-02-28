import discord
from discord.ext import commands
from random import *
from settings import Settings

"""After more structure has been added, this will be refactored into a class definition"""

bot = commands.Bot(command_prefix='!', description='Poppy is a personalized Discord chat bot for anime, manga, games, and more!')

@bot.event
async def on_ready():
    print('Hello, I am ' + bot.user.name)

@bot.command()
async def hello():
    await bot.say('Hello!')

@bot.command()
async def ayy():
    msgA = ''
    msgB = ''
    for x in range(randint(0, 4) + 1):
        msgA += chr(32 * randint(0, 1) + 65)
    for x in range(randint(0, 4) + 1):
        msgB += chr(32 * randint(0, 1) + 79)

    await bot.say('lm' + msgA + msgB + '!')

@bot.command(pass_context=True)
async def say(ctx, *, something):
    await bot.say(something)
    await bot.delete_message(ctx.message)

settings = Settings()
bot.run(settings.token)
