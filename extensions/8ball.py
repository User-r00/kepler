#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""Games extension for Kepler."""

import asyncio
import aiohttp
import aiosqlite
import random

import discord
from discord.ext import commands

from config import config as C


class EightBall(commands.Cog):
    """8ball class."""

    def __init__(self, bot):
        """Init."""
        self.bot = bot
        self.task = self.bot.loop.create_task(self.check_db('8ball', 'responses'))
        self.task = self.bot.loop.create_task(self.propogate_responses())

    async def check_db(self, name, table):
        """Create db if it doesn't exist."""
        async with aiosqlite.connect(f'databases/{name}.db') as db:
            self.bot.logger.info('Creating 8 ball responses table.')
            await db.execute(f'CREATE TABLE IF NOT EXISTS {table} (response text PRIMARY KEY)')
            await db.commit()

    async def propogate_responses(self):
        """Generate 8ball responses."""
        resps = ['It is certain.',
                 'It is decidedly so.',
                 'Without a doubt.',
                 'Yes - definitely.',
                 'You may rely on it.',
                 'As I see it, yes.',
                 'Most likely.',
                 'Outlook good.',
                 'Yes.',
                 'Signs point to yes.',
                 'Reply hazy, try again.',
                 'Ask again later.',
                 'Better not tell you now.',
                 'Cannot predict now.',
                 'Concentrate and ask again.',
                 'Don\'t count on it.',
                 'My reply is no.',
                 'My sources say no.',
                 'Outlook not so good.',
                 'Very doubtful.']

        async with aiosqlite.connect(f'databases/8ball.db') as db:
            self.bot.logger.info('Propogating 8 ball resonses.')
            for response in resps:
                data = (response, )
                await db.execute('INSERT OR IGNORE INTO responses VALUES (?)', data)
                await db.commit()

    async def random_response(self):
        """Return random Magic 8 Ball response."""
        async with aiosqlite.connect(f'databases/8ball.db') as db:
            async with db.execute('SELECT response FROM responses ORDER BY RANDOM() LIMIT 1') as cursor:
                response = await cursor.fetchone()
        return response[0]

    @commands.command(name='8ball', aliases=[])
    async def magic8ball_command(self, ctx, question=None):
        """Shake the Magic 8 Ball."""
        response = await self.random_response()
        msg = f'**Magic 8 Ball says**\n```{response}```'
        await ctx.send(msg, delete_after=C.DEL_DELAY)
        await ctx.message.delete(delay=C.DEL_DELAY)

        self.bot.logger.info(f'{ctx.author} used {ctx.command}.')


def setup(bot):
    """Add cog to bot."""
    bot.add_cog(EightBall(bot))
