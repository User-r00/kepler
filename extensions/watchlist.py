#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""Movie extension for Kepler."""

import asyncio
import aiohttp
import aiosqlite
from datetime import datetime
import random

import discord
from discord.ext import commands

from config import config as C
from paste_it import Paste_it


class Watchlist(commands.Cog):
    """Server movie watchlist."""

    def __init__(self, bot):
        """Init."""
        self.bot = bot
        self.task = self.bot.loop.create_task(self.check_db('watchlist', 'movies'))

    async def check_db(self, name, table):
        """Create db if it doesn't exist."""
        async with aiosqlite.connect(f'databases/{name}.db') as db:
            await db.execute('CREATE TABLE IF NOT EXISTS movies (title text PRIMARY KEY, date_added text, date_watched text, watched integer)')
            await db.commit()

    async def capitalize_title(self, title):
        """Sanitize movie title spellings. Prevents ugly formatting."""
        ignored_words = ['of',
                         'the',
                         'a',
                         'an',
                         'at',
                         'by',
                         'for',
                         'in',
                         'on',
                         'to',
                         'up',
                         'and',
                         'as',
                         'but',
                         'or',
                         'nor',
                         'with']

        title = title.lower()
        split_title = title.split(' ')
        for word in split_title:
            if split_title.index(word) == 0:
                i = split_title.index(word)
                word = word.capitalize()
                split_title[i] = word
            elif word not in ignored_words:
                i = split_title.index(word)
                word = word.capitalize()
                split_title[i] = word
            else:
                continue

        return ' '.join(split_title)

    @commands.has_any_role(C.MOD, C.SUB)
    @commands.command(name='addmovie')
    async def add_movie_command(self, ctx, *, title):
        """Add a movie to the watchlist."""
        title = await self.capitalize_title(title)
        async with aiosqlite.connect('databases/watchlist.db') as db:
            date_added = datetime.today().strftime('%m/%d/%y')
            date_watched = "11/22/87"
            watched = 0
            data = (title, date_added, date_watched, watched)
            await db.execute('INSERT OR IGNORE INTO movies VALUES (?,?,?,?)', data)
            await db.commit()
        await ctx.send(f'{title} added to the watchlist.',
                       delete_after=C.DEL_DELAY)
        await ctx.message.delete(delay=C.DEL_DELAY)
        self.bot.logger.info(f'{ctx.author} added {title} to the watch list.')

    @commands.has_any_role(C.MOD, C.SUB)
    @commands.command(name='removeemovie')
    async def delete_movie_commmand(self, ctx, *, title):
        """Delete a movie from the watchlist."""
        title = await self.capitalize_title(title)

        async with aiosqlite.connect('databases/watchlist.db') as db:
            data = (title, )
            async with db.execute('SELECT * FROM movies WHERE title=?', data) as cursor:
                exists = await cursor.fetchall()
            if exists:
                async with aiosqlite.connect('databases/watchlist.db') as db:
                    data = (title,)
                    await db.execute('DELETE FROM movies WHERE title=?', data)
                    await db.commit()
                await ctx.send(f'{title} removed from the watchlist.')
                self.bot.logger.info(f'{ctx.author} removed {title} from the watch list.')
            else:
                await ctx.send(f'{title} does not appear to exist.')
                self.bot.logger.info(f'{ctx.author} tried to remove {title} from the watch list but it doesn\'t exist.')

    @commands.has_any_role(C.MOD, C.SUB)
    @commands.command(name='watched')
    async def watched_command(self, ctx, *, title):
        """Mark a movie as watched."""
        title = await self.capitalize_title(title)

        async with aiosqlite.connect('databases/watchlist.db') as db:
            data = (title, )
            async with db.execute('SELECT * FROM movies WHERE title=?', data) as cursor:
                exists = await cursor.fetchall()

            if exists:
                async with aiosqlite.connect('databases/watchlist.db') as db:
                    date_watched = datetime.today().strftime('%m/%d/%y')
                    watched = 1
                    data = (date_watched, watched, title)
                    await db.execute('UPDATE movies SET date_watched=?, watched=? WHERE title=?', data)
                    await db.commit()
                await ctx.send(f'{title} marked as watched.')
                self.bot.logger.info(f'{ctx.author} marked {title} as watched.')
            else:
                await ctx.send(f'{title} does not appear to exist.')
                self.bot.logger.info(f'{ctx.author} tried to mark {title} as watched but it doesn\'t exist.')

    @commands.command(name='watchlist')
    async def watchlist_command(self, ctx):
        """Return a list of all movies in the watchlist."""
        async with aiosqlite.connect('databases/watchlist.db') as db:
            async with db.execute('SELECT * FROM movies ORDER BY title ASC') as cursor:
                movies = await cursor.fetchall()
                movie_list = 'Server watch list.\n\nLEGEND\n------\n-  watched\n+ not watched\n\nMOVIES\n-------\n'
                for movie in movies:
                    if movie[3] == 1:
                        movie_list = f'{movie_list}\n- {movie[0]}'
                    else:
                        movie_list = f'{movie_list}\n+ {movie[0]}'
        paste = Paste_it()
        results = await paste.new_paste(movie_list)
        self.bot.logger.info(f'{ctx.author} used {ctx.command}.')

        await ctx.send(results)

    @commands.command(name='lastwatched')
    async def last_watched_command(self, ctx, *, title):
        """Return the last watched date for a title."""
        title = await self.capitalize_title(title)
        async with aiosqlite.connect('databases/watchlist.db') as db:
            data = (title,)
            async with db.execute('SELECT * FROM movies WHERE title=?', data) as cursor:
                movies = await cursor.fetchall()
                for movie in movies:
                    if movie[3] == 1:
                        await ctx.send(f'{title} was watched on {movie[2]}')
                    else:
                        await ctx.send(f'{title} hasn\'t been watched yet. Get to it!')
        self.bot.logger.info(f'{ctx.author} used {ctx.command}.')

    @commands.command(name='countdown')
    async def countdown_command(self, ctx, *, seconds=10):
        """Start a 10 second countdown."""
        seconds = int(seconds)
        if seconds < 5:
            await ctx.send('Please enter a time of at least 5.',
                           delete_after=C.DEL_DELAY)
            await ctx.message.delete(delay=C.DEL_DELAY)
            return
        elif seconds > 10:
            await ctx.send('Please enter a time no greater than 10.',
                           delete_after=C.DEL_DELAY)
            await ctx.message.delete(delay=C.DEL_DELAY)
            return

        for i in range(seconds, 0, -1):
            delay = seconds + 10
            await ctx.send(f'{i}', delete_after=delay)
            await asyncio.sleep(1)

        await ctx.send('p', delete_after=delay)
        await ctx.message.delete(delay=C.DEL_DELAY)
        self.bot.logger.info(f'{ctx.author} used {ctx.command}.')


def setup(bot):
    bot.add_cog(Watchlist(bot))
