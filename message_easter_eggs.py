from random import randint
import datetime
import re

class MessageEasterEggs:
    def __init__(self, bot):
        self.bot = bot
        self.eggs = [self.ayy, self.ree]

    async def process_eggs(self, msg):
        if msg.author == self.bot.user:
            return

        for egg in self.eggs:
            await egg(msg)

    """Whenever 'ayy' is present within a message, the bot will respond with 'lmao'"""
    async def ayy(self, msg):
        if not bool(re.search("(a|A)(y|Y){2}", msg.content)):
            return

        aRep = ''
        oRep = ''
        for x in range(randint(1, 5)):
            aRep += chr(32 * randint(0, 1) + 65)
        for x in range(randint(1, 5)):
            oRep += chr(32 * randint(0, 1) + 79)

        res = "**lm{0}{1}!**".format(aRep, oRep)

        await self.bot.send_message(msg.channel, res)

    """Upon message receive, the bot has a 1/100 chance of yelling 'REEEE' in the chat"""
    async def ree(self, msg):
        if randint(0, 100) != 50:
            return

        rChar = chr(32 * randint(0, 1) + 82)
        eRep = ""
        for y in range(randint(10, 40)):
            eRep += chr(32 * randint(0, 1) + 69)

        res = "**{0}{1}**".format(rChar, eRep)

        await self.bot.send_message(msg.channel, res)

