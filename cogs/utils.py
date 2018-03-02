import discord
from discord.ext import commands
from random import *


class UtilsCog:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def hello(self):
        await self.bot.say('Hello!')

    @commands.command()
    async def ayy(self):
        msgA = ''
        msgB = ''
        for x in range(randint(0, 4) + 1):
            msgA += chr(32 * randint(0, 1) + 65)
        for x in range(randint(0, 4) + 1):
            msgB += chr(32 * randint(0, 1) + 79)

        await self.bot.say('lm' + msgA + msgB + '!')

    @commands.command(pass_context=True)
    async def say(self, ctx, *, something):
        await self.bot.say(something)
        await self.bot.delete_message(ctx.message)


def setup(bot):
    bot.add_cog(UtilsCog(bot))