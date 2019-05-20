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


class Twitch(commands.Cog):
    """Twitch commands for Kepler."""

    def __init__(self, bot):
        """Init."""
        self.bot = bot
        self.check_channel.start()

    @tasks.loop(seconds=10.0)
    async def check_channel(self):
        """Check if a Twitch channel is live."""
        # Channel to send notifications.
        announce_channel = self.bot.get_channel(574845713016553490)
        if announce_channel is not None:
            self.bot.logger.info('Got announce channel.')

        # Twitch channel ID for one r00 boi.
        USER = '195457791'

        # Payload to send to the Twitch API call.
        CLIENT_ID = TOKENS.TWITCH_CLIENT
        HEADERS = {'client-id': TOKENS.TWITCH_CLIENT,
                   'Accept': 'application/vnd.twitchtv.v5+json'}
        URL = f'https://api.twitch.tv/kraken/streams/{USER}'

        # Context manager for hitting the Twitch API.
        async with aiohttp.ClientSession() as session:
            async with session.get(URL, headers=HEADERS) as resp:
                data = await resp.json()
                stream = data['stream']

                # If stream is live.
                if stream is not None:
                    if semaphores.is_live is False:
                        # Set live semaphore.
                        semaphores.is_live = True

                        # Embed data
                        URL = stream['channel']['url']
                        GAME = stream['game']
                        NAME = stream['channel']['display_name']
                        TITLE = f'{NAME} is streaming {GAME}!'
                        DESC = stream['channel']['status']
                        IMAGE = stream['preview']['large']

                        # Package the embed.
                        embed = discord.Embed(title=TITLE,
                                              description=DESC,
                                              color=0x6441a5,
                                              url=URL)
                        embed.set_image(url=IMAGE)

                        # Get Twitch Announcements role.
                        guild = self.bot.guilds[0]
                        role = guild.get_role(577531901515137054)

                        # Alert users.
                        await announce_channel.send(role.mention)
                        await announce_channel.send(embed=embed)

                        self.bot.logger.info(f'{NAME} is live. Notifying the gang.')  
                else:
                    semaphores.is_live = False
                    self.bot.logger.info('User is not live. Checking again '
                                             'in 60 seconds.')

    @check_channel.before_loop
    async def before_check_channel(self):
        """Run before the task above is done."""
        await self.bot.wait_until_ready()


def setup(bot):
    """Add extension to bot."""
    bot.add_cog(Twitch(bot))

# .r00
