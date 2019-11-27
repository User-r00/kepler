#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Confession extension for Kepler."""

import discord
from discord.ext import commands

from config import config as C

class Confession(commands.Cog):
    """Confession extension."""
    
    def __init__(self, bot):
        """Init."""
        self.bot = bot
        
    @commands.dm_only()    
    @commands.command(name='confess')
    async def confess_command(self, ctx, *, confession):
        """Anonymously send a confession to the server."""
        # Get general channel.
        channel = self.bot.get_channel(479341433623543811)
        
        # Send message.
        await channel.send(f'**Confession:**{confession}')
        
def setup(bot):
    """Add cog to bot."""
    bot.add_cog(Confession(bot))