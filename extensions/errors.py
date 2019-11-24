#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Error handling."""

import random
import sys
import traceback

import asyncio
import discord
from discord.ext import commands

from config import config as C


class Errors(commands.Cog):
    """Handle errors thrown by the bot."""

    def __init__(self, bot):
        """Init."""
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Error handling."""
        if hasattr(ctx.command, 'on_error'):
            return

        ignored = (commands.CommandNotFound)

        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return

        elif isinstance(error, commands.DisabledCommand):
            self.bot.logger.warning(f'{ctx.author} tried to user '
                                    f'{ctx.command} but it is disabled.')
            return await ctx.send('This command has been disabled.',
                                  delete_after=C.DEL_DELAY)

        elif isinstance(error, commands.NoPrivateMessage):
            self.bot.logger.warning(f'{ctx.author} tried to use '
                                    f'{ctx.command} in a DM but that is '
                                     'disabled.')
            return await ctx.author.send(f'{ctx.command} can not be used '
                                          'in DM.', delete_after=C.DEL_DELAY)

        elif isinstance(error, commands.BadArgument):
            self.bot.logger.warning(f'{ctx.author} tried to use {ctx.command}'
                                     ' but provided bad arguments.')
            return await ctx.send('One of the options you provided did not '
                                  'work.', delete_after=C.DEL_DELAY)

        elif isinstance(error, commands.UserInputError):
            await ctx.send(f'{ctx.command} failed. Here is a guide:')
            await ctx.send_help(ctx.command)
            self.bot.logger.error(f'{ctx.author} tried to use {ctx.command} '
                                   'but failed. Helper displayed.')

        elif isinstance(error, commands.MissingRole):
            await ctx.send('You are missing one of the roles required to run '
                           'this command.', delete_after=C.DEL_DELAY)
            self.bot.logger.warning(f'{ctx.author} tried to run a command but '
                                     'does not have high enough priveleges.')

        elif isinstance(error, commands.MissingAnyRole):
            await ctx.send('You are missing one of the roles required to run '
                           'this command.', delete_after=C.DEL_DELAY)
            self.bot.logger.warning(f'{ctx.author} tried to run a command but '
                                     'does not have high enough priveleges.')

        else:
            print(f'Ignoring exception in command {ctx.command}',
                   file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__,
                                      file=sys.stderr)


def setup(bot):
    """Add cog to bot."""
    bot.add_cog(Errors(bot))