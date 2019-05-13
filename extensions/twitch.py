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


class Twitch(commands.Cog):
    """Utility commands."""

    def __init__(self, bot):
        """Init."""
        self.bot = bot
        self.check_channel.start()

    @tasks.loop(seconds=10.0)
    # @commands.command(name='live')
    async def check_channel(self):
        """Check if a Twitch channel is live."""
        print('Checking if user is live...')
        # announce_channel = self.bot.get_channel(574845914477363210)
 
        USER = '195457791'
        CLIENT_ID = TOKENS.TWITCH_CLIENT
        HEADERS = {'client-id': TOKENS.TWITCH_CLIENT,
                   'Accept': 'application/vnd.twitchtv.v5+json'}
        URL = f'https://api.twitch.tv/kraken/streams/{USER}'
        async with aiohttp.ClientSession() as session:
            async with session.get(URL, headers=HEADERS) as resp:
                data = await resp.json()
                pprint(data)

                stream = data['stream']

                if data['stream'] is not None:
                    # Stream is live.
                    print('Stream is live.')
                    semaphores.is_live = True
                    URL = stream['channel']['url']
                    GAME = stream['game']
                    TITLE = f'r00 is streaming {GAME}!'
                    DESC = stream['channel']['status'].split('|')[0]
                    IMAGE = stream['preview']['large']

                    embed=discord.Embed(title=TITLE,
                                        description=DESC,
                                        color=0x6441a5,
                                        url=URL)
                    embed.set_image(url=IMAGE)
                    await announce_channel.send(embed=embed)
                else:
                    print('Stream is offline.')
                    semaphores.is_live = False

    @check_channel.before_loop
    async def before_check_channel(self):
        print('Waiting for bot to stand up...')
        await self.bot.wait_until_ready()
                
def setup(bot):
    """Add extension to bot."""
    bot.add_cog(Twitch(bot))

# .r00

