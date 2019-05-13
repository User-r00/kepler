#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Error handling for Kepler."""

import asyncio
import discord
import traceback
import sys
from discord.ext import commands


class Errors(commands.Cog):
    """Handles errors thrown by the bot."""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Docstring."""
        if hasattr(ctx.command, 'on_error'):
            return

        ignored = (commands.CommandNotFound)

        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return

        elif isinstance(error, commands.DisabledCommand):
            return await ctx.send('This command has been disabled.')

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.author.send(f'{ctx.command} can not be '
                                              'used in DM.')
            except TypeError:
                pass

        elif isinstance(error, commands.BadArgument):
            if ctx.command.qualified_name == 'tag list':
                return await ctx.send('Could not find that member. Please try '
                                      'again.')

        elif isinstance(error, commands.UserInputError):
            await ctx.send(f'{ctx.command} failed. Here is the helper:')
            await ctx.send_help(ctx.command)
            self.bot.logger.error(f'{ctx.author} tried to use {ctx.command} '
                                   'but failed.')

        else:
            print('Ignoring exception in command {}'.format(ctx.command),
                  file=sys.stderr)
            traceback.print_exception(type(error),
                                      error, error.__traceback__,
                                      file=sys.stderr)


def setup(bot):
    """Add cog to bot."""
    bot.add_cog(Errors(bot))

# .r00
