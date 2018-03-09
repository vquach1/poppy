import discord
from discord.ext import commands
from random import *
import requests
import urllib
import json
import praw
import os
import re
from pprint import pprint

dir = os.path.dirname(__file__)
parentdir = os.path.abspath(os.path.join(dir, os.pardir))
url_cache_dir = parentdir + "/url_cache"
resources_dir = parentdir + "/resources"

class UtilsCog:
    def __init__(self, bot):
        self.bot = bot

        reddit_client_id = self.bot.settings.reddit_client_id
        reddit_client_secret = self.bot.settings.reddit_client_secret
        self.reddit = praw.Reddit(user_agent="windows:poppidiscordbot:v0.3 (by /u/Ocarina1493)",
                                  client_id=reddit_client_id,
                                  client_secret=reddit_client_secret)

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

    """TODO: 
        -Refactor into a cache handler
        -Handle youtube, imgur, etc
        -Make it more robust with error handling/try catch"""

    @commands.command(pass_context=True)
    async def meme(self, ctx):
        sub = self.reddit.subreddit("Animemes")
        post = sub.random()

        contents = requests.get(post.url).content
        print(post.url)
        print(post.title)

        try:
            match = re.search(r'(?<=i.redd.it/)([^\.]+).(.+)', post.url)
            name = match.group(1)
            ext = match.group(2)
            filename = name + "." + ext
            path = "{}/{}".format(dir, filename)

            f = open(path, "wb")
            f.write(contents)
            f.close()

            f = open(path, "rb")
            await self.bot.send_file(ctx.message.channel, f)
            f.close()

            # For now, we remove the file after we're done with it
            os.remove(path)
        except:
            """TEMPORARY: Sends a default image if the random submission is something that hasn't been handled"""
            path = resources_dir + "/default_meme.jpg"
            f = open(path, "rb")
            await self.bot.send_file(ctx.message.channel, f)
            f.close()

    @commands.command(pass_context=True)
    async def dance(self, ctx):
        path = resources_dir + "/dance.gif"
        f = open(path, "rb")

        try:
            await self.bot.send_file(ctx.message.channel, f)
        finally:
            f.close()



def setup(bot):
    bot.add_cog(UtilsCog(bot))
