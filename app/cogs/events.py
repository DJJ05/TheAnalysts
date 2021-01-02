# -*- coding: utf-8 -*-

import discord

from discord.ext import commands


class events(commands.Cog, command_attrs={'hidden': True}):
    """Event handler"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener(name="on_message")
    async def on_bot_ping(self, message):
        if message.content in ("<@!794925480125792256>", "<@794925480125792256>"):
            guildpre = await self.bot.get_prefix(message)
            guildpre = f'{guildpre[2]}'
            appinfo = await self.bot.application_info()
            _commands = []
            for c in self.bot.commands:
                if c.enabled:
                    _commands.append(c.name)
            embed = discord.Embed(title=f"{appinfo.name} | {appinfo.id}",
                                  colour=self.bot.colour,
                                  description=f":diamond_shape_with_a_dot_inside: `Guild Prefix:` **{guildpre}**\
                                                  \n\n**Do** `{guildpre}help` **to view a full command list.**\
                                                  \n**Do** `{guildpre}help [command]` **to view specific command help.**")
            embed.set_author(
                name=f'Requested by {message.author}',
                icon_url=message.author.avatar_url)
            await message.reply(embed=embed)

def setup(bot):
    bot.add_cog(events(bot))
