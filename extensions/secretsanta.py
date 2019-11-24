#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Secret Santa extension for Kepler."""

import json
import random
from urllib.parse import urlparse

import aiosqlite
import asyncio
import discord
from discord.ext import commands

from paste_it import Paste_it

class SecretSanta(commands.Cog):
    """Secret Santa commands."""
    def __init__(self, bot):
        self.bot = bot
        self.task = self.bot.loop.create_task(self.check_db())

    async def check_db(self):
        """Create db if it doesn't exist."""
        async with aiosqlite.connect(f'databases/secretsanta.db') as db:
            await db.execute('CREATE TABLE IF NOT EXISTS participants (participant text PRIMARY KEY, participant_id integer, partner text, partner_id integer, link)')
            await db.commit()

    async def generate_participants(self):
        """Generate a list of all participants for Secret Santa."""
        guild = self.bot.guilds[0]
        role = guild.get_role(643634148988289054)
        users = role.members

        participants = {}
        for user in users:
            participants[user.name] = {}
            participants[user.name]['name'] = user.name
            participants[user.name]['id'] = user.id
            participants[user.name]['matched'] = False

        return participants

    @commands.has_any_role(472219677162995713)
    @commands.command(name='naughtylist', hidden=True)
    async def naughty_list_command(self, ctx):
        """Test command."""

        match_list = {
            'Olas': {
                'bad_matches': ['UrkaPls', 'Olas']
            },
            'Stephxieh': {
                'bad_matches': ['Olas', 'Stephxieh']
            },
            'feath3rz': {
                'bad_matches': ['feath3rz', 'UrkaPls']
            },
            'lun4r_dust': {
                'bad_matches': ['r00', 'lun4r_dust', 'UrkaPls']
            },
            'r00': {
                'bad_matches': ['lun4r_dust', 'r00', 'UrkaPls']
            },
            'poetaster': {
                'bad_matches': ['poetaster', 'UrkaPls']
            },
            'UrkaPls': {
                'bad_matches': ['Olas', 'UrkaPls']
            },
            'zevlag': {
                'bad_matches': ['zevlag', 'UrkaPls']
            },
            'EdDillinger': {
                'bad_matches': ['EdDillinger', 'UrkaPls']
            },
            'Kero': {
                'bad_matches': ['Kero', 'UrkaPls']
            },
            'autumn': {
                'bad_matches': ['autumn', 'UrkaPls']
            }
        }

        primaries = await self.generate_participants()
        secondaries = await self.generate_participants()

        count = 0
        loops = len(list(primaries.keys()))

        while count < loops:
            # Choose a random person from the list and remove it.
            i = random.choice(list(primaries.keys()))
            user = primaries[i]
            name = user['name']

            matched = False
            while not matched:
                # Choose a random partner
                i = random.choice(list(secondaries.keys()))
                partner = secondaries[i]

                # Force steph
                if user['name'] == 'Stephxieh':
                    partner = {'name': 'UrkaPls', 'id': 292046383752544256}


                if partner['name'] in match_list[user['name']]['bad_matches']:
                    continue
                else:
                    name = user['name']

                    async with aiosqlite.connect('databases/secretsanta.db') as db:
                        data = (user['name'], user['id'], partner['name'], partner['id'], None)
                        await db.execute('INSERT OR IGNORE INTO participants VALUES (?,?,?,?,?)', data)
                        await db.commit()

                    matched = True

                    del primaries[user['name']]
                    del secondaries[partner['name']]
                    count += 1

        self.bot.logger.info(f'{ctx.author.name} used {ctx.command}.')

    @commands.has_any_role(472219677162995713)
    @commands.command(name='notify', hidden=True)
    async def notify_command(self, ctx):
        """Notify users."""
        async with aiosqlite.connect('databases/secretsanta.db') as db:
            async with db.execute('SELECT * FROM participants') as cursor:
                users = await cursor.fetchall()

        for user in users:
            participant = self.bot.get_user(user[1])
            partner = user[2]
            msg1 = f':santa: **HO HO HO! IT\'S SECRET SANTA TIME!** :santa:\n\nI\'ve been hard at work making my list for this year and can reveal that you\'ve been matched with **{partner}**! There are a few things to do before you can get started on the Secret Santa event. Please read the following very carefully as it contains information on how the process will work as well as how to keep yourself private throughout.\n\n**Create your own wishlist**\nYou need to create your own wishlist. Visit <https://www.amazon.com/gp/registry/wishlist> and login. If you do not have an account, create one. Navigate to Account>Lists and create a new list with the following options:\n\n```This list is for: You\nChoose a list type: Wishlist\nList name: Secret Santa\nPrivacy: Public\nRecipient name: Your Discord username```\n\nOnce the list has been created, click the 3 dot menu and choose `Manage list`. Find the Shipping section and add your address. Check the boxes labelled `Third party shipping agreement` and `Don\'t spoil my surprise`. Lastly, change your account name to your Discord name, remove or change your account photo, and set any other lists to private. These options will hide your personal information during checkout. The one exception is that your city *will* be shown. Add items to the list bearing in mind a $25 price limit. It would be wise to add a variety of items from $1 to $25 so that your Secret Santa has many options.\n\n'
            msg2 = f'_ _\n_ _**Add your wishlist to the bot**\n You need to add your own wishlist to the bot so that others can find it. Run the command `.addwishlist link`. Link should be replaced with the link to your Amazon wishlist.\n\n**Buy items for your Secret Santa recipient**\nTo get the wishlist for {partner} please run `.wishlist` in the #secret-santa channel so that only participants can see it. This will print out all wishlists so be sure to find the one for your Secret Santa recipient. Once you have the list, I recommend spending no more than $25. But I\'m not your mother...I\'m Santa. I can\'t tell you what to do. If you want to buy {partner} a Ferrari, then fuck it! Do what you want.\n\n(╯°□°）╯︵ ┻━┻\n\n**Deadline**\nOrders must be completed by December 20th, 2019 at 12:00 am. Failure to follow through on your commitment to the Secret Santa event will result in permanent ban and public shaming. Lots and lots of public shaming. I\'m not above buying a TV ad to tell the world how shitty of a person you are. I will personally send Rudolph and his 8 shifty friends to shit on your grave.\n\nHappy Holidays,\n*The completely real (and totally not made up for commercial benefit) Santa*'
            await participant.send(msg1)
            await participant.send(msg2)

        self.bot.logger.info(f'{ctx.author.name} used {ctx.command}.')

    @commands.has_any_role(643634148988289054)
    @commands.command(name='addwishlist')
    async def add_wishlist_command(self, ctx, *, link):
        """Save a wishlist."""
        # Check url
        parsed = urlparse(link)
        if parsed.scheme:
            async with aiosqlite.connect('databases/secretsanta.db') as db:
                data = (link, ctx.author.name)
                await db.execute('UPDATE participants SET link=? WHERE participant=?', data)
                await db.commit()

            await ctx.send('Wishlist added!')
        else:
            await ctx.send('That doesn\'t look like a link.')

        self.bot.logger.info(f'{ctx.author.name} used {ctx.command}.')

    @commands.command(name='wishlist')
    async def wishlist_command(self, ctx):
        """Print all wishlists."""
        async with aiosqlite.connect('databases/secretsanta.db') as db:
            async with db.execute('SELECT * FROM participants') as cursor:
                users = await cursor.fetchall()

        msg = '**SECRET SANTA WISHLIST**\n\n**Nice List**'

        naughty = []
        for user in users:
            name = user[0]
            link = f'<{user[4]}>'

            if link.endswith('?ref_=wl_share>'):
                link = link.replace('?ref_=wl_share', '')

            if link == '<None>':
                naughty.append(name)
                # Add to naughty list.
            else:
                # Add to nice list.
                msg = f'{msg}\n{name}: {link}'

        # Add naughty users.
        msg = f'{msg}\n\n**Naughty List**'
        count = len(naughty)
        for user in naughty:
            if count == len(naughty):
                msg = f'{msg}\n{user}'
                count -= 1
            elif count == 1:
                msg = f'{msg}, and {user} have not added their wishlists. Guess who\'s getting coal!'
            else:
                msg = f'{msg}, {user}'
                count -= 1

        await ctx.send(msg)

        self.bot.logger.info(f'{ctx.author.name} used {ctx.command}.')

def setup(bot):
    """Add cog to bot."""
    bot.add_cog(SecretSanta(bot))

# .r00
