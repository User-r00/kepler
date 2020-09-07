#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Utility commands for Kepler."""

import json
import sqlite3

import aiosqlite
from config import config as C
import logging

import discord
from discord.ext import commands
from paste_it import Paste_it


class Roles(commands.Cog):
    """Role commands."""
    def __init__(self, bot):
        self.bot = bot
        self.db = 'roles'
        self.task = self.bot.loop.create_task(self.check_db(self.db, 'roles'))

    async def check_db(self, name, table):
        """Create db if it doesn't exist."""
        async with aiosqlite.connect(f'databases/{name}.db') as db:
            self.bot.logger.info(f'Creating {name} db with {table} table.')
            try:
                cmd = f'CREATE TABLE IF NOT EXISTS {table} (name text)'
                await db.execute(cmd)
                await db.commit()
            except OperationalError as e:
                print(f'[WARN] Sqlite3 operational error: {e}. Skipping.')

    @commands.has_any_role('Member')
    @commands.command(name='roleslist')
    async def roleslist_command(self, ctx):
        """List all self-joinable ranks."""
        # If the roleslist has changed since we last sent it in the server
        # then create a new paste with the updates.
        if C.role_cache_updated:
            async with aiosqlite.connect(f'databases/{self.db}.db') as db:
                async with db.execute('SELECT * FROM roles') as cursor:
                    data = await cursor.fetchall()

            msg = '[All available self-joinable Kepler Roles]\n\n'

            for i in data:
                msg = msg + f'{i[0]}\n'

            paste = Paste_it()
            role_list = await paste.new_paste(msg)
            C.role_cache_updated = False
            C.role_link = role_list
        else:
            # Otherwise send what is cached.
            role_list = C.role_link

        await ctx.send(role_list)

    @commands.has_any_role('Member')
    @commands.command(name='subscribe', aliases=['join', 'leave'])
    async def toggle_roll_command(self, ctx, *, role_name: str):
        """Add or remove requested role for a user."""
        role = discord.utils.get(ctx.guild.roles, name=role_name)

        # Check for role in DB.
        async with aiosqlite.connect(f'databases/{self.db}.db') as db:
            data = (role_name, )
            cmd = 'SELECT * FROM roles where name=?'
            async with db.execute(cmd, data) as cursor:
                joinable_roles = await cursor.fetchall()

            # If the role does not exist, abort.
            if len(joinable_roles) == 0:
                await ctx.send(f'The role {role_name} does not exist or it '
                               f'is not self-joinable. Use `.roleslist` to '
                               f'confirm.',
                               delete_after=C.DEL_DELAY)
                await ctx.message.delete(delay=C.DEL_DELAY)
                return

            # If there is more than one role matching, abort.
            # In theory, this should never happen. *shrug*
            if len(joinable_roles) > 1:
                await ctx.send(f'More than one result for {role_name}.'
                               f' Check with a moderator.',
                               delete_after=C.DEL_DELAY)
                await ctx.message.delete(delay=C.DEL_DELAY)
                return

            # Check if role is joinable.
            # role_joinable = joinable_roles[0][1]
            #
            # if role_joinable == 1:
            user_roles = ctx.author.roles
            if role in user_roles:
                await ctx.author.remove_roles(role)
                await ctx.send(f'You have left {role_name}.')
            else:
                await ctx.author.add_roles(role)
                await ctx.send(f'You have joined {role_name}.')

    @commands.has_any_role(C.MOD)
    @commands.command(name='createrole', aliases=['newrole', 'addrole'])
    async def createrole_command(self, ctx, role: str, color: discord.Colour):
        """Create self-joinable role."""
        # Check if role already exists.
        async with aiosqlite.connect(f'databases/{self.db}.db') as db:
            name = (role, )
            cmd = 'SELECT * FROM roles WHERE name=?'
            async with db.execute(cmd, name) as cursor:
                response = await cursor.fetchall()

            # If so, abort.
            if len(response) > 0:
                await ctx.send(f'The role {role} already exists.',
                               delete_after=C.DEL_DELAY)
                await ctx.message.delete(delay=C.DEL_DELAY)
                return

        # Create the role.
        await ctx.guild.create_role(name=role, color=color)

        # If the role is joinable, add it to the db.
        # if joinable:
        async with aiosqlite.connect(f'databases/{self.db}.db') as db:
            data = (role, )
            await db.execute('INSERT INTO roles VALUES (?)', data)
            await db.commit()

        await ctx.send(f'Created role {role}.')

        C.role_cache_updated = True

    @commands.has_any_role(C.MOD)
    @commands.command(name='deleterole', aliases=['delrole', 'removerole'])
    async def deleterole_command(self, ctx, *, role_name):
        """Delete self-joinable role."""
        # Check if the role exists in the Discord server.
        role = discord.utils.get(ctx.guild.roles, name=role_name)

        # If the role exists:
        if role:
            async with aiosqlite.connect(f'databases/{self.db}.db') as db:
                cmd = 'SELECT * FROM roles WHERE name=?'
                data = (role_name, )
                response = await db.execute(cmd, data)
                roles = await response.fetchall()

            if len(roles) > 1:
                await ctx.send(f'There are too many roles matching the name '
                               f'{role_name}. This needs to be handled '
                               f'manually.', delete_after=C.DEL_DELAY)
                await ctx.message.delete(delay=C.DEL_DELAY)
                return

            if len(roles) == 1:
                async with aiosqlite.connect(f'databases/{self.db}.db') as db:
                    cmd = 'DELETE FROM roles WHERE name=?'
                    await db.execute('DELETE FROM roles WHERE name=?', data)
                    await db.commit()
                await role.delete()
                C.role_cache_updated = True
                await ctx.send(f'Deleted role {role_name}.')
            else:
                await ctx.send(f'No roles matching `{role_name}` were '
                               f'found in the db.', delete_after=C.DEL_DELAY)
                await ctx.message.delete(delay=C.DEL_DELAY)
        else:
            await ctx.send(f'No roles matching `{role_name}` were '
                           f'found in Discord.', delete_after=C.DEL_DELAY)
            await ctx.message.delete(delay=C.DEL_DELAY)


def setup(bot):
    """Add cog to bot."""
    bot.add_cog(Roles(bot))

# .r00
