from discord.ext import commands
from errors import *


def is_owner():
    def predicate(ctx):
        if ctx.message.server.owner == ctx.message.author:
            raise NotOwner()
        return True
    return commands.check(predicate)


def is_in_voice_channel():
    def predicate(ctx):
        if not ctx.bot.voice_client_in(ctx.message.server):
            raise NotInVoiceChannel()
        return True
    return commands.check(predicate)
