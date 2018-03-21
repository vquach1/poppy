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

        self.champs = self._init_champs()
        self.version = self.get_current_version()

    def _init_champs(self):
        champ_id_to_name = {}
        champs = self.get_champions()["data"]
        for champ_name in champs:
            champ_id = champs[champ_name]["id"]
            champ_id_to_name[champ_id] = champ_name

        return champ_id_to_name

    @commands.group(pass_context=True)
    async def league(self, ctx):
        pass

    @league.command(aliases=["user", "summoner"], pass_context=True)
    async def league_summoner(self, ctx, name):
        summoner = self.get_summoner(name=name)
        id = summoner["id"]
        self.summoner_ids[name] = id

        des="Top Three Champions:\n"
        masteries = self.get_champion_mastery(id)
        print(masteries)
        print(self.champs)

        for i in range(0,3):
            mastery = masteries[i]
            champ_name = self.champs[mastery["championId"]]
            champ_level = mastery["championLevel"]
            champ_points = mastery["championPoints"]

            des += "**{0}. {1}** - Lv. {2}, {3}pts\n".format(i+1,
                                                             champ_name,
                                                             champ_level,
                                                             champ_points)

        summoner_icon_url = "http://ddragon.leagueoflegends.com/cdn" \
                            "/{0}/img/profileicon/{1}.png".format(self.version, summoner["profileIconId"])

        em = discord.Embed(title=name,
                           description=des,
                           color=discord.Color.dark_green())
        em.set_thumbnail(url=summoner_icon_url)
        em.set_footer(text="League of Legends",
                      icon_url="http://2.bp.blogspot.com/-HqSOKIIV59A/"
                               "U8WP4WFW28I/AAAAAAAAT5U/qTSiV9UgvUY/s1600/icon.png")

        await self.bot.say(embed=em)

    @league.command(aliases=["champ", "champion"], pass_context=True)
    async def league_champion(self, ctx, name):
        await self.bot.say("TODO: League Champion")
        pass

    def get_current_version(self):
        url = "https://na1.api.riotgames.com/lol/static-data/v3/versions?api_key={0}".format(self.key)
        res = requests.get(url, self.headers)

        data = json.loads(res.content)
        return data[0]

    def get_champions(self, **kwargs):
        base = "https://na1.api.riotgames.com/lol/static-data/v3/champions"

        if "champ_id" in kwargs:
            ext = "/{0}".format(kwargs["champ_id"])
        else:
            ext = ""

        url = "{0}{1}?api_key={2}".format(base, ext, self.key)
        res = requests.get(url, self.headers)
        data = json.loads(res.content)
        return data

    def get_summoner(self, **kwargs):
        """ Performs a summoner search, based on either summoner name or summoner ID
            -If name is provided, search by name
            -If id is provided, search by id"""

        base = "https://na1.api.riotgames.com/lol/summoner/v3/summoners"
        if "name" in kwargs:
            ext = "by-name/{0}".format(kwargs["name"])
        elif "summ_id" in kwargs:
            ext = "by-account/{0}".format(kwargs["id"])

        url = "{0}/{1}?api_key={2}".format(base, ext, self.key)
        res = requests.get(url, self.headers)
        data = json.loads(res.content)
        return data

    def get_champion_mastery(self, summ_id, **kwargs):
        """Provides a summoner's play statistics for different champions
            -If champ_id is provided, give back specific champion info
            -Otherwise, give back all champion info for the summoner"""

        base = "https://na1.api.riotgames.com/lol/champion-mastery/" \
               "v3/champion-masteries/by-summoner/{0}".format(summ_id)

        if "champ_id" in kwargs:
            ext = "/by-champion/{0}".format(kwargs["champ_id"])
        else:
            ext = ""

        url="{0}{1}?api_key={2}".format(base, ext, self.key)
        res = requests.get(url, self.headers)
        data = json.loads(res.content)
        return data

    def get_champion_mastery_total(self, summ_id):
        """Provides a summoner's total mastery levels"""

        url = "/lol/champion-mastery/v3/scores/by-summoner/{0}?api_key={1}".format(summ_id, self.key)
        res = requests.get(url, self.headers)
        data = json.loads(res.content)
        return data


def setup(bot):
    bot.add_cog(LeagueCog(bot))