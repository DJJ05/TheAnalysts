# -*- coding: utf-8 -*-

import datetime
import discord

from discord.ext import menus

class Source(menus.ListPageSource):
    def __init__(self, data):
        super().__init__(data, per_page=1)

    async def format_page(self, menu, entries):
        offset = menu.current_page * self.per_page
        a = ''.join(f'{v}' for i, v in enumerate(entries, start=offset))
        a = discord.Embed(
            description=f'{a}'
        )
        return a


class SignupMenu(menus.Menu):
    def __init__(self, *, check_embeds=False, message=None,
                 creator=None, seconds=43200):
        super().__init__(timeout=seconds, delete_message_after=True, clear_reactions_after=True, check_embeds=check_embeds, message=message)
        self.seconds = seconds
        self.creator = creator
        self.participants = []

    def reaction_check(self, payload):
        if payload.member and payload.member.bot:
            return False
        return True

    async def send_initial_message(self, ctx, channel):
        embed = discord.Embed(
            color=0x013220,
            title=f'New game started by {self.creator.name}',
            description=f'__React with \N{MEMO} to signup!__\n\n**Participants:**',
            timestamp=datetime.datetime.now() + datetime.timedelta(seconds=self.seconds)
        )
        embed.set_footer(text='Signups end:')
        return await channel.send(embed=embed)

    @menus.button('\N{MEMO}')
    async def on_signup(self, payload):
        if payload.member:
            self.participants.append(payload.member.id)
            try:
                await payload.member.send(f'You signed up for a game in {self.message.guild.name}!')
                embed = self.message.embeds[0]
                embed.description = f'{embed.description}\n> {payload.member}'
                await self.message.edit(embed=embed)
            except discord.Forbidden or AttributeError:
                pass
        else:
            if payload.user_id not in self.participants:
                return
            self.participants.remove(payload.user_id)
            user = self.bot.get_user(payload.user_id)
            try:
                await user.send(f'You removed your sign up for a game in {self.message.guild.name}')
            except discord.Forbidden or AttributeError:
                pass
            embed = self.message.embeds[0]
            embed.description = embed.description.replace(f'\n> {str(user)}', '')
            await self.message.edit(embed=embed)

    @menus.button('\N{NO ENTRY SIGN}')
    async def on_stop(self, payload):
        if payload.member == self.creator:
            return self.stop()
        try:
            await self.message.remove_reaction(payload.emoji, payload.member)
        except discord.Forbidden:
            pass
