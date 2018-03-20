import discord
from discord.ext import commands
import requests
import json

class LeagueCog:
    def __init__(self, bot):
        self.bot = bot
        self.key = self.bot.settings.league_api_key
        self.summoner_ids = {} # Summoner name to ID

        self.headers = {
            "User-Agent": "Poppi Discord Bot (Contact: vitungquach1494@gmail.com)"
        }

    @commands.group(pass_context=True)
    async def league(self, ctx):
        pass

    @league.command(aliases=["user", "summoner"], pass_context=True)
    async def league_summoner(self, ctx, name):
        res = self.get_summoner(name=name)
        if res.status_code != 200:
            await self.bot.say("HTTP Request Error in league_summoner")
            return

        summoner = json.loads(res.content)
        self.summoner_ids[summoner.name] = summoner.id

        await self.bot.say("TODO: League Summoner")

    @league.command(aliases=["champ", "champion"], pass_context=True)
    async def league_champion(self, ctx, name):
        await self.bot.say("TODO: League Champion")
        pass

    """ Performs a summoner search, based on either summoner name or summoner ID
        -If name is provided, search by name
        -If id is provided, search by id"""
    def get_summoner(self, **kwargs):
        base = "https://na1.api.riotgames.com/lol/summoner/v3/summoners"
        if "name" in kwargs:
            ext = "by-name/{0}".format(kwargs.name)
        elif "summ_id" in kwargs:
            ext = "by-account/{0}".format(kwargs.id)

        url = "{0}/{1}?api_key={2}".format(base, ext, self.key)
        return requests.get(url, self.headers)

    """Provides a summoner's play statistics for different champions
        -If champ_id is provided, give back specific champion info
        -Otherwise, give back all champion info for the summoner"""
    def get_champion_mastery(self, summ_id, **kwargs):
        base = "https://na1.api.riotgames.com/lol/champion-mastery/" \
               "v3/champion-masteries/by-summoner/{0}".format(summ_id)

        if "champ_id" in kwargs:
            ext = "/by-champion/{0}".format(kwargs.champ_id)
        else:
            ext = ""

        url="{0}{1}".format(base, ext)
        return requests.get(url, self.headers)

    """Provides a summoner's total mastery levels"""
    def get_champion_mastery_total(self, summ_id):
        url = "/lol/champion-mastery/v3/scores/by-summoner/{0}".format(summ_id)
        return requests.get(url, self.headers)


def setup(bot):
    bot.add_cog(LeagueCog(bot))