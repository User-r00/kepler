#!usr/bin/env python3

"""Twitch extension for Kepler."""

import json

import aiohttp
import asyncio
import logging
from pprint import pprint

import discord
from discord.ext import tasks, commands
import semaphores
from tokens import tokens as TOKENS


class General(commands.Cog):
    """Twitch commands for Kepler."""

    def __init__(self, bot):
        """Init."""
        self.bot = bot

    @commands.command(name='wishlist')
    async def wishlist_cmd(self, ctx):
        '''Respond with Amazon wishlist link.'''
        await ctx.send('https://www.amazon.com/hz/wishlist/ls/38YUIJLQQTS0F?ref_=wl_share')


def setup(bot):
    """Add extension to bot."""
    bot.add_cog(General(bot))

# .r00
