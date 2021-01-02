# -*- coding: utf-8 -*-

import asyncio
import json
import os

import discord
from discord.ext import commands

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"


class Bot(commands.Bot):
    def __init__(self, event_loop: asyncio.AbstractEventLoop, intents: discord.Intents) -> None:
        super().__init__(command_prefix=self.get_prefix,
                         intents=intents,
                         case_insensitive=True,
                         loop=event_loop,
                         description="")
        print('——————————————————————————————')
        for filename in os.listdir('app/cogs'):
            if filename.endswith('.py'):
                self.load_extension(f'cogs.{filename[:-3]}')
                print(f'[LOADED] cogs.{filename}')
        self.load_extension(name='jishaku')
        print('[LOADED] jishaku\n——————————————————————————————')
        print(f'Cogs are loaded, logging in...\n——————————————————————————————')
        self.colour = 0x013220

    async def get_prefix(self, message: discord.Message) -> str:
        return commands.when_mentioned_or('w!')(self, message)

    async def on_ready(self) -> None:
        print(f'Logged in as: {self.user}')
        print(f'With ID: {self.user.id}\n——————————————————————————————')
        await self.change_presence(activity=discord.Activity(type=5, name="World War 2"))
        print(f'Status changed successfully \n——————————————————————————————')

    def run(self) -> None:
        token = json.load(open('app/config.json'))['token']
        super().run(token)


def main() -> None:
    intents = discord.Intents.all()
    event_loop = asyncio.get_event_loop()
    bot = Bot(event_loop=event_loop, intents=intents)
    bot.run()


if __name__ == '__main__':
    main()
