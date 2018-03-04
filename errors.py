from discord.ext import commands


class NotOwner(commands.CheckFailure):
    pass

class NotInVoiceChannel(commands.CheckFailure):
    pass

class UserNotInVoiceChannel(commands.CheckFailure):
    pass