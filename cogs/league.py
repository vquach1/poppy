import discord
from discord.ext import commands
from utils.league_api_wrapper import *

league_icon_url = "http://2.bp.blogspot.com/-HqSOKIIV59A/U8WP4WFW28I/AAAAAAAAT5U/qTSiV9UgvUY/s1600/icon.png"
dragon_base = "http://ddragon.leagueoflegends.com/cdn"


class League:
    def __init__(self, bot):
        self.bot = bot
        self.summoner_ids = {} # Summoner name to ID
        self.league_api = LeagueApiWrapper(self.bot.settings.league_api_key)

        self.version = self.league_api.get_current_version()
        self.champs = self._init_champs()
        self.dragon_base = "{0}/{1}".format(dragon_base, self.version)  # Base must include the version number

    def _init_champs(self):
        """Maps all champion IDs to names"""

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
        self.summoner_ids[name] = summoner["id"]

        #  Form the strings related to rank (e.g. Gold V, and 120 / 104 win/loss ratio)
        rank = self.get_rank(summoner["id"])
        if rank is None:
            rank_str = "None"
            win_loss_str = "0 / 0"
        else:
            rank_str = "{0} {1}".format(rank["tier"], rank["rank"])
            win_loss_str = "{0} / {1}".format(rank["wins"], rank["losses"])

        #  Format the player's (up to) top 3 champions
        masteries = self.league_api.get_champion_mastery(summoner["id"])
        des="**Top Three:**\n"
        for i in range(0, min(3, len(masteries))):
            mastery = masteries[i]
            des += "**{0}. {1}** - Lv. {2}, {3}pts\n".format(
                i+1,
                self.champs[mastery["championId"]],
                mastery["championLevel"],
                mastery["championPoints"])

        summoner_icon_url = "{0}/img/profileicon/{1}.png".format(self.dragon_base, summoner["profileIconId"])

        em = discord.Embed(description=des, color=discord.Color.dark_green())
        em.set_thumbnail(url=summoner_icon_url)
        em.add_field(name="Level", value=summoner["summonerLevel"], inline=False)
        em.add_field(name="Rank", value=rank_str, inline=False)
        em.add_field(name="Win / Loss", value=win_loss_str, inline=False)
        em.set_author(name=summoner["name"], icon_url=ctx.message.author.avatar_url)
        em.set_footer(text="League of Legends", icon_url=league_icon_url)

        await self.bot.say(embed=em)

    @league.command(aliases=["champ", "champion"], pass_context=True)
    async def league_champion(self, ctx, name):
        await self.bot.say("TODO: League Champion")
        pass

    def get_rank(self, summ_id):
        positions = self.league_api.get_position(summ_id)
        for pos in positions:
            print(pos["queueType"])
            if pos["queueType"] == "RANKED_SOLO_5x5":
                return pos

        return None


def setup(bot):
    bot.add_cog(League(bot))
