import discord
from discord.ext import commands
import spice_api
from bs4 import *
from urllib.parse import quote
import googlesearch
import re


class JapaneseMediaCog:
    def __init__(self, bot):
        self.bot = bot

        mal_user = self.bot.settings.mal_user
        mal_pass = self.bot.settings.mal_pass
        self.mal_creds = spice_api.init_auth(mal_user, mal_pass)

    """Removes HTML tags, truncates if length too long, and corrects italics/bolded characters"""
    def _clean_synopsis(self, html):
        synopsis = BeautifulSoup(html, "lxml").get_text()
        if len(synopsis) > 1000:
            synopsis = synopsis[0:996] + "..."

        synopsis = re.sub("\[\/?i\]", "_", synopsis)
        return synopsis

    """Create a discord.Embed with info about the anime/manga"""
    def _create_embed(self, media, link):
        synopsis = self._clean_synopsis(media.synopsis)
        title = media.title
        image_url = media.image_url
        episodes = media.episodes
        start_date = media.dates[0]
        end_date = media.dates[1].replace("0000-00-00", "Present")
        dates = "{} - {}".format(start_date, end_date)

        em = discord.Embed(title=title,
                           url=link,
                           color=discord.Color.green())
        em.set_thumbnail(url=image_url)
        em.add_field(name="Synopsis", value=synopsis, inline=False)
        em.add_field(name="Episodes", value=episodes, inline=True)
        em.add_field(name="Dates", value=dates, inline=True)
        em.set_footer(text=link,
                      icon_url="https://myanimelist.cdn-dena.com/images/faviconv5.ico")

        return em

    """This temporarily uses Google to search the anime. 
       Eventually, change this to use Python scraping instead on
       https://myanimelist.net/search/all?q=<NAME OF ANIME HERE>
       
       There's no perfect solution. For now, Google appaers to give the best result
       to user queries such as...
       !anime jojo part 4
    """

    @commands.command(pass_context=True)
    async def anime(self, ctx, *, name):
        search_str = name + " myanimelist"
        link = list(googlesearch.search(search_str, num=1, start=0, stop=1, pause=2.0))[0]
        id = int(re.search("(?<=https://myanimelist.net/anime/).+(?=/.+)", link).group(0))

        print("ID of " + link + " is " + str(id))

        medium = spice_api.get_medium("anime")
        #anime = spice_api.search(name, medium, self.mal_creds)[0]
        anime = spice_api.search_id(id, medium, self.mal_creds)
        em = self._create_embed(anime, link)

        await self.bot.say(embed=em)

def setup(bot):
    bot.add_cog(JapaneseMediaCog(bot))
