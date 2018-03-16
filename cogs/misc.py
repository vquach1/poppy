import discord
from discord.ext import commands
from random import *
import requests
import urllib
import json
import praw
import prawcore
import os
import re
from pprint import pprint

dir = os.path.dirname(__file__)
parentdir = os.path.abspath(os.path.join(dir, os.pardir))
url_cache_dir = parentdir + "/url_cache"
resources_dir = parentdir + "/resources"

MAX_NUM_SUBREDDITS = 15

"""TODO: Change default_meme_sources to use subreddit objects instead of strings"""

class MiscCog:
    default_meme_sources = ["Animemes", "anime_irl"]

    def __init__(self, bot):
        self.bot = bot
        self.meme_sources = {}

        reddit_client_id = self.bot.settings.reddit_client_id
        reddit_client_secret = self.bot.settings.reddit_client_secret
        self.reddit = praw.Reddit(user_agent="windows:poppidiscordbot:v0.3 (by /u/Ocarina1493)",
                                  client_id=reddit_client_id,
                                  client_secret=reddit_client_secret)

    @commands.command(name="8ball", pass_context=True)
    async def ball8(self, ctx, *, msg):
        msg_encoded = urllib.parse.quote(msg)
        url = "https://8ball.delegator.com/magic/JSON/" + msg_encoded
        result = requests.get(url)
        conv = json.loads(result.text)
        await self.bot.say(":eye_in_speech_bubble: " + conv["magic"]["answer"])

    @commands.group(pass_context=True)
    async def meme(self, ctx):
        server_id = ctx.message.server.id
        if server_id not in self.meme_sources:
            self.meme_sources[server_id] = list(MiscCog.default_meme_sources)

        if ctx.invoked_subcommand is None:
            sources = self.meme_sources[server_id]
            if len(sources) == 0:
                await self.bot.say("There are no subreddits to choose from")
                return

            sub_name = sources[randint(0, len(sources) - 1)]
            sub = self.reddit.subreddit(sub_name)
            post = sub.random()

            contents = requests.get(post.url).content
            print(post.url)
            print(post.title)

            em = discord.Embed(title=sub_name,
                               color=discord.Color.dark_grey(),
                               url=post.url,
                               description="**{}**".format(post.title))

            if "imgur" in post.url and "gifv" not in post.url:
                image_url = post.url + ".png"
            else:
                image_url = post.url
            em.set_image(url=image_url)

            em.set_footer(text=post.url,
                          icon_url="https://www.redditstatic.com/desktop2x/img/favicon/apple-icon-57x57.png")
            await self.bot.say(embed=em)

    @meme.command(name="source", aliases=["sources"], pass_context=True)
    async def meme_source(self, ctx):
        server_id = ctx.message.server.id
        sources = self.meme_sources[server_id]

        if len(sources) == 0:
            sources_str = "There are no subreddits to pull memes from"
        else:
            sources_str = ""
            for idx, src in enumerate(sources):
                sources_str += "**{0}. {1}**\n".format(idx + 1, src)

        em = discord.Embed(description=sources_str,
                           color=discord.Color.dark_purple())
        em.set_author(name="Reddit Meme Sources", icon_url=ctx.message.author.avatar_url)

        await self.bot.say(embed=em)

    @meme.command(name="add", pass_context=True)
    async def meme_add(self, ctx, *subreddits):
        server_id = ctx.message.server.id
        sources = self.meme_sources[server_id]

        for sub_name in subreddits:
            if len(sources) == MAX_NUM_SUBREDDITS:
                await self.bot.say("You can only pull from a maximum of {} subreddits".format(MAX_NUM_SUBREDDITS))
                return

            if sub_name in sources:
                await self.bot.say(sub_name + " is already in the list of subreddits")
                continue

            try:
                sub = self.reddit.subreddits.search_by_name(sub_name, exact=True)
                sources.append(sub_name)
                await self.bot.say("Added {} to the list of meme sources".format(sub_name))
            except prawcore.NotFound:
                await self.bot.say(sub_name + " does not exist or is not public")

    @meme.command(name="remove", pass_context=True)
    async def meme_remove(self, ctx, *subreddits):
        server_id = ctx.message.server.id
        sources = self.meme_sources[server_id]

        for sub_name in subreddits:
            if sub_name not in sources:
                await self.bot.say(sub_name + " is not in the list of subreddits")
            else:
                sources.remove(sub_name)
                await self.bot.say(sub_name + " has been removed from the list of subreddits")

    @commands.command(pass_context=True)
    async def dance(self, ctx):
        path = resources_dir + "/dance.gif"
        f = open(path, "rb")

        try:
            await self.bot.send_file(ctx.message.channel, f)
        finally:
            f.close()



def setup(bot):
    bot.add_cog(MiscCog(bot))
