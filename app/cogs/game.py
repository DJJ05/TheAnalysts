# -*- coding: utf-8 -*-

import asyncio
import discord

from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from helpers.paginator import SignupMenu
from helpers.timeconverter import TimeConverter


class game(commands.Cog):
    """Gameplay and main bot function cog"""

    def __init__(self, bot):
        self.bot = bot
        self.ongoing = dict()

    async def makecategory(self, guild: discord.Guild) -> discord.CategoryChannel:
        """Makes a category for the bot if one doesn't exist"""
        category = discord.utils.find(lambda cc: cc.name == 'TheAnalysts', guild.categories)
        if category:
            return category
        try:
            return await guild.create_category(name='TheAnalysts',
                                               reason='Game category for TheAnalysts, configure permissions manually.')
        except discord.Forbidden:
            raise commands.BadArgument(
                "Bot missing permissions to create game category. Please create a category: 'TheAnalysts' or provide manage_channels permissions.")

    async def makeannouncements(self, category: discord.CategoryChannel) -> discord.TextChannel:
        """Makes an announcement channel for the bot if one doesn't exist"""
        channel = discord.utils.find(lambda tc: tc.name == 'announcements', category.text_channels)
        if channel:
            return channel
        overwrites = {
            category.guild.default_role: discord.PermissionOverwrite(
                read_messages=True,
                send_messages=False,
            ),
            category.guild.me: discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True,
            )
        }
        try:
            return await category.create_text_channel(name='announcements', overwrites=overwrites,
                                                      reason='Announcements channel for TheAnalysts, configure permissions manually.')
        except discord.Forbidden:
            raise commands.BadArgument(
                "Bot missing permissions to create announcements channel. Please create a channel: 'announcements' inside TheAnalysts category or provide manage_channels permissions.")

    @commands.max_concurrency(1, per=BucketType.guild)
    @commands.command(aliases=['playgame', 'creategame'])
    async def makegame(self, ctx, time_until_end: TimeConverter = None):
        """Creates a game with a specified time until signups end. Given in the format '<amount><unit>', for example '5h4m2s' would end signups after 5 hours, 4 minutes and 2 seconds."""
        time_until_end = (None, 43200) if not time_until_end else time_until_end
        category = await self.makecategory(ctx.guild)
        channel = await self.makeannouncements(category)
        menu = SignupMenu(seconds=time_until_end[1], creator=ctx.author)
        await menu.start(ctx, channel=channel)
        await ctx.reply(f'Opened signups for new game in {channel.mention}. Use \N{NO ENTRY SIGN} to cancel the game.')
        while True:
            if menu._running:
                await asyncio.sleep(5)
            else:
                break
        await ctx.send('it ended')


def setup(bot):
    bot.add_cog(game(bot))
