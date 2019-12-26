#!usr/bin/env python3

"""Twitch extension for Kepler."""

import json

import aiohttp
import asyncio
import logging
from pprint import pprint
import subprocess

import discord
from discord.ext import tasks, commands
import semaphores
from credentials import tokens as TOKENS

from config import config as C
from paste_it import Paste_it

class General(commands.Cog):
    """Twitch commands for Kepler."""

    def __init__(self, bot):
        """Init."""
        self.bot = bot

    @commands.command(name='socials', aliases=['twitter', 'instagram', 'insta'])
    async def social_command(self, ctx):
        """Social links."""
        twitter = 'https://www.twitter.com/spaceboyr00'
        insta = 'https://www.instagram.com/spaceboyr00'
        await ctx.send(f'Follow me on Twitter: {twitter} or Instagram: '
                       f'{insta} .')

    @commands.command(name='address')
    async def address_command(self, ctx):
        """Shipping address."""
        await ctx.send('Shirts, "cook books", and glitter bombs can be sent '
                       'to P.O. Box 28331, San Jose CA, 95159.')

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

    @commands.command(name='log')
    async def log_command(self, ctx):
        """Retrieve the last 25 lines of the logs."""
        lines = subprocess.check_output(['tail', '-20', 'logs/kepler.log'])
        lines = lines.decode('utf-8')
        paste = Paste_it()
        results = await paste.new_paste(lines)
        await ctx.message.delete(delay=C.DEL_DELAY)
        self.bot.logger.info(f'{ctx.author} used {ctx.command}.')
        await ctx.send(results)


def setup(bot):
    """Add extension to bot."""
    bot.add_cog(General(bot))

# .r00
