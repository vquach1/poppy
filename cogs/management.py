import discord
from discord.ext import commands
from checks import *


class Management:
    def __init__(self, bot):
        self.bot = bot

    @is_owner()
    @commands.group(pass_context=True)
    async def role(self, ctx):
        pass

    @role.command(name="create", pass_context=True)
    async def role_create(self, ctx, role):
        await self.bot.create_role(ctx.message.server, name=role, hoist=True)
        resp = "{} has been created as a role!".format(role)
        await self.bot.say(resp)

    @role.command(name="delete", pass_context=True)
    async def role_delete(self, ctx, role: discord.Role):
        await self.bot.delete_role(ctx.message.server, role)
        resp = "{} is no longer a role".format(role.name)
        await self.bot.say(resp)

    @role.command(name="add", pass_context=True)
    async def role_add(self, ctx, member: discord.Member, role: discord.Role):
        await self.bot.add_roles(member, role)
        resp = "{} is now a proud member of {}!".format(member.name, role.name)
        await self.bot.say(resp)

    @role.command(name="remove", pass_context=True)
    async def role_remove(self, ctx, member: discord.Member, role: discord.Role):
        await self.bot.remove_roles(member, role)
        resp = "{} is no longer a proud member of {}".format(member.name, role.name)
        await self.bot.say(resp)


def setup(bot):
    bot.add_cog(Management(bot))
