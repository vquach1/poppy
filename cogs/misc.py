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

table_flip_collection = [
    "(╯°□°）╯︵ ┻━┻",
    "(┛◉Д◉)┛彡┻━┻",
    "(ﾉ≧∇≦)ﾉ ﾐ ┸━┸",
    "(ノಠ益ಠ)ノ彡┻━┻",
    "(╯ರ ~ ರ）╯︵ ┻━┻",
    "(┛ಸ_ಸ)┛彡┻━┻",
    "(ﾉ´･ω･)ﾉ ﾐ ┸━┸",
    "(ノಥ,_｣ಥ)ノ彡┻━┻",
    "(┛✧Д✧))┛彡┻━┻"
]

table_set_collection = [
    "┬──┬ ノ( ゜-゜ノ)",
    "┬──┬﻿ ¯\_(ツ)",
    "(ヘ･_･)ヘ┳━┳",
    "ヘ(´° □°)ヘ┳━┳",
    "┣ﾍ(≧∇≦ﾍ)… (≧∇≦)/┳━┳"
]

MAX_NUM_SUBREDDITS = 15


class Miscellaneous:
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

    @commands.command(aliases=["coinflip"], pass_context=True)
    async def flip(self, ctx):
        face = "Heads" if randint(0, 1) == 0 else "Tails"
        await self.bot.say("{0} flipped a coin, which landed on {1}".format(ctx.message.author.name, face))

    @commands.command(aliases=["dice"], pass_context=True)
    async def roll(self, ctx, faces=6):
        face = randint(0, faces-1) + 1
        await self.bot.say(":game_die: {0} rolled a die, which landed on {1}".format(ctx.message.author.name, face))

    @commands.command(aliases=["fliptable"], pass_context=True)
    async def tableflip(self, ctx):
        table = table_flip_collection[randint(0, len(table_flip_collection))-1]
        await self.bot.say(table)

    @commands.command(aliases=["settable"], pass_context=True)
    async def tableset(self, ctx):
        table = table_set_collection[randint(0, len(table_set_collection))-1]
        await self.bot.say(table)

    @commands.group(pass_context=True)
    async def meme(self, ctx):
        server_id = ctx.message.server.id
        if server_id not in self.meme_sources:
            self.meme_sources[server_id] = list(Miscellaneous.default_meme_sources)

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
    bot.add_cog(Miscellaneous(bot))
