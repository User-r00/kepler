#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Never Have I Ever extension for Kepler."""

import asyncio
import aiohttp
import discord
from discord.ext import commands

from config import config as C


class NeverHaveIEver(commands.Cog):
    """Polls base class."""

    def __init__(self, bot):
        """Init."""
        self.bot = bot

    @commands.command(name='neverhaveiever', aliases=['nhie'])
    async def nhie_command(self, ctx, *, question):
        """Create a new NHIE."""
        await ctx.channel.send(f'**New NHIE.**')
        message = await ctx.channel.send(f'```fix\nNever have I ever {question}\n```')
        await message.add_reaction('🍺')
        await ctx.message.delete(delay=C.DEL_DELAY)
        self.bot.logger.info(f'{ctx.author} created a NHIE on {question}.')


def setup(bot):
    """Add cog to bot."""
    bot.add_cog(NeverHaveIEver(bot))