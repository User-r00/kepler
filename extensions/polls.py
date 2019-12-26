#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Polls extension for Kepler."""

import asyncio
import aiohttp
import discord
from discord.ext import commands

from config import config as C


class Polls(commands.Cog):
    """Polls base class."""

    def __init__(self, bot):
        """Init."""
        self.bot = bot

    @commands.command(name='poll')
    async def poll_command(self, ctx, *, question):
        """Create a new poll."""
        await ctx.channel.send(f'**New poll from {ctx.author.display_name}.**')
        message = await ctx.channel.send('```fix\n{}\n```'.format(question))
        await message.add_reaction('👍')
        await message.add_reaction('👎')
        await ctx.message.delete(delay=C.DEL_DELAY)
        self.bot.logger.info(f'{ctx.author} created a poll on {question}.')


def setup(bot):
    """Add cog to bot."""
    bot.add_cog(Polls(bot))
