# -*- coding: utf-8 -*-

import asyncio
import discord
import random

from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from helpers.team import Team
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

    async def maketeamchannels(self, category: discord.CategoryChannel, axis: list, allies: list) -> dict:
        """Makes announcement, text channel and voice channels for each team"""
        axisannouncements = discord.utils.find(lambda tc: tc.name == 'axis-announcements', category.text_channels)
        axistext = discord.utils.find(lambda tc: tc.name == 'axis-text', category.text_channels)
        alliesannouncements = discord.utils.find(lambda tc: tc.name == 'allies-announcements', category.text_channels)
        alliestext = discord.utils.find(lambda tc: tc.name == 'allies-text', category.text_channels)
        axisoverwrites = {
            category.guild.default_role: discord.PermissionOverwrite(
                read_messages=False,
                send_messages=False,
            )
        }
        alliesoverwrites = {
            category.guild.default_role: discord.PermissionOverwrite(
                read_messages=False,
                send_messages=False,
            )
        }
        axisannouncementsoverwrites = {
            category.guild.default_role: discord.PermissionOverwrite(
                read_messages=False,
                send_messages=False,
            )
        }
        alliesannouncementsoverwrites = {
            category.guild.default_role: discord.PermissionOverwrite(
                read_messages=False,
                send_messages=False,
            )
        }
        for axi in axis:
            axisoverwrites[axi] = discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True,
            )
            axisannouncementsoverwrites[axi] = discord.PermissionOverwrite(
                read_messages=True,
                send_messages=False,
            )
        for allie in allies:
            alliesoverwrites[allie] = discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True,
            )
            alliesannouncementsoverwrites[allie] = discord.PermissionOverwrite(
                read_messages=True,
                send_messages=False,
            )
        try:
            if not axisannouncements:
                axisannouncements = await category.create_text_channel(name='axis-announcements',
                                                                       overwrites=axisannouncementsoverwrites,
                                                                       reason='Axis team announcements')
            if not axistext:
                axistext = await category.create_text_channel(name='axis-text', overwrites=axisoverwrites,
                                                              reason='Axis team text')
            if not alliesannouncements:
                alliesannouncements = await category.create_text_channel(name='allies-announcements',
                                                                         overwrites=alliesannouncementsoverwrites,
                                                                         reason='Allies team announcements')
            if not alliestext:
                alliestext = await category.create_text_channel(name='allies-text', overwrites=alliesoverwrites,
                                                                reason='Allies team text')
        except discord.Forbidden:
            raise commands.BadArgument(
                'Bot missing permissions to create team channels. Please provide manage_channels permissions.')
        return {
            'alliesannouncements': alliesannouncements,
            'alliestext': alliestext,
            'axisannouncements': axisannouncements,
            'axistext': axistext
        }

    @commands.max_concurrency(1, per=BucketType.channel)
    @commands.cooldown(1, 15, BucketType.guild)
    async def answer(self, ctx, answer):
        if ctx.guild.id not in list(self.ongoing.keys()):
            raise commands.BadArgument('Your guild doesn\'t have an ongoing game, or it hasn\'t started yet. Use `w!playgame` to start one.')
        team = None
        for team_ in self.ongoing[ctx.guild.id].values():
            if ctx.author in team_.members:
                team = team_
        if not team:
            raise commands.BadArgument('It looks like you\'re not currently participating in your guild\'s ongoing game.')
        if ctx.author not in team.generals:
            raise commands.BadArgument('You need to be a general on your team in order to register answers.')

        # TODO: Validate answer against team.current_message.answer once current_message object created

    @commands.max_concurrency(1, per=BucketType.guild)
    @commands.command(aliases=['playgame', 'creategame'])
    async def makegame(self, ctx, time_until_end: TimeConverter = None):
        """Creates a game with a specified time until signups end. Given in the format '<amount><unit>', for example '5h4m2s' would end signups after 5 hours, 4 minutes and 2 seconds."""
        if ctx.guild.id in list(self.ongoing.keys()):
            raise commands.BadArgument('There cannot be more than one ongoing game per guild, please wait for the current game to end.')
        time_until_end = (None, 43200) if not time_until_end else time_until_end
        category = await self.makecategory(ctx.guild)
        announcements = await self.makeannouncements(category)
        menu = SignupMenu(seconds=time_until_end[1], creator=ctx.author)
        await menu.start(ctx, channel=announcements)
        await ctx.reply(
            f'Opened signups for new game in {announcements.mention}. Use \N{NO ENTRY SIGN} to cancel the game, or \N{LARGE GREEN CIRCLE} to force-start it.')
        while True:
            if menu._running:
                await asyncio.sleep(5)
            else:
                break
        if menu.cancelled:
            return await ctx.reply('Game has been cancelled.')
        menu.participants.extend([204255221017214977, 720229743974285312, 505532526257766411])
        participants = [ctx.guild.get_member(id_) for id_ in menu.participants]
        if len(participants) < 4:
            for participant in participants:
                try:
                    await participant.send(
                        f'The ongoing game in {ctx.guild.name} has been cancelled due to lack of participation. Minimum players is 4.')
                except discord.HTTPException:
                    pass
            return
        axis = random.sample(participants, round(len(participants) / 2))
        allies = list(set(participants) - set(axis))

        # TODO: Add encryption as current_message object and use in class constructor

        channels = await self.maketeamchannels(category=category, axis=axis, allies=allies)
        axis = Team(members=axis, channels=channels, current_message='stuff', faction='axis')
        allies = Team(members=allies, channels=channels, current_message='stuff', faction='allies')
        for axi in axis.members:
            try:
                await axi.send(
                    f'The ongoing game in {ctx.guild.name} has started. You are on the **axis** team. You have a 10 minute grace period to talk in {channels["axistext"].mention} before encrypted messages will be revealed.')
            except discord.HTTPException:
                await channels["axisannouncements"].send(f'{axi.mention}', delete_after=0.1)
        for allie in allies.members:
            try:
                await allie.send(
                    f'The ongoing game in {ctx.guild.name} has started. You are on the **allies** team. You have a 10 minute grace period to talk in {channels["alliestext"].mention} before encrypted messages will be revealed.')
            except discord.HTTPException:
                await channels["alliesannouncements"].send(f'{allie.mention}', delete_after=0.1)
        msg = f'Welcome axis. In 1 minute you will receive an encrypted message, intercepted from the allies. ' \
              f'You will need to decrypt this message as quickly as possible, in order to score points and damage the ' \
              f'allies.\n\nHowever, the allies will be receiving an intercepted communication package from us at the same ' \
              f'time, with the same rewards. With your points, you may research certain techniques that may help you to ' \
              f'decrypt your messages, or to provide progress updates on the enemy. Be warned that certain among you may ' \
              f'not share your interests...\n\nThe faction that reaches zero health the first will lose. Good luck axis.\n\u2800'
        msg2 = f'Welcome allies. In 1 minute you will receive an encrypted message, intercepted from the axis. ' \
               f'You will need to decrypt this message as quickly as possible, in order to score points and damage the ' \
               f'axis.\n\nHowever, the axis will be receiving an intercepted communication package from us at the same ' \
               f'time, with the same rewards. With your points, you may research certain techniques that may help you to ' \
               f'decrypt your messages, or to provide progress updates on the enemy. Be warned that certain among you may ' \
               f'not share your interests...\n\nThe faction that reaches zero health the first will lose. Good luck allies.\n\u2800'
        await channels["axisannouncements"].send(msg)
        await channels["alliesannouncements"].send(msg2)
        await asyncio.sleep(60)
        msg3 = 'Your allocated generals are {}. These are the people that can use `w!research` and `w!deploy`, to see the catalogue of items available for purchase. ' \
               'Consider them your leaders. Use `w!help game` to see the commands you can use to help you, although you will ' \
               'need to rack up some points for that first, which you get from decrypting messages.\n\nYour first message to ' \
               'decrypt is:\n`insert encrypted message here`\nUse `w!answer <answer>` to register your answer for points. Good luck.\n\u2800'
        await channels["axisannouncements"].send(msg3.format(', '.join([m.mention for m in axis.generals])))
        await channels["alliesannouncements"].send(msg3.format(', '.join([m.mention for m in allies.generals])))
        self.ongoing[ctx.guild.id] = dict(axis=axis, allies=allies)


def setup(bot):
    bot.add_cog(game(bot))
