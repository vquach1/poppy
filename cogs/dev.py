import discord
from discord.ext import commands

"""This cog's initial motivation is to make it easy to load/unload cogs from the Discord chat
   without stopping the bot. However, the bot needs to be taken down whenever this cog is modified.
   Ironic."""


class DevCog:
    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True)
    async def cog(self, ctx):
        pass

    @cog.command(alias=["add", "load"], pass_context=True)
    async def cog_add(self, ctx, cog):
        self.bot.load_extension("cogs." + cog)
        await self.bot.say(cog + " has been loaded!")

    @cog.command(alias=["remove", "unload"], pass_context=True)
    async def cog_remove(self, ctx, cog):
        self.bot.unload_extension("cogs." + cog)
        await self.bot.say(cog + " has been unloaded!")

    @cog.command(name="reload", pass_context=True)
    async def cog_reload(self, ctx, cog):
        if cog == "anime" or cog == "manga":
            cog = "japanese_media"

        self.bot.unload_extension("cogs." + cog)
        self.bot.load_extension("cogs." + cog)
        await self.bot.say(cog + " has been reloaded!")


def setup(bot):
    bot.add_cog(DevCog(bot))
