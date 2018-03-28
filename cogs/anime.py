import discord
from discord.ext import commands
from bs4 import *
import re
import requests
import urllib
from base64 import b64encode
from mal_parser.mal import *
from mal_parser.media_objects import *

"""
TODO: 
    -MyAnimeList's public-facing API is very very bad. Replace with Anilist API at some point
    -Manga/anime are basically identical for now, but their implementations may change later on
    -Use memcached or redis and replace the temporary caching approach
"""


temp_cache_anime = {}
temp_cache_manga = {}

class Anime:
    def __init__(self, bot):
        self.bot = bot
        self.mal = Mal(self.bot.settings.mal_user, self.bot.settings.mal_pass)

    """Create a discord.Embed with info about the anime"""
    def _create_embed_anime(self, ctx, anime):
        em = discord.Embed(color=discord.Color.green())
        em.set_author(name=anime.title, icon_url=ctx.message.author.avatar_url, url=anime.link)
        em.set_thumbnail(url=anime.image)
        em.add_field(name="Synopsis", value=anime.truncate_synopsis(), inline=False)
        em.add_field(name="Episodes", value=anime.episodes, inline=True)
        em.add_field(name="Score", value=anime.score, inline=True)
        em.set_footer(text=anime.link, icon_url="https://myanimelist.cdn-dena.com/images/faviconv5.ico")
        return em

    """Create a discord.Embed with info about the manga"""
    def _create_embed_manga(self, ctx, manga):
        em = discord.Embed(color=discord.Color.blue())
        em.set_author(name=manga.title, icon_url=ctx.message.author.avatar_url, url=manga.link)
        em.set_thumbnail(url=manga.image)
        em.add_field(name="Synopsis", value=manga.truncate_synopsis(), inline=False)
        em.add_field(name="Chapters", value=manga.chapters, inline=True)
        em.add_field(name="Score", value=manga.score, inline=True)
        em.set_footer(text=manga.link, icon_url="https://myanimelist.cdn-dena.com/images/faviconv5.ico")
        return em


    @commands.command(pass_context=True)
    async def anime(self, ctx, *, name):
        if name in temp_cache_anime:
            await self.bot.say(embed=temp_cache_anime[name])
            return

        """Perform a search on MyAnimeList"""
        anime = self.mal.search(name, MediaTypes.anime)
        if anime is None:
            await self.bot.say(":confounded: No results found. Try rephrasing the name")
            return

        """If result found, create an embed and display formatted result"""
        em = self._create_embed_anime(ctx, anime)
        temp_cache_anime[name] = em
        await self.bot.say(embed=em)

    @commands.command(pass_context=True)
    async def manga(self, ctx, *, name):
        if name in temp_cache_manga:
            await self.bot.say(embed=temp_cache_manga[name])
            return

        manga = self.mal.search(name, MediaTypes.manga)
        if manga is None:
            await self.bot.say(":confounded: No results found. Try rephrasing the name")
            return

        em = self._create_embed_manga(ctx, manga)
        temp_cache_manga[name] = em
        await self.bot.say(embed=em)

def setup(bot):
    bot.add_cog(Anime(bot))
