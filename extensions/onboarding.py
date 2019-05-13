#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Onboarding commands for Kepler."""

import asyncio
import discord
from discord.ext import commands


class Onboarding(commands.Cog):
    """Utility commands."""

    def __init__(self, bot):
        """Init."""
        self.bot = bot
        self._last_member = None

    @commands.command(name='join_r00m8', hidden=True)
    async def join_argsociety_command(self, ctx):
        """Self add member role to user."""
        # Get target role.
        role = discord.utils.get(ctx.guild.roles, name='Member')

        # Only run if in Terminal channel.
        if ctx.channel.id == 577021097116041216:
            await ctx.channel.send('Loading r00m 8...',
                                   delete_after=5.0)
            await ctx.author.add_roles(role)

            self.bot.logger.info(f'Adding {role} to user {ctx.author}.')

            await asyncio.sleep(2)
            await ctx.channel.send(f'Welcome {ctx.author.display_name}.',
                                    delete_after=5.0)
            await asyncio.sleep(5)
            await ctx.message.delete()

            self.bot.logger.info(f'{ctx.author} joined r00m 8.')

            # Get General channel.
            channel = self.bot.get_channel(479341433623543811)
            if channel is not None:
                self._last_member = ctx.author
                member = ctx.author.display_name
                greetings = [f'**Beep b00p. It\'s {member}**',
                             f'**Oh now that\'s nice. It\'s {member}.**',
                             f'**Unfortunately, we\'re all human. Except {member}, of course.**',
                             f'**Never trust a {member} with a rat tail. Too easy to carve secrets out of them.**',
                             f'**ಠ_ಠ {member}.**',
                             f'**Well it\'s not {member}.**',
                             f'**A wild {member} appears.**',
                             f'**{member} will save us.**',
                             f'**Don\'t mistake my {member} for {member}.**'
                ]
                msg = random.choice(greetings)
                await channel.send(f'{msg} Welcome.')
        else:
            await ctx.channel.send('You have already joined r00m 8.',
                                   delete_after=7.0)

            self.bot.logger.error(f'{ctx.author} tried to join r00m 8 ' \
                                   'but they are already a member.')

    @commands.command()
    async def hello(self, ctx, *, member: discord.Member = None):
        """Welcome most recent member join."""
        if self._last_member is None and member is None:
            self.bot.logger.error(f'{ctx.author} tried to say hello to ')
            await ctx.send_help(ctx.command)
        else:
            try:
                await ctx.send('Bonsoir {0.mention}.'.format(self._last_member))
            except AttributeError:
                self.bot.logger.error(f'{member} does not appear to mentionable. ' \
                                       'They may have left the server.')

    @commands.command(hidden=True)
    async def set_last_member(self, ctx, *, member: discord.Member):
        """Welcome most recent member join."""
        self._last_member = member


def setup(bot):
    """Add cog to bot."""
    bot.add_cog(Onboarding(bot))

# .r00
