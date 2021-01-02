# -*- coding: utf-8 -*-

import discord

from discord.ext import commands


class HelpCommand(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            embed = discord.Embed(description=page, colour=0xff9300)
            await destination.send(embed=embed)


class meta(commands.Cog):
    """Meta commands about the bot"""

    def __init__(self, bot):
        self.bot = bot

        self._original_help_command = bot.help_command
        bot.help_command = HelpCommand()
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self._original_help_command

    @commands.command(aliases=['latency'])
    async def ping(self, ctx):
        embed = discord.Embed(
            colour=self.bot.colour,
            description=f'`Bot latency:` {round(self.bot.latency * 100)}ms'
        )
        await ctx.reply(embed=embed)


def setup(bot):
    bot.add_cog(meta(bot))
