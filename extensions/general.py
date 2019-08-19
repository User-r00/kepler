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
        '''Amason stream wishlist.'''
        await ctx.send('Want to help move the stream forward? Check out the link https://www.amazon.com/hz/wishlist/ls/38YUIJLQQTS0F?ref_=wl_share !')

    @commands.command(name='socials', aliases=['twitter', 'instagram', 'insta'])
    async def social_command(self, ctx):
        """Social links."""
        twitter = 'https://www.twitter.com/DarkPlagueDr'
        insta = 'https://www.instagram.com/DarkPlagueDr'
        await ctx.send(f'Follow me on Twitter: {twitter} or Instagram: '
                       f'{insta} .')

    @commands.command(name='address')
    async def address_command(self, ctx):
        """Shipping address."""
        await ctx.send('Shirts, spandex, and glitter bombs can be sent to P.O. '
                       'Box 28331, San Jose CA, 95159.')

    @commands.command(name='repo', aliases=['code', 'github', 'git'])
    async def repo_command(self, ctx):
        """Github repo."""
        URL = 'https://github.com/User-r00'
        await ctx.send(f'Check out my code at {URL} !')

    @commands.command(name='steam')
    async def steam_command(self, ctx):
        """Steam profile."""
        URL = 'https://steamcommunity.com/profiles/76561198828992335/'
        await ctx.send(f'Check my Steam profile at {URL} ! Be sure to add me '
                       f'while you\'re there!')


def setup(bot):
    """Add extension to bot."""
    bot.add_cog(General(bot))

# .r00
