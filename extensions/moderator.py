#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""Moderator extension for Kepler."""

import asyncio
import aiohttp
import aiosqlite
from datetime import datetime
import random
import re

import discord
from discord.ext import commands

from config import config as C
from paste_it import Paste_it


class Moderator(commands.Cog):
    """Moderator commands."""
    def __init__(self, bot):
        """Init."""
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """Log when a message is deleted."""
        # Ignore bot messages.
        if message.author == self.bot.user:
            return

        # Ignore terminal messages.
        if message.channel.id == 577021097116041216:
            return

        # Labels.
        author = message.author.name
        channel = message.channel.name
        content = message.content
        date = message.created_at.strftime('%m/%d/%y')
        time = message.created_at.strftime('%H:%S')

        # Formatter
        embed = discord.Embed(title='Message deleted.',
                              description=f'Sent by {author} on {date} at {time}.',
                              color=0x000000,
                              url=None)
        embed.add_field(name='Original message',
                        value=content,
                        inline=False)
        
        channel = self.bot.get_channel(C.LOG_CHANNEL)
        await channel.send(embed=embed)


    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """Log when a message is edited."""
        # Ignore bot messages.
        if before.author == self.bot.user:
            return

        # Labels.
        author = before.author.name
        channel = before.channel.name
        before_content = before.content
        after_content = after.content
        date = before.created_at.strftime('%m/%d/%y')
        time = before.created_at.strftime('%H:%S')

        # Formatter
        embed = discord.Embed(title='Message edited.',
                              description=f'Sent by {author} on {date} at {time}.',
                              color=0x000000,
                              url=None)
        embed.add_field(name=f'Original message.',
                        value=before_content,
                        inline=False)
        embed.add_field(name='New message',
                        value=after_content,
                        inline=False)
        
        channel = self.bot.get_channel(C.LOG_CHANNEL)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Log when a user joins the server."""

        # Labels.
        date = before.created_at.strftime('%m/%d/%y')
        time = before.created_at.strftime('%H:%S')

        # Formatter
        embed = discord.Embed(title='User joined the server.',
                              description=f'{member.name} joined on {date} at {time}.',
                              color=0x000000,
                              url=None)
        
        channel = self.bot.get_channel(C.LOG_CHANNEL)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Log when a user leaves the server."""

        # Labels.
        date = before.created_at.strftime('%m/%d/%y')
        time = before.created_at.strftime('%H:%S')

        # Formatter
        embed = discord.Embed(title='User left the server.',
                              description=f'{member.name} left on {date} at {time}.',
                              color=0x000000,
                              url=None)
        
        channel = self.bot.get_channel(C.LOG_CHANNEL)
        await channel.send(embed=embed)

def setup(bot):
    bot.add_cog(Moderator(bot))
