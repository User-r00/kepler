#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Utility commands for Kepler."""

from datetime import datetime
import json
import pprint
import sqlite3

import aiohttp
import asyncio
from config import config
import logging
from tokens import tokens

import discord
from discord.ext import commands


class Movies(commands.Cog):
    """Utility commands."""
    def __init__(self, bot):
        """Init."""
        self.bot = bot

    @commands.command(name='info')
    async def info_command(self, ctx, *, movie):
        """Lookup a T.V. show or movie."""
        print(f'Checking for {movie}.')
        link = f'http://www.omdbapi.com/?apikey={tokens.OMDB_KEY}&t={movie}'
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                data = await resp.json()

                success = data['Response']
                if success == 'False':
                    omdb_error = data['Error'] 
                    await ctx.send(f'{omdb_error}')
                elif success == 'True':
                    genre = data['Genre']
                    released = data['Released']
                    plot = data['Plot']
                    runtime = data['Runtime']
                    imdbID = data['imdbID']
                    imdbLink = f'https://www.imdb.com/title/{imdbID}/'
                    director = data['Director']

                    movie_title = data['Title']
                    year = data['Year']
                    title = f'{movie_title} ({year})'
                    embed = discord.Embed(title=title,
                                          description=plot,
                                          color=0xf5d142,
                                          url=imdbLink)

                    details = f'{runtime} | {genre} | {released}'
                    embed.add_field(name='Starring',
                                    value=data['Actors'],
                                    inline=False)
                    embed.add_field(name='Details',
                                    value=details)
                    embed.add_field(name='Director',
                                    value=f'Directed by {director}',
                                    inline=False)
                    embed.set_image(url=data['Poster'])
                    await ctx.channel.send(embed=embed)
                else:
                    print('Unexpected status.')

    @commands.has_role('Moderator')
    @commands.command(name='watch', hidden=True)
    async def watch_command(self, ctx, movie, ):
        """Setup a watch party."""
        # Get date.
        await ctx.channel.send('What date?')
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        msg = await self.bot.wait_for('message', check=check)
        msg_content = msg.content
        try:
            d = datetime.strptime(msg_content, "%m/%d/%y")
        except ValueError:
            await ctx.channel.send('Bad date dawg.')

        # Get time.
        await ctx.channel.send('What time?')
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        msg = await self.bot.wait_for('message', check=check)
        msg_content = msg.content
        try:
            t = datetime.strptime(msg_content, "%I:%M %p")
            # Convert t to string so split on line 98 doesn't fail.
        except ValueError:
            await ctx.channel.send('Bad time dawg.')

        t, p = t.split(' ')
        hour, minute = time.split(':')
        if period == 'PM':
            hour += 12

        print(f'H: {hour}')
        print(f'M: {minute}')
        print(f'P: {period}')



        


        # Convert both to datetime object

        # Stash it.


        print(msg.content)

def setup(bot):
    """Add cog to bot."""
    bot.add_cog(Movies(bot))
