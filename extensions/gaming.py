#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""Gaming extension for Kepler."""

import asyncio
import aiohttp
import aiosqlite
from datetime import datetime
import random
import re

import discord
from discord.ext import commands

from config import config as C
from paste_it import Paste_it


class Gaming(commands.Cog):
    """Gaming commands."""

    def __init__(self, bot):
        """Init."""
        self.bot = bot
        self.task = self.bot.loop.create_task(self.check_db('gaming', 'nintendofriendcodes'))

    async def check_db(self, name, table):
        """Create db if it doesn't exist."""
        async with aiosqlite.connect(f'databases/{name}.db') as db:
            await db.execute('CREATE TABLE IF NOT EXISTS nintendofriendcodes (name text PRIMARY KEY, code text)')
            await db.commit()


    async def sanitize_code(self, code):
        """Santize a Nintendo friend code."""

        # Strip all non-numbers.
        code = re.sub('[^0-9]', '', code)

        # Check code length. Needs to be 12 to be valid.
        if code is None:
            return 'empty code'

        elif len(code) != 12:
            return 'invalid length'

        # Insert dashes to make all codes uniform.
        split_code = [char for char in code]
        split_code.insert(4, '-')
        split_code.insert(9, '-')

        sanitized_code = ''
        for i in split_code:
            sanitized_code = f'{sanitized_code}{i}'

        return sanitized_code


    @commands.command(name='savefc', aliases=['addfc', 'newfc', 'stashfc'])
    async def save_fc_command(self, ctx, code=None, user: discord.Member=None):
        """Save a friend code."""
        # If a friend code wasn't provided set the user to the message author.
        if user is None:
            user = ctx.author

        # If a code has not been provided then alert the user.
        if code is None:
            await ctx.send('You need to provide a friend code.', delete_after=C.DEL_DELAY)
            await ctx.message.delete(C.DEL_DELAY)
            self.bot.logger.info(f'{ctx.author.name} tried to add an empty friend code.')
            return

        code = await self.sanitize_code(code)

        if code == 'invalid length':
            await ctx.send('That code doesn\'t have enough digits.', delete_after=C.DEL_DELAY)
            await ctx.message.delete(delay=C.DEL_DELAY)
            self.bot.logger.info(f'{ctx.author.name} tried to save a friend code that is too short.')
            return

        if code == 'empty code':
            await ctx.send('A code was not provided.', delete_after=C.DEL_DELAY)
            await ctx.message.delete(delay=C.DEL_DELAY)
            self.bot.logger.info(f'{ctx.author.name} tried to save an empty friend code.')
            return

        # Otherwise, we have a good code and can continue.        
        async with aiosqlite.connect('databases/gaming.db') as db:
            data = (user.name, )
            async with db.execute('SELECT * FROM nintendofriendcodes WHERE name=?', data) as cursor:
                exists = await cursor.fetchall()

            # If a code exists then notify the user.
            if exists:
                await ctx.send(f'A friend code already exists for {user.name}.', delete_after=C.DEL_DELAY)
                await ctx.message.delete(delay=C.DEL_DELAY)
                self.bot.logger.info(f'{ctx.author.name} tried to add a friend for a user that already exists.')
                return

            # Check if the friend code already exists
            data = (code, )
            async with db.execute('SELECT * FROM nintendofriendcodes WHERE code=?', data) as cursor:
                exists = await cursor.fetchall()

            if exists:
                await ctx.send(f'The code {code} already belongs to someone.', delete_after=C.DEL_DELAY)
                await ctx.message.delete(delay=C.DEL_DELAY)
                self.bot.logger.info(f'{ctx.author.name} tried to add a friend code already belongs to someone.')
                return

            # Finally, add the code and notify the user.
            async with aiosqlite.connect('databases/gaming.db') as db:
                data = (user.name, code)
                await db.execute('INSERT INTO nintendofriendcodes VALUES (?,?)', data)
                await db.commit()
            await ctx.send(f'{user.name}\'s friend code saved.', delete_after=C.DEL_DELAY)
            await ctx.message.delete(delay=C.DEL_DELAY)
            self.bot.logger.info(f'{ctx.author.name} added {user}\'s friend code.')

    @commands.command(name='fc')
    async def fc_command(self, ctx, user: discord.Member=None):
        """Lookup a friend code."""
        # If a user isn't provided then assume we are looking up the message author.
        if user is None:
            user = ctx.author

        async with aiosqlite.connect('databases/gaming.db') as db:
            data = (user.name, )
            async with db.execute('SELECT code FROM nintendofriendcodes WHERE name=?', data) as cursor:
                codes = await cursor.fetchall()

                if len(codes) > 0:
                    for code in codes:
                        await ctx.send(f'{user.name}\'s friend code is `{code[0]}`.', delete_after=C.DEL_DELAY)
                        await ctx.message.delete(delay=C.DEL_DELAY)
                        self.bot.logger.info(f'{ctx.author.name} used {ctx.command} on {user.name}. Code successfully sent.')
                else:
                    await ctx.send(f'Unable to find a code for {user.name}.', delete_after=C.DEL_DELAY)
                    await ctx.message.delete(delay=C.DEL_DELAY)
                    self.bot.logger.info(f'{ctx.author.name} used {ctx.command}. No code was found.')

    @commands.command(name='fclist', aliases=['listfc', 'listfcs'])
    async def list_fc_command(self, ctx):
        """List all friend codes."""
        async with aiosqlite.connect('databases/gaming.db') as db:
            async with db.execute('SELECT * FROM nintendofriendcodes') as cursor:
                fcs = await cursor.fetchall()

                # Generate a string with all of the friend codes.
                msg = 'NINTENDO FRIEND CODES\n------------------------\n'
                for fc in fcs:
                    msg = f'{msg}\n{fc[0]}: {fc[1]}'

                # Make a new paste.
                paste = Paste_it()
                fclist = await paste.new_paste(msg)

                # Send the message.
                self.bot.logger.info(f'{ctx.author.name} used {ctx.command.name}.')
                await ctx.send(fclist, delete_after=C.DEL_DELAY)
                await ctx.message.delete(delay=C.DEL_DELAY)

    @commands.has_any_role(C.MOD)
    @commands.command(name='deletefc', aliases=['removefc', 'killfc'])
    async def delete_fc_command(self, ctx, user: discord.Member=None):
        """Delete a friend code."""
        # If a user isn't provided then assume we are looking up the message author.
        if user is None:
            user = ctx.author

        # Check if entry exists.
        async with aiosqlite.connect('databases/gaming.db') as db:
            data = (user.name, )
            async with db.execute('SELECT * FROM nintendofriendcodes WHERE name=?', data) as cursor:
                exists = await cursor.fetchall()

            if exists:
                # Delete entry
                data = (user.name, )
                await db.execute('DELETE FROM nintendofriendcodes WHERE name=?', data)
                await db.commit()

                # Notify user.
                await ctx.send(f'Deleted friend code for {user.name}.', delete_after=C.DEL_DELAY)
                await ctx.message.delete(delay=C.DEL_DELAY)
                self.bot.logger.info(f'{ctx.author.name} deleted the friend code for {user.name}.')
            else:
                await ctx.send(f'Unable to find a friend code for {user.name}.', delete_after=C.DEL_DELAY)
                await ctx.message.delete(delay=C.DEL_DELAY)
                self.bot.logger.info(f'{ctx.author.name} used {ctx.command.name}. No entries were found.')

    @commands.has_any_role(C.MOD)
    @commands.command(name='updatefc', aliases=['rewritefc', 'replacefc', 'overwritefc'])
    async def overwrite_fc_command(self, ctx, code=None, user: discord.Member=None):
        """Replace a friend code."""
        # If a friend code wasn't provided set the user to the message author.
        if user is None:
            user = ctx.author

        # If a code has not been provided then alert the user.
        if code is None:
            await ctx.send('You need to provide a friend code.', delete_after=C.DEL_DELAY)
            await ctx.message.delete(delay=C.DEL_DELAY)
            self.bot.logger.info(f'{ctx.author.name} tried to overwrite with an empty friend code.')
            return

        code = await self.sanitize_code(code)

        if code == 'invalid length':
            await ctx.send('That code doesn\'t have enough digits.', delete_after=C.DEL_DELAY)
            await ctx.message.delete(C.DEL_DELAY)
            self.bot.logger.info(f'{ctx.author.name} tried to overwrite a friend code that is too short.')
            return

        if code == 'empty code':
            await ctx.send('A code was not provided.', delete_after=C.DEL_DELAY)
            await ctx.message.delete(delay=C.DEL_DELAY)
            self.bot.logger.info(f'{ctx.author.name} tried to update an empty friend code.')
            return

        # Otherwise, we have a good code and can continue.        
        async with aiosqlite.connect('databases/gaming.db') as db:
            data = (user.name, )
            async with db.execute('SELECT * FROM nintendofriendcodes WHERE name=?', data) as cursor:
                exists = await cursor.fetchall()

            # If a user/code exists then update it.
            if exists:
                # Update the entry in the db.
                data = (code, user.name)
                await db.execute('UPDATE nintendofriendcodes SET code=? WHERE name=?', data)
                await db.commit()

                # Notify the user.
                await ctx.send(f'{user.name}\'s code updated.', delete_after=C.DEL_DELAY)
                await ctx.message.delete(delay=C.DEL_DELAY)
                self.bot.logger.info(f'{ctx.author.name} updated {user.name}\'s friend code.')
            else:
                # Notify user that the user didn't exist.
                await ctx.send(f'No codes found for {user.name}.', delete_after=C.DEL_DELAY)
                await ctx.message.delete(delay=C>DEL_DELAY)
                self.bot.logger.info(f'{ctx.author.name} tried to update {user.name}\'s friend code but one didn\'t exist.')
                return

def setup(bot):
    bot.add_cog(Gaming(bot))
