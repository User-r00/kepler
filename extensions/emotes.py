#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""Emote commands for Brave Traveler."""

from datetime import datetime
import json
import os
import random
import sqlite3

import asyncio
import aiohttp
from PIL import Image

from config import config as C
import discord
from discord.ext import commands
from paste_it import Paste_it


class Emotes(commands.Cog):
    def __init__(self, bot):
        """Init. Create the emote database if it doesn't exist."""
        self.bot = bot

        conn = sqlite3.connect('databases/emotes.db')
        c = conn.cursor()
        try:
            c.execute('CREATE TABLE emotes (name text, link text, filename text, count real, date_added text)')
        except sqlite3.OperationalError as e:
            pass

        conn.commit()
        conn.close()

    # @commands.has_any_role(C.MOD, C.OPS)
    @commands.command(name='addemote')
    async def addemote_command(self, ctx, name, link):
        """Create a new emote."""
        if name == 'meatloaf':
            await ctx.channel.send('Meatloaf already exists. It is a sacred '
                                   'emote and may not be overwritten.',
                                   delete_after=C.DEL_DELAY)
            self.bot.logger.warning(f'{ctx.author} tried to add the emote {name} but it is reserved.')
            return

        conn = sqlite3.connect('databases/emotes.db')
        c = conn.cursor()

        # Check if command exists.
        new_name = (name, )
        search = c.execute('SELECT * FROM emotes WHERE name=?', new_name)
        data = c.fetchall()

        if len(data) > 0:
            await ctx.channel.send(f'Sorry {ctx.author.display_name}! That '
                                   'emote already exists.',
                                   delete_after=C.DEL_DELAY)
            await ctx.message.delete(delay=C.DEL_DELAY)

            self.bot.logger.warning(f'{ctx.author} tried to add the emote {name} but it is already exists.')
        else:
            if not os.path.isdir('emotes'):
                os.makedirs('emotes')
            # Check for supported formats.
            if link.endswith('.jpg'):
                filename = f'{name}.jpg'
            elif link.endswith('.jpeg'):
                filename = f'{name}.jpeg'
            elif link.endswith('.gif'):
                filename = f'{name}.gif'
            elif link.endswith('.png'):
                filename = f'{name}.png'
            else:
                filename = None

            if filename is None:
                await ctx.channel.send('Kepler doesn\'t currently support that format. Message .r00 if you would like it to be.', delete_after=C.DEL_DELAY)
                await ctx.message.delete(delay=C.DEL_DELAY)
                self.bot.logger.warning(f'{ctx.author} tried to add the emote {name} but the format is not supported.')
                return
            else:
                async with aiohttp.ClientSession() as session:
                        async with session.get(link) as resp:
                            image = await resp.read()
                            with open(f'emotes/{filename}', 'wb') as f:
                                f.write(image)

                date = datetime.today().strftime('%m/%d/%y')
                data = (name, link, filename, 0, date)
                c.execute('INSERT INTO emotes VALUES (?,?,?,?,?)', data)
                conn.commit()
                conn.close()

                # Register emote cache has been modified.
                C.emote_cache_updated = True

                await ctx.channel.send(f'Emote {name} created.',
                                       delete_after=C.DEL_DELAY)
                self.bot.logger.info(f'{ctx.author} added the emote {name}.')

    @commands.has_any_role(C.MOD)
    @commands.command(name='overwriteemote')
    async def overwrite_emote_command(self, ctx, name, link):
        """Overwrite an emote. Mod only."""
        conn = sqlite3.connect('databases/emotes.db')
        c = conn.cursor()

        # Check if command exists.
        new_name = (name, )
        search = c.execute('SELECT * FROM emotes WHERE name=?', new_name)
        data = c.fetchall()

        if len(data) > 0:
            print(f'{name} exists. Deleting it.')
            deleted = c.execute('DELETE FROM emotes WHERE name=?', new_name)

        # # Verify folder exists
        if not os.path.isdir('emotes'):
            os.makedirs('emotes')

        # Check for supported formats.
            if link.endswith('.jpg'):
                filename = f'{name}.jpg'
            elif link.endswith('.jpeg'):
                filename = f'{name}.jpeg'
            elif link.endswith('.gif'):
                filename = f'{name}.gif'
            elif link.endswith('.png'):
                filename = f'{name}.png'
            else:
                filename = None

        if filename is None:
            await ctx.channel.send('Kepler doesn\'t currently support that format. Message r00 if you would like it to.', delete_after=C.DEL_DELAY)
            await ctx.message.delete(delay=C.DEL_DELAY)
            self.bot.logger.warning(f'{ctx.author} tried to add the emote {name} but the format is unsupported.')
            return
        else:
            # Generate filename and download image
            async with aiohttp.ClientSession() as session:
                        async with session.get(link) as resp:
                            image = await resp.read()
                            with open(f'emotes/{filename}', 'wb') as f:
                                f.write(image)

        date = datetime.today().strftime('%m/%d/%y')
        data = (name, link, filename, 0, date)
        c.execute('INSERT INTO emotes VALUES (?,?,?,?,?)', data)
        conn.commit()
        conn.close()

        C.emote_cache_updated = True

        await ctx.send(f'{name} has been overwritten.',
                       delete_after=C.DEL_DELAY)
        self.bot.logger.info(f'{ctx.author} overwrote the emote {name}.')

    @commands.has_any_role(C.MOD)
    @commands.command(name='removeemote')
    async def deleteemote_command(self, ctx, emote_name):
        """Delete emote. Mod only."""
        conn = sqlite3.connect('databases/emotes.db')
        c = conn.cursor()

        # Fetch emote.
        name = (emote_name, )
        search = c.execute('SELECT * FROM emotes WHERE name=?', name)
        data = c.fetchone()

        # Delete the file.
        filename = data[2]
        os.remove(f'emotes/{filename}')

        # Update the db record.
        data = (emote_name, )
        deleted = c.execute('DELETE FROM emotes WHERE name=?', data)
        conn.commit()
        conn.close()

        C.emote_cache_updated = True

        image_name = name[0]
        await ctx.channel.send(f'{image_name} has been deleted.',
                               delete_after=C.DEL_DELAY)

        self.bot.logger.info(f'{ctx.author} deleted the emote {name}.')

    @commands.command(name='emotelist')
    async def emotelist_command(self, ctx, *, filter=None):
        """List all emotes."""
        conn = sqlite3.connect('databases/emotes.db')
        c = conn.cursor()
        data = c.execute('SELECT * FROM emotes')

        if filter and len(filter) < 2:
            await ctx.send('Try a longer search term.',
                           delete_after=C.DEL_DELAY)
            self.bot.logger.warning(f'{ctx.author} tried to search for an emote but did not provide enough info.')
        else:
            if filter:
                filtered_names = [name[0] for name in data if filter in name[0]]
                if filtered_names:
                    filtered_names = '\n'.join(filtered_names)
                    msg = f'**I found these related emotes.**\n{filtered_names}'
                    await ctx.send(msg, delete_after=C.DEL_DELAY)
                else:
                    await ctx.send('I didn\'t find any emotes with that '
                                   'filter.', delete_after=C.DEL_DELAY)

                self.bot.logger.info(f'{ctx.author} used {ctx.command} to search for {filter}.')
            else:
                if C.emote_cache_updated:
                    msg = 'ARGSociety Emotes\n\n'

                    for i in data:
                        msg = msg + f'{i[0]}\n'

                    paste = Paste_it()
                    emote_list = await paste.new_paste(msg)
                    C.emote_cache_updated = False
                    C.emote_link = emote_list
                else:
                    emote_list = C.emote_link

                await ctx.send(emote_list, delete_after=C.DEL_DELAY)
                await ctx.message.delete(delay=C.DEL_DELAY)

                self.bot.logger.info(f'{ctx.author} used {ctx.command}.')

    @commands.command(name='usage')
    async def emote_use_count(self, ctx, name):
        """Show emote usage count."""
        conn = sqlite3.connect('databases/emotes.db')
        c = conn.cursor()
        new_name = (name, )
        search = c.execute('SELECT * FROM emotes WHERE name=?', new_name)
        data = c.fetchall()

        if len(data) > 0:
            for emote in data:
                if emote[3] == 1.0:
                    await ctx.send(f'{name} has been used {int(emote[3])} time.', delete_after=C.DEL_DELAY)
                    self.bot.logger.info(f'{ctx.author} used {ctx.command} on {name}.')
                    await ctx.message.delete(delay=C.DEL_DELAY)
                else:
                    await ctx.send(f'{name} has been used {int(emote[3])} times.', delete_after=C.DEL_DELAY)
                    self.bot.logger.info(f'{ctx.author} used {ctx.command} on {name}.')
                    await ctx.message.delete(delay=C.DEL_DELAY)
        else:
            await ctx.send(f'{name} doesn\'t appear to exist.')
            self.bot.logger.warning(f'{ctx.author} used {ctx.command} on {name}.')

    @commands.command(name='date')
    async def get_date_added(self, ctx, name):
        '''Get the data an emote was added.'''
        conn = sqlite3.connect('databases/emotes.db')
        c = conn.cursor()
        new_name = (name, )
        search = c.execute('SELECT * FROM emotes WHERE name=?', new_name)
        data = c.fetchall()

        if len(data) > 0:
            for emote in data:
                date = emote[4]
                await ctx.send(f'{name} was added on {date}.',
                               delete_after=C.DEL_DELAY)
                self.bot.logger.info(f'{ctx.author} requested the creationg date of {name}.')
        else:
            await ctx.send(f'{name} doesn\'t appear to exist.',
                           delete_after=C.DEL_DELAY)
            self.bot.logger.warn(f'{ctx.author} used {ctx.command} on {name} but it does not exist.')

        await ctx.message.delete(delay=C.DEL_DELAY)

    @commands.command(name='top10')
    async def emote_top10(self, ctx):
        '''Get the top 10 most used emotes.'''
        conn = sqlite3.connect('databases/emotes.db')
        c = conn.cursor()
        emotes = c.execute('SELECT * FROM emotes ORDER BY count DESC')
        data = c.fetchall()

        msg = '**Top 10 emotes by usage**\n'
        for i in range(0, 10):
            msg = msg + f'{data[i][0]} - {int(data[i][3])}\n'
        await ctx.send(msg, delete_after=C.DEL_DELAY)
        await ctx.message.delete(delay=C.DEL_DELAY)
        self.bot.logger.info(f'{ctx.author} used {ctx.command}.')


def setup(bot):
    bot.add_cog(Emotes(bot))

# .r00
