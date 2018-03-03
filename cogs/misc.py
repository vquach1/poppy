import discord
from discord.ext import commands
from random import *
import requests
import urllib
import json


class UtilsCog:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ayy(self):
        msgA = ''
        msgB = ''
        for x in range(randint(0, 4) + 1):
            msgA += chr(32 * randint(0, 1) + 65)
        for x in range(randint(0, 4) + 1):
            msgB += chr(32 * randint(0, 1) + 79)

        await self.bot.say('lm' + msgA + msgB + '!')

    @commands.command(name="8ball", pass_context=True)
    async def ball8(self, ctx, *, msg):
        msg_encoded = urllib.parse.quote(msg)
        url = "https://8ball.delegator.com/magic/JSON/" + msg_encoded
        result = requests.get(url)
        conv = json.loads(result.text)
        await self.bot.say(":eye_in_speech_bubble: " + conv["magic"]["answer"])


def setup(bot):
    bot.add_cog(UtilsCog(bot))