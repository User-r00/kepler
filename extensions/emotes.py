#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""Emote commands for Brave Traveler."""

from datetime import datetime
import os
import sqlite3

import aiohttp
from bs4 import BeautifulSoup as bs

from config import config as C
from discord.ext import commands
from paste_it import Paste_it


class Emotes(commands.Cog):
    def __init__(self, bot):
        """Init. Create the emote database if it doesn't exist."""
        self.bot = bot

        conn = sqlite3.connect('databases/emotes.db')
        c = conn.cursor()
        try:
            c.execute('CREATE TABLE emotes (name text, link text, '
                      'filename text, count real, date_added text)')
        except sqlite3.OperationalError as e:
            print(e)
            pass

        if not os.path.isdir('emotes'):
            os.makedirs('emotes')

        conn.commit()
        conn.close()

    # @commands.has_any_role(C.MOD, C.OPS)
    @commands.command(name='addemote')
    async def addemote_command(self, ctx, name, link):
        """Create a new emote."""
        conn = sqlite3.connect('databases/emotes.db')
        c = conn.cursor()

        # Check if command exists.
        new_name = (name, )

        # search = c.execute('SELECT * FROM emotes WHERE name=?', new_name)
        c.execute('SELECT * FROM emotes WHERE name=?', new_name)
        data = c.fetchall()

        if len(data) > 0:
            await ctx.channel.send(f'Sorry {ctx.author.display_name}! That '
                                   'emote already exists.')

            self.bot.logger.warning(f'{ctx.author} tried to add the emote '
                                    f'{name} but it is already exists.')
        else:
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

            # Handle tenor links.
            if 'tenor' in link:
                filename = f'{name}.gif'
                # Download the full tenor page.
                async with aiohttp.ClientSession() as session:
                    async with session.get(link) as resp:
                        page_data = await resp.text()

                # Find the gif.
                soup = bs(page_data, 'html.parser')
                div = soup.find('div', class_='Gif')
                img = div.findChildren('img', recursive=False)[0]['src']
                link = img.split('?')[0]

            if filename is None:
                await ctx.channel.send('This emote format is not supported.')
                self.bot.logger.info(f'{ctx.author} tried to add an '
                                     'unsupported emote.')
                return

            # Download the emote.
            async with aiohttp.ClientSession() as session:
                async with session.get(link) as resp:
                    image = await resp.read()
                    with open(f'emotes/{filename}', 'wb') as f:
                        f.write(image)

            # Save the emote data to file.
            date = datetime.today().strftime('%m/%d/%y')
            data = (name, link, filename, 0, date)
            c.execute('INSERT INTO emotes VALUES (?,?,?,?,?)', data)
            conn.commit()
            conn.close()

            # Register emote cache has been modified.
            C.emote_cache_updated = True

            # Announce.
            await ctx.channel.send(f'Emote {name} created.')
            self.bot.logger.info(f'{ctx.author} added the emote {name}.')

    @commands.has_any_role(C.MOD)
    @commands.command(name='overwriteemote')
    async def overwrite_emote_command(self, ctx, name, link):
        """Overwrite an emote. Mod only."""
        conn = sqlite3.connect('databases/emotes.db')
        c = conn.cursor()

        # Check if command exists.
        new_name = (name, )
        c.execute('SELECT * FROM emotes WHERE name=?', new_name)
        data = c.fetchall()

        if len(data) > 0:
            print(f'{name} exists. Deleting it.')
            c.execute('DELETE FROM emotes WHERE name=?', new_name)

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

        # Handle tenor links.
        if 'tenor' in link:
            filename = f'{name}.gif'
            # Download the full tenor page.
            async with aiohttp.ClientSession() as session:
                async with session.get(link) as resp:
                    page_data = await resp.text()

            # Find the gif.
            soup = bs(page_data, 'html.parser')
            div = soup.find('div', class_='Gif')
            img = div.findChildren('img', recursive=False)[0]['src']
            link = img.split('?')[0]

        if filename is None:
            await ctx.channel.send('This emote format is not supported.')
            self.bot.logger.info(f'{ctx.author} tried to add an '
                                 'unsupported emote.')
            return

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

        await ctx.send(f'{name} has been overwritten.')
        self.bot.logger.info(f'{ctx.author} overwrote the emote {name}.')

    @commands.has_any_role(C.MOD)
    @commands.command(name='removeemote', aliases=['remove', 'delete'])
    async def deleteemote_command(self, ctx, emote_name):
        """Delete emote. Mod only."""
        conn = sqlite3.connect('databases/emotes.db')
        c = conn.cursor()

        # Fetch emote.
        name = (emote_name, )
        c.execute('SELECT * FROM emotes WHERE name=?', name)
        data = c.fetchone()

        # Delete the file.
        try:
            filename = data[2]
        except TypeError:
            await ctx.channel.send('That emote doesn\'t exist.')
            return

        try:
            os.remove(f'emotes/{filename}')
        except FileNotFoundError:
            self.bot.logger.info(f'{ctx.author} tried to delete the '
                                 f'{emote_name} emote but the source file was '
                                 'missing. It may have been manually removed.')

        # Update the db record.
        data = (emote_name, )
        c.execute('DELETE FROM emotes WHERE name=?', data)
        conn.commit()
        conn.close()

        # Update the emote cache.
        C.emote_cache_updated = True

        image_name = name[0]
        await ctx.channel.send(f'{image_name} has been deleted.')

        self.bot.logger.info(f'{ctx.author} deleted the emote {name}.')

    @commands.command(name='emotelist')
    async def emotelist_command(self, ctx, *, filter=None):
        """List all emotes."""
        conn = sqlite3.connect('databases/emotes.db')
        c = conn.cursor()
        data = c.execute('SELECT * FROM emotes')

        if filter and len(filter) < 2:
            await ctx.send('Try a longer search term.')
            self.bot.logger.warning(f'{ctx.author} tried to search for an '
                                    'emote but did not provide enough info.')
        else:
            if filter:
                filtered_names = [n[0] for n in data if filter in n[0]]
                if filtered_names:
                    filtered_names = '\n'.join(filtered_names)
                    msg = f'**I found these related emotes.**\n' \
                          f'{filtered_names}'
                    await ctx.send(msg)
                else:
                    await ctx.send('I didn\'t find any emotes with that '
                                   'filter.')

                self.bot.logger.info(f'{ctx.author} used {ctx.command} to '
                                     f'search for {filter}.')
            else:
                if C.emote_cache_updated:
                    msg = 'The r00m Emotes\n\n'

                    for i in data:
                        msg = msg + f'{i[0]}\n'

                    paste = Paste_it()
                    emote_list = await paste.new_paste(msg)
                    C.emote_cache_updated = False
                    C.emote_link = emote_list
                else:
                    emote_list = C.emote_link

                await ctx.send(emote_list)

                self.bot.logger.info(f'{ctx.author} used {ctx.command}.')

    @commands.command(name='usage')
    async def emote_use_count(self, ctx, name):
        """Show emote usage count."""
        conn = sqlite3.connect('databases/emotes.db')
        c = conn.cursor()
        new_name = (name, )
        c.execute('SELECT * FROM emotes WHERE name=?', new_name)
        data = c.fetchall()

        if len(data) > 0:
            for emote in data:
                if emote[3] == 1.0:
                    await ctx.send(f'{name} has been used {int(emote[3])} '
                                   'time.')
                    self.bot.logger.info(f'{ctx.author} used {ctx.command} '
                                         f'on {name}.')
                else:
                    await ctx.send(f'{name} has been used {int(emote[3])} '
                                   'times.')
                    self.bot.logger.info(f'{ctx.author} used {ctx.command} '
                                         f'on {name}.')
        else:
            await ctx.send(f'{name} doesn\'t appear to exist.')
            self.bot.logger.warning(f'{ctx.author} used {ctx.command} '
                                    f'on {name}.')

    @commands.command(name='date')
    async def get_date_added(self, ctx, name):
        '''Get the data an emote was added.'''
        conn = sqlite3.connect('databases/emotes.db')
        c = conn.cursor()
        new_name = (name, )
        c.execute('SELECT * FROM emotes WHERE name=?', new_name)
        data = c.fetchall()

        if len(data) > 0:
            for emote in data:
                date = emote[4]
                await ctx.send(f'{name} was added on {date}.')
                self.bot.logger.info(f'{ctx.author} requested the creationg '
                                     f'date of {name}.')
        else:
            await ctx.send(f'{name} doesn\'t appear to exist.')
            self.bot.logger.warn(f'{ctx.author} used {ctx.command} on '
                                 f'{name} but it does not exist.')

    @commands.command(name='top10')
    async def emote_top10(self, ctx):
        '''Get the top 10 most used emotes.'''
        conn = sqlite3.connect('databases/emotes.db')
        c = conn.cursor()
        c.execute('SELECT * FROM emotes ORDER BY count DESC')
        data = c.fetchall()

        msg = '**Top 10 emotes by usage**\n```'
        for i in range(0, 10):
            try:
                msg = msg + f'{data[i][0]} - {int(data[i][3])}\n'
            except IndexError:
                continue
        msg = f'{msg}```'
        await ctx.send(msg)
        self.bot.logger.info(f'{ctx.author} used {ctx.command}.')


def setup(bot):
    bot.add_cog(Emotes(bot))
