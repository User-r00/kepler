#!usr/bin/env python3

"""Twitch extension for Kepler."""

import json

import aiohttp
import asyncio
import logging

import discord
from discord.ext import tasks, commands
import semaphores
from tokens import tokens as TOKENS


class Twitch(commands.Cog):
    """Utility commands."""

    def __init__(self, bot):
        """Init."""
        self.bot = bot
        self.check_channel.start()

    @tasks.loop(seconds=60.0)
    # @commands.command(name='live')
    async def check_channel(self, ctx):
        """Check if a Twitch channel is live."""

        announce_channel = self.bot.get_channel(574845713016553490)

        USER = '195457791'  # r00
        USER = '191552265'  # Hex
        CLIENT_ID = TOKENS.TWITCH_CLIENT
        HEADERS = {'client-id': TOKENS.TWITCH_CLIENT,
                   'Accept': 'application/vnd.twitchtv.v5+json'}
        URL = f'https://api.twitch.tv/kraken/streams/{USER}'

        self.bot.logger.info(f'Checking if {USER} is live.')

        async with aiohttp.ClientSession() as session:
            async with session.get(URL, headers=HEADERS) as resp:
                self.bot.logger.info(f'Checking with Twitch.')
                data = await resp.json()

                stream = data['stream']

                if data['stream'] is not None:
                    # Stream is live.
                    self.bot.logger.info(f'User is live.')
                    semaphores.is_live = True
                    URL = stream['channel']['url']
                    GAME = stream['game']
                    TITLE = f'r00 is streaming {GAME}!'
                    DESC = stream['channel']['status'].split('|')[0]
                    IMAGE = stream['preview']['large']

                    embed = discord.Embed(title=TITLE,
                                          description=DESC,
                                          color=0x6441a5,
                                          url=URL)
                    embed.set_image(url=IMAGE)

                    channel = self.bot.get_channel(574845713016553490)
                    role = ctx.guild.get_role(574845243908947988)
                    await channel.send(role.mention)
                    await announce_channel.send(embed=embed)
                else:
                    semaphores.is_live = False
                    self.bot.logger.info('User is not live. Checking again '
                                         'in 60 seconds.')

    @check_channel.before_loop
    async def before_check_channel(self):
        self.bot.logger.info('Waiting for bot to stand up...')
        await self.bot.wait_until_ready()

    @commands.command()
    async def testping(self, ctx):
        print('Sending announce.')
        announce_channel = self.bot.get_channel(574845713016553490)

        USER = '195457791'  # r00
        CLIENT_ID = TOKENS.TWITCH_CLIENT
        HEADERS = {'client-id': TOKENS.TWITCH_CLIENT,
                   'Accept': 'application/vnd.twitchtv.v5+json'}
        URL = f'https://api.twitch.tv/kraken/streams/{USER}'

        self.bot.logger.info(f'Checking if {USER} is live.')

        async with aiohttp.ClientSession() as session:
            async with session.get(URL, headers=HEADERS) as resp:
                self.bot.logger.info(f'Checking with Twitch.')
                data = await resp.json()

                stream = data['stream']

                if data['stream'] is not None:
                    # Stream is live.
                    self.bot.logger.info(f'User is live.')
                    semaphores.is_live = True
                    URL = stream['channel']['url']
                    GAME = stream['game']
                    TITLE = f'r00 is streaming {GAME}!'
                    DESC = stream['channel']['status'].split('|')[0]
                    IMAGE = stream['preview']['large']

                    embed = discord.Embed(title=TITLE,
                                          description=DESC,
                                          color=0x6441a5,
                                          url=URL)
                    embed.set_image(url=IMAGE)

                    channel = self.bot.get_channel(574845713016553490)
                    role = ctx.guild.get_role(574845243908947988)
                    await channel.send(role.mention)
                    await announce_channel.send(embed=embed)
                else:
                    semaphores.is_live = False
                    self.bot.logger.info('User is not live. Checking again '
                                         'in 60 seconds.')


def setup(bot):
    """Add extension to bot."""
    bot.add_cog(Twitch(bot))

# .r00
