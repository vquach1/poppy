import discord
from discord.ext import commands
from utils.league_api_wrapper import *


class LeagueCog:
    def __init__(self, bot):
        self.bot = bot
        self.summoner_ids = {} # Summoner name to ID
        self.league_api = LeagueApiWrapper(self.bot.settings.league_api_key)

        self.version = self.league_api.get_current_version()
        self.champs = self._init_champs()

    def _init_champs(self):
        champ_id_to_name = {}
        champs = self.league_api.get_champions()["data"]
        for champ_name in champs:
            champ_id = champs[champ_name]["id"]
            champ_id_to_name[champ_id] = champ_name

        return champ_id_to_name

    @commands.group(pass_context=True)
    async def league(self, ctx):
        pass

    @league.command(aliases=["user", "summoner"], pass_context=True)
    async def league_summoner(self, ctx, name):
        summoner = self.league_api.get_summoner(name=name)
        id = summoner["id"]
        self.summoner_ids[name] = id

        des="**Top Three:**\n"
        masteries = self.league_api.get_champion_mastery(id)
        print(summoner)

        rank = self.get_rank(id)
        if rank is None:
            rank_str = "None"
        else:
            rank_str = "{0} {1}".format(rank["tier"], rank["rank"])

        for i in range(0, min(3, len(masteries))):
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

        em = discord.Embed(title=summoner["name"],
                           description=des,
                           color=discord.Color.dark_green())
        em.set_thumbnail(url=summoner_icon_url)
        em.add_field(name="Level", value=summoner["summonerLevel"], inline=False)
        em.add_field(name="Rank", value=rank_str, inline=False)
        em.set_footer(text="League of Legends",
                      icon_url="http://2.bp.blogspot.com/-HqSOKIIV59A/"
                               "U8WP4WFW28I/AAAAAAAAT5U/qTSiV9UgvUY/s1600/icon.png")

        await self.bot.say(embed=em)

    @league.command(aliases=["champ", "champion"], pass_context=True)
    async def league_champion(self, ctx, name):
        await self.bot.say("TODO: League Champion")
        pass

    def get_rank(self, summ_id):
        positions = self.league_api.get_position(summ_id)
        for pos in positions:
            if pos["queueType"] == "RANKED_SOLO_5X5":
                return pos

        return None

def setup(bot):
    bot.add_cog(LeagueCog(bot))
