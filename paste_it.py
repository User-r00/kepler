#!usr/bin/env python3
# -*- coding: utf-8 -*-


"""Paste class for Kepler."""

import aiohttp
import json


class Paste_it():
    """Creates a new paste on a hastebin server."""

    async def new_paste(self, content):
        async with aiohttp.ClientSession() as session:
            async with session.post('http://r00b.in/documents',
                                    data=content.encode('utf-8')) as response:
                json = await response.json()
                link = json['key']
                return f'Results: <http://r00b.in/{link}>'

# .r00
