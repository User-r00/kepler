#!usr/bin/env python3

"""Twitch extension for Kepler."""

import json

import aiohttp
import asyncio
import logging
import os
from pprint import pprint
import subprocess

import discord
from discord.ext import tasks, commands
import semaphores
from credentials import tokens as TOKENS
from config import config as C


class Minecraft(commands.Cog):
    """Minecraft server status for Kepler."""

    def __init__(self, bot):
        """
        Init.
        """
        self.bot = bot
        self.check_server_heartbeat.start()
        self.first_run = True
        self.mc_is_alive = False

    @tasks.loop(seconds=60.0)
    async def check_server_heartbeat(self):
        """
        Check if the Minecraft server is alive.
        """
        # Channel to send notifications.
        channel = self.bot.get_channel(630157496568512543)

        # Ping the server
        cmd = f'nc -vz {C.mc_server_ip} {C.mc_server_port}'
        pipe = asyncio.subprocess.PIPE
        proc = await asyncio.create_subprocess_shell(cmd,
                                                     stdout=pipe,
                                                     stderr=pipe)

        stdout, stderr = await proc.communicate()

        # If the server is up.
        if proc.returncode == 0:

            # If the bot was previously down.
            if not self.mc_is_alive:

                # Record that the bot is alive.
                self.mc_is_alive = True

                if not self.first_run:
                    msg = 'The r00m\'s Minecraft server appears to be back ' \
                          'online after an outage.'

                    await channel.send(msg)

                    with open(f'command_images/yay.gif', 'rb') as f:
                        await channel.send(file=discord.File(f))

            self.bot.logger.info('MC Server heartbeat.')
            self.first_run = False
        # If the server is down.
        else:
            if self.mc_is_alive:
                self.mc_is_alive = False
                msg = 'The r00m\'s Minecraft server is experiencing issues.' \
                      '  Ping r00 if it persists.'
                await channel.send(msg)

                with open(f'command_images/pitchforks.gif', 'rb') as f:
                    await channel.send(file=discord.File(f))

                log = 'The Minecraft server appears to be having issues.'
                self.bot.logger.warning(log)

            self.first_run = False
        

    @check_server_heartbeat.before_loop
    async def before_check_server_heartbeat(self):
        """
        Wait until the bot is ready and then run the above loop.
        """
        await self.bot.wait_until_ready()


    @commands.command(name='mcstatus', aliases=[])
    async def mc_server_status_command(self, ctx):
        """
        Check Minecraft server status.
        """
        if semaphores.mc_is_alive:
            await ctx.channel.send('The MC server is online. If you are ' \
                                   'experiencing issues, check with ' \
                                   'Minecraft support.',
                                   delete_after=C.DEL_DELAY)
            await ctx.message.delete(delay=C.DEL_DELAY)
        else:
            await ctx.channel.send('The Minecraft server is reporting ' \
                                   'offline. Ping r00 if it persists.',
                                   delete_after=C.DEL_DELAY)
            await ctx.message.delete(delay=C.DEL_DELAY)

def setup(bot):
    """Add extension to bot."""
    bot.add_cog(Minecraft(bot))

# .r00
