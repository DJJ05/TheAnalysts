# -*- coding: utf-8 -*-

import discord
import sys
import traceback

from discord.ext import commands


class errorhandler(commands.Cog, command_attrs={'hidden': True}):
    """Error handler"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener(name='on_command_error')
    async def error_handler(self, ctx, error):
        """Command error handler"""
        if isinstance(ctx.channel, discord.DMChannel):
            return

        if hasattr(ctx.command, 'on_error'):
            return

        default = (commands.BadArgument,
                   commands.TooManyArguments,
                   commands.MissingRequiredArgument,
                   commands.CommandOnCooldown,
                   commands.MaxConcurrencyReached,
                   discord.Forbidden,
                   commands.CheckFailure,
                   commands.DisabledCommand)
        ignored = (commands.CommandNotFound,)
        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return

        if isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send(f'{ctx.command} cannot be used in Private Messages. Please use it in your guild.')
            except discord.HTTPException:
                pass

        elif type(error) in default:
            await ctx.send('\n'.join(error.args))

        else:
            print('Ignoring exception in command {}:'.format(
                ctx.command), file=sys.stderr)
            traceback.print_exception(
                type(error), error, error.__traceback__, file=sys.stderr)
            errchannel = self.bot.get_channel(748962623487344753)
            etype = type(error)
            trace = error.__traceback__
            verbosity = 2
            lines = traceback.format_exception(etype, error, trace, verbosity)
            traceback_text = f'```py\n{"".join(lines)}\n```'.replace(
                'rajsharma', 'dev')
            embed = discord.Embed(title=f'Error during `{ctx.command.qualified_name}`',
                                  colour=self.bot.colour,
                                  description=f'ID: {ctx.message.id}\n[Jump]({ctx.message.jump_url})\n\
                                                    {traceback_text}')
            await errchannel.send(embed=embed)
            lines = traceback.format_exception(etype, error, trace, 1)
            traceback_text = f'```py\n{"".join(lines)}\n```'.replace(
                'rajsharma', 'dev')
            embed.description = f'ID: {ctx.message.id}\n[Jump]({ctx.message.jump_url})\n{traceback_text}'
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(errorhandler(bot))
