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
            if not os.path.isdir('command_images'):
                os.makedirs('command_images')
            # Check for supported formats.
            if link.endswith('.jpg'):
                filename = 'command_images/{}.jpg'.format(name)
            elif link.endswith('.jpeg'):
                filename = 'command_images/{}.jpeg'.format(name)
            elif link.endswith('.gif'):
                filename = 'command_images/{}.gif'.format(name)
            elif link.endswith('.png'):
                filename = 'command_images/{}.png'.format(name)
            else:
                filename = None

            if filename is None:
                await ctx.channel.send('Brave Traveler doesn\'t currently support that format. Message .r00 if you would like it to be.', delete_after=C.DEL_DELAY)
                await ctx.message.delete(delay=C.DEL_DELAY)
                self.bot.logger.warning(f'{ctx.author} tried to add the emote {name} but the format is not supported.')
                return
            else:
                async with aiohttp.ClientSession() as session:
                        async with session.get(link) as resp:
                            image = await resp.read()
                            with open(filename, 'wb') as f:
                                f.write(image)

                # Auto-trim
                # if filename.endswith('.png'):
                #     image = Image.open(filename)

                #     # Image content bounds
                #     bounds = image.convert('RGBa').getbbox()

                #     # Crop to content bounds
                #     image = image.crop(bounds)

                #     # Image dimensions
                #     (width, height) = image.size

                #     # Padding
                #     padding = 0

                #     width += padding * 2
                #     height += padding * 2

                #     # Create a new image
                #     cropped_image = Image.new('RGBA', (width, height))
                #     cropped_image.paste(image, (padding, padding))

                #     # Save the image
                #     cropped_image.save(filename)

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
        if not os.path.isdir('command_images'):
            os.makedirs('command_images')

        if link.endswith('.jpg'):
            filename = 'command_images/{}.jpg'.format(name)
        elif link.endswith('.jpeg'):
            filename = 'command_images/{}.jpeg'.format(name)
        elif link.endswith('.gif'):
            filename = 'command_images/{}.gif'.format(name)
        elif link.endswith('.png'):
            filename = 'command_images/{}.png'.format(name)
        else:
            filename = None

        if filename is None:
            await ctx.channel.send('Brave Traveler doesn\'t currently support that format. Message r00 if you would like it to.', delete_after=C.DEL_DELAY)
            await ctx.message.delete(delay=C.DEL_DELAY)
            self.bot.logger.warning(f'{ctx.author} tried to add the emote {name} but the format is unsupported.')
            return
        else:
            # Generate filename and download image
            async with aiohttp.ClientSession() as session:
                        async with session.get(link) as resp:
                            image = await resp.read()
                            with open(filename, 'wb') as f:
                                f.write(image)

        # Auto-trim
        # if filename.endswith('.png'):  # Only do this on transparent images
        #     image = Image.open(filename)

        #     # Image content bounds
        #     bounds = image.convert('RGBa').getbbox()

        #     # Crop to content bounds
        #     image = image.crop(bounds)

        #     # Image dimensions
        #     (width, height) = image.size

        #     # Padding
        #     padding = 0

        #     width += padding * 2
        #     height += padding * 2

        #     # Create a new image
        #     cropped_image = Image.new('RGBA', (width, height))
        #     cropped_image.paste(image, (padding, padding))

        #     # Save the image
        #     cropped_image.save(filename)

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
    async def deleteemote_command(self, ctx, name):
        """Delete emote. Mod only."""
        conn = sqlite3.connect('databases/emotes.db')
        c = conn.cursor()

        data = (name, )
        deleted = c.execute('DELETE FROM emotes WHERE name=?', data)
        conn.commit()
        conn.close()

        C.emote_cache_updated = True

        await ctx.channel.send(f'{name} has been deleted.',
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

    @commands.command(name='randombrag')
    async def random_brag_command(self, ctx):
        '''Show a random brag emote.'''
        conn = sqlite3.connect('databases/emotes.db')
        c = conn.cursor()
        data = c.execute('SELECT * FROM emotes')

        brag_emotes = [name[0] for name in data if 'brag' in name[0]]
        brag = random.choice(brag_emotes)

        try:
            name = (brag, )
            search = c.execute('SELECT * FROM emotes WHERE name=?', name)
            data = c.fetchone()

            if data is not None:
                # Send emote.
                with open(data[2], 'rb') as f:
                    await ctx.send(file=discord.File(f))
                    self.bot.logger.info(f'{ctx.author} used {ctx.command}.')
        except (sqlite3.IntegrityError, TypeError) as e:
            self.bot.logger.error(f'[ERR] {e}.')


def setup(bot):
    bot.add_cog(Emotes(bot))

# .r00
