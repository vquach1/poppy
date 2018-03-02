from discord.ext import commands
from errors import *


def is_owner():
    def predicate(ctx):
        if ctx.message.server.owner == ctx.message.author:
            raise NotOwner()
        return True
    return commands.check(predicate)
