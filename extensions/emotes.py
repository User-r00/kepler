#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""Emote commands for Kepler."""

import os
import json
import sqlite3
import urllib.request
from datetime import datetime

import asyncio
import aiohttp
from PIL import Image

import config
import discord
from discord.ext import commands
from paste_it import Paste_it


class Emotes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        conn = sqlite3.connect('databases/emotes.db')
        c = conn.cursor()
        try:
            c.execute('CREATE TABLE emotes (name text, link text, filename text, count real, date_added text)')
        except sqlite3.OperationalError as e:
            print(f'[WARN] Sqlite3 operational error: {e}. Skipping.')

        conn.commit()
        conn.close()

    @commands.command(name='addemote', alias=['newemote', 'createemote'])
    async def addemote_command(self, ctx, emote_name: str, link: str):
        """Add an emote."""
        if emote_name == 'meatloaf':
            await ctx.channel.send('Meatloaf already exists. It is a sacred emote and may not be overwritten.')
            return

        conn = sqlite3.connect('databases/emotes.db')
        c = conn.cursor()

        # Check if command exists.
        name = (emote_name, )
        search = c.execute('SELECT * FROM emotes WHERE name=?', name)
        data = c.fetchall()

        if len(data) > 0:
            await ctx.channel.send('Sorry {0.author.mention}! That emote already exists.'.format(ctx.message, delete_after=5.0))
            await asyncio.sleep(5)
            await ctx.message.delete()
        else:
            if not os.path.isdir('command_images'):
                os.makedirs('command_images')
            # Check for supported formats.
            if link.endswith('.jpg'):
                filename = 'command_images/{}.jpg'.format(emote_name)
            elif link.endswith('.jpeg'):
                filename = 'command_images/{}.jpeg'.format(emote_name)
            elif link.endswith('.gif'):
                filename = 'command_images/{}.gif'.format(emote_name)
            elif link.endswith('.png'):
                filename = 'command_images/{}.png'.format(emote_name)
            else:
                filename = None

            if filename is None:
                await ctx.channel.send('Brave Traveler doesn\'t currently support that format. Message .r00 if you would like it to be.')
                return
            else:
                async with aiohttp.ClientSession() as session:
                        async with session.get(link) as resp:
                            image = await resp.read()
                            with open(filename, 'wb') as f:
                                f.write(image)

                # Auto-trim
                if filename.endswith('.png'):
                    image = Image.open(filename)

                    # Image content bounds
                    bounds = image.convert('RGBa').getbbox()

                    # Crop to content bounds
                    image = image.crop(bounds)

                    # Image dimensions
                    (width, height) = image.size

                    # Padding
                    padding = 0

                    width += padding * 2
                    height += padding * 2

                    # Create a new image
                    cropped_image = Image.new('RGBA', (width, height))
                    cropped_image.paste(image, (padding, padding))

                    # Save the image
                    cropped_image.save(filename)

                date = datetime.today().strftime('%m/%d/%y')
                data = (emote_name, link, filename, 0, date)
                c.execute('INSERT INTO emotes VALUES (?,?,?,?,?)', data)
                conn.commit()
                conn.close()

                # Register emote cache has been modified.
                config.emote_cache_updated = True

                await ctx.channel.send('Emote {} created.'.format(emote_name))

    @commands.command(name='overwrite_emote', aliases=['replaceemote'], hidden=True)
    @commands.has_role('Moderator')
    async def overwrite_emote_command(self, ctx, emote_name: str, link: str):
        """Overwrite an emote. Mod only."""
        conn = sqlite3.connect('databases/emotes.db')
        c = conn.cursor()

        # Check if command exists.
        name = (emote_name, )
        search = c.execute('SELECT * FROM emotes WHERE name=?', name)
        data = c.fetchall()

        if len(data) > 0:
            print(f'{emote_name} exists. Deleting it.')
            deleted = c.execute('DELETE FROM emotes WHERE name=?', name)

        # # Verify folder exists
        if not os.path.isdir('command_images'):
            os.makedirs('command_images')

        if link.endswith('.jpg'):
            filename = 'command_images/{}.jpg'.format(emote_name)
        elif link.endswith('.jpeg'):
            filename = 'command_images/{}.jpeg'.format(emote_name)
        elif link.endswith('.gif'):
            filename = 'command_images/{}.gif'.format(emote_name)
        elif link.endswith('.png'):
            filename = 'command_images/{}.png'.format(emote_name)
        else:
            filename = None

        if filename is None:
            await ctx.channel.send('Brave Traveler doesn\'t currently support that format. Message r00 if you would like it to.')
            return
        else:
            # Generate filename and download image
            async with aiohttp.ClientSession() as session:
                        async with session.get(link) as resp:
                            image = await resp.read()
                            with open(filename, 'wb') as f:
                                f.write(image)

        # Auto-trim
        if filename.endswith('.png'):  # Only do this on transparent images
            image = Image.open(filename)

            # Image content bounds
            bounds = image.convert('RGBa').getbbox()

            # Crop to content bounds
            image = image.crop(bounds)

            # Image dimensions
            (width, height) = image.size

            # Padding
            padding = 0

            width += padding * 2
            height += padding * 2

            # Create a new image
            cropped_image = Image.new('RGBA', (width, height))
            cropped_image.paste(image, (padding, padding))

            # Save the image
            cropped_image.save(filename)

        date = datetime.today().strftime('%m/%d/%y')
        data = (emote_name, link, filename, 0, date)
        c.execute('INSERT INTO emotes VALUES (?,?,?,?,?)', data)
        conn.commit()
        conn.close()

        config.emote_cache_updated = True

        await ctx.send(f'{emote_name} has been overwritten.')

    @commands.command(name='deleteemote', aliases=['removeemote', 'demote'], hidden=True)
    @commands.has_role('Moderator')
    async def deleteemote_command(self, ctx, emote_name: str):
        """Delete emote."""
        conn = sqlite3.connect('databases/emotes.db')
        c = conn.cursor()

        data = (emote_name, )
        deleted = c.execute('DELETE FROM emotes WHERE name=?', data)
        conn.commit()
        conn.close()

        config.emote_cache_updated = True

        await ctx.channel.send(f'{emote_name} has been deleted.')

    @commands.command(name='emotelist')
    async def emotelist_command(self, ctx):
        """List all emotes."""
        conn = sqlite3.connect('databases/emotes.db')
        c = conn.cursor()
        data = c.execute('SELECT * FROM emotes')

        if config.emote_cache_updated:
            print('[OK] Emote cache updated. Sending new link.')
            msg = '[All available Brave Traveler Emotes]\n\n'

            for i in data:
                msg = msg + f'{i[0]}\n'

            msg = '{}\nIf you don\'t see the emote you\'re looking for, consider adding it with .addemote.'.format(msg)
            paste = Paste_it()
            emote_list = await paste.new_paste(msg)
            config.emote_cache_updated = False
            config.emote_link = emote_list
        else:
            print('[OK] Emote cache not updated. Sending the last known link.')
            emote_list = config.emote_link

        await ctx.send(emote_list)

    @commands.command(name='usage')
    async def emote_use_count(self, ctx, emote_name):
        """Show emote usage count."""
        conn = sqlite3.connect('databases/emotes.db')
        c = conn.cursor()
        name = (emote_name, )
        search = c.execute('SELECT * FROM emotes WHERE name=?', name)
        data = c.fetchall()

        if len(data) > 0:
            for emote in data:
                if emote[3] == 1.0:
                    print(f'{emote_name} has been used {int(emote[3])} time.')
                    await ctx.send(f'{emote_name} has been used {int(emote[3])} time.', delete_after=10.0)
                    await asyncio.sleep(10)
                    await ctx.message.delete()
                else:
                    print(f'{emote_name} has been used {int(emote[3])} times.')
                    await ctx.send(f'{emote_name} has been used {int(emote[3])} times.', delete_after=10.0)
                    await asyncio.sleep(10)
                    await ctx.message.delete()
        else:
            await ctx.send(f'{emote_name} doesn\'t appear to exist.')

    @commands.command(name='date')
    async def get_date_added(self, ctx, emote_name):
        '''Get the data an emote was added.'''
        conn = sqlite3.connect('databases/emotes.db')
        c = conn.cursor()
        name = (emote_name, )
        search = c.execute('SELECT * FROM emotes WHERE name=?', name)
        data = c.fetchall()

        if len(data) > 0:
            for emote in data:
                date = emote[4]
                await ctx.send(f'{emote_name} was added on {date}.')
        else:
            await ctx.send(f'{emote_name} doesn\'t appear to exist.')

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
        await ctx.send(msg)

    @commands.command(name='cullemotes')
    async def trim_low_use_emotes(self, ctx):
        '''Delete emotes with usage counts below a threshold.'''
        conn = sqlite3.connect('databases/emotes.db')
        c = conn.cursor()
        emotes = c.execute('SELECT * FROM emotes')
        data = c.fetchall()

        culled_emotes = []
        for i in data:
            if i[3] < 5:
                name = (i[0], )
                c.execute('DELETE FROM emotes WHERE name=?', name)
                culled_emotes.append(i[0])

        conn.commit()
        conn.close()

        config.emote_cache_updated = True

        msg = '**Deleted emotes**\n'
        for i in culled_emotes:
            msg = msg + f'{i}\n'
        await ctx.send(msg)

    @commands.command(name='convertdbs')
    async def convert_dbs(self, ctx):
        '''Convert dbs to have primary keys.'''
        # Convert dbs to use primary keys.
        conn = sqlite3.connect('flags.db')
        c = conn.cursor()
        try:
            c.execute('CREATE TABLE flags (name text, enabled integer)')
        except sqlite3.OperationalError as e:
            print(f'[WARN] Sqlite3 operational error: {e}. Skipping.')


def setup(bot):
    """Add cog to bot."""
    bot.add_cog(Emotes(bot))

# .r00
