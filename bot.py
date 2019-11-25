#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Kepler - A discord bot for r00m 8.

This bot has been created specifically for the r00m 8 community. It
provides tools for moderation, and entertainment.

Please direct any questions to u/r00__.
"""

import json
import os
import sqlite3

import asyncio
import logging

import discord
from discord.ext import commands
from config import config as C
from credentials import tokens as TOKENS

# Extensions to load at runtime.
startup_extensions = ['extensions.emotes',
                      'extensions.errors',
                      'extensions.fmk',
                      'extensions.gaming',
                      'extensions.general',
                      'extensions.moderator',
                      'extensions.movies',
                      'extensions.onboarding',
                      'extensions.roles',
                      'extensions.secretsanta',
                      'extensions.twitch',
                      'extensions.watchlist']


def get_prefix(bot, message):
    """Get the callable prefix for the bot."""
    prefixes = [C.PREFIX]

    # If we are in a guild, we allow for the user to mention us or use any of
    # the prefixes.
    return commands.when_mentioned_or(*prefixes)(bot, message)


bot = commands.Bot(command_prefix=get_prefix, description=C.DESCRIPTION)

# Setup logger.
logger = logging.getLogger('Kepler')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='kepler.log',
                              encoding='utf-8',
                              mode='a')
# form = '%(asctime)s:%(levelname)s:%(name)s:%(message)s'
log_form = '%(asctime)s | %(levelname)s | %(message)s'
handler.setFormatter(logging.Formatter(log_form))
logger.addHandler(handler)
bot.logger = logger


@bot.event
async def on_ready():
    """Run when bot loads."""
    # Create database folder if it doesnt' exist.
    if not os.path.isdir('databases'):
            print('[WARN] Databases folder does not exist. Creating it.')
            os.makedirs('databases')

    bot.logger.info(f'\nLogged in as: {bot.user.name}\n')

    # Set bot presence
    await bot.change_presence(activity=discord.Game(name=C.PRESENCE))


@bot.event
async def on_message(message):
    """Run when a new message is received."""
    # Ignore messages from the bot
    if message.author == bot.user:
        return

    # Monitor Terminal channel and delete anything that isn't our command.
    if message.channel.id == 577021097116041216:
        if message.content != '.join_r00m':
            await message.channel.send('Enter .join_r00m.',
                                       delete_after=10.0)
            await asyncio.sleep(10)
            await message.delete()

    # Check for bot command
    if message.content.startswith(C.PREFIX):
        emote_name = message.content.split(C.PREFIX)[1]

        conn = sqlite3.connect('databases/emotes.db')
        c = conn.cursor()

        try:
            # Fetch emote.
            name = (emote_name, )
            search = c.execute('SELECT * FROM emotes WHERE name=?', name)
            data = c.fetchone()

            if data is not None:
                # Send emote.
                with open(data[2], 'rb') as f:
                    await message.channel.send(file=discord.File(f))

                # Update emote usage.
                data = (data[3] + 1, emote_name)
                c.execute('UPDATE emotes SET count=? WHERE name=?', data)
                bot.logger.info(f'Emote {emote_name} usage updated.')

        except (sqlite3.IntegrityError, TypeError) as e:
            bot.logger.error(f'[WARN] {e}.')

        conn.commit()
        conn.close()

    # Allows bot to continue processing commands. Required.
    await bot.process_commands(message)


# Load the bot extensions.
if __name__ == '__main__':
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            bot.logger.error(f'[ERR] Can\'t load extension {extension}\n{exc}')
            print(f'[ERR] Can\'t load extension {extension}\n{exc}')

# Run the bot
bot.run(C.TOKEN, bot=True, reconnect=True)

# .r00
