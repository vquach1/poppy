import discord
from discord.ext import commands
from settings import Settings

"""After more structure has been added, this will be refactored into a class definition"""

bot = commands.Bot(command_prefix='!', description='Poppy is a personalized Discord chat bot for anime, manga, games, and more!')


@bot.event
async def on_ready():
    bot.load_extension("cogs.dev")
    bot.load_extension("cogs.management")
    bot.load_extension("cogs.utils")
    print("Poppy is online!")

settings = Settings()
bot.run(settings.token)