#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Utility commands for Kepler."""

import json
import sqlite3

import asyncio
import config
import logging

import discord
from discord.ext import commands
from paste_it import Paste_it


class Utilities(commands.Cog):
    """Utility commands."""
    def __init__(self, bot):
        self.bot = bot

        conn = sqlite3.connect('databases/roles.db')
        c = conn.cursor()
        try:
            c.execute('CREATE TABLE roles (name text, joinable int)')
        except sqlite3.OperationalError as e:
            print(f'[WARN] Sqlite3 operational error: {e}. Skipping.')

        conn.commit()
        conn.close()

    @commands.command(name='ping', aliases=['pet'])
    async def ping_command(self, ctx):
        """Ping the bot."""
        await ctx.channel.send('Pong', delete_after=5.0)
        self.bot.logger.info(f'{ctx.author} pinged the bot.')

    @commands.has_any_role('Member')
    @commands.command(name='roleslist')
    async def roleslist_command(self, ctx):
        """List all self-joinable ranks."""
        conn = sqlite3.connect('databases/roles.db')
        c = conn.cursor()
        data = c.execute('SELECT * FROM roles')

        if config.role_cache_updated:
            msg = '[All available self-joinable Kepler Roles]\n\n'

            for i in data:
                msg = msg + f'{i[0]}\n'

            paste = Paste_it()
            role_list = await paste.new_paste(msg)
            config.role_cache_updated = False
            config.role_link = role_list
        else:
            role_list = config.role_link

        await ctx.send(role_list)

    @commands.has_any_role('Member')
    @commands.command(name='subscribe')
    async def toggle_roll_command(self, ctx, *, role_name: str):
        """Add or remove requested role for a user."""
        role = discord.utils.get(ctx.guild.roles, name=role_name)

        if role is not None:
            roles = ctx.author.roles
            if role in roles:
                await ctx.author.remove_roles(role)
                await ctx.send(f'You have left {role_name}.')
            else:
                await ctx.author.add_roles(role)
                await ctx.send(f'You have joined {role_name}.')
        else:
            ctx.send('The role {role_name} doesn\'t seem to exist. Use '
                     '.roleslist to confirm.')

    @commands.has_any_role('Moderator')
    @commands.command(name='createrole', aliases=['newrole', 'addrole'])
    async def createrole_command(self, ctx, role: str, color: discord.Colour,
                                 joinable=False):
        """Create self-joinable role."""
        # Check if role exists.
        conn = sqlite3.connect('databases/roles.db')
        c = conn.cursor()

        name = (role, )
        search = c.execute('SELECT * FROM roles WHERE name=?', name)
        data = c.fetchall()

        if len(data) > 0:
            # Role already exists.
            await ctx.send('That role already exists.')
        else:
            # Create the role.
            print('Running createrole')
            await ctx.guild.create_role(name=role, color=color)

            print('Role created.')

            if joinable is not False:
                # Stash the role in the database.
                data = (role, joinable)
                c.execute('INSERT INTO roles VALUES (?,?)', data)
                conn.commit()
                conn.close()

            await ctx.send('Created role {}.'.format(role))

        config.role_cache_updated = True

    @commands.has_any_role('Moderator')
    @commands.command(name='deleterole', aliases=['delrole', 'removerole'])
    async def deleterole_command(self, ctx, *, role_name):
        """Delete self-joinable role."""
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        
        if role is not None:
            conn = sqlite3.connect('databases/roles.db')
            c = conn.cursor()

            name = (role_name, )
            search = c.execute('SELECT * FROM roles WHERE name=?', name)
            data = c.fetchall()

            if len(data) > 0:
                deleted = c.execute('DELETE FROM roles WHERE name=?', name)
            else:
                await ctx.send('That emote does not exist.')

            conn.commit()
            conn.close()

            config.role_cache_updated = True

            await ctx.send(f'Deleted role {role_name}.')
        else:
            await ctx.send(f'{role_name} does not exist.')


def setup(bot):
    """Add cog to bot."""
    bot.add_cog(Utilities(bot))

# .r00
