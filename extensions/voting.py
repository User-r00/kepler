#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""Voting extension for Kepler."""

import random

import aiosqlite
import asyncio
import discord
from discord.ext import commands

from config import config as C
from paste_it import Paste_it


class Voting(commands.Cog):
    """Voting base class."""

    def __init__(self, bot):
        """Init."""
        self.bot = bot


    @commands.command(name='vote')
    async def vote_command(self, ctx, option1, option2, time=60):
        """Automated voting between two items."""
        # Disallow timeframes greater than five minutes.
        if time > 300:
            await ctx.channel.send('Votes can\'t be longer than 5 minutes.')
            return

        # Send preparatory messages.
        await ctx.channel.send('**Cast your vote.**')
        lock_msg = await ctx.channel.send(f'Voting will close '
                                          f'in {time} seconds.')

        # Get message objects to manipulate later.
        message1 = await ctx.channel.send(f'```fix\n{option1}\n```')
        message2 = await ctx.channel.send(f'```fix\n{option2}\n```')

        # Add reactions to start voting.
        await message1.add_reaction('👍')
        await message2.add_reaction('👍')

        # Add space for formatting.
        # await ctx.channel.send('_ _\n')

        # Delete the invocation message.
        # await ctx.message.delete(delay=C.DEL_DELAY)

        # Log the event.
        self.bot.logger.info(f'{ctx.author} started a vote for {option1} or {option2}.')

        # Wait for votes to settle.
        await asyncio.sleep(time)

        # Reload messages to get reactions
        message1 = await ctx.fetch_message(message1.id)
        message2 = await ctx.fetch_message(message2.id)

        react_count1 = 0
        react_count2 = 0

        for reaction in message1.reactions:
            if str(reaction.emoji) == '👍':
                react_count1 += reaction.count

        for reaction in message2.reactions:
            if str(reaction.emoji) == '👍':
                react_count2 += reaction.count

        # Calculate who won
        if react_count1 > react_count2:
            await lock_msg.edit(content='Votes are locked. The winner has been selected.')
            await asyncio.sleep(2)
            await message1.edit(content='```diff\n+ {} - WINNER\n```'.format(option1))
            await message2.edit(content='```diff\n- {}\n```'.format(option2))
            await message1.clear_reactions()
            await message2.clear_reactions()
        elif react_count2 > react_count1:
            await lock_msg.edit(content='Votes are locked. The winner has been selected.')
            await asyncio.sleep(2)
            await message2.edit(content='```diff\n+ {} - WINNER\n```'.format(option2))
            await message1.edit(content='```diff\n- {}\n```'.format(option1))
            await message1.clear_reactions()
            await message2.clear_reactions()
        else:
            await lock_msg.edit(content='Votes are locked. The winner has been selected.')
            await asyncio.sleep(2)
            await message2.edit(content='```asciidoc\n[{} - DRAW]\n```'.format(option2))
            await message1.edit(content='```asciidoc\n[{} - DRAW]\n```'.format(option1))
            await message1.clear_reactions()
            await message2.clear_reactions()
            await ctx.channel.send('Voting ended in a tie.')


def setup(bot):
    bot.add_cog(Voting(bot))
