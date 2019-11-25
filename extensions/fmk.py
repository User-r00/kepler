#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""Fuck, marry, kill extension for Kepler."""

import random

import aiosqlite
import discord
from discord.ext import commands

from config import config as C
from paste_it import Paste_it


class FMK(commands.Cog):
    """Fuck, marry, kill game."""

    def __init__(self, bot):
        """Init."""
        self.bot = bot
        self.task = self.bot.loop.create_task(self.check_db())
        self.task = self.bot.loop.create_task(self.populate_db())

    async def check_db(self):
        """Create db if it doesn't exist."""
        async with aiosqlite.connect(f'databases/fmk.db') as db:
            await db.execute('CREATE TABLE IF NOT EXISTS names (name text PRIMARY KEY)')
            await db.commit()

    async def capitalize_name(self, name):
        """Capitalize a name."""
        # Drop the name to lowercase and split into separate words.
        words = name.lower().split(' ')

        # Create and empty store for later.
        store = []

        # Capitalize each word and add it to the result store.
        for word in words:
            store.append(word.capitalize())

        # Repackage store into final name.
        return ' '.join(store)

    async def populate_db(self):
        """Populate the name db with a default set."""
        names = ['Jessica Alba',
                 'Scarett Johansson'
                 'Megan Fox',
                 'Mila Kunis',
                 'Natalie Portman',
                 'Angelina Jolie',
                 'Adriana Lima',
                 'Selena Gomez',
                 'Shakira',
                 'Emma Watson',
                 'Eve Mendes',
                 'Charlize Theron',
                 'Keira Knightley',
                 'Halle Berry',
                 'Jessica Biel',
                 'Hayden Panettiere',
                 'Margot Robbie',
                 'Gal Gadot',
                 'Katy Perry',
                 'Emma Stone',
                 'Olivia Wilde',
                 'Taylor Swift',
                 'Anne Hathaway',
                 'Jennifer Lawrence',
                 'Kristen Bell',
                 'Rachel McAdams',
                 'Blake Lively',
                 'Zooey Deschanel',
                 'Alexandra Daddario',
                 'Ariana Grande',
                 'Emily Blunt',
                 'Chloë Grace Moretz',
                 'Anna Kendrick',
                 'Zac Efron',
                 'Chris Hemsworth',
                 'Chris Evans',
                 'Channing Tatum',
                 'Ian Somerhalder',
                 'Ryan Reynolds',
                 'Liam Hemsworth',
                 'James Franco',
                 'David Beckham',
                 'Bradley Cooper',
                 'Leonardo DiCaprio',
                 'Johnny Depp',
                 'Brad Pitt',
                 'Ryan Gosling',
                 'Robert Downey Jr.',
                 'Chris Pratt',
                 'Adam Levine',
                 'Tom Hiddleston',
                 'Hugh Jackman',
                 'Heath Ledger',
                 'Orlando Bloom',
                 'James McAvoy',
                 'Henry Cavill',
                 'Justin Timberlake',
                 'Jude Law',
                 'Nick Jonas',
                 'Taylor Lautner',
                 'Christian Slater',
                 'Alan Rickman',
                 'Tom Cruise',
                 'Mark Ruffalo',
                 'Dave Franco',
                 'Michael Fassbender',
                 'Daniel Radcliffe',
                 'Christian Bale',
                 'Kanye West',
                 'Mr. T',
                 'Jim Carrey',
                 'Ben Stiller',
                 'Robin Williams',
                 'Adam Sandler',
                 'Will Ferrell',
                 'Sacha Baron Cohen',
                 'Jack Black',
                 'Maggie Smith',
                 'Severus Snape',
                 'Harry Potter',
                 'Taron Egerton'
            ]

        async with aiosqlite.connect('databases/fmk.db') as db:
            for name in names:
                data = (name, )
                await db.execute('INSERT OR IGNORE INTO names VALUES (?)', data)
                await db.commit()


    @commands.command(name='addname')
    async def add_name_command(self, ctx, *, name):
        """Save a new name to the FMK list."""
        # Parse the name.
        name = await self.capitalize_name(name)

        # Save to db.
        async with aiosqlite.connect('databases/fmk.db') as db:
            data = (name, )
            await db.execute('INSERT OR IGNORE INTO names VALUES (?)', data)
            await db.commit()

        # Notify server.
        await ctx.send(f'{name} added to the FMK list.',
                       delete_after=C.DEL_DELAY)
        await ctx.message.delete(delay=C.DEL_DELAY)
        self.bot.logger.info(f'{ctx.author} added {name} to the FMK list.')

    @commands.command(name='deletename')
    async def delete_name_commmand(self, ctx, *, name):
        """Delete a name from the FMK list."""
        # Parse the name.
        name = await self.capitalize_name(name)

        # Delete from DB if the name exists.
        async with aiosqlite.connect('databases/fmk.db') as db:
            data = (name, )
            async with db.execute('SELECT * FROM names WHERE name=?', data) as cursor:
                exists = await cursor.fetchall()
            if exists:
                async with aiosqlite.connect('databases/fmk.db') as db:
                    data = (name, )
                    await db.execute('DELETE FROM names WHERE name=?', data)
                    await db.commit()
                await ctx.send(f'{name} removed from the FMK list.', 
                               delete_after=C.DEL_DELAY)
                await ctx.message.delete(delay=C.DEL_DELAY)
                self.bot.logger.info(f'{ctx.author} removed {name} from the FMK list.')
            else:
                await ctx.send(f'{name} does not appear to exist in the FMK list.',
                               delete_after=C.DEL_DELAY)
                await ctx.message.delete(delay=C.DEL_DELAY)
                self.bot.logger.info(f'{ctx.author} tried to remove {name} from the FMK list but it doesn\'t exist.')

    @commands.command(name='fmk')
    async def fmk_command(self, ctx):
        """Fuck, marry, kill game."""
        # Connect to the FMK db and get all names.
        async with aiosqlite.connect('databases/fmk.db') as db:
            async with db.execute('SELECT * FROM names') as cursor:
                data = await cursor.fetchall()

        # Generate a list of all names.
        names = [name[0] for name in data]

        # Empty store for names.
        store = []

        # If Autumn is playing.
        if ctx.author.id == 240287770512326657:
            store.append('Christian Slater')

        # Select three names from the list and store them.
        while len(store) < 3:
            name = random.choice(names)
            if name in store:
                continue
            else:
                store.append(name)

        # Format message to send.
        msg = f'**Fuck, marry, kill**\n{store[0]}, {store[1]}, and {store[2]}.'
        await ctx.send(msg)

        # Log the usage.
        self.bot.logger.info(f'{ctx.author} used {ctx.command.name}.')


def setup(bot):
    bot.add_cog(FMK(bot))
